export type TopicMessageHandler = (data: any) => void;

export type ConnectionUpdateHandler = (
  newState: WebSocket["readyState"],
) => void;

export type MessageCountHandler = (count: number, delta: number) => void;

export type SocketMessage = {
  channel: string;
  data: any;
};

const SOCKET_CLIENT_INTERVAL_DELTA_MS = 1000;

class SocketClient {
  socket!: WebSocket;
  socketUrl = "ws://localhost:8000/backend-socket";

  lastReadyState: WebSocket["readyState"] = WebSocket.CLOSED;
  reconnectAmount: number = 0;
  messageCount: number = 0;

  channelHandlerMap = new Map<string, TopicMessageHandler[]>();
  connUpdateHandler: ConnectionUpdateHandler[] = [];
  messageCountHandler: MessageCountHandler[] = [];

  infoLogIntervalHandle = setInterval(() => {
    this.notifyMessageCountHandler(
      this.messageCount,
      SOCKET_CLIENT_INTERVAL_DELTA_MS,
    );

    if (this.socket) {
      if (this.socket.readyState != this.lastReadyState) {
        this.lastReadyState = this.socket.readyState;
        this.notifyConnectionHandler(this.socket.readyState);
      }
    }

    this.messageCount = 0;
  }, SOCKET_CLIENT_INTERVAL_DELTA_MS);

  async connect() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    if (this.reconnectAmount > 0) {
      const waitTime = Math.min(
        10_000,
        200 * Math.pow(2, this.reconnectAmount - 1),
      );
      console.log(waitTime);
      await new Promise((resolve) => setTimeout(resolve, waitTime));
      this.reconnectAmount++;
    }

    this.socketUrl = `ws://${window.location.hostname}:${window.location.port}/socket`;
    console.log("Connecting socket to " + this.socketUrl);

    this.socket = new WebSocket(this.socketUrl);

    this.socket.onopen = () => {
      console.log("WebSocket connected");

      this.reconnectAmount = 0;
      this.notifyConnectionHandler(this.socket.readyState);
    };

    this.socket.onerror = this.handleError;
    this.socket.onclose = () => {
      if (this.reconnectAmount == 0) {
        this.reconnectAmount = 1;
      }
      this.handleOnClose();
    };
    this.socket.onmessage = (evt) => {
      this.handleMessage(evt);
    };
  }

  handleError(e: any) {
    console.error(e);
  }

  handleOnClose() {
    console.warn("WebSocket closed!");
    this.notifyConnectionHandler(this.socket.readyState);
    this.connect();
  }

  notifyConnectionHandler(newState: WebSocket["readyState"]) {
    for (const handler of this.connUpdateHandler) {
      if (handler) {
        handler.call(null, newState);
      }
    }
  }

  notifyMessageCountHandler(count: number, delta: number) {
    for (const handler of this.messageCountHandler) {
      if (handler) {
        handler.call(null, count, delta);
      }
    }
  }

  handleMessage(evt: MessageEvent) {
    const data = JSON.parse(evt.data);

    if ("channel" in data) {
      if (data["channel"] == "batch") {
        this.messageCount += data["data"].length ?? 1;
      } else {
        this.messageCount++;
      }

      const handlerList = this.channelHandlerMap.get(data.channel) || [];
      for (const handler of handlerList) {
        if (handler) {
          handler.call(null, data.data);
        }
      }
    }
  }

  addChannelListener(channel: string, handler: TopicMessageHandler) {
    console.log("New Handler for channel:", channel);
    if (!this.channelHandlerMap.has(channel)) {
      this.channelHandlerMap.set(channel, []);
    }
    this.channelHandlerMap.get(channel)?.push(handler);
  }

  addConnectionListener(handler: ConnectionUpdateHandler) {
    this.connUpdateHandler.push(handler);
  }

  addMessageCountListener(handler: MessageCountHandler) {
    this.messageCountHandler.push(handler)
  }
}

export default SocketClient;
