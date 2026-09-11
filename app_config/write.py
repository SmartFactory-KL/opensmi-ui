import shlex
from pathlib import Path
from typing import Annotated, get_args, get_origin, get_type_hints

from app_config.app_config import AppConfig, AppConfigEntry
from app_config.read import AppConfigError, get_env_name, visit_config_entries

_CONFIG_DOCS_PATH = Path("docs/config")


def write_config_documentation(
    config: AppConfig,
    env_prefix: str | None = None,
    output_dir: Path = Path("docs/config"),
):
    """Creates both yaml example and markdown docs for configuration"""
    write_config_yaml_example(config, output_dir=output_dir)
    write_config_markdown(config, env_prefix, output_dir=output_dir)


def write_config_yaml_example(
    config: AppConfig, output_dir: Path = Path("docs/config")
) -> None:
    """Creates docs/config/config.yml.example with documented configuration entries."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "config.example.yml"

    lines = []

    def visit(field_name: str, entry: AppConfigEntry) -> None:
        type_hints = get_type_hints(AppConfig, include_extras=True)
        value_type = _get_unwrapped_type(type_hints[field_name])
        default_value = getattr(config, field_name)

        lines.append(f"# {entry.description}")
        lines.append(f"# Type: {_format_type_annotation(value_type)}")
        lines.append(f"# Is Secret: {entry.is_secret}")
        lines.append(f"{field_name}: {_format_yaml_value(default_value)}")
        lines.append(" ")

    visit_config_entries(config, visit)

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_config_markdown(
    config: AppConfig,
    env_prefix: str | None = None,
    output_dir: Path = Path("docs/config"),
) -> None:
    """Creates docs/config/config.md with configuration documentation and examples."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "DefaultConfiguration.md"

    type_hints = get_type_hints(AppConfig, include_extras=True)

    entries: list[tuple[str, AppConfigEntry]] = []

    def collect_entry(field_name: str, entry: AppConfigEntry) -> None:
        entries.append((field_name, entry))

    visit_config_entries(config, collect_entry)

    lines = [
        "# Application Configuration",
        "",
        "## Configuration",
        "",
        "| ENV | Variable | Type | Default | Is Secret | Description |",
        "|---|---|---|---|---|---|",
    ]

    for field_name, entry in entries:
        value_type = _get_unwrapped_type(type_hints[field_name])
        default_value = getattr(config, field_name)
        env_name = get_env_name(env_prefix, field_name)

        lines.append(
            "| "
            f"{env_name} | "
            f"{field_name} | "
            f"`{_format_type_annotation(value_type)}` | "
            f"`{_format_yaml_value(default_value)}` | "
            f"{entry.is_secret} | "
            f"{entry.description} |"
        )

    lines.extend(
        [
            "",
            "## Docker Compose",
            "",
            "Example environment block using the default values:",
            "",
            "```yaml",
            "environment:",
        ]
    )

    for field_name, entry in entries:
        default_value = getattr(config, field_name)
        env_name = get_env_name(env_prefix, field_name)

        lines.append(f"  {env_name}: {_format_yaml_value(default_value)}")

    lines.extend(
        [
            "```",
            "",
            "## Docker Run",
            "",
            "Example `docker run` command using the default values:",
            "",
            "```bash",
            "docker run \\",
        ]
    )

    docker_envs = []

    for field_name, entry in entries:
        default_value = getattr(config, field_name)
        env_name = get_env_name(env_prefix, field_name)

        docker_envs.append(f"-e {env_name}={shlex.quote(str(default_value))}")

    for index, env in enumerate(docker_envs):
        suffix = " \\" if index < len(docker_envs) - 1 else ""
        lines.append(f"  {env}{suffix}")

    lines.append("  your-image:latest")
    lines.append("```")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _get_unwrapped_type(value_type: object) -> object:
    """Returns the actual type from an Annotated type."""
    if get_origin(value_type) is Annotated:
        return get_args(value_type)[0]

    return value_type


def _format_type_annotation(value_type: object) -> str:
    """Returns a readable representation of a configuration type."""
    value_type = _get_unwrapped_type(value_type)

    if value_type is str:
        return "str"

    if value_type is int:
        return "int"

    if value_type is float:
        return "float"

    if value_type is bool:
        return "bool"

    raise AppConfigError(f"Unsupported configuration type {value_type}")


def _format_yaml_value(value: object) -> str:
    """Formats a value as a single-line YAML value."""
    if isinstance(value, str):
        return f'"{value!s}"'

    return f"{value!s}"
