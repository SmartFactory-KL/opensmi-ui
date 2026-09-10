import { defineStore } from "pinia";
import SocketClient from "../util/SocketClient";
import { GenericUpdateMessage } from "../types/UpdateTypes";
import { simplyGet } from "../util/SimplyFetch";
import Notify from "../util/Notify";

export const usePinGuardStore = defineStore("pin-guard", {
  state: () => {
    return {
      isPending: false,
      pinState: {
        isEnabled: false,
        isLocked: false,
      } as PinGuardState,
      pinModalVisible: false,
      digits: [] as Number[],
      pinFeedback: "",
      onPinSetCallback: null as null | (() => void),
    };
  },
  getters: {
    isLocked(state) {
      if (state.pinState.isEnabled) {
        return state.pinState.isLocked;
      }

      // if not enabled, it will never be locked
      return false;
    },
  },
  actions: {
    attachToSocketClient() {
      SocketClient.addChannelListener("PinGuard", this.handleUpdate);
    },
    async refreshPinGuardData() {
      this.isPending = true;

      try {
        const result = (await simplyGet(
          "/api/server/pin-guard"
        )) as PinGuardState;
        this.pinState = result;
        console.log("PinGuard State: ");
        console.log(this.pinState);
      } catch (e) {
        Notify.notify("error", "MachineStore Error: " + (e as Error).message);
        console.error(e);
      } finally {
        this.isPending = false;
      }
    },
    hidePinModal() {
      this.pinModalVisible = false;
    },
    addNumber(val: number) {
      switch (val) {
        case 0:
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
        case 9:
          this.digits.push(val)
          break
        default:
          return
      }
    },
    resetPin() {
      this.digits = [];
    },
    removeLast() {
      this.digits.pop()
    },
    async sendPin() {
      try {
        if (this.digits.length == 0) {
          throw new Error("Please specify a PIN with at least one digit");
        }

        const input = {
          pin: this.digits.join(""),
        };

        await fetch("/api/server/pin-guard/unlock", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(input),
        }).then(async (result) => {
          if (!result.ok) {
            const details = await result.json();
            throw new Error(details.detail);
          }
        });

        this.pinFeedback = "";
        this.pinModalVisible = false;

        if (this.onPinSetCallback !== null) {
          this.onPinSetCallback();
        }
      } catch (e) {
        console.error(e);
        this.pinFeedback = (e as Error).message;
      }

      this.resetPin();
    },
    async sendLockRequest() {
      try {
        await simplyGet("/api/server/pin-guard/lock");
      } catch (e) {
        console.error(e);
        this.pinFeedback = (e as Error).message;
      }
    },
    async requestPinInput(onPinSentCallback: () => void) {
      this.onPinSetCallback = onPinSentCallback;
      if (!this.pinModalVisible) {
        this.pinModalVisible = true;
      }
    },
    handleUpdate(update: GenericUpdateMessage) {
      if (!update || !update.updateType) {
        return;
      }

      switch (update.updateType) {
        case "PinGuardStateUpdate":
          this.pinState.isLocked = update.updateContent.newIsLocked;
          break;
        default:
          console.warn("Received invalid updateType for Variable:");
          console.warn(update);
          break;
      }
    },
  },
});
