<script setup lang="ts">
import IconButton from "@/components/IconButton.vue";
import { useServerStore } from "@/stores/ServerSessionStore";
import { LogInIcon, LogOutIcon } from "@lucide/vue";

const serverStore = useServerStore();

function requestConnect() {
    serverStore.requestConnect();
}

function requestDisconnect() {
    serverStore.requestDisconnect();
}
</script>

<template>
    <div>
        <!-- Connect -->
        <IconButton
            class="bg-slate-700 hover:bg-slate-800 text-white"
            @click="requestConnect"
            v-show="serverStore.isDisconnected"
        >
            <LogInIcon :size="16" />
        </IconButton>

        <!-- Disconnect -->
        <IconButton
            class="bg-slate-400 hover:bg-slate-800 text-white"
            @click="requestDisconnect"
            v-show="serverStore.isConnected"
        >
            <LogOutIcon :size="16" />
        </IconButton>
    </div>
</template>
