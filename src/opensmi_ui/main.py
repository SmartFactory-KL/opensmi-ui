import logging
import sys

import appysetty
from appysetty.read import visit_config_strings
from dotenv import load_dotenv

from opensmi_ui.app_config.config import AppConfig
from opensmi_ui.app_config.validate import InvalidConfigError, validate_config
from opensmi_ui.compose.composer import Composer, ComposerInitError

logger = logging.getLogger("uvicorn.opensmi_ui.main")

# read configuration input
try:
    load_dotenv()

    cfg = appysetty.read_configuration(
        AppConfig, [appysetty.YamlSource(), appysetty.EnvSource()]
    )

    validate_config(cfg)

    logger.info("-"*20)
    logger.info("### Configuration")
    visit_config_strings(
        cfg,
        lambda field_name, field_type, field_value: logger.info(
            f"# {field_name}: {field_value}"
        ),
    )
    logger.info("### End Configuration")
    logger.info("-"*20)

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


# remote_server = ServerModule()
# message_broadcaster_instance = message_broadcaster.MessageBroadcaster()
#
# stats_counter = StatsCounter()
#
# provider_load_images()
#
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # The adapter seems to attach a root logger to logging
#     # and logs send to a logging.getLogger seem to propagate
#     # to the root logger by default.
#     # So to prevent duplicated messages propagate on the uvicorn logger has to be disabled
#     # and since logging.getLogger() for the same name always returns the same logger
#     # this should apply to all uvicorn logger references.
#     uviLogger = logging.getLogger("uvicorn")
#     uviLogger.propagate = False
#
#     # handle creating and connecting to the module
#     # await adapter_client.request_connect()
#     # UPDATE: This was moved to an api endpoint
#     # so reconnecting for some reason does not involve
#     # restarting the backend+
#
#     # This is the openapi export. It will export and then stop execution
#     # UPDATE: The commit hook takes care of that, so this is disabled for now.
#     # if app_config.is_set("OPENAPI_EXPORT_ONLY"):
#     #     openapi_spec = app.openapi()
#     #     try:
#     #         with open("./docs/openapi.yaml", "w") as openapi_output_file:
#     #             yaml.dump(openapi_spec, openapi_output_file, sort_keys=False)
#     #     except Exception as e:
#     #         print("Failed to create OpenAPI document")
#     #         print(e)
#     #         raise ValueError("Failed to create OpenAPI document")
#
#     #     sys.exit(0)
#
#     # before running the application, check config for undefined combinations
#     if app_config.is_set(
#         "SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA"
#     ) or app_config.is_set("SERVER_ENABLE_AUTO_CONNECT"):
#         if (
#             len(app_config.get_text("OPC_UA_DEFAULT_SERVER_USERNAME")) == 0
#             or len(app_config.get_text("OPC_UA_DEFAULT_SERVER_URL")) == 0
#             or len(app_config.get_text("OPC_UA_DEFAULT_SERVER_PASSWORD")) == 0
#         ):
#             raise ValueError(
#                 "When using SERVER_ONLY_ALLOW_DEFAULT_CONNECTION_DATA or SERVER_ENABLE_AUTO_CONNECT, you have to provide OPC_UA_DEFAULT_SERVER_URL, OPC_UA_DEFAULT_SERVER_USERNAME and OPC_UA_DEFAULT_SERVER_PASSWORD. One of them was empty."
#             )
#
#     # With Pin Guard enabled, the PIN and delay seconds need to be valid numbers > 1
#     if app_config.is_set("PIN_GUARD_ENABLED"):
#         if (
#             len(app_config.get_text("PIN_GUARD_PIN")) == 0
#             or not app_config.get_text("PIN_GUARD_PIN").isdigit()
#         ):
#             raise ValueError(
#                 "When using PIN mode your PIN_GUARD_PIN needs to have at least one digit and be a valid number"
#             )
#         if (
#             len(app_config.get_text("PIN_GUARD_AUTOLOCK_DELAY_SECONDS")) == 0
#             or not app_config.get_text("PIN_GUARD_AUTOLOCK_DELAY_SECONDS").isdigit()
#             or not app_config.get_int("PIN_GUARD_AUTOLOCK_DELAY_SECONDS") > 0
#         ):
#             raise ValueError(
#                 "When using PIN Guard your PIN_GUARD_AUTOLOCK_DELAY_SECONDS needs to be a valid number > 0"
#             )
#
#     # With locking enabled, Auto-free delay must be a valid number above 0
#     if app_config.is_set("LOCKING_ENABLED"):
#         if (
#             len(app_config.get_text("LOCKING_AUTOFREE_DELAY_SECONDS")) == 0
#             or not app_config.get_text("LOCKING_AUTOFREE_DELAY_SECONDS").isdigit()
#             or not app_config.get_int("LOCKING_AUTOFREE_DELAY_SECONDS") > 0
#         ):
#             raise ValueError(
#                 "When using Locking your LOCKING_AUTOFREE_DELAY_SECONDS needs to be a valid number > 0"
#             )
#
#     # read default values and locking mode
#     remote_server.read_defaults()
#
#     # auto connect if set
#     if app_config.is_set("SERVER_ENABLE_AUTO_CONNECT"):
#         connection_data = ServerConnectRequest(
#             server_url=app_config.get_text("OPC_UA_DEFAULT_SERVER_URL"),
#             username=app_config.get_text("OPC_UA_DEFAULT_SERVER_USERNAME"),
#             password=app_config.get_text("OPC_UA_DEFAULT_SERVER_PASSWORD"),
#         )
#
#         await remote_server.request_connect(
#             connection_data, is_auto_connect_request=True
#         )
#
#     # log configuration
#     app_config.log_configuration(uviLogger)
#
#     # start stats counter
#     stats_counter.start_stats_counter_task()
#
#     # running the main FastAPI application
#     yield
#
#     # handle disconnecting
#     # will still be here to properly release lock and connection
#     stats_counter.stop_stats_counter_task()
#     remote_server.get_pin_guard().unlock_for_shutdown()
#     await remote_server.request_disconnect()
#
#
# app = FastAPI(
#     lifespan=lifespan,
#     title="Module UI Backend",
#     summary="Backend for Module UI connecting to PyUAAdapter Module",
#     version=app_config.get_text("APP_VERSION"),
# )
#
#
# # add a handler for when the request itself is invalid
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(_, exc):
#     return PlainTextResponse(str(exc), status_code=400)
#
#
# app.include_router(router=ServerRouter)
# app.include_router(router=MachineRouter)
# app.include_router(router=ImageRouter)
#
#
# @app.get("/api/version", tags=["version"])
# async def request_version() -> str:
#     """Get the currently running version"""
#     return app_config.get_text("APP_VERSION")
#
#
# @app.get("/api/health", tags=["health"])
# async def request_health() -> HealthResponse:
#     """Health endpoint"""
#     return HealthResponse(is_healthy=True)
#
#
# ## WebSocket for Client
# @app.websocket("/socket")
# async def websocket_endpoint(websocket: WebSocket):
#     await message_broadcaster_instance.connect(websocket)
#     # await message_socket.send_refresh_message(websocket)
#     try:
#         while True:
#             data = await websocket.receive_json()
#             await websocket.send_json(data)
#     except WebSocketDisconnect:
#         await message_broadcaster_instance.disconnect(websocket=websocket)
#
#
# ## Needs to be after all the routers as it uses the root path
# app.mount("/", StaticFiles(directory="public", html=True), name="frontend")
