import ComponentPage from "@/pages/ComponentPage.vue";
import ConnectPage from "@/pages/ConnectPage.vue";
import DashboardOverviewPage from "@/pages/DashboardOverviewPage.vue";
import DashboardPage from "@/pages/DashboardPage.vue";
import GenericEntityPage from "@/pages/GenericEntityPage.vue";
import HomePage from "@/pages/HomePage.vue";
import MethodPage from "@/pages/MethodPage.vue";
import NotificationPage from "@/pages/NotificationPage.vue";
import SkillPage from "@/pages/SkillPage.vue";
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
    {
      path: "/skill/:entityId",
      component: SkillPage,
    },
    {
      path: "/method/:entityId",
      component: MethodPage,
    },
    {
      path: "/dashboard",
      component: DashboardPage,
    },
    {
      path: "/dashboard/:dashboardId",
      component: DashboardPage,
    },
  ],
});

export default router;
