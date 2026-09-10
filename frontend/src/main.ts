import { createApp } from "vue";
import "./style.css";

import { createPinia } from "pinia";
import { createRouter, createWebHashHistory } from "vue-router";

import "./assets/fontawesome/fontawesome.css";
import "./assets/fontawesome/solid.css";
import "./assets/fontawesome/regular.css";

import "uplot/dist/uPlot.min.css";

import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";

import SocketClient from "./util/SocketClient";
import Notify from "./util/Notify";

import { useMachineStore } from "./stores/MachineStore";
import { useServerStore } from "./stores/ServerStore";
import { useNotificationStore } from "./stores/NotificationStore";

import App from "./App.vue";

import HomePage from "./components/pages/HomePage.vue";
import ServerConnectPage from "./components/pages/ServerConnectPage.vue";
import MachinePage from "./components/pages/MachinePage.vue";
import NotificationPage from "./components/pages/NotificationPage.vue";
import ComponentPage from "./components/pages/ComponentPage.vue";
import SkillPage from "./components/pages/SkillPage.vue";
import { usePageStore } from "./stores/PageStore";
import MethodPage from "./components/pages/MethodPage.vue";
import { usePinGuardStore } from "./stores/PinStore";
import PlotBuffer from "./plotting/PlotBuffer";
import DebugInformationPage from "./components/pages/DebugInformationPage.vue";

const routes = [
  {
    path: "/",
    component: HomePage,
  },
  {
    path: "/server",
    component: ServerConnectPage,
  },
  {
    path: "/logs",
    component: NotificationPage,
  },
  {
    path: "/machine/:machineEntityId",
    component: MachinePage,
  },
  {
    path: "/component/:componentEntityId",
    component: ComponentPage,
  },
  {
    path: "/skill/:skillEntityId",
    component: SkillPage,
  },
  {
    path: "/method/:methodEntityId",
    component: MethodPage,
  },
  {
    path: "/debug-info",
    component: DebugInformationPage,
  },
];

const pinia = createPinia();
const app = createApp(App);

const router = createRouter({
  history: createWebHashHistory(),
  routes: routes,
});

app.use(pinia);
app.use(router);

// has to be after "app.use(pinia)" since it is attached to a store
SocketClient.connect();

const machineStore = useMachineStore();
machineStore.attachToSocketClient();

const serverStore = useServerStore();
serverStore.attachToSocketClient();
serverStore.loadLocalData();
serverStore.getServerInformation();

const notificationStore = useNotificationStore();
Notify.init(notificationStore);
notificationStore.startDeltaInterval();

const pageStore = usePageStore();
pageStore.updateAppVersion();
pageStore.loadShowFlags();
pageStore.$subscribe(pageStore.storeShowFlags);

const pinGuardStore = usePinGuardStore();
pinGuardStore.attachToSocketClient();
pinGuardStore.refreshPinGuardData();

PlotBuffer.attachToSocketClient();

// Notify.notify("info", "Test")SocketClient

app.mount("#app");
