import logging
import os
import typing

import yaml

# This module does not use the uvicorn logger
# as that does not exist yet when config is loaded
# also disable propagate to prevent duplicat messages on root logger
logger = logging.getLogger("fastapi_cli")
logger.propagate = False

# These keys of the configuration are masked for the debugging output
MASKED_KEYS = ["OPC_UA_DEFAULT_SERVER_PASSWORD", "PIN_GUARD_PIN"]

# Default values with descriptions
_default_configuration = [
    {
        "key": "APP_VERSION",
        "default": "25.06-dev-local",
        "description": "Version to be shown in frontend. Should be set by some pipeline",
    },
    {
        "key": "SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA",
        "default": "false",
        "description": "If this flag is set, only the OPC_UA_DEFAULT_xxx data will be used for connecting. Other user data is simply ignored.",
    },
    {
        "key": "SERVER_ENABLE_AUTO_CONNECT",
        "default": "false",
        "description": "If this flag is set, the server will automatically try to connect on startup using the provided OPC_UA_DEFAULT_xxx data",
    },
    {
        "key": "OPC_UA_DEFAULT_SERVER_URL",
        "default": "opc.tcp://localhost:4843",
        "description": "URL of the OPC UA to connect to",
    },
    {
        "key": "OPC_UA_DEFAULT_SERVER_USERNAME",
        "default": "operator",
        "description": "Default username for OPC UA (might be overwritten by localStorage in client)",
    },
    {
        "key": "OPC_UA_DEFAULT_SERVER_PASSWORD",
        "default": "operator",
        "description": "Default password for OPC UA (might be overwritten by localStorage in client)",
    },
    {
        "key": "OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS",
        "default": "5",
        "description": "Default timeout in seconds used for connection request of pyuaadapter connect method",
    },
    {
        "key": "LOCKING_ENABLED",
        "default": "true",
        "description": "If set, lock actions (toggle, break) will be usable. Only disable for read-only applications. To protect against unintended usage, please use PIN_GUARD.",
    },
    {
        "key": "LOCKING_SIMULATION_ENABLED",
        "default": "false",
        "description": "If set, locking will only be simulated on the backend, no actual lock requests are sent to the OPC UA server. Intended for OPC UA servers, that do not support locking while still having the nodes for it.",
    },
    {
        "key": "LOCKING_AUTOFREE_DELAY_SECONDS",
        "default": "180",
        "description": "Timeout for the automated freeing of a machine after any action has occured.",
    },
    {
        "key": "PIN_GUARD_ENABLED",
        "default": "false",
        "description": "If set to true, all write actions are only allowed after the PIN_GUARD_PIN has been entered. Will auto-lock after PIN_GUARD_AUTOLOCK_DELAY_MS has passed.",
    },
    {
        "key": "PIN_GUARD_AUTOLOCK_DELAY_SECONDS",
        "default": "180",
        "description": "Amount of seconds with no action, after which the PIN_GUARD will be automatically locked.",
    },
    {
        "key": "PIN_GUARD_PIN",
        "default": "123321",
        "description": "Digit-based PIN (usually 6 digits) to unlock the Locking feature. Only needed, if SERVER_LOCKING_MODE is set to UI_PIN. Empty PINs are not allowed (have at least 1 digit).",
    },
]


# Config containing the values
# Will be filled with all default values from _default_configuration
configuration = {}

# Important: Keep these up-to-date for autocomplete of app_config methods
ConfigKey = typing.Literal[
    "APP_VERSION",
    "ENABLE_OPENAPI_EXPORT_ON_STARTUP",
    "SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA",
    "SERVER_ENABLE_AUTO_CONNECT",
    "OPC_UA_DEFAULT_SERVER_URL",
    "OPC_UA_DEFAULT_SERVER_USERNAME",
    "OPC_UA_DEFAULT_SERVER_PASSWORD",
    "OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS",
    "LOCKING_ENABLED",
    "LOCKING_SIMULATION_ENABLED",
    "LOCKING_AUTOFREE_DELAY_SECONDS",
    "PIN_GUARD_ENABLED",
    "PIN_GUARD_AUTOLOCK_DELAY_SECONDS",
    "PIN_GUARD_PIN",
]


