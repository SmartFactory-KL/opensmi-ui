import type { ToastClass, ToastMessage, ToastSettings } from "@/toast/Toaster";
import { defineStore } from "pinia";

export const useToasterStore = defineStore("toaster", {
  state(): {
    toasts: ToastMessage[];
    nextId: number;
  } {
    return {
      toasts: [],
      nextId: 0,
    };
  },
  getters: {},
  actions: {
    addToast(
      toastClass: ToastClass,
      msg: string,
      settings: ToastSettings,
    ) {
      this.nextId++

      this.toasts.push({
        id: this.nextId,
        toastClass,
        msg,
        settings,
      } as ToastMessage);
    },

    removeToast(id: number) {
      this.toasts = this.toasts.filter((toast) => toast.id !== id);
    },

    clearToasts() {
      this.toasts = [];
    },
  },
});
