<script setup lang="ts">
import { usePageStore } from "@/stores/PageStore";
import {
    ArrowDownIcon,
    GaugeIcon,
    MonitorCheckIcon,
    MonitorDotIcon,
    MonitorOffIcon,
} from "@lucide/vue";

const WebSocketState = {
    OPEN: WebSocket.OPEN,
    CLOSED: WebSocket.CLOSED,
    CONNECTING: WebSocket.CONNECTING,
    CLOSING: WebSocket.CLOSING,
};

const pageStore = usePageStore();
</script>

<template>
    <div
        class="flex flex-col items-center border-4 rounded-lg h-13 w-16 p-0.5 shadow-lg"
        title="Incoming socket messages per second"
        :class="
            pageStore.isSocketConnected
                ? ['border-green-600', 'bg-green-100']
                : ['border-red-600', 'bg-red-100']
        "
    >
        <MonitorCheckIcon
            v-show="pageStore.socket.state === WebSocketState.OPEN"
            :size="32"
            class="text-green-500"
        />
        <MonitorDotIcon
            v-show="pageStore.socket.state === WebSocketState.CONNECTING"
            :size="32"
            class="text-amber-500"
        />
        <MonitorOffIcon
            v-show="
                pageStore.socket.state === WebSocketState.CLOSED ||
                pageStore.socket.state === WebSocketState.CLOSING
            "
            :size="32"
            class="w-10 text-red-500"
        />

        <div
            class="flex flex-row justify-center items-center text-slate-800 gap-x-1"
        >
            <GaugeIcon :size="14"></GaugeIcon>
            <span class="text-xs" v-if="pageStore.isSocketConnected">{{
                pageStore.socket.receivedMessages
            }}</span>
            <span class="text-xs" v-else>-</span>
        </div>
    </div>
</template>
