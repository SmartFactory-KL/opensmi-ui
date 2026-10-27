import type SocketClient from "@/socket/SocketClient";
import type { NodeIdData, LocalizedTextData } from "@/types/OPCTypes";
import { defineStore } from "pinia";

export const MAX_NOTIFICATION_COUNT = 1000;

export type NotificationLevel = "info" | "error" | "warning";

export interface NotificationEvent {
  eventId: string;
  eventType: NodeIdData;
  sourceNode: NodeIdData;
  sourceName: string;

  time: string;
  message: LocalizedTextData;
  severity: number;
}

export const NOTIFICATION_MAX_COUNT = 999;

export const useNotificationStore = defineStore("notification", {
  state: (): {
    notificationContent: {
      info: NotificationEvent[];
      warning: NotificationEvent[];
      error: NotificationEvent[];
    };

    tickIntervalHandle: ReturnType<typeof setInterval> | null;

    animate: {
      info: ReturnType<typeof setTimeout> | null;
      warning: ReturnType<typeof setTimeout> | null;
      error: ReturnType<typeof setTimeout> | null;
    };

    currentTab: NotificationLevel;
  } => {
    return {
      notificationContent: {
        info: [] as NotificationEvent[],
        warning: [] as NotificationEvent[],
        error: [] as NotificationEvent[],
      },

      // used for a basic tick. If null, the tick is not active
      tickIntervalHandle: null,

      animate: {
        info: null,
        warning: null,
        error: null,
      },

      currentTab: "info",
    };
  },
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      socketClient.addChannelListener("Notification", this.handleNotification);
    },
    handleNotification(notification: any) {
      for (const list of [
        this.notificationContent.info,
        this.notificationContent.warning,
        this.notificationContent.error,
      ]) {
        if (list.length >= MAX_NOTIFICATION_COUNT - 1) {
          const excess = list.length - MAX_NOTIFICATION_COUNT;
          list.splice(0, excess);
        }
      }

      let level: "info" | "warning" | "error";
      switch (notification.severity) {
        case 555:
          level = "warning";
        case 999:
          level = "error";
        default:
          level = "info";
      }

      this.notificationContent[level].push(notification);
      if (this.animate[level] === null) {
        this.animate[level] = setTimeout(() => {
          this.animate[level] = null;
        }, 350);
      }
    },
    tick() {
      // not used right now
    },
    setTab(newTab: NotificationLevel) {
      if (newTab !== this.currentTab) {
        this.currentTab = newTab;
      }
    },
    startTickInterval() {
      if (this.tickIntervalHandle !== null) {
        this.tickIntervalHandle = setInterval(this.tick, 1000);
      }
    },
    stopDeltaInterval() {
      if (this.tickIntervalHandle !== null) {
        clearInterval(this.tickIntervalHandle);
        this.tickIntervalHandle = null;
      }
    },
  },
});
