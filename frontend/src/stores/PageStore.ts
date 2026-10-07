import { defineStore } from "pinia";
import { simplyGet } from "../util/SimplyFetch";
import { useServerStore } from "./ServerStore";

const LOCAL_STORAGE_PAGE_FLAGS_KEY = "sf-module-ui-page-show-flags";

export const usePageStore = defineStore("page", {
  state: () => {
    return {
      showNavigation: true,
      showFooter: false,
      webSocketConnected: false,
      socketStatistics: {
        sentMessages: 0,
        receivedMessages: 0,
      },
      showFlags: {
        entityIds: false,
        nodeIds: false,
        devOptions: false,
        specializedPages: true,
        timestamps: false,
      } as { [key: string]: boolean },
      appVersion: "",
    };
  },
  actions: {
    storeShowFlags() {
      localStorage.setItem(
        LOCAL_STORAGE_PAGE_FLAGS_KEY,
        JSON.stringify(this.showFlags),
      );
    },
    loadShowFlags() {
      const input = localStorage.getItem(LOCAL_STORAGE_PAGE_FLAGS_KEY);
      if (!input) {
        return;
      }

      const inputFlags = JSON.parse(input);
      for (const key of Object.keys(this.showFlags)) {
        if (inputFlags.hasOwnProperty(key)) {
          this.showFlags[key] = inputFlags[key] == true ? true : false;
        }
      }
    },
    async updateAppVersion() {
      try {
        const result = await simplyGet("/api/version");
        this.appVersion = result;
        console.log("App Version: " + this.appVersion);
      } catch (e) {
        console.log(e);
      }
    },
    toggleShowNavigation() {
      this.showNavigation = !this.showNavigation;
    },
    toggleShowFooter() {
      this.showFooter = !this.showFooter;
    },
    setSocketOffline() {
      this.webSocketConnected = false;
    },
    setSocketOnline() {
      this.webSocketConnected = true;
    },
    updateSocketStatistics(input: {
      sentMessages: number;
      receivedMessages: number;
    }) {
      this.socketStatistics.sentMessages = input.sentMessages;
      this.socketStatistics.receivedMessages = input.receivedMessages;
    },
  },
});
