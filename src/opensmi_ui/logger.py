import logging


class AsyncuaLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.name.startswith("asyncua"):
            record.msg = f"<asyncua> {record.msg}"

        return True


class ModuleLoggerAdapter(logging.LoggerAdapter):
    module_name: str

    def __init__(self, logger: logging.Logger, module_name: str) -> None:
        super().__init__(logger, {})
        self.module_name = module_name

    def process(self, msg, kwargs):
        return f"<ui:{self.module_name}> {msg}", kwargs


def get_module_logger(module_name: str) -> ModuleLoggerAdapter:
    return ModuleLoggerAdapter(
        logging.getLogger(f"uvicorn.opensmi_ui.{module_name}"), module_name
    )


uvicorn_logger = logging.getLogger("uvicorn")
asyncua_logger = logging.getLogger("asyncua")

asyncua_filter = AsyncuaLogFilter()

for handler in uvicorn_logger.handlers:
    handler.addFilter(asyncua_filter)
    asyncua_logger.addHandler(handler)

asyncua_logger.propagate = False
