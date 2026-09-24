from opensmi_ui.app_config.config import AppConfig
from opensmi_ui.parse.url import validate_url


class ConfigValidationError:
    def __init__(self, field: str, msg: str):
        self.field = field
        self.message = msg


class InvalidConfigError(Exception):
    def __init__(self, msg: str, fields: list[ConfigValidationError] | None = None):
        if fields is None:
            fields = []

        self.message = msg
        self.affected_fields = fields

        details = "; ".join(
            f"{error.field}: {error.message}" for error in self.affected_fields
        )

        super().__init__(f"{msg}: {details}" if details else msg)


def validate_config(cfg: AppConfig):
    """Checks if the given config contains valid inputs. Raises errors if not."""

    # All URLs must contain valid urls when non-empty
    if len(cfg.opc_ua_default_server_url) > 0:
        try:
            validate_url(cfg.opc_ua_default_server_url, schemes=["opc.tcp"])
        except ValueError as e:
            raise InvalidConfigError(f"opc_ua_default_server_url is not valid: {e}")
        except Exception:
            raise

    if cfg.opc_ua_connect_request_timeout_seconds < 0:
        raise InvalidConfigError(
            "opc_ua_connect_request_timeout_seconds must be greater than 0 (or 0 to disable it)",
            [
                ConfigValidationError(
                    field="opc_ua_connect_request_timeout_seconds", msg="must be >= 0"
                )
            ],
        )

    # AUTO_CONNECT and ONLY_ALLOW_DEFAULT need actual connection data
    if cfg.server_only_allow_default_connection_data or cfg.server_enable_auto_connect:
        # if one of these is set, the default connection data need to be valid
        fields = {
            "opc_ua_default_server_url": cfg.opc_ua_default_server_url,
            "opc_ua_default_server_username": cfg.opc_ua_default_server_username,
            "opc_ua_default_server_password": cfg.opc_ua_default_server_password,
        }

        invalid_fields = [
            ConfigValidationError(field=field, msg="must not be empty")
            for field, value in fields.items()
            if not value
        ]

        if len(invalid_fields) > 0:
            raise InvalidConfigError(
                "When using server_only_allow_default_connection_data or "
                "server_enable_auto_connect all connection data must be set",
                invalid_fields,
            )

    # Pin Guard needs valid PIN (0 is valid, but -1 not) and positive delay
    if cfg.pin_guard_enabled:
        if cfg.pin_guard_autolock_delay_seconds <= 0:
            raise InvalidConfigError(
                "When pin_guard_enabled is set, the delay must be greater than 0",
                [
                    ConfigValidationError(
                        field="pin_guard_autolock_delay_seconds", msg="must be > 0"
                    )
                ],
            )

        if cfg.pin_guard_pin < 0:
            raise InvalidConfigError(
                "When pin_guard_enabled is set, the PIN must be greater than 0",
                [ConfigValidationError(field="pin_guard_pin", msg="must be > 0")],
            )

    # When Locking is enabled, Autofree must be positive
    if (
        cfg.locking_enabled or cfg.locking_simulation_enabled
    ) and cfg.locking_autofree_delay_seconds <= 0:
        raise InvalidConfigError(
            "When locking_enabled or locking_simulation_enabled is set, the delay must be greater than 0",
            [
                ConfigValidationError(
                    field="locking_autofree_delay_seconds", msg="must be > 0"
                )
            ],
        )
