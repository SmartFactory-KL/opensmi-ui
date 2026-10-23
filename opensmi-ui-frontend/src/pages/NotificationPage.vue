<script setup lang="ts">
import { useNotificationStore } from "@/stores/NotificationStore";
import NotificationTerminal from "../notification/NotificationTerminal.vue";
import NotificationTerminalTab from "../notification/NotificationTerminalTab.vue";
import {
    BugIcon,
    MessageCircleIcon,
    MessageSquareIcon,
    TriangleAlertIcon,
} from "@lucide/vue";

const notificationStore = useNotificationStore();
</script>

<template>
    <main class="w-full h-full flex flex-col justify-stretch items-stretch">
        <div class="h-16 flex flex-row justify-around items-stretch w-full">
            <!-- Tabs -->
            <NotificationTerminalTab
                level="info"
                class="text-blue-200 flex flex-row justify-center items-center gap-x-2"
            >
                <MessageCircleIcon
                    :size="24"
                    class="fill-blue-500 text-blue-600"
                >
                </MessageCircleIcon>
                Info
            </NotificationTerminalTab>
            <NotificationTerminalTab level="warning" class="text-amber-200">
                <TriangleAlertIcon
                    :size="24"
                    class="fill-amber-400 text-amber-600"
                ></TriangleAlertIcon>
                Warning
            </NotificationTerminalTab>
            <NotificationTerminalTab level="error" class="text-red-200">
                <BugIcon :size="24" class="fill-red-400 text-red-600"></BugIcon>
                Error
            </NotificationTerminalTab>
        </div>

        <div style="height: calc(100% - 4rem)">
            <!-- Terminal -->
            <NotificationTerminal
                :notifications="notificationStore.notificationContent.info!"
            ></NotificationTerminal>
            <!-- <NotificationTerminal
                :notifications="notificationStore.notificationContent.warning!"
            ></NotificationTerminal>
            <NotificationTerminal
                :notifications="notificationStore.notificationContent.error!"
            ></NotificationTerminal> -->
        </div>
    </main>
</template>
