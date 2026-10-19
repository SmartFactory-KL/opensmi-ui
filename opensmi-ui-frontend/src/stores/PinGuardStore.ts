import { simplyGetToJSON } from "@/fetch/simplyFetch";
import type SocketClient from "@/socket/SocketClient";
import Toaster from "@/toast/Toaster";
import type { GenericUpdateMessage } from "@/types/GenericTypes";
import { defineStore } from "pinia";

export interface PinGuardState {
  isEnabled: boolean;
  isLocked: boolean;
}

export const usePinGuardStore = defineStore("pin-guard", {
  state: (): {
    requestState: {
      isPending: boolean;
      error: string | null;
    };
    state: PinGuardState;

    pinInput: {
      modalVisible: boolean;
      digits: Number[];
    };
  } => {
    return {
      requestState: {
        isPending: false,
        error: null,
      },
      state: {
        isEnabled: false,
        isLocked: false,
      },
      pinInput: {
        modalVisible: false,
        digits: [],
      },
    };
  },
  getters: {
    isLocked(data) {
      if (data.state.isEnabled) {
        return data.state.isLocked;
      }

      return false;
    },
  },
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      socketClient.addChannelListener("PinGuard", this.handleUpdate);
    },
    async requestData() {
      if (this.requestState.isPending === true) {
        return;
      }

      this.requestState.isPending = true;

      try {
        const result = (await simplyGetToJSON(
          "/api/pin-guard/state",
        )) as PinGuardState;
        this.state = result;
      } catch (e) {
        this.requestState.error = `Failed to gather PinGuard State: ${e}`;
        Toaster.error(this.requestState.error);
      } finally {
        this.requestState.isPending = false;
      }
    },
    handleUpdate(update: GenericUpdateMessage<any>) {
      if (!update || !update.updateType) {
        return;
      }

      switch (update.updateType) {
        case "PinGuardStateUpdate":
          this.state.isLocked = update.updateContent.newIsLocked;
          break;
        default:
          console.warn("Received invalid updateType for Variable:");
          console.warn(update);
          break;
      }
    },
  },
});
