from pathlib import Path

import appysetty

from opensmi_ui.app_config.config import AppConfig

appysetty.write_configuration_documentation(
    AppConfig, env_prefix="OPENSMI_UI", output_dir=Path("docs/config")
)
