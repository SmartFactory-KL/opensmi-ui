import os
import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields, replace
from enum import Enum
from pathlib import Path
from typing import Annotated, get_args, get_origin, get_type_hints

import yaml

from app_config.app_config import AppConfig, AppConfigEntry


class AppConfigSource(Enum):
    ENV = "env"
    YAML = "yaml"


class AppConfigError(Exception):
    """Raised when the provided input has invalid content"""


class AppConfigWarning(UserWarning):
    """Warning raised for uncommon use of configuration"""


AppConfigVisitor = Callable[[str, str], None]
AppConfigEntryVisitor = Callable[[str, AppConfigEntry], None]


@dataclass
class AppConfigOptions:
    env_prefix: str | None = None
    """prefix to use to read environment variables. Should be UPPER_SNAKE_CASE."""
    yaml_path: Path | str | None = None
    """Path to read YAML values from. Defaults to ./(config)/config.y(a)ml if not set"""
    overwrite: Mapping[str, str] | None = None
    """Mapping to overwrite any existing values. Mostly useful for testing, not intended for production use"""


def read_configuration(
    sources: AppConfigSource | Sequence[AppConfigSource],
    options: AppConfigOptions | None = None,
) -> AppConfig:
    """Read application configuration from at least one source

    Sources are read in the provided order, with later values overwriting previos ones.
    If no values are provided the default values of AppConfig will be used.
    Note that ENV will only read UPPER_SNAKE_CASE variants of the name with a prefix as defined.

    Args:
        sources: list of sources to read

        options: further options like env_prefix and yaml_path and overwrites for tests

    Returns:
        The resulting application configuration

    Raises:
        AppConfigError: whenever the provided value is invalid
    """
    if isinstance(sources, AppConfigSource):
        sources = [sources]

    config = AppConfig()

    if not sources:
        warnings.warn(
            "No configuration sources defined. This is fine for testing but may be unintentional in production.",
            AppConfigWarning,
            stacklevel=2,
        )

    for source in sources:
        if source == AppConfigSource.ENV:
            config = _read_env(config, options)
        elif source == AppConfigSource.YAML:
            config = _read_yaml(config, options)
        else:
            raise AppConfigError(f"Unsupported source: {source}")

    if options is not None and options.overwrite is not None:
        config = _apply_overwrite(config, options.overwrite)

    return config


def visit_config_entries(config: AppConfig, visitor: AppConfigEntryVisitor):
    """Runs the method once for every configuration entry without the actual value. Intended to generate documentation."""
    type_hints = get_type_hints(AppConfig, include_extras=True)

    for field in fields(config):
        entry = _get_config_entry(type_hints[field.name])
        if entry is None:
            continue
        visitor(field.name, entry)


def visit_config_strings(config: AppConfig, visitor: AppConfigVisitor):
    """Runs visitor once for every tuple of [key:str, value:str] for the configuration. Masks anything marked with is_secret."""
    type_hints = get_type_hints(AppConfig, include_extras=True)

    for field in fields(config):
        field_name = field.name
        field_metadata = _get_config_entry(type_hints[field.name])
        field_value = str(getattr(config, field.name))

        if field_metadata is not None and field_metadata.is_secret:
            field_value = f"Masked[len:{len(field_value)}]"

        visitor(field_name, field_value)


def _read_env(config: AppConfig, options: AppConfigOptions | None) -> AppConfig:
    """Reads the environment while using a possible env_prefix in UPPER_SNAKE_CASE"""
    prefix = options.env_prefix if options is not None else None
    type_hints = get_type_hints(AppConfig, include_extras=True)

    values: dict[str, object] = {}

    for field in fields(config):
        env_name = get_env_name(prefix, field.name)
        val = os.environ.get(env_name, None)

        if val is None:
            continue

        try:
            values[field.name] = _parse_value_from_string(
                val,
                type_hints[field.name],
            )
        except Exception as e:
            raise AppConfigError(f"Failed to parse {env_name} from ENV: {e}") from e

    return replace(config, **values)


