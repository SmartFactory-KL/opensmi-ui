<script setup lang="ts">
import { computed } from "vue";
import { CircleAlert } from "@lucide/vue";

import type { SkillControlEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import type { SkillControlAction } from "@/types/UpdateTypes";
import { simplyPostToText } from "@/fetch/simplyFetch";
import Toaster from "@/toast/Toaster";
import {
    SkillControlControls,
    SkillControlStateStyles,
    SkillState,
    type StateConfig,
} from "./additionalData/SkillControl";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillControlEntityData);

const state = computed<StateConfig | undefined>(() => {
    const value = entity.value.currentState;

    if (typeof value === "number") {
        return SkillControlStateStyles[value];
    }

    const normalized = value.trim().toLowerCase();
    const numericValue = Number(normalized);

    if (normalized !== "" && Number.isInteger(numericValue)) {
        return SkillControlStateStyles[numericValue];
    }

    const labels: Record<string, number> = {
        halted: SkillState.HALTED,
        ready: SkillState.READY,
        running: SkillState.RUNNING,
        suspended: SkillState.SUSPENDED,
        completed: SkillState.COMPLETED,
        starting: SkillState.STARTING,
        halting: SkillState.HALTING,
        completing: SkillState.COMPLETING,
        resetting: SkillState.RESETTING,
        suspending: SkillState.SUSPENDING,
    };

    const code = labels[normalized];
    return code === undefined ? undefined : SkillControlStateStyles[code];
});

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
    <section
        class="w-full bg-white text-slate-900"
        :aria-label="`${entity.name} state`"
    >
        <div class="flex items-stretch h-8">
            <div
                class="w-1 shrink-0"
                :class="state?.barColor ?? 'bg-slate-400'"
            />

            <div class="flex min-w-0 flex-1 items-center gap-2.5 px-1 py-0.5">
                <!-- State icon -->
                <div
                    class="flex size-6 shrink-0 items-center justify-center rounded-full border"
                    :class="
                        state ? state.color : 'border-slate-200 bg-slate-50'
                    "
                >
                    <component
                        :is="state ? state.icon : CircleAlert"
                        class="size-4"
                        :class="
                            state
                                ? [
                                      state.iconColor,
                                      state.isBusy &&
                                          'animate-spin motion-reduce:animate-none',
                                  ]
                                : 'text-slate-500'
                        "
                        :aria-label="state?.label ?? 'Unknown state'"
                    />
                </div>

                <!-- Controls pill, upper right corner -->
                <div class="flex shrink-0 items-center gap-2 p-0.5">
                    <button
                        v-for="control in SkillControlControls"
                        :key="control.action"
                        type="button"
                        class="flex size-5 items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 cursor-pointer active:scale-95"
                        :class="control.classes"
                        :title="control.label"
                        :aria-label="control.label"
                        @click="requestAction(control.action)"
                    >
                        <component :is="control.icon" class="size-7" />
                    </button>
                </div>
            </div>
        </div>
    </section>
</template>
