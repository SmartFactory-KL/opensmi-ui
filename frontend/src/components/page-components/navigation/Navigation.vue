<script setup lang="ts">
import { useMachineStore } from "../../../stores/MachineStore";
import { usePageStore } from "../../../stores/PageStore";

import NavigationCommonLinks from "./NavigationCommonLinks.vue";
import NavigationMachineItem from "./NavigationMachineItem.vue";

const pageStore = usePageStore();
const machineStore = useMachineStore();

function toggleNavigation() {
  pageStore.toggleShowNavigation();
}
</script>

<template>
  <div class="navigation" :class="{ hide: !pageStore.showNavigation }">
    <div class="control" @click="toggleNavigation">
      <i class="fa-solid fa-angles-left" v-show="pageStore.showNavigation"></i>
      <i
        class="fa-solid fa-angles-right"
        v-show="!pageStore.showNavigation"
      ></i>
    </div>
    <div class="nav-content">
      <div class="nav-top">
        <div class="nav-module-dashboard">
          <NavigationCommonLinks></NavigationCommonLinks>
        </div>
        <div class="nav-item-list">
          <NavigationMachineItem
            :machine="machine"
            v-for="[nodeId, machine] in machineStore.machines"
            :key="nodeId"
          ></NavigationMachineItem>
        </div>
      </div>
      <div class="nav-bottom">
        <div class="font-thin text-orange-300">
          {{ pageStore.appVersion }}
        </div>
        <div>
          made with <i class="fa-solid fa-heart-pulse"></i>
          | WebSocket
          <span v-show="pageStore.webSocketConnected">online</span>
          <span
            class="text-red-400 animate-pulse"
            v-show="!pageStore.webSocketConnected"
            >offline</span
          >
        </div>
      </div>
    </div>
    <div class="blank"></div>
  </div>
</template>

<style scoped>
.navigation {
  @apply bg-gray-200 text-gray-200;
  height: 100%;

  display: grid;
  grid-template-rows: 4rem auto;
  grid-template-columns: auto 2rem;

  grid-template-areas:
    "navigation-items control"
    "navigation-items blank";
}

.control {
  @apply bg-gray-700;
  grid-area: control;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.control:hover {
  @apply bg-gray-700;
}

.nav-content {
  @apply bg-gray-700;
  grid-area: navigation-items;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: stretch;
  transition: width 0.5s ease;
  width: 20rem;
  overflow: hidden;
}

.nav-module-dashboard {
  overflow: hidden;
  flex-shrink: 0;
  height: 6rem;
}

.nav-top {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  height: calc(100% - 2rem);
}

.nav-item-list {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  row-gap: 0.5rem;
  padding-left: 1rem;
  overflow-y: auto;
}

.nav-item {
  @apply font-bold text-xl text-secondary p-2 pl-4;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: flex-start;
  align-items: center;
  column-gap: 1rem;
  width: 100%;
}

.nav-item.router-link-active {
  @apply text-gray-200 bg-primary;
}

.nav-item:hover {
  @apply bg-gray-500;
}

.nav-bottom {
  @apply text-xs text-orange-300;
  height: 2rem;
  text-align: center;
}

.blank {
  @apply bg-primary;
  grid-area: blank;
}

.hide .blank {
  @apply bg-secondary;
  opacity: 0.5;
}

.hide .nav-content {
  width: 0;
  /* display: none; */
}
</style>
