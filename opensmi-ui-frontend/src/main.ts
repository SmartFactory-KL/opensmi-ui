import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

import '@fontsource-variable/inter';
import "./main.css";

import SocketClient from "./socket/SocketClient";
import { usePageStore } from "./stores/PageStore";
import { usePinGuardStore } from "./stores/PinGuardStore";
import { useServerStore } from "./stores/ServerSessionStore";
import Toaster from "./toast/Toaster";
import { useModelStore } from "./stores/ModelStore";
import { useNotificationStore } from "./stores/NotificationStore";

const app = createApp(App);

app.use(createPinia());
app.use(router);

async function compose() {
  Toaster.attachStore();

  const pageStore = usePageStore();
  await pageStore.requestPageInfo();

  const socketClient = new SocketClient();
  socketClient.connect();

  pageStore.attachToSocketClient(socketClient);

  const pinGuardStore = usePinGuardStore();
  pinGuardStore.attachToSocketClient(socketClient);
  pinGuardStore.requestData();

  const serverStore = useServerStore();
  serverStore.attachToSocketClient(socketClient);

  const notificationStore = useNotificationStore();
  notificationStore.attachToSocketClient(socketClient)
  notificationStore.startTickInterval()

  const modelStore = useModelStore();
  modelStore.attachToSocketClient(socketClient);

  pageStore.writeDefaultsToServerStore(serverStore);
}

app.mount("#app");
compose();
