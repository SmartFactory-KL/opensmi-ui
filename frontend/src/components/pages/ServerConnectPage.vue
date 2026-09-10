<script setup lang="ts">
import { usePageStore } from "../../stores/PageStore";
import { usePinGuardStore } from "../../stores/PinStore";
import { useServerStore } from "../../stores/ServerStore";

import BlueButton from "../BlueButton.vue";

const serverStore = useServerStore();
const pageStore = usePageStore();
const pinGuardStore = usePinGuardStore();

function requestConnection() {
  serverStore.requestConnect();
}
</script>

<template>
  <div class="m-4">
    <h4 class="text-4xl">Connect to Module Server</h4>

    <div class="mt-4">
      <BlueButton
        @click="serverStore.resetToDefaults()"
        :disabled="pinGuardStore.isLocked"
      >
        Reset to server defaults
      </BlueButton>
    </div>

    <div
      class="border-2 border-purple-600 text-purple-800 bg-purple-200 p-4 flex flex-col justify-start items-center"
      style="width: 25rem"
      v-show="pinGuardStore.isLocked"
    >
      <div>
        <i class="fa fa-shield fa-xl"></i>
        <span class="text-xl ml-2">PinGuard Active!</span>
      </div>
      <div class="text-xs mt-2">
        To use this page, please unlock the PinGuard first
      </div>
    </div>

    <div class="input-columns mt-1">
      <div>
        <span
          class="text-sm text-primary"
          v-show="!(serverStore.connectionState == 'open')"
        >
          Server is currently connected or pending. To change these inputs,
          disconnect first.
        </span>
      </div>
      <div class="input-box">
        <label for="server-url">Server URL</label>
        <input
          name="server-url"
          type="text"
          v-model="serverStore.userInput.serverUrl"
          :disabled="
            !(serverStore.connectionState == 'open') || pinGuardStore.isLocked
          "
        />
      </div>
      <div class="input-box">
        <label for="username">Username</label>
        <input
          type="text"
          v-model="serverStore.userInput.username"
          :disabled="
            !(serverStore.connectionState == 'open') || pinGuardStore.isLocked
          "
        />
      </div>
      <div class="input-box">
        <label for="password">Password</label>
        <input
          type="password"
          v-model="serverStore.userInput.password"
          :disabled="
            !(serverStore.connectionState == 'open') || pinGuardStore.isLocked
          "
        />
      </div>

      <div
        v-show="serverStore.isInOnlyPresetMode"
        class="bg-yellow-200 border border-yellow-800 text-yellow-800 p-2"
      >
        The server is in "only prefedined mode". This means, that the connection
        data from above will be ignored, but you can still use the "Connect" and
        "Disconnect" buttons.
      </div>

      <div class="flex flex-col gap-y-2">
        <span class="text-sm">Current connection state to server:</span>
        <span
          class="p-2"
          :class="{
            green: serverStore.connectionState == 'connected',
            blue: serverStore.connectionState == 'browsing',
            yellow: serverStore.connectionState == 'pending',
            red: serverStore.connectionState == 'open',
          }"
        >
          {{ serverStore.connectionState }}
        </span>
        <span
          v-show="serverStore.connectionState == 'connected'"
          class="flex flex-col"
        >
          <span class="text-sm">Connection Information:</span>
          <span class="text-pink-500">
            {{ serverStore.connectionData.serverUrl }}
          </span>
          as
          <span class="text-pink-500">
            {{ serverStore.connectionData.username }}
          </span>
        </span>
      </div>
      <div class="submit-box flex flex-row justify-end gap-x-4">
        <BlueButton
          type="button"
          @click="requestConnection"
          :disabled="
            serverStore.connectionState != 'open' || pinGuardStore.isLocked
          "
          >Connect</BlueButton
        >
        <BlueButton
          type="button"
          @click="serverStore.requestDisconnect"
          :disabled="
            serverStore.connectionState == 'open' || pinGuardStore.isLocked
          "
          >Disconnect</BlueButton
        >
      </div>

      <hr class="border-primary" />

      <div class="flex flex-col items-start">
        <span class="text-xs">
          The connection data of the last successful connection will be stored
          locally. You can clear them here:
        </span>
        <BlueButton
          @click="serverStore.clearLocalData()"
          :disabled="pinGuardStore.isLocked"
        >
          Clear local user data
        </BlueButton>
      </div>

      <hr class="border-primary" v-show="pageStore.showFlags.devOptions" />

      <div v-show="pageStore.showFlags.devOptions">
        <span class="text-lg font-bold text-red-400">Danger Zone</span>
        <p class="text-base text-red-600">
          These operations might break things. Only use them if you know what
          you are doing. During normal operation these are never needed.
        </p>

        <div class="border border-red-600 bg-red-100 shadow-lg p-4 my-2">
          <div>
            Force Disconnect will try to disconnect without regards for current
            connection state.
          </div>
          <div>
            <BlueButton
              class="text-red-500 bg-red-200"
              @click="serverStore.requestForceDisconnect()"
              :disabled="pinGuardStore.isLocked"
            >
              Force Disconnect
            </BlueButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-columns {
  display: flex;
  flex-direction: column;
  row-gap: 2rem;
  width: 25rem;
}

.input-box {
  display: flex;
  flex-direction: column;
}

.green {
  @apply bg-green-200 text-green-600;
}

.red {
  @apply bg-red-200 text-red-600;
}

.yellow {
  @apply bg-yellow-200 text-yellow-600;
}

.blue {
  @apply bg-blue-300 text-blue-600;
}
</style>
