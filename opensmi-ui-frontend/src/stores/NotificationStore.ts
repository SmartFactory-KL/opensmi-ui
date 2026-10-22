import { defineStore } from "pinia";

export type NotificationLevel = "info" | "error" | "warning";

export type UINotification = {
  level: NotificationLevel;
  message: string;
  debugMessage: string;
  createTime: string;
  createTimeStamp: number;
};

export type UINotificationStatistic = {
  level: NotificationLevel;
  total: number;
  lastDelta: number;
  currentDelta: number;
};

export const NOTIFICATION_MAX_COUNT = 999;

export const useNotificationStore = defineStore("notification", {
  state: () => {
    return {
      notificationContent: {
        info: [] as UINotification[],
        warning: [] as UINotification[],
        error: [] as UINotification[],
      } as { [key: string]: UINotification[] },

      notificationInput: {
        info: [] as UINotification[],
        warning: [] as UINotification[],
        error: [] as UINotification[],
      },

      // used to manage the deltas of the stats
      // which basically show how many new messages came in
      // in the last period
      deltaIntervalHandle: 0,
      deltaIntervalRunning: false,

      // which tab is currently shown on the NotificationPage
      currentTab: "info" as string,

      // this is used to batch incoming messages to only be rendered
      // at 100ms intervals (roughly)
      batchingIntervalHandle: 0,
      batchingIntervalRunning: false,

      notificationStatistics: {
        info: {
          level: "info",
          total: 0,
          lastDelta: 0,
          currentDelta: 0,
        } as UINotificationStatistic,
        warning: {
          level: "warning",
          total: 0,
          lastDelta: 0,
          currentDelta: 0,
        } as UINotificationStatistic,
        error: {
          level: "error",
          total: 0,
          lastDelta: 0,
          currentDelta: 0,
        } as UINotificationStatistic,
      } as { [key: string]: UINotificationStatistic },
    };
  },
  actions: {
    addNotification(
      level: NotificationLevel,
      message: string,
      debugMessage = "",
    ) {
      let listToUse: UINotification[] | null = null;
      let statToUse: UINotificationStatistic | null = null;
      let listKeyToUse: string | null = null;
      switch (level) {
        case "warning":
          statToUse = this.notificationStatistics.warning!;
          listToUse = this.notificationContent.warning!;
          listKeyToUse = "warning";
          break;
        case "error":
          statToUse = this.notificationStatistics.error!;
          listToUse = this.notificationContent.error!;
          listKeyToUse = "error";
          break;
        default:
          statToUse = this.notificationStatistics.info!;
          listToUse = this.notificationContent.info!;
          listKeyToUse = "info";
          break;
      }

      if (listToUse == null || statToUse == null || listKeyToUse == null) {
        return;
      }

      listToUse.push({
        level,
        message,
        debugMessage,
        createTime: new Date().toLocaleString(navigator.language, {
          dateStyle: "medium",
          timeStyle: "medium",
          hour12: false,
        }),
        createTimeStamp: Date.now(),
      });

      if (listToUse.length >= NOTIFICATION_MAX_COUNT) {
        this.notificationContent[listKeyToUse] = listToUse.slice(
          listToUse.length - NOTIFICATION_MAX_COUNT + 1,
          listToUse.length,
        );
      }

      statToUse.total = listToUse.length;
      statToUse.currentDelta++;
    },
    updateDeltas() {
      for (const statItemKey in this.notificationStatistics) {
        this.notificationStatistics[statItemKey]!.lastDelta =
          this.notificationStatistics[statItemKey]!.currentDelta;
        this.notificationStatistics[statItemKey]!.currentDelta = 0;
      }
    },
    startDeltaInterval() {
      if (!this.deltaIntervalRunning) {
        this.deltaIntervalHandle = setInterval(() => {
          this.updateDeltas();
        }, 5000);
        this.updateDeltas();
        this.deltaIntervalRunning = true;
      }
    },
    stopDeltaInterval() {
      if (this.deltaIntervalRunning) {
        clearInterval(this.deltaIntervalHandle);
        this.deltaIntervalRunning = false;
      }
    },
  },
});
