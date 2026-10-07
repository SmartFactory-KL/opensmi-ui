import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

import "./main.css";
import SocketClient from "./socket/SocketClient";
import { usePageStore } from "./stores/PageStore";
import { usePinGuardStore } from "./stores/PinGuardStore";
import { useServerStore } from "./stores/ServerStore";

const app = createApp(App);

app.use(createPinia());
app.use(router);

async function compose() {
  const pageStore = usePageStore();
  await pageStore.requestPageInfo();

  const socketClient = new SocketClient(pageStore);
  socketClient.connect();

  const pinGuardStore = usePinGuardStore();
  pinGuardStore.attachToSocketClient(socketClient);
  pinGuardStore.requestData()

  const serverStore = useServerStore();
  serverStore.attachToSocketClient(socketClient)

  pageStore.writeDefaultsToServerStore(serverStore)

  serverStore.requestServerStatus()
}

app.mount("#app");
compose()
