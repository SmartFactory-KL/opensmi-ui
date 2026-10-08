import sys

import appysetty
from appysetty.read import visit_config_strings
from dotenv import load_dotenv

from opensmi_ui.app_config.config import AppConfig
from opensmi_ui.app_config.validate import InvalidConfigError, validate_config
from opensmi_ui.compose.composer import Composer, ComposerInitError
from opensmi_ui.logger import get_module_logger

logger = get_module_logger("main")

# read configuration input
try:
    load_dotenv()

    cfg = appysetty.read_configuration(
        AppConfig, [appysetty.YamlSource(), appysetty.EnvSource()]
    )

    validate_config(cfg)

    logger.info("-" * 20)
    logger.info("### Configuration")
    visit_config_strings(
        cfg,
        lambda field_name, field_type, field_value: logger.info(
            f"# {field_name}: {field_value}"
        ),
    )
    logger.info("### End Configuration")
    logger.info("-" * 20)

except appysetty.AppConfigError as e:
    print(f"failed to read configuration: {e}")
    sys.exit(1)
except InvalidConfigError as e:
    print(f"invalid configuration: {e}")
    sys.exit(1)
except Exception:
    raise

# compose the application
# depending on usage, this couls then be used with fastapi dev and a special entrypoint
try:
    composer = Composer()
    app = composer.compose_application(config=cfg)
except ComposerInitError as e:
    print(f"Composer failed to initialize: {e}")
    sys.exit(1)
