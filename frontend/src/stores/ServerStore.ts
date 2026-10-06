import { defineStore } from "pinia";
import SocketClient from "../util/SocketClient";

import { simplyGet, simplyPost } from "../util/SimplyFetch";
import Notify from "../util/Notify";
import {
  GenericUpdateMessage,
  RemoteServerStatus,
  ServerStateUpdateMessage,
  ServerTimeUpdateMessage,
} from "../types/UpdateTypes";

const LOCAL_STORAGE_SERVER_URL = "sf-module-ui-server-url";
const LOCAL_STORAGE_SERVER_USERNAME = "sf-module-ui-server-username";
const LOCAL_STORAGE_SERVER_PASSWORD = "sf-module-ui-server-password";

export type ServerConnectionData = {
  serverUrl: string;
  username: string;
  password: string;
};

export const useServerStore = defineStore("server", {
  state: () => {
    return {
      connectionState: "" as RemoteServerStatus,
      serverTime: "",
      isInOnlyPresetMode: false,
      userInput: {
        serverUrl: "",
        username: "",
        password: "",
      } as ServerConnectionData,
      defaultValues: {
        serverUrl: "",
        username: "",
        password: "",
      } as ServerConnectionData,
      connectionData: {
        serverUrl: "",
        username: "",
      },
    };
  },
  actions: {
    attachToSocketClient() {
      SocketClient.addChannelListener("Server", this.handleServerUpdate);
      SocketClient.addChannelListener("refresh", this.refreshContent);
    },
    loadLocalData() {
      let localServerUrl = window.localStorage.getItem(
        LOCAL_STORAGE_SERVER_URL,
      );
      this.userInput.serverUrl = localServerUrl ?? "";

      let localUser = window.localStorage.getItem(
        LOCAL_STORAGE_SERVER_USERNAME,
      );
      this.userInput.username = localUser ?? "";

      let localPassword = window.localStorage.getItem(
        LOCAL_STORAGE_SERVER_PASSWORD,
      );
      this.userInput.password = localPassword ?? "";
    },
    storeUserInputLocally() {
      window.localStorage.setItem(
        LOCAL_STORAGE_SERVER_URL,
        this.userInput.serverUrl,
      );
      window.localStorage.setItem(
        LOCAL_STORAGE_SERVER_USERNAME,
        this.userInput.username,
      );
      window.localStorage.setItem(
        LOCAL_STORAGE_SERVER_PASSWORD,
        this.userInput.password,
      );
    },
    clearLocalData() {
      window.localStorage.clear();
      Notify.notify(
        "info",
        "Local data has been cleared. Refresh to see effect.",
      );
    },
    resetToDefaults() {
      this.userInput.serverUrl = this.defaultValues.serverUrl;
      this.userInput.username = this.defaultValues.username;
      this.userInput.password = this.defaultValues.password;
    },
    refreshContent() {
      this.getServerInformation();
    },
    async getServerInformation() {
      try {
        const result = (await simplyGet("/api/server/")) as any;

        this.connectionState = result.connectionState;
        this.connectionData.serverUrl = result.serverUrl;
        this.connectionData.username = result.username;

        const defaultsResult = await simplyGet(
          "/api/server/default-connection-data",
        );

        this.defaultValues.serverUrl = defaultsResult.defaultServerUrl;
        this.defaultValues.username = defaultsResult.defaultServerUsername;
        this.defaultValues.password = defaultsResult.defaultServerPassword;

        this.isInOnlyPresetMode = defaultsResult.isInOnlyPresetMode;

        // Only setting defaults to userInput if NONE of the inputs was set previously
        if (
          this.userInput.serverUrl == "" &&
          this.userInput.username == "" &&
          this.userInput.password == ""
        ) {
          this.userInput.serverUrl = defaultsResult.defaultServerUrl;
          this.userInput.username = defaultsResult.defaultServerUsername;
          this.userInput.password = defaultsResult.defaultServerPassword;
        }
      } catch (e) {
        Notify.notify(
          "error",
          "ServerStore Error: getServerInformation() -> " +
            (e as Error).message,
        );
        console.warn("error while getting server state");
        console.warn(e);
      }
    },
    async requestConnect() {
      console.log("Requesting connection to " + this.userInput.serverUrl);

      try {
        const result = await simplyPost("/api/server/connect", this.userInput);
        console.log(result);

        this.connectionData.serverUrl = result.serverUrl;
        this.connectionData.username = result.username;

        this.storeUserInputLocally();
      } catch (e) {
        Notify.notify(
          "error",
          "ServerStore Error: requestConnect() -> " + (e as Error).message,
        );
        console.warn("Error during connection request");
        console.warn(e);
      }
    },
    async requestDisconnect() {
      console.log(
        "Requesting disconnect from " + this.connectionData.serverUrl,
      );

      try {
        const result = await simplyPost("/api/server/disconnect", {});
        console.log(result);
        this.connectionState = "DISCONNECTED";
        this.connectionData.serverUrl = "";
        this.connectionData.username = "";
      } catch (e) {
        Notify.notify(
          "error",
          "ServerStore Error: requestDisconnect() -> " + (e as Error).message,
        );
        console.warn("Error during disconnect request");
        console.warn(e);
      }
    },
    async requestForceDisconnect() {
      console.warn(
        "Requesting forced disconnect from " + this.connectionData.serverUrl,
      );

      try {
        const result = await simplyPost(
          "/api/server/disconnect?force=true",
          {},
        );
        console.log(result);
        this.connectionState = "DISCONNECTED";
        this.connectionData.serverUrl = "";
        this.connectionData.username = "";
      } catch (e) {
        Notify.notify(
          "error",
          "ServerStore Error: requestForceDisconnect() -> " +
            (e as Error).message,
        );
        console.warn("Error during forced disconnect request");
        console.warn(e);
      }
    },
    handleServerUpdate(update: GenericUpdateMessage) {
      if (!update || !update.updateType) {
        return;
      }

      switch (update.updateType) {
        case "ServerStateUpdate":
          this.connectionState =
            update.updateContent as ServerStateUpdateMessage;
          break;
        case "ServerTimeUpdate":
          this.serverTime = update.updateContent as ServerTimeUpdateMessage;
          break;
        default:
          console.warn("invalid update type for server");
          console.warn(update);
          break;
      }
    },
  },
});
