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

  pageStore!: ReturnType<typeof usePageStore>;

  channelHandlerMap = new Map<string, TopicMessageHandler[]>();

  reconnectIntervalHandle = 0;
  reconnectCount = 0;

  infoLogIntervalHandle = setInterval(() => {
    if (this.pageStore) {
      this.pageStore.updateSocketStatistics({
        sentMessages: this.messageCount.out,
        receivedMessages: this.messageCount.in,
      });
    }

    this.messageCount.in = 0;
    this.messageCount.out = 0;
  }, 5000);

  messageCount = {
    in: 0,
    out: 0,
  };

  async connect() {
    this.pageStore = usePageStore();
    this.pageStore.setSocketOffline();

    console.log("Connecting socket...");
    clearInterval(this.reconnectIntervalHandle);

    await this.requestSocketUrl();

    this.socket = new WebSocket(this.socketUrl);

    this.socket.onopen = () => {
      console.log("WS connected");
      this.pageStore.setSocketOnline();
    };

    this.socket.onerror = this.handleError;
    this.socket.onclose = () => {
      this.handleOnClose();
    };
    this.socket.onmessage = (evt) => {
      this.handleMessage(evt);
    };
  }

  async requestSocketUrl() {
    const socketUrl = `ws://${window.location.hostname}:${window.location.port}/socket`;
    this.socketUrl = socketUrl;
  }

  handleError(e: any) {
    console.error(e);
  }

  handleOnClose() {
    console.log("WS closed");
    this.pageStore.setSocketOffline();
    this.connect();
  }

  handleMessage(evt: MessageEvent) {
    const data = JSON.parse(evt.data);

    console.log(data)

    if ("channel" in data) {
      if (data["channel"] == "batch") {
        this.messageCount.in += data["data"].length ?? 1;
      } else {
        this.messageCount.in++;
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
    console.log("add topic handler for ", channel);
    if (!this.channelHandlerMap.has(channel)) {
      this.channelHandlerMap.set(channel, []);
    }
    this.channelHandlerMap.get(channel)?.push(handler);
  }

  sendData(channel: string, data: any) {
    this.messageCount.out++;
    this.socket.send(JSON.stringify({ channel, data }));
  }
}

export default new SocketClient();
