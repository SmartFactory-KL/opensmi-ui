<script setup lang="ts">
import { useNotificationStore } from "@/stores/NotificationStore";
import { BugIcon, MessageCircleIcon, TriangleAlertIcon } from "@lucide/vue";
import { nextTick, onUnmounted, ref, watch } from "vue";

const notificationStore = useNotificationStore();
</script>

<template>
    <div
        class="flex flex-row justify-end items-center gap-x-2 border-2 border-slate-500 rounded-md px-2 py-1 bg-slate-200 cursor-pointer"
        @click="$router.push('/notification')"
    >
        <div class="text-blue-600 flex flex-col justify-center items-center">
            <MessageCircleIcon :size="24" class="fill-blue-500" :class="{'breathe-animation': notificationStore.animate.info !== null}">
            </MessageCircleIcon>
            <span class="text-xs">
                {{ notificationStore.notificationContent.info.length || 0 }}
            </span>
        </div>
        <div class="text-amber-600 flex flex-col justify-center items-center">
            <TriangleAlertIcon
                :size="24"
                class="fill-amber-400"
             :class="{'breathe-animation': notificationStore.animate.warning !== null}"></TriangleAlertIcon>
            <span class="text-xs">
                {{ notificationStore.notificationContent.warning.length || 0 }}
            </span>
        </div>
        <div class="text-red-600 flex flex-col justify-center items-center">
            <BugIcon :size="24" class="fill-red-400" :class="{ 'breathe-animation': notificationStore.animate.error !== null }"" ></BugIcon>
            <span class="text-xs">
                {{ notificationStore.notificationContent.error.length || 0 }}
            </span>
        </div>
    </div>
</template>

<style scoped>
.breathe-animation {
    animation: breathe 210ms ease-in-out;
}

@keyframes breathe {
    0% {
        transform: scale(1);
        opacity: 1.0;
    }
    40% {
        transform: scale(1.08);
        opacity: 0.8;
    }
    70% {
        transform: scale(0.96);
        opacity: 0.9;
    }
    100% {
        transform: scale(1);
        opacity: 1.0;
    }
}

@media (prefers-reduced-motion: reduce) {
    .breathe-animation {
        animation: none;
    }
}
</style>
