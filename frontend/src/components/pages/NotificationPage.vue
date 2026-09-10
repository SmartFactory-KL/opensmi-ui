<script setup lang="ts">
import { useNotificationStore } from "../../stores/NotificationStore";

import NotificationTerminal from "../notification/NotificationTerminal.vue";
import NotificationTerminalTab from "../notification/NotificationTerminalTab.vue";

const notificationStore = useNotificationStore();
</script>

<template>
  <div class="w-full h-full flex flex-col justify-stretch items-stretch">
    <div class="h-16 flex flex-row justify-around items-stretch w-full">
      <!-- Tabs -->
      <NotificationTerminalTab
        level="info"
        :is-active="notificationStore.currentTab == 'info'"
        @click="notificationStore.currentTab = 'info'"
        class="text-blue-200"
        ><i class="fa-solid fa-info-circle fa-2xl"></i>
        Info</NotificationTerminalTab
      >
      <NotificationTerminalTab
        level="warning"
        :is-active="notificationStore.currentTab == 'warning'"
        @click="notificationStore.currentTab = 'warning'"
        class="text-amber-200"
        ><i class="fa-solid fa-warning fa-2xl"></i>
        Warning</NotificationTerminalTab
      >
      <NotificationTerminalTab
        level="error"
        :is-active="notificationStore.currentTab == 'error'"
        @click="notificationStore.currentTab = 'error'"
        class="text-red-200"
        ><i class="fa-solid fa-bug fa-2xl"></i> Error</NotificationTerminalTab
      >
    </div>

    <div style="height: calc(100% - 4rem)">
      <!-- Terminal -->
      <NotificationTerminal
        v-if="notificationStore.currentTab == 'info'"
        :notifications="notificationStore.notificationContent.info"
      ></NotificationTerminal>
      <NotificationTerminal
        v-if="notificationStore.currentTab == 'warning'"
        :notifications="notificationStore.notificationContent.warning"
      ></NotificationTerminal>
      <NotificationTerminal
        v-if="notificationStore.currentTab == 'error'"
        :notifications="notificationStore.notificationContent.error"
      ></NotificationTerminal>
    </div>
  </div>
</template>
