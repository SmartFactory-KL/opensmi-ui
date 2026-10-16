from opensmi_ui.opc_session.session import OPCSession


class OPCSubscriber:
    opc_session: OPCSession

    def __init__(self, opc_session: OPCSession):
        self.opc_session = opc_session
