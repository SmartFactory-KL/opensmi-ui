import {
  NotificationLevel,
  useNotificationStore,
} from "../stores/NotificationStore";

class Notify {
  notificationStore!: ReturnType<typeof useNotificationStore>;
  init(notificationStore: ReturnType<typeof useNotificationStore>) {
    this.notificationStore = notificationStore;
  }

  notify(level: NotificationLevel | number, message: string) {
    if (typeof level == "number" && Number.isInteger(level)) {
      let intSeverityLevel = "info" as NotificationLevel;
      switch (level) {
        case 0: // info
          intSeverityLevel = "info";
          break;
        case 555: // warning
          intSeverityLevel = "warning";
          break;
        case 999: // error
          intSeverityLevel = "error";
          break;
        default:
          intSeverityLevel = "info";
      }
      this.notificationStore.addNotification(
        intSeverityLevel as NotificationLevel,
        message
      );
    } else {
      this.notificationStore.addNotification(
        level as NotificationLevel,
        message
      );
    }
  }
}

export default new Notify();