def init_config_values():
    """
    Generate configuration by reading default config and applying environment variables to it
    """
    for idx in _default_configuration:
        configuration[idx["key"]] = idx["default"]

    for env_key in os.environ:
        for config_key, _ in configuration.items():
            if env_key.upper() == config_key:
                configuration[config_key] = os.getenv(env_key)

    # if there exists a config.yml file, this will take max priority
    if os.path.exists("config.yml"):
        read_yaml_values("config.yml")
    elif os.path.exists("config.yaml"):
        read_yaml_values("config.yaml")
    else:
        logger.info("No config.yml found")


def read_yaml_values(file_path):
    with open(file_path, "r") as config_stream:
        logger.info(f"Found {file_path}")
        try:
            yaml_input = yaml.load(config_stream, Loader=yaml.loader.BaseLoader)
            if yaml_input is not None:
                for env_key, env_val in yaml_input.items():
                    for config_key, _ in configuration.items():
                        if env_key.upper() == config_key:
                            configuration[config_key] = env_val
            else:
                logger.warning(f"{file_path} is present but contains no entries")
        except yaml.YAMLError as e:
            logger.warning(e)


def log_configuration(logger_to_use: logging.Logger):
    """
    Log configuration to the specified logger.
    logger_to_use needs to be specified, as app_config uses the fastapi_cli logger directly,
    since uvicorn logger is not available until of fastapi started
    """
    logger_to_use.info("#####################")
    logger_to_use.info("## Configuration ####")
    for config_key, config_value in configuration.items():
        logger_to_use.info(f"# - {config_key} : {config_value}")
    logger_to_use.info("#####################")


def create_configuration_documentation(file_path: str = "docs/DefaultConfiguration.md"):
    """
    Create or update DefaultConfiguration.md with the default configuration from above.
    This is only intended to be used within a config documentation refresh script.
    """

    with open(file_path, "w", encoding="utf-8") as config_documentation_md:
        config_documentation_md.write("# Default Configuration Overview\n\n")
        config_documentation_md.write("| Key | Default | Description |\n")
        config_documentation_md.write("| --- | --- | --- |\n")

        for line in _default_configuration:
            config_documentation_md.write(
                f"| {line['key']} | {line['default']} | {line['description']} | \n"
            )


def get_masked_configuration() -> dict:
    """
    This creates a dict copy of configuration where all MASKED_KEYS are masked.
    Useful for debugging info within the frontend
    """
    output = {}

    for key, val in configuration.items():
        if key in MASKED_KEYS:
            output[key] = f"[masked] - length {len(val)}"
        else:
            output[key] = val

    return output


def get_text(key: ConfigKey) -> str:
    """
    Get config setting as string. Raises KeyError if key is not present.
    """
    if key in configuration:
        return configuration[key]
    raise KeyError(f"Configuration key {key} does not exist")


def get_int(key: ConfigKey) -> int:
    """
    Get config setting as int. Raises KeyError if key is not present.
    """
    if key in configuration:
        return int(configuration[key])
    raise KeyError(f"Configuration key {key} does not exist")


def get_float(key: ConfigKey) -> float:
    """
    Get config setting as float. Raises KeyError if key is not present.
    """
    if key in configuration:
        return float(configuration[key])
    raise KeyError(f"Configuration key {key} does not exist")


def is_set(key: ConfigKey) -> bool:
    """
    Returns true, if the key is True, true, yes, 1 or on
    """
    if key in configuration:
        if (configuration[key]).lower() in ["true", "yes", "1", "on"]:
            return True
        return False
    raise KeyError(f"Configuration key {key} does not exist")
