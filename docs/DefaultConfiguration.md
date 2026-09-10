# Default Configuration Overview

| Key | Default | Description |
| --- | --- | --- |
| APP_VERSION | 25.06-dev-local | Version to be shown in frontend. Should be set by some pipeline | 
| SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA | false | If this flag is set, only the OPC_UA_DEFAULT_xxx data will be used for connecting. Other user data is simply ignored. | 
| SERVER_ENABLE_AUTO_CONNECT | false | If this flag is set, the server will automatically try to connect on startup using the provided OPC_UA_DEFAULT_xxx data | 
| OPC_UA_DEFAULT_SERVER_URL | opc.tcp://localhost:4843 | URL of the OPC UA to connect to | 
| OPC_UA_DEFAULT_SERVER_USERNAME | operator | Default username for OPC UA (might be overwritten by localStorage in client) | 
| OPC_UA_DEFAULT_SERVER_PASSWORD | operator | Default password for OPC UA (might be overwritten by localStorage in client) | 
| OPC_UA_CONNECT_REQUEST_TIMEOUT_SECONDS | 5 | Default timeout in seconds used for connection request of pyuaadapter connect method | 
| LOCKING_ENABLED | true | If set, lock actions (toggle, break) will be usable. Only disable for read-only applications. To protect against unintended usage, please use PIN_GUARD. | 
| LOCKING_SIMULATION_ENABLED | false | If set, locking will only be simulated on the backend, no actual lock requests are sent to the OPC UA server. Intended for OPC UA servers, that do not support locking while still having the nodes for it. | 
| LOCKING_AUTOFREE_DELAY_SECONDS | 180 | Timeout for the automated freeing of a machine after any action has occured. | 
| PIN_GUARD_ENABLED | false | If set to true, all write actions are only allowed after the PIN_GUARD_PIN has been entered. Will auto-lock after PIN_GUARD_AUTOLOCK_DELAY_MS has passed. | 
| PIN_GUARD_AUTOLOCK_DELAY_SECONDS | 180 | Amount of seconds with no action, after which the PIN_GUARD will be automatically locked. | 
| PIN_GUARD_PIN | 123321 | Digit-based PIN (usually 6 digits) to unlock the Locking feature. Only needed, if SERVER_LOCKING_MODE is set to UI_PIN. Empty PINs are not allowed (have at least 1 digit). | 
