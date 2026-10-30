<script setup lang="ts">
import type { SkillControlEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { computed } from "vue";
import { normalizeSkillState, type StateConfig } from "./SkillData";
import {
    CircleChevronLeftIcon,
    CircleIcon,
    PauseCircleIcon,
    PlayCircleIcon,
    StopCircleIcon,
    type LucideIcon,
} from "@lucide/vue";
import type { SkillControlAction } from "@/types/UpdateTypes";
import { simplyPostToText } from "@/fetch/simplyFetch";
import Toaster from "@/toast/Toaster";
import { useModelStore } from "@/stores/ModelStore";

const props = defineProps<{
    feature: FeatureNode;
    tiny?: boolean;
}>();

const entity = computed(() => {
    return props.feature.entity as SkillControlEntityData;
});

const state = computed<StateConfig | null>(() => {
    const value = entity.value.currentState;
    return normalizeSkillState(value);
});

const firstParentLock = computed(() => {
    if (!props.feature?.parentComponentNodeEntityId) {
        return null;
    }

    let curComponent = useModelStore().entityIdComponentNodeMap.get(
        props.feature.parentComponentNodeEntityId,
    );

    if (!curComponent) {
        return null;
    }

    let lock: FeatureNode | null = null;
    let count = 0;
    while (lock === null && count < 1000) {
        count++;

        for (const feature of curComponent.features) {
            if (feature.entityType == "Lock") {
                lock = feature;
                break;
            }
        }

        if (!curComponent.parentComponentNodeEntityId) {
            break;
        }

        curComponent = useModelStore().entityIdComponentNodeMap.get(
            curComponent.parentComponentNodeEntityId,
        );

        if (!curComponent) {
            break;
        }
    }

    if (count >= 1000) {
        console.warn("Count Overflow while looking for Lock");
        return null;
    }

    return lock;
});

type Action = SkillControlAction["requestedAction"];

const enabledButtons = computed<Record<Action, boolean>>(() => {
    const stateLabel = state.value?.label;

    const activeButtons = {
        Reset: false,
        Start: false,
        Suspend: false,
        Halt: false,
    };

    if (!stateLabel) {
        return activeButtons;
    }

    let isLocked = false;
    if (firstParentLock.value !== null) {
        isLocked = firstParentLock.value.entity.isLocked;
    }

    if (isLocked === false) {
        return activeButtons;
    }

    switch (stateLabel) {
        case "Halted":
            activeButtons.Reset = true;
            break;
        case "Ready":
            activeButtons.Start = true;
            activeButtons.Halt = true;
            break;
        case "Running":
            activeButtons.Halt = true;
            activeButtons.Suspend = entity.value.isSuspendable;
            break;
        case "Suspended":
            activeButtons.Reset = true;
            activeButtons.Halt = true;
            activeButtons.Start = true;
            break;
        case "Completed":
            activeButtons.Reset = true;
            activeButtons.Halt = true;
            break;
        case "Starting":
            activeButtons.Halt = true;
            break;
        case "Halting":
            activeButtons.Halt = true;
            break;
        case "Completing":
            activeButtons.Halt = true;
            break;
    }

    return activeButtons;
});

const SkillControlControls: {
    action: SkillControlAction["requestedAction"];
    label: string;
    icon: LucideIcon;
    classes: string;
}[] = [
    {
        action: "Reset",
        label: "Reset",
        icon: CircleChevronLeftIcon,
        classes:
            "text-violet-600 bg-violet-50 hover:text-violet-700 focus-visible:ring-violet-500",
    },
    {
        action: "Start",
        label: "Start",
        icon: PlayCircleIcon,
        classes:
            "text-emerald-600 bg-emerald-50 hover:text-emerald-700 focus-visible:ring-emerald-500",
    },
    {
        action: "Suspend",
        label: "Suspend",
        icon: PauseCircleIcon,
        classes:
            "text-amber-600 bg-amber-50 hover:text-amber-700 focus-visible:ring-amber-500",
    },
    {
        action: "Halt",
        label: "Halt",
        icon: StopCircleIcon,
        classes:
            "text-red-600 bg-red-50 hover:text-red-700 focus-visible:ring-red-500",
    },
];

async function requestAction(
    requestedAction: SkillControlAction["requestedAction"],
) {
    try {
        const action = {
            entityId: props.feature.entityId,
            actionType: "SkillControlAction",
            action: {
                requestedAction: requestedAction,
            } as SkillControlAction,
        };

        await simplyPostToText("/api/opc-model/action", action);
    } catch (e) {
        console.error(e);
        Toaster.error("Failed to call skill action: " + e);
    }
}
</script>

<template>
    <div
        class="flex items-center self-start"
        :class="[tiny ? 'gap-0 p-0' : 'gap-2 p-1']"
    >
        <button
            v-for="control in SkillControlControls"
            :key="control.action"
            type="button"
            class="flex items-center justify-center border duration-75 transition-colors cursor-pointer active:scale-95 disabled:cursor-not-allowed disabled:bg-stone-50 disabled:border-stone-100 disabled:text-stone-300"
            :class="[control.classes, tiny ? 'size-8' : 'size-10']"
            :title="control.label"
            :aria-label="control.label"
            :disabled="enabledButtons[control.action] != true"
            @click="requestAction(control.action)"
        >
            <component
                :is="control.icon"
                class="size-6"
                v-if="enabledButtons[control.action]"
            />
            <CircleIcon class="size-6" v-else />
        </button>
    </div>
</template>
