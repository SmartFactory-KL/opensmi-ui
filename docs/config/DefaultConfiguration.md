# Application Configuration

## Configuration

| ENV | Variable | Type | Default | Is Secret | Description |
|---|---|---|---|---|---|
| OPENSMI_UI_APP_VERSION | app_version | str | 25.06-dev-local | False | Version to be shown in frontend. Should be set by some pipeline |
| OPENSMI_UI_SERVER_ENABLE_AUTO_CONNECT | server_enable_auto_connect | bool | False | False | If this flag is set, the server will automatically try to connect on startup using the provided OPC_UA_DEFAULT_xxx data |
| OPENSMI_UI_OPC_UA_DEFAULT_SERVER_URL | opc_ua_default_server_url | str | opc.tcp://localhost:4843 | False | URL of the OPC UA to connect to |
| OPENSMI_UI_OPC_UA_DEFAULT_SERVER_USERNAME | opc_ua_default_server_username | str | operator | False | Default username for OPC UA (might be overwritten by localStorage in client) |
| OPENSMI_UI_OPC_UA_DEFAULT_SERVER_PASSWORD | opc_ua_default_server_password | str | Masked[len:8] | True | Default password for OPC UA (might be overwritten by localStorage in client) |
| OPENSMI_UI_OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS | opc_ua_connect_request_timeout_seconds | int | 5 | False | Default timeout in seconds used for connection request of pyuaadapter connect method |
| OPENSMI_UI_LOCKING_ENABLED | locking_enabled | bool | True | False | If set, lock actions (toggle, break) will be usable. Only disable for read-only applications. To protect against unintended usage, please use PIN_GUARD. |
| OPENSMI_UI_LOCKING_SIMULATION_ENABLED | locking_simulation_enabled | bool | False | False | If set, locking will only be simulated on the backend, no actual lock requests are sent to the OPC UA server. Intended for OPC UA servers, that do not support locking while still having the nodes for it. |
| OPENSMI_UI_LOCKING_AUTOFREE_DELAY_SECONDS | locking_autofree_delay_seconds | int | 180 | False | Timeout for the automated freeing of a machine after any action has occured. |
| OPENSMI_UI_PIN_GUARD_ENABLED | pin_guard_enabled | bool | False | False | If set to true, all write actions are only allowed after the PIN_GUARD_PIN has been entered. Will auto-lock after PIN_GUARD_AUTOLOCK_DELAY_SECONDS has passed. |
| OPENSMI_UI_PIN_GUARD_AUTOLOCK_DELAY_SECONDS | pin_guard_autolock_delay_seconds | int | 180 | False | Amount of seconds with no action, after which the PIN_GUARD will be automatically locked. |
| OPENSMI_UI_PIN_GUARD_PIN | pin_guard_pin | int | Masked[len:4] | True | Digit-based PIN (usually 6 digits) to unlock the Locking feature. Only needed, if SERVER_LOCKING_MODE is set to UI_PIN. Empty PINs are not allowed (have at least 1 digit). |

## Docker Compose

Example environment block using the default values:

```yaml
environment:
  OPENSMI_UI_APP_VERSION: 25.06-dev-local
  OPENSMI_UI_SERVER_ENABLE_AUTO_CONNECT: false
  OPENSMI_UI_OPC_UA_DEFAULT_SERVER_URL: opc.tcp://localhost:4843
  OPENSMI_UI_OPC_UA_DEFAULT_SERVER_USERNAME: operator
  OPENSMI_UI_OPC_UA_DEFAULT_SERVER_PASSWORD: Masked[len:8]
  OPENSMI_UI_OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS: 5
  OPENSMI_UI_LOCKING_ENABLED: true
  OPENSMI_UI_LOCKING_SIMULATION_ENABLED: false
  OPENSMI_UI_LOCKING_AUTOFREE_DELAY_SECONDS: 180
  OPENSMI_UI_PIN_GUARD_ENABLED: false
  OPENSMI_UI_PIN_GUARD_AUTOLOCK_DELAY_SECONDS: 180
  OPENSMI_UI_PIN_GUARD_PIN: Masked[len:4]
```

## Docker Run

Example `docker run` command using the default values:

```bash
docker run \
  -e OPENSMI_UI_APP_VERSION=25.06-dev-local \
  -e OPENSMI_UI_SERVER_ENABLE_AUTO_CONNECT=False \
  -e OPENSMI_UI_OPC_UA_DEFAULT_SERVER_URL=opc.tcp://localhost:4843 \
  -e OPENSMI_UI_OPC_UA_DEFAULT_SERVER_USERNAME=operator \
  -e OPENSMI_UI_OPC_UA_DEFAULT_SERVER_PASSWORD='Masked[len:8]' \
  -e OPENSMI_UI_OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS=5 \
  -e OPENSMI_UI_LOCKING_ENABLED=True \
  -e OPENSMI_UI_LOCKING_SIMULATION_ENABLED=False \
  -e OPENSMI_UI_LOCKING_AUTOFREE_DELAY_SECONDS=180 \
  -e OPENSMI_UI_PIN_GUARD_ENABLED=False \
  -e OPENSMI_UI_PIN_GUARD_AUTOLOCK_DELAY_SECONDS=180 \
  -e OPENSMI_UI_PIN_GUARD_PIN='Masked[len:4]' \
  your-image:latest
```
