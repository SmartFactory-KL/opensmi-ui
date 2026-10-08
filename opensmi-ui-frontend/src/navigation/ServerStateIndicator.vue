<script setup lang="ts">
import { computed } from "vue";
import { useServerStore } from "@/stores/ServerStore";
import {
    CheckCircle2Icon,
    ServerIcon,
    LinkIcon,
    RotateCcwIcon,
    LogOutIcon,
    CircleOffIcon,
    CircleAlertIcon,
} from "@lucide/vue";

const props = withDefaults(
    defineProps<{
        tiny?: boolean;
    }>(),
    {
        tiny: false,
    },
);

const serverStore = useServerStore();

const stateConfig = computed(() => {
    switch (serverStore.sessionData.state) {
        case "CONNECTED":
            return {
                label: "Connected",
                description: "Connected to the OPC UA server.",
                icon: CheckCircle2Icon,
                classes: "bg-teal-200 border-teal-200 text-teal-700",
                iconClasses: "text-teal-600",
                animate: false,
            };

        case "BROWSING":
            return {
                label: "Browsing",
                description: "Connected and browsing the server.",
                icon: ServerIcon,
                classes: "bg-indigo-200 border-indigo-200 text-indigo-700",
                iconClasses: "text-indigo-500",
                animate: true,
            };

        case "CONNECTING":
            return {
                label: "Connecting",
                description: "Establishing a connection to the OPC UA server.",
                icon: LinkIcon,
                classes: "bg-violet-200 border-violet-200 text-violet-700",
                iconClasses: "text-violet-500",
                animate: true,
            };

        case "RECONNECTING":
            return {
                label: "Reconnecting",
                description: "Attempting to restore the server connection.",
                icon: RotateCcwIcon,
                classes: "bg-violet-200 border-violet-200 text-violet-700",
                iconClasses: "text-violet-500",
                animate: true,
            };

        case "DISCONNECTING":
            return {
                label: "Disconnecting",
                description: "Closing the connection to the OPC UA server.",
                icon: LogOutIcon,
                classes: "bg-stone-200 border-stone-200 text-stone-600",
                iconClasses: "text-stone-400",
                animate: true,
            };

        case "DISCONNECTED":
            return {
                label: "Disconnected",
                description: "No OPC UA server connection is active.",
                icon: CircleOffIcon,
                classes: "bg-stone-200 border-stone-200 text-stone-600",
                iconClasses: "text-stone-400",
                animate: false,
            };

        default:
            return {
                label: "Unknown",
                description: "The server connection state is unknown.",
                icon: CircleAlertIcon,
                classes: "bg-rose-200 border-rose-200 text-rose-700",
                iconClasses: "text-rose-500",
                animate: false,
            };
    }
});
</script>

<template>
    <!-- Tiny mode -->
    <div
        v-if="tiny"
        :class="[
            'flex size-9 items-center justify-center border shadow-sm rounded-full cursor-pointer active:scale-95',
            'transition-colors duration-100',
            stateConfig.classes,
            { 'animate-spin': stateConfig.animate },
        ]"
        :title="`${stateConfig.label}: ${stateConfig.description}`"
        :aria-label="stateConfig.label"

        @click="$router.push('/connect')"
    >
        <component
            :is="stateConfig.icon"
            :class="['size-6', stateConfig.iconClasses]"
            :stroke-width="2"
        />
    </div>

    <!-- Full mode -->
    <section
        v-else
        :class="[
            'flex items-center gap-3 border px-3 py-2.5 shadow-sm cursor-pointer active:scale-95',
            'transition-colors duration-100',
            stateConfig.classes,
        ]"

        @click="$router.push('/connect')"
    >
        <div class="flex size-9 shrink-0 items-center justify-center">
            <component
                :is="stateConfig.icon"
                :class="[
                    'size-6',
                    stateConfig.iconClasses,
                    { 'animate-spin': stateConfig.animate },
                ]"
                :stroke-width="2"
            />
        </div>

        <div class="min-w-0">
            <p class="text-sm font-semibold leading-tight">
                {{ stateConfig.label }}
            </p>

            <p class="mt-0.5 text-xs opacity-75">
                {{ stateConfig.description }}
            </p>
        </div>
    </section>
</template>
