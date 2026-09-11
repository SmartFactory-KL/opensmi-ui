from app_config.app_config import AppConfig
from app_config.write import write_config_documentation

write_config_documentation(AppConfig(), env_prefix="OPENSMI_UI")
