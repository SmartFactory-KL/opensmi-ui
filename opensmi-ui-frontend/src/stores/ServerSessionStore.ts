import { simplyGetToJSON, simplyPostToText } from "@/fetch/simplyFetch";
import type SocketClient from "@/socket/SocketClient";
import type { GenericUpdateMessage } from "@/types/GenericTypes";
import type { OPCClientState, ServerStateUpdate, ServerTimeUpdate } from "@/types/UpdateTypes";
import { defineStore } from "pinia";
import { usePageStore } from "./PageStore";
import Toaster from "@/toast/Toaster";

export interface OPCSessionSettings {
  timeout: number;
  autoReconnect: boolean;
  reconnectMaxDelay: number;
  watchdogInterval: number;
  reconnectRequestTimeout: number;
}

export interface OPCSessionData {
  url: string;
  username: string;

  state: OPCClientState;

  applicationUri: string;
  productUri: string;
  namespaces: string[];

  settings: OPCSessionSettings;
}

export interface ServerStoreUserInput {
  serverUrl: string;
  username: string;
  password: string;
}

export const useServerStore = defineStore("server", {
  state: (): {
    serverTime: string;

    requestData: {
      isPending: boolean;
      error: string | null;
    };

    userInput: ServerStoreUserInput;

    sessionData: OPCSessionData;
  } => {
    return {
      serverTime: "--:--:--",

      requestData: {
        isPending: false,
        error: null,
      },

      userInput: {
        serverUrl: "",
        username: "",
        password: "",
      },

      sessionData: {
        applicationUri: "",
        productUri: "",
        state: "disconnected",
        namespaces: [],
        url: "",
        username: "",
        settings: {
          autoReconnect: false,
          reconnectMaxDelay: 0,
          reconnectRequestTimeout: 0,
          timeout: 0,
          watchdogInterval: 0,
        },
      },
    };
  },
  getters: {
    isConnected(data) {
      return data.sessionData.state === "connected";
    },
    isDisconnected(data) {
      return data.sessionData.state === "disconnected";
    },
    getState(data) {
      return data.sessionData.state;
    },
  },
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      socketClient.addChannelListener("Server", this.handleServerUpdate);

      socketClient.addConnectionListener(this.handleSocketStateUpdate);
    },
    async requestServerStatus() {
      if (this.requestData.isPending) {
        return;
      }

      this.requestData.isPending = true;
      this.requestData.error = null;

      try {
        const sessionData = await simplyGetToJSON("/api/opc-session/info");
        this.sessionData = sessionData;

        console.log(this.sessionData);
      } catch (e) {
        this.requestData.error = `Failed to connect: ${e}`;
      } finally {
        this.requestData.isPending = false;
      }
    },
    handleRefresh() {
      // TODO
    },
    writeUserInput(input: ServerStoreUserInput) {
      this.userInput.serverUrl = input.serverUrl;
      this.userInput.username = input.username;
      this.userInput.password = input.password;
    },
    applyPageDefaults() {
      const pageStore = usePageStore();

      this.writeUserInput({
        serverUrl: pageStore.pageSettings.defaultServerUrl,
        username: pageStore.pageSettings.defaultServerUsername,
        password: pageStore.pageSettings.defaultServerPassword,
      });
    },
    async requestConnect() {
      if (this.requestData.isPending) {
        return;
      }

      this.requestData.isPending = true;
      this.requestData.error = null;

      try {
        if (
          this.userInput.serverUrl.trim().length == 0 ||
          this.userInput.username.trim().length == 0 ||
          this.userInput.password.trim().length == 0
        ) {
          throw new Error(
            "Missing inputs: Please provide URL, Username and Password!",
          );
        }

        await simplyPostToText("/api/opc-session/connect", {
          url: this.userInput.serverUrl,
          username: this.userInput.username,
          password: this.userInput.password,
        });

        usePageStore().storeLocalConnectionData();

        await this.requestServerStatus();
      } catch (e) {
        this.requestData.error = `Failed to connect: ${e}`;
        Toaster.error(this.requestData.error);
      } finally {
        this.requestData.isPending = false;
      }
    },
    async requestDisconnect() {
      if (this.requestData.isPending) {
        return;
      }

      this.requestData.isPending = true;
      this.requestData.error = null;

      try {
        await simplyPostToText("/api/opc-session/disconnect", {});
      } catch (e) {
        this.requestData.error = `Failed to disconnect: ${e}`;
      } finally {
        this.requestData.isPending = false;
      }
    },
    handleServerUpdate(update: GenericUpdateMessage<any>) {
      if (!update || !update.updateType) {
        return;
      }

      let content: any;
      switch (update.updateType) {
        case "ServerStateUpdate":
          content = update.updateContent as ServerStateUpdate;
          this.sessionData.state = content.newState;
          break;
        case "ServerTimeUpdate":
          content = update.updateContent as ServerTimeUpdate;
          this.serverTime = content.newTime.substring(11, 19);
          break;
        default:
          console.warn("invalid update type for server");
          console.warn(update);
          break;
      }
    },
    handleSocketStateUpdate(newState: WebSocket["readyState"]) {
      if (newState == WebSocket.OPEN) {
        this.requestServerStatus();
      }
    },
  },
});
