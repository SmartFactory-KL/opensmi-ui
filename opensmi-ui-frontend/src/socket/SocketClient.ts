import { usePageStore } from "../stores/PageStore";
// import Notify from "./Notify";
// import { simplyGet } from "./SimplyFetch";

export type TopicMessageHandler = (data: any) => void;

export type SocketMessage = {
  channel: string;
  data: any;
};

class SocketClient {
  socket!: WebSocket;
  socketUrl = "ws://localhost:8000/backend-socket";

  lastReadyState: WebSocket["readyState"] = WebSocket.CLOSED;
  reconnectAmount: number = 0;

  pageStore!: ReturnType<typeof usePageStore>;
  messageCount: number = 0;

  channelHandlerMap = new Map<string, TopicMessageHandler[]>();

  infoLogIntervalHandle = setInterval(() => {
    this.pageStore.updateMessageCount(this.messageCount);

    if (this.socket) {
      if (this.socket.readyState != this.lastReadyState) {
        this.lastReadyState = this.socket.readyState;
        this.pageStore.updateSocketState(this.socket.readyState);
      }
    }

    this.messageCount = 0;
  }, 1000);

  constructor(pageStore: ReturnType<typeof usePageStore>) {
    this.pageStore = pageStore;
  }

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

      this.pageStore.updateSocketState(WebSocket.OPEN);
      this.pageStore.updateMessageCount(0);
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
    this.pageStore.updateSocketState(WebSocket.CLOSED);
    this.connect();
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
}

export default SocketClient;
