<script setup lang="ts">
import { computed } from "vue";
import { CircleAlert } from "@lucide/vue";

import type { SkillControlEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import { simplyPostToText } from "@/fetch/simplyFetch";
import Toaster from "@/toast/Toaster";

import type { SkillControlAction } from "@/types/UpdateTypes";

import {
    ArrowDownLeftFromSquareIcon,
    CircleCheck,
    CirclePause,
    CirclePlay,
    CircleStop,
    LoaderCircle,
    PauseCircleIcon,
    PlayCircleIcon,
    RotateCcw,
    StopCircleIcon,
    Timer,
    type LucideIcon,
} from "@lucide/vue";

const SkillState = {
    HALTED: 11,
    READY: 12,
    RUNNING: 13,
    SUSPENDED: 14,
    COMPLETED: 15,
    STARTING: 16,
    HALTING: 17,
    COMPLETING: 18,
    RESETTING: 19,
    SUSPENDING: 20,
} as const;

type StateConfig = {
    label: string;
    description: string;
    icon: LucideIcon;
    color: string;
    iconColor: string;
    barColor: string;
    isBusy: boolean;
};

const SkillControlControls: {
    action: SkillControlAction["requestedAction"];
    label: string;
    icon: LucideIcon;
    classes: string;
}[] = [
    {
        action: "Reset",
        label: "Reset",
        icon: ArrowDownLeftFromSquareIcon,
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

const SkillControlStateStyles: Record<number, StateConfig> = {
    [SkillState.HALTED]: {
        label: "Halted",
        description: "Stopped · Reset required",
        icon: StopCircleIcon,
        color: "bg-red-50 text-red-800 border-red-200",
        iconColor: "text-red-600",
        barColor: "bg-red-500",
        isBusy: false,
    },
    [SkillState.READY]: {
        label: "Ready",
        description: "Ready to start",
        icon: CircleCheck,
        color: "bg-violet-50 text-violet-800 border-violet-200",
        iconColor: "text-violet-600",
        barColor: "bg-violet-500",
        isBusy: false,
    },
    [SkillState.RUNNING]: {
        label: "Running",
        description: "Execution in progress",
        icon: CirclePlay,
        color: "bg-blue-50 text-blue-800 border-blue-200",
        iconColor: "text-blue-600",
        barColor: "bg-blue-500",
        isBusy: true,
    },
    [SkillState.SUSPENDED]: {
        label: "Suspended",
        description: "Execution paused",
        icon: CirclePause,
        color: "bg-amber-50 text-amber-800 border-amber-200",
        iconColor: "text-amber-600",
        barColor: "bg-amber-500",
        isBusy: false,
    },
    [SkillState.COMPLETED]: {
        label: "Completed",
        description: "Execution completed",
        icon: CircleCheck,
        color: "bg-teal-50 text-teal-800 border-teal-200",
        iconColor: "text-teal-600",
        barColor: "bg-teal-500",
        isBusy: false,
    },
    [SkillState.STARTING]: {
        label: "Starting",
        description: "Transitioning to running",
        icon: LoaderCircle,
        color: "bg-sky-50 text-sky-800 border-sky-200",
        iconColor: "text-sky-600",
        barColor: "bg-sky-500",
        isBusy: true,
    },
    [SkillState.HALTING]: {
        label: "Halting",
        description: "Transitioning to halted",
        icon: CircleStop,
        color: "bg-orange-50 text-orange-800 border-orange-200",
        iconColor: "text-orange-600",
        barColor: "bg-orange-500",
        isBusy: true,
    },
    [SkillState.COMPLETING]: {
        label: "Completing",
        description: "Finishing execution",
        icon: CircleCheck,
        color: "bg-teal-50 text-teal-800 border-teal-200",
        iconColor: "text-teal-600",
        barColor: "bg-teal-500",
        isBusy: true,
    },
    [SkillState.RESETTING]: {
        label: "Resetting",
        description: "Returning to ready",
        icon: RotateCcw,
        color: "bg-violet-50 text-violet-800 border-violet-200",
        iconColor: "text-violet-600",
        barColor: "bg-violet-500",
        isBusy: true,
    },
    [SkillState.SUSPENDING]: {
        label: "Suspending",
        description: "Transitioning to suspended",
        icon: Timer,
        color: "bg-amber-50 text-amber-800 border-amber-200",
        iconColor: "text-amber-600",
        barColor: "bg-amber-500",
        isBusy: true,
    },
};

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

const lastChange = computed(() => {
    const value = entity.value.currentStateLastChange;

    if (!value) return "Unknown";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return value;

    return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
});

const lastChangeTitle = computed(() => {
    const value = entity.value.currentStateLastChange;
    if (!value) return undefined;

    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
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
        <div class="flex items-stretch">
            <div
                class="w-1 shrink-0"
                :class="state?.barColor ?? 'bg-slate-400'"
            />

            <div class="flex min-w-0 flex-1 items-center gap-2.5 px-3 py-2">
                <!-- State icon -->
                <div
                    class="flex size-9 shrink-0 items-center justify-center rounded-full border"
                    :class="
                        state ? state.color : 'border-slate-200 bg-slate-50'
                    "
                >
                    <component
                        :is="state ? state.icon : CircleAlert"
                        class="size-5"
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

                <!-- Name, state, last change -->
                <div class="min-w-20 flex-1">
                    <p
                        v-if="state"
                        class="text-sm font-medium leading-snug"
                        :class="state.iconColor"
                    >
                        {{ state.label }}
                    </p>
                    <p
                        v-else
                        class="break-all text-sm leading-snug text-slate-500"
                    >
                        Unknown state: {{ entity.currentState }}
                    </p>


                </div>

                <!-- Controls pill, upper right corner -->
                <div class="flex shrink-0 items-center gap-2 self-start p-0.5">
                    <button
                        v-for="control in SkillControlControls"
                        :key="control.action"
                        type="button"
                        class="flex size-10 items-center justify-center border-2 rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 cursor-pointer active:scale-95"
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
