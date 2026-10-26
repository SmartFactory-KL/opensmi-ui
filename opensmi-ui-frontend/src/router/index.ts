import ComponentPage from "@/pages/ComponentPage.vue";
import ConnectPage from "@/pages/ConnectPage.vue";
import GenericEntityPage from "@/pages/GenericEntityPage.vue";
import HomePage from "@/pages/HomePage.vue";
import NotificationPage from "@/pages/NotificationPage.vue";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: HomePage,
    },
    {
      path: "/connect",
      component: ConnectPage,
    },
    {
      path: "/notification",
      component: NotificationPage,
    },
    {
      path: "/entity/:entityId",
      component: GenericEntityPage,
    },
    {
      path: "/component/:entityId",
      component: ComponentPage,
    },
  ],
});

export default router;
