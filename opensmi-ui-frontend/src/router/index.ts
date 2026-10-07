import ConnectPage from "@/pages/ConnectPage.vue";
import HomePage from "@/pages/HomePage.vue";
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
  ],
});

export default router;
