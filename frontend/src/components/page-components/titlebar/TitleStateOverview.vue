<script setup lang="ts">
import { ref } from "vue";
import { usePageStore } from "../../../stores/PageStore";
import { useServerStore } from "../../../stores/ServerStore";
import { useRouter } from "vue-router";
import TitlebarHeartrate from "./TitlebarHeartrate.vue";

const router = useRouter();

const titleText = ref("");

function handleMouseEnter(evt: MouseEvent) {
  titleText.value = (evt.target as HTMLElement).title || "";
}

function handleMouseLeave() {
  titleText.value = "";
}

const serverStore = useServerStore();
const pageStore = usePageStore();
</script>

<template>
  <div class="state">
    <!-- <div class="state-title text-xs">
      {{ titleText }}
    </div> -->
    <div
      class="state-overview"
      :class="{
        red: pageStore.webSocketConnected != true,
      }"
    >
      <div
        class="state-overview-symbol cursor-pointer"
        title="Connection to Module"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
        @click="router.push('/server')"
        :class="{
          green: serverStore.connectionState == 'connected',
          blue: serverStore.connectionState == 'browsing',
          yellow: serverStore.connectionState == 'pending',
          red: serverStore.connectionState == 'open',
        }"
      >
        <span class="fa-stack fa-1x">
          <i class="fa-solid fa-tower-observation fa-stack-1x"></i>
          <i
            class="fa-solid fa-ban fa-stack-2x text-red-400 opacity-70"
            v-show="serverStore.connectionState == 'open'"
          ></i>
        </span>
      </div>

      <div
        class="socket-stats text-gray-400 text-xs flex flex-col justify-center items-stretch"
      >
        <span class="flex flex-col justify-center items-center">
          <span class="text-xs"> Server Time </span>
          <span v-show="serverStore.serverTime?.length">
            <span
              class="text-gray-400"
              style="font-size: 8pt; line-height: 8pt"
            >
              <!-- {{ serverStore.serverTime.substring(11, 19) }} UTC -->
              {{ new Date(serverStore.serverTime).toLocaleTimeString() }}
            </span>
          </span>
        </span>
      </div>

      <div class="divider"></div>

      <div
        class="text-gray-400 text-xs"
        title="Websocket Messages in the last 5 seconds"
      >
        <TitlebarHeartrate
          :message-count="pageStore.socketStatistics.receivedMessages"
        ></TitlebarHeartrate>
      </div>

      <div
        class="state-overview-symbol"
        title="Websocket Connection"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
        :class="{
          green: pageStore.webSocketConnected == true,
          red: pageStore.webSocketConnected != true,
        }"
      >
        <span class="fa-stack fa-1x">
          <i class="fa-solid fa-rss fa-stack-1x"></i>
          <i
            class="fa-solid fa-ban fa-stack-2x text-red-400 opacity-70"
            v-show="pageStore.webSocketConnected != true"
          ></i>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.state {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
}

.state-overview {
  @apply border border-gray-200 bg-gray-200 m-2 p-1;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  column-gap: 0.4rem;
  align-items: center;
  min-width: 14rem;
  height: 3rem;
  border-radius: 5rem;
}

.state-overview-symbol {
  @apply bg-gray-200 text-gray-600 border border-gray-600;
  border-radius: 50%;
  width: 2.6rem;
  height: 2.6rem;
  display: grid;
  place-items: center;
}

.state-overview-symbol:hover {
  scale: 1.1;
}

.state-overview-symbol.green {
  @apply bg-green-200 text-green-600 border-green-600;
}

.state-overview-symbol.red {
  @apply bg-red-200 text-red-600 border-red-600;
}

.state-overview-symbol.yellow {
  @apply bg-yellow-200 text-yellow-600 border-yellow-600 animate-spin;
}

.state-overview-symbol.blue {
  @apply bg-blue-200 text-blue-600 border-blue-600 animate-spin;
}

.state-overview.red {
  @apply border bg-red-200 text-red-600 border-red-600;
}

.divider {
  @apply bg-gray-500;
  height: 80%;
  width: 0.1rem;
}
</style>