def _read_yaml(config: AppConfig, options: AppConfigOptions | None) -> AppConfig:
    """Reads configuration from a flat yaml file"""
    yaml_path = _get_yaml_path(options)

    if yaml_path is None:
        raise AppConfigError("YAML was used as source, but no yaml file was found")

    try:
        with yaml_path.open("r", encoding="utf-8") as file:
            values = yaml.safe_load(file)
    except OSError as e:
        raise AppConfigError(
            f"Failed to read YAML configuration from {yaml_path}: {e}"
        ) from e
    except yaml.YAMLError as e:
        raise AppConfigError(
            f"Failed to parse YAML configuration from {yaml_path}: {e}"
        ) from e

    if values is None:
        return config

    if not isinstance(values, Mapping):
        raise AppConfigError(
            f"Expected YAML configuration to contain a mapping, but got {type(values).__name__}"
        )

    type_hints = get_type_hints(AppConfig, include_extras=True)
    parsed_values: dict[str, object] = {}

    for field in fields(config):
        try:
            if field.name not in values:
                continue

            value = values[field.name]
            if value is None:
                continue

            parsed_values[field.name] = _parse_value(value, type_hints[field.name])
        except Exception as e:
            raise AppConfigError(f"Failed to parse {field.name} from YAML: {e}") from e

    return config


def _apply_overwrite(config: AppConfig, values: Mapping[str, str]) -> AppConfig:
    """Uses the string mapping as ENV to write configuration. Intended for testing."""
    type_hints = get_type_hints(AppConfig, include_extras=True)
    config_fields = {field.name for field in fields(config)}

    parsed_values: dict[str, object] = {}

    for name, value in values.items():
        if name not in config_fields:
            raise AppConfigError(f"Unknown configuration field in overwrite: {name}")

        try:
            parsed_values[name] = _parse_value_from_string(
                value,
                type_hints[name],
            )
        except Exception as e:
            raise AppConfigError(f"Failed to parse overwrite for {name}: {e}") from e

    return replace(config, **parsed_values)


def get_env_name(prefix: str | None, field_name: str) -> str:
    """Returns MY_PREFIX_FIELD_NAME from MY_PREFIX and the fields name"""
    name = field_name.upper()

    if prefix is None or len(prefix.strip()) == 0:
        return name

    return f"{prefix.rstrip('_')}_{name}"


def _get_yaml_path(options: AppConfigOptions | None) -> Path | None:
    """Returns either the set yaml_path in options or the first found path for (config)/config.y(a)ml.
    Returns None if no path was found"""
    if options is not None and options.yaml_path is not None:
        return Path(options.yaml_path)

    candidates = (
        Path("config.yaml"),
        Path("config.yml"),
        Path("config", "config.yaml"),
        Path("config", "config.yml"),
    )

    for yaml_path in candidates:
        if yaml_path.is_file():
            return yaml_path

    return None


def _parse_value_from_string(value: str, value_type: object) -> object:
    """Parses a string to either str, int, float or bool. Other types are not supported."""
    if get_origin(value_type) is Annotated:
        value_type = get_args(value_type)[0]

    if value_type is str:
        return value

    if value_type is int:
        return int(value)

    if value_type is float:
        return float(value)

    if value_type is bool:
        normalized = value.lower()
        return normalized in {"true", "1", "yes", "on"}

    raise AppConfigError(f"Unsupported configuration type {value_type}")


def _parse_value(value: object, value_type: object) -> object:
    """Parses more generic input to either str, int, float or bool. Other types are not supported."""
    if get_origin(value_type) is Annotated:
        value_type = get_args(value_type)[0]

    if isinstance(value, str):
        return _parse_value_from_string(value=value, value_type=value_type)

    if value_type is int and isinstance(value, int) and not isinstance(value, bool):
        return value

    if (
        value_type is float
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    ):
        return float(value)

    if value_type is bool and isinstance(value, bool):
        return value

    raise AppConfigError(
        f"Invalid value: expected {value_type}, got {type(value).__name__}"
    )


def _get_config_entry(value_type: object) -> AppConfigEntry | None:
    """Returns the AppConfigEntry metadata of a field if it exists"""
    args = get_args(value_type)

    if get_origin(value_type) is not Annotated:
        return None

    for metadata in args[1:]:
        if isinstance(metadata, AppConfigEntry):
            return metadata

    return None
