<script setup lang="ts">
import type { MachineryItemStateEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import {
    CircleHelpIcon,
    CirclePauseIcon,
    CirclePlayIcon,
    PowerOffIcon,
    WrenchIcon,
} from "@lucide/vue";
import { computed, type Component } from "vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => {
    return props.feature.entity as MachineryItemStateEntityData;
});

type StateKey =
    "executing" | "notexecuting" | "outofservice" | "notavailable" | "unknown";

interface StateStyle {
    label: string;
    icon: Component;
    description: string;
    // Full class strings so Tailwind can detect them
    pill: string;
    iconClass: string;
}

const STATES: Record<StateKey, StateStyle> = {
    executing: {
        label: "Executing",
        icon: CirclePlayIcon,
        description: "The machine is actively working",
        pill: "bg-emerald-100 text-emerald-900 border-emerald-400",
        iconClass: "text-emerald-600",
    },
    notexecuting: {
        label: "Not executing",
        icon: CirclePauseIcon,
        description: "Ready, but currently not working",
        pill: "bg-amber-100 text-amber-900 border-amber-400",
        iconClass: "text-amber-600",
    },
    outofservice: {
        label: "Out of service",
        icon: WrenchIcon,
        description: "Taken out of service, e.g. for maintenance or a fault",
        pill: "bg-red-100 text-red-900 border-red-400",
        iconClass: "text-red-600",
    },
    notavailable: {
        label: "Not available",
        icon: PowerOffIcon,
        description: "The machine is not available",
        pill: "bg-slate-200 text-slate-800 border-slate-400",
        iconClass: "text-slate-500",
    },
    unknown: {
        label: "Unknown",
        icon: CircleHelpIcon,
        description: "The state could not be determined",
        pill: "bg-stone-100 text-stone-700 border-stone-400 border-dashed",
        iconClass: "text-stone-500",
    },
};

// "Not Executing", "NotExecuting", "not_executing" all map to "notexecuting"
function normalize(text: string | null | undefined): string {
    return (text ?? "").replace(/[\s_-]/g, "").toLowerCase();
}

const stateKey = computed<StateKey>(() => {
    const key = normalize(entity.value.currentState?.text);
    return key in STATES ? (key as StateKey) : "unknown";
});

const style = computed(() => STATES[stateKey.value]);

// For states we don't recognise, still show the raw text if the server sent one
const label = computed(() => {
    if (stateKey.value === "unknown") {
        return entity.value.currentState?.text || style.value.label;
    }
    return style.value.label;
});
</script>

<template>
    <span
        class="inline-flex items-center gap-2 rounded-lg border px-3 py-1 text-sm font-semibold shadow-sm"
        :class="style.pill"
        :title="style.description"
    >
        <span class="relative flex size-5 items-center justify-center">
            <!-- soft ping behind the icon while executing -->
            <span
                v-if="stateKey === 'executing'"
                class="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-50"
            ></span>
            <component
                :is="style.icon"
                class="relative size-5"
                :class="style.iconClass"
            />
        </span>
        <span>{{ label }}</span>
    </span>
</template>
