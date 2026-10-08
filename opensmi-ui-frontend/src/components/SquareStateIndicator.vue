<script lang="ts" setup>
import { computed, type Component } from "vue";
import { CircleCheck, CircleDot, Pause, Play, Power } from "@lucide/vue";

const props = defineProps<{
    state: string | number | null;
    squareOnly?: boolean;
}>();

const stateLabelMap = new Map<number, string>([
    [11, "Halted"],
    [12, "Ready"],
    [13, "Running"],
    [14, "Suspended"],
    [15, "Completed"],
    [16, "Starting"],
    [17, "Halting"],
]);

const stateLabel = computed(() => {
    if (Number.isInteger(props.state)) {
        return stateLabelMap.get(props.state as number) ?? "no state";
    }

    return props.state || "no state";
});

const stateColor = computed(() => {
    switch (props.state) {
        case "Halted":
        case 11:
            return "bg-blue-500 text-blue-200";

        case "Ready":
        case 12:
            return "bg-green-500 text-gray-700";

        case "Running":
        case 13:
            return "animate-pulse border-4 border-lime-600 bg-green-500 text-gray-700";

        case "Suspended":
        case 14:
            return "bg-pink-500 text-gray-700";

        case "Completed":
        case 15:
            return "bg-violet-500 text-violet-200";

        case "Starting":
        case 16:
            return "bg-yellow-500 text-yellow-200";

        case "Halting":
        case 17:
            return "bg-yellow-500 text-yellow-200";

        case "unknown":
            return "bg-pink-500 text-pink-200";

        default:
            return "bg-gray-300 text-gray-400";
    }
});

const stateSymbol = computed<Component>(() => {
    switch (stateLabel.value) {
        case "Halted":
            return Power;

        case "Ready":
            return Play;

        case "Running":
            return CircleDot;

        case "Suspended":
            return Pause;

        case "Completed":
            return CircleCheck;

        case "Starting":
            return Play;

        case "Halting":
            return Power;

        default:
            return CircleDot;
    }
});
</script>

<template>
    <div
        v-if="squareOnly"
        :title="stateLabel as string"
        :class="[stateColor, 'flex items-center justify-center']"
    >
        <component :is="stateSymbol" :size="32" :stroke-width="2" />
    </div>

    <div
        v-else
        :title="stateLabel as string"
        :class="[
            stateColor,
            'flex h-[1.6rem] w-28 items-center justify-center gap-1.5 rounded-2xl text-xs',
        ]"
    >
        <component :is="stateSymbol" :size="14" :stroke-width="2" />

        <span>
            {{ stateLabel }}
        </span>
    </div>
</template>
