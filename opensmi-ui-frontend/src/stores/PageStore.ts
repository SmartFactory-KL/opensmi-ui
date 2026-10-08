import { simplyGetToJSON } from "@/fetch/simplyFetch";
import { mergeStoredSettings } from "@/util/merge";
import { defineStore } from "pinia";
import type { useServerStore } from "./ServerStore";
import type SocketClient from "@/socket/SocketClient";

const LOCAL_STORAGE_PAGE_SETTINGS = "opensmi-ui-page-settings";
const LOCAL_STORAGE_CONNECTION_DATA = "opensmi-ui-connection-data";

export interface PageSettings {
  appVersion: string;
  isAutoConnect: boolean;

  defaultServerUrl: string;
  defaultServerUsername: string;
  defaultServerPassword: string;
}

export interface LocalSettings {
  entityIds: false;
  nodeIds: false;
}

export interface LocalConnectionData {
  localServerUrl: string;
  localServerUsername: string;
  localServerPassword: string;
}

export const usePageStore = defineStore("page", {
  state: (): {
    socket: {
      state: WebSocket["readyState"];
      receivedMessages: number;
    };
    requestData: {
      isPending: boolean;
      error: string | null;
    };
    pageSettings: PageSettings;
    localSettings: LocalSettings;
    localConnectionData: LocalConnectionData;
  } => {
    return {
      socket: {
        state: WebSocket.CLOSED,
        receivedMessages: 0,
      },
      requestData: {
        isPending: false,
        error: null,
      },
      pageSettings: {
        appVersion: "",
        isAutoConnect: false,

        defaultServerUrl: "",
        defaultServerUsername: "",
        defaultServerPassword: "",
      },
      localSettings: {
        entityIds: false,
        nodeIds: false,
      },
      localConnectionData: {
        localServerUrl: "",
        localServerUsername: "",
        localServerPassword: "",
      },
    };
  },
  getters: {
    isSocketConnected(state) {
      return state.socket.state === WebSocket.OPEN;
    },
  },
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      socketClient.addConnectionListener(this.updateSocketState);
      socketClient.addMessageCountListener(this.updateMessageCount);
    },
    storeLocalSettings() {
      try {
        localStorage.setItem(
          LOCAL_STORAGE_PAGE_SETTINGS,
          JSON.stringify(this.localSettings),
        );
      } catch (e) {
        console.warn(`failed to store settings: ${e}`);
      }
    },
    storeLocalConnectionData() {
      try {
        localStorage.setItem(
          LOCAL_STORAGE_CONNECTION_DATA,
          JSON.stringify(this.localConnectionData),
        );
      } catch (e) {
        console.warn(`failed to store connection data: ${e}`);
      }
    },
    clearLocalData() {
      this.clearLocalConnectionData();
      this.clearLocalSettings();
    },
    clearLocalSettings() {
      try {
        localStorage.removeItem(LOCAL_STORAGE_PAGE_SETTINGS);
      } catch (e) {
        console.warn(`failed to clear local settings: ${e}`);
      }
    },
    clearLocalConnectionData() {
      try {
        localStorage.removeItem(LOCAL_STORAGE_CONNECTION_DATA);
      } catch (e) {
        console.warn(`failed to clear local connection data: ${e}`);
      }
    },
    loadSettings() {
      try {
        const settingsInput = localStorage.getItem(LOCAL_STORAGE_PAGE_SETTINGS);
        if (settingsInput !== null) {
          const settings = JSON.parse(settingsInput);
          this.localSettings = mergeStoredSettings<LocalSettings>(
            this.localSettings,
            settings,
          );
        }

        const connectionDataInput = localStorage.getItem(
          LOCAL_STORAGE_CONNECTION_DATA,
        );
        if (connectionDataInput !== null) {
          const connectionData = JSON.parse(connectionDataInput);

          this.localConnectionData = mergeStoredSettings<LocalConnectionData>(
            this.localConnectionData,
            connectionData,
          );
        }
      } catch (e) {
        console.warn(`failed to load settings: ${e}`);
      }

      // fill defaults if non other are there
      if (this.localConnectionData.localServerUrl.length == 0) {
        this.localConnectionData.localServerUrl =
          this.pageSettings.defaultServerUrl;
      }

      if (this.localConnectionData.localServerUsername.length == 0) {
        this.localConnectionData.localServerUsername =
          this.pageSettings.defaultServerUsername;
      }

      if (this.localConnectionData.localServerPassword.length == 0) {
        this.localConnectionData.localServerPassword =
          this.pageSettings.defaultServerPassword;
      }
    },
    updateMessageCount(newAmount: number, _: number) {
      this.socket.receivedMessages = newAmount;
    },
    updateSocketState(newState: WebSocket["readyState"]) {
      this.socket.state = newState;
    },
    writeDefaultsToServerStore(serverStore: ReturnType<typeof useServerStore>) {
      console.log(this.localSettings);
      serverStore.writeUserInput({
        serverUrl: this.localConnectionData.localServerUrl,
        username: this.localConnectionData.localServerUsername,
        password: this.localConnectionData.localServerPassword,
      });
    },
    async requestPageInfo() {
      if (this.requestData.isPending == true) {
        return;
      }

      this.requestData.isPending = true;
      this.requestData.error = null;

      try {
        const result = (await simplyGetToJSON(
          "/api/info/settings",
        )) as PageSettings;

        this.pageSettings = result;
        this.loadSettings();
      } catch (e) {
        this.requestData.error = `Failed to load Page: ${e}`;
      } finally {
        this.requestData.isPending = false;
      }
    },
  },
});
