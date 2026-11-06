import { useToasterStore } from "@/stores/ToasterStore";

export type ToastClass = "info" | "warning" | "success" | "error";

export interface ToastSettings {
  delayMS?: number;
}

export interface ToastMessage {
  id: number;
  toastClass: ToastClass;
  msg: string;
  errorCode?: string;
  settings: ToastSettings;
}

class Toaster {
  store?: ReturnType<typeof useToasterStore>;

  attachStore() {
    this.store = useToasterStore();
  }

  addMessage(
    toastClass: ToastClass,
    msg: string,
    errorCode: string | null = null,
    settings: ToastSettings = {
      delayMS: 750,
    },
  ) {
    if (!this.store) {
      return;
    }

    this.store.addToast(toastClass, msg, errorCode, settings);
  }

  info(msg: string) {
    this.addMessage("info", msg, null, {
      delayMS: 2500,
    });
  }

  success(msg: string) {
    this.addMessage("success", msg, null, {
      delayMS: 2500,
    });
  }

  warning(msg: string) {
    this.addMessage("warning", msg, null, {
      delayMS: 5000,
    });
  }

  error(msg: string, errorCode: string | null = null) {
    this.addMessage("error", msg, errorCode, {
      delayMS: 5000,
    });
  }
}

export default new Toaster();
