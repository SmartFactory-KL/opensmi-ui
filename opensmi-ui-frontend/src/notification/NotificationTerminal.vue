<script setup lang="ts">
import type { NotificationEvent } from "@/stores/NotificationStore";
import { nextTick, onMounted, ref, watch } from "vue";

const props = defineProps<{
    notifications: NotificationEvent[];
}>();

const stickToBottom = ref(true);
const terminalContainer = ref<HTMLElement | null>(null);

const BOTTOM_THRESHOLD = 20;

function handleScroll() {
    if (!terminalContainer.value) {
        return;
    }

    stickToBottom.value = isAtBottom(terminalContainer.value);
}

function isAtBottom(el: HTMLElement) {
    return el.scrollHeight - el.scrollTop - el.clientHeight < BOTTOM_THRESHOLD;
}

function scrollToBottom() {
    if (terminalContainer.value) {
        terminalContainer.value.scrollTop =
            terminalContainer.value.scrollHeight;
    }
}

watch(
    () => props.notifications.length,
    async () => {
        await nextTick();

        if (stickToBottom.value) {
            scrollToBottom();
        }
    },
);

onMounted(() => {
    scrollToBottom();
});
</script>

<template>
    <div
        ref="terminalContainer"
        class="h-full font-mono text-xs bg-slate-800 text-stone-200 p-4 m-0 overflow-y-scroll"
        v-on:scroll="handleScroll"
    >
        <div v-for="notification in notifications" class="mb-1">
            {{ notification.time }} [{{ notification.sourceNode.identifier }}]:
            {{ notification.message.text }}
            <span
                v-if="notification.errorCode"
                class="bg-red-50 text-slate-500 px-2 py-0.5 text-xs rounded-full"
                >{{ notification.errorCode }}</span
            >
        </div>

        <div v-show="!notifications.length" class="text-gray-400 font-mono">
            no notifications to show
        </div>

        <button
            v-if="true"
            class="absolute bottom-4 right-6 bg-blue-800 text-slate-50 px-3 py-1 rounded text-lg hover:bg-blue-600"
            @click="
                scrollToBottom();
                stickToBottom = true;
            "
        >
            <i class="fa fa-arrow-down"></i> Show latest
        </button>

        <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
        <div class="on-screen-placeholder" style="height: 25vh"></div>
    </div>
</template>
