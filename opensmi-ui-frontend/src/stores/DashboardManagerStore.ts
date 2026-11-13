import { defineStore } from "pinia";

export const useDashboardManagerStore = defineStore("dashboard-manager", {
  state: (): {
    currentDashboard: string;
  } => {
    return {
      currentDashboard: "",
    };
  },
});
