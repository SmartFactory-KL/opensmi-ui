from dataclasses import dataclass
from typing import Annotated

from appysetty import AppConfigEntry


@dataclass
class AppConfig:
    app_version: Annotated[
        str,
        AppConfigEntry(
            description="Version to be shown in frontend. Should be set by some pipeline",
        ),
    ] = "25.06-dev-local"

    server_enable_auto_connect: Annotated[
        bool,
        AppConfigEntry(
            description=(
                "If this flag is set, the server will automatically try to connect "
                "on startup using the provided OPC_UA_DEFAULT_xxx data"
            ),
        ),
    ] = False

    opc_ua_default_server_url: Annotated[
        str,
        AppConfigEntry(
            description="URL of the OPC UA to connect to",
        ),
    ] = "opc.tcp://localhost:4843"

    opc_ua_default_server_username: Annotated[
        str,
        AppConfigEntry(
            description="Default username for OPC UA (might be overwritten by localStorage in client)",
        ),
    ] = "operator"

    opc_ua_default_server_password: Annotated[
        str,
        AppConfigEntry(
            description="Default password for OPC UA (might be overwritten by localStorage in client)",
            is_secret=True,
        ),
    ] = "operator"

    opc_ua_connect_request_timeout_seconds: Annotated[
        int,
        AppConfigEntry(
            description=(
                "Default timeout in seconds used for connection request "
                "of pyuaadapter connect method"
            ),
        ),
    ] = 5

    locking_enabled: Annotated[
        bool,
        AppConfigEntry(
            description=(
                "If set, lock actions (toggle, break) will be usable. "
                "Only disable for read-only applications. To protect against "
                "unintended usage, please use PIN_GUARD."
            ),
        ),
    ] = True

    locking_simulation_enabled: Annotated[
        bool,
        AppConfigEntry(
            description=(
                "If set, locking will only be simulated on the backend, "
                "no actual lock requests are sent to the OPC UA server. "
                "Intended for OPC UA servers, that do not support locking "
                "while still having the nodes for it."
            ),
        ),
    ] = False

    locking_autofree_delay_seconds: Annotated[
        int,
        AppConfigEntry(
            description=(
                "Timeout for the automated freeing of a machine "
                "after any action has occured."
            ),
        ),
    ] = 180

    pin_guard_enabled: Annotated[
        bool,
        AppConfigEntry(
            description=(
                "If set to true, all write actions are only allowed after "
                "the PIN_GUARD_PIN has been entered. Will auto-lock after "
                "PIN_GUARD_AUTOLOCK_DELAY_SECONDS has passed."
            ),
        ),
    ] = False

    pin_guard_autolock_delay_seconds: Annotated[
        int,
        AppConfigEntry(
            description=(
                "Amount of seconds with no action, after which the "
                "PIN_GUARD will be automatically locked."
            ),
        ),
    ] = 180

    pin_guard_pin: Annotated[
        int,
        AppConfigEntry(
            description=(
                "Digit-based PIN (usually 6 digits) to unlock the Locking feature. "
                "Only needed, if SERVER_LOCKING_MODE is set to UI_PIN. "
                "Empty PINs are not allowed (have at least 1 digit)."
            ),
            is_secret=True,
        ),
    ] = 1234
