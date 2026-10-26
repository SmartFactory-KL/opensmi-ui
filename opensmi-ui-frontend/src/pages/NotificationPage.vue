<script setup lang="ts">
import { useNotificationStore } from "@/stores/NotificationStore";
import NotificationTerminal from "../notification/NotificationTerminal.vue";
import NotificationTerminalTab from "../notification/NotificationTerminalTab.vue";
import { BugIcon, MessageCircleIcon, TriangleAlertIcon } from "@lucide/vue";

const notificationStore = useNotificationStore();
</script>

<template>
    <main class="w-full h-full flex flex-col justify-stretch items-stretch">
        <div class="h-16 flex flex-row justify-around items-stretch w-full">
            <!-- Tabs -->
            <NotificationTerminalTab
                level="info"
                class="text-blue-200 flex flex-row justify-center items-center gap-x-2"
                :is-active="notificationStore.currentTab == 'info'"
                @click="notificationStore.setTab('info')"
            >
                <MessageCircleIcon
                    :size="24"
                    class="fill-blue-500 text-blue-600"
                >
                </MessageCircleIcon>
                Info
                <span>
                    [{{
                        notificationStore.notificationContent.info.length || 0
                    }}]
                </span>
            </NotificationTerminalTab>
            <NotificationTerminalTab
                level="warning"
                class="text-amber-200"
                :is-active="notificationStore.currentTab == 'warning'"
                @click="notificationStore.setTab('warning')"
            >
                <TriangleAlertIcon
                    :size="24"
                    class="fill-amber-400 text-amber-600"
                ></TriangleAlertIcon>
                Warning
                <span>
                    [{{
                        notificationStore.notificationContent.warning.length ||
                        0
                    }}]
                </span>
            </NotificationTerminalTab>
            <NotificationTerminalTab
                level="error"
                class="text-red-200"
                :is-active="notificationStore.currentTab == 'error'"
                @click="notificationStore.setTab('error')"
            >
                <BugIcon :size="24" class="fill-red-400 text-red-600"></BugIcon>
                Error
                <span>
                    [{{
                        notificationStore.notificationContent.error.length || 0
                    }}]
                </span>
            </NotificationTerminalTab>
        </div>

        <div style="height: calc(100% - 4rem)">
            <!-- Terminal -->
            <NotificationTerminal
                v-show="notificationStore.currentTab === 'info'"
                :notifications="notificationStore.notificationContent.info!"
            ></NotificationTerminal>
            <NotificationTerminal
                v-show="notificationStore.currentTab === 'warning'"
                :notifications="notificationStore.notificationContent.warning!"
            ></NotificationTerminal>
            <NotificationTerminal
                v-show="notificationStore.currentTab === 'error'"
                :notifications="notificationStore.notificationContent.error!"
            ></NotificationTerminal>
        </div>
    </main>
</template>
