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
    | "executing"
    | "notexecuting"
    | "outofservice"
    | "notavailable"
    | "unknown";

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
        pill: "bg-transparent",
        iconClass: "text-emerald-600",
    },
    notexecuting: {
        label: "Not executing",
        icon: CirclePauseIcon,
        description: "Ready, but currently not working",
        pill: "bg-transparent",
        iconClass: "text-amber-600",
    },
    outofservice: {
        label: "Out of service",
        icon: WrenchIcon,
        description: "Taken out of service, e.g. for maintenance or a fault",
        pill: "bg-transparent",
        iconClass: "text-red-600",
    },
    notavailable: {
        label: "Not available",
        icon: PowerOffIcon,
        description: "The machine is not available",
        pill: "bg-transparent",
        iconClass: "text-slate-500",
    },
    unknown: {
        label: "Unknown",
        icon: CircleHelpIcon,
        description: "The state could not be determined",
        pill: "bg-transparent",
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
        class="inline-flex items-center gap-2 rounded-lg py-1 text-sm"
        :class="style.pill"
        :title="style.description"
    >
        <span class="relative flex size-5 items-center justify-center">
            <component
                :is="style.icon"
                class="relative size-5"
                :class="style.iconClass"
            />
        </span>
        <span>{{ label }}</span>
    </span>
</template>
