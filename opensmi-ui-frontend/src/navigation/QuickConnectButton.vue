<script setup lang="ts">
import IconButton from "@/components/IconButton.vue";
import { useServerStore } from "@/stores/ServerSessionStore";
import { LogInIcon, LogOutIcon, PlugZapIcon, UnplugIcon } from "@lucide/vue";
import { computed } from "vue";

defineProps<{
    tiny?: boolean;
}>();

const serverStore = useServerStore();

function requestConnect() {
    serverStore.requestConnect();
}

function requestDisconnect() {
    serverStore.requestDisconnect();
}

const isPending = computed(() => {
    return serverStore.requestData.isPending;
});
</script>

<template>
    <div>
        <!-- Connect -->
        <IconButton
            class="bg-slate-700 hover:bg-slate-800 text-white"
            @click="requestConnect"
            :disabled="isPending"
            v-show="serverStore.isDisconnected"
        >
            <PlugZapIcon :size="16" :class="{ 'animate-spin': isPending }" />
            <span v-if="!tiny">Connect</span>
        </IconButton>

        <!-- Disconnect -->
        <IconButton
            class="bg-slate-400 hover:bg-slate-800 text-white"
            @click="requestDisconnect"
            :disabled="isPending"
            v-show="serverStore.isConnected"
        >
            <UnplugIcon :size="16" :class="{ 'animate-spin': isPending }" />
            <span v-if="!tiny">Disconnect</span>
        </IconButton>
    </div>
</template>
