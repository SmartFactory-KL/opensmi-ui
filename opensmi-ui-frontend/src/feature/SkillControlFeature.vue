<script setup lang="ts">
import { computed } from "vue";
import {
    ArrowDownLeftFromSquareIcon,
    CircleAlert,
    CircleCheck,
    CirclePause,
    CirclePlay,
    CircleStop,
    Clock,
    LoaderCircle,
    PauseCircleIcon,
    PlayCircleIcon,
    RotateCcw,
    ShieldAlert,
    StopCircleIcon,
    Timer,
    type LucideIcon,
} from "@lucide/vue";

import type { SkillControlEntityData } from "@/types/EntityTypes";
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import type { SkillControlAction } from "@/types/UpdateTypes";
import { simplyPostToText } from "@/fetch/simplyFetch";
import IconButton from "@/components/IconButton.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as SkillControlEntityData);

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
};

const states: Record<number, StateConfig> = {
    [SkillState.HALTED]: {
        label: "Halted",
        description: "Stopped · Reset required",
        icon: ShieldAlert,
        color: "bg-red-50 text-red-800 border-red-200",
        iconColor: "text-red-600",
        barColor: "bg-red-500",
    },
    [SkillState.READY]: {
        label: "Ready",
        description: "Ready to start",
        icon: CircleCheck,
        color: "bg-emerald-50 text-emerald-800 border-emerald-200",
        iconColor: "text-emerald-600",
        barColor: "bg-emerald-500",
    },
    [SkillState.RUNNING]: {
        label: "Running",
        description: "Execution in progress",
        icon: CirclePlay,
        color: "bg-blue-50 text-blue-800 border-blue-200",
        iconColor: "text-blue-600",
        barColor: "bg-blue-500",
    },
    [SkillState.SUSPENDED]: {
        label: "Suspended",
        description: "Execution paused",
        icon: CirclePause,
        color: "bg-amber-50 text-amber-800 border-amber-200",
        iconColor: "text-amber-600",
        barColor: "bg-amber-500",
    },
    [SkillState.COMPLETED]: {
        label: "Completed",
        description: "Execution completed",
        icon: CircleCheck,
        color: "bg-teal-50 text-teal-800 border-teal-200",
        iconColor: "text-teal-600",
        barColor: "bg-teal-500",
    },
    [SkillState.STARTING]: {
        label: "Starting",
        description: "Transitioning to running",
        icon: LoaderCircle,
        color: "bg-sky-50 text-sky-800 border-sky-200",
        iconColor: "text-sky-600",
        barColor: "bg-sky-500",
    },
    [SkillState.HALTING]: {
        label: "Halting",
        description: "Transitioning to halted",
        icon: CircleStop,
        color: "bg-orange-50 text-orange-800 border-orange-200",
        iconColor: "text-orange-600",
        barColor: "bg-orange-500",
    },
    [SkillState.COMPLETING]: {
        label: "Completing",
        description: "Finishing execution",
        icon: CircleCheck,
        color: "bg-teal-50 text-teal-800 border-teal-200",
        iconColor: "text-teal-600",
        barColor: "bg-teal-500",
    },
    [SkillState.RESETTING]: {
        label: "Resetting",
        description: "Returning to ready",
        icon: RotateCcw,
        color: "bg-violet-50 text-violet-800 border-violet-200",
        iconColor: "text-violet-600",
        barColor: "bg-violet-500",
    },
    [SkillState.SUSPENDING]: {
        label: "Suspending",
        description: "Transitioning to suspended",
        icon: Timer,
        color: "bg-amber-50 text-amber-800 border-amber-200",
        iconColor: "text-amber-600",
        barColor: "bg-amber-500",
    },
};

const state = computed<StateConfig | undefined>(() => {
    const value = entity.value.currentState;

    if (typeof value === "number") {
        return states[value];
    }

    const normalized = value.trim().toLowerCase();
    const numericValue = Number(normalized);

    if (normalized !== "" && Number.isInteger(numericValue)) {
        return states[numericValue];
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
    return code === undefined ? undefined : states[code];
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
    }
}
</script>

<template>
    <section
        class="w-full border border-slate-200 bg-white text-slate-900"
        :aria-label="`${entity.name} state`"
    >
        <header
            class="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3"
        >
            <div class="min-w-0">
                <p class="truncate text-sm font-semibold">
                    {{ entity.name }}
                </p>
                <p class="mt-0.5 text-xs text-slate-500">Skill state</p>
            </div>

            <IconButton @click="requestAction('Start')">
                <PlayCircleIcon></PlayCircleIcon> Start
            </IconButton>

            <IconButton @click="requestAction('Halt')">
                <StopCircleIcon></StopCircleIcon> Halt
            </IconButton>

            <IconButton @click="requestAction('Reset')">
                <ArrowDownLeftFromSquareIcon></ArrowDownLeftFromSquareIcon>
                Reset
            </IconButton>

            <IconButton @click="requestAction('Suspend')">
                <PauseCircleIcon></PauseCircleIcon> Suspend
            </IconButton>

            <Clock class="size-4 shrink-0 text-slate-400" />
        </header>

        <div class="flex items-stretch">
            <div
                class="w-1 shrink-0"
                :class="state?.barColor ?? 'bg-slate-400'"
            />

            <div class="min-w-0 flex-1 p-4">
                <template v-if="state">
                    <div class="flex items-center gap-3">
                        <div
                            class="flex size-11 shrink-0 items-center justify-center border"
                            :class="state.color"
                        >
                            <component
                                :is="state.icon"
                                class="size-6"
                                :class="state.iconColor"
                                :aria-label="state.label"
                            />
                        </div>

                        <div class="min-w-0 flex-1">
                            <div class="flex flex-wrap items-center gap-2">
                                <h3 class="text-lg font-semibold leading-tight">
                                    {{ state.label }}
                                </h3>

                                <span
                                    class="border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                                    :class="state.color"
                                >
                                    {{ entity.currentState }}
                                </span>
                            </div>

                            <p class="mt-1 text-sm text-slate-500">
                                {{ state.description }}
                            </p>
                        </div>
                    </div>
                </template>

                <div v-else class="flex items-center gap-3">
                    <div
                        class="flex size-11 shrink-0 items-center justify-center border border-slate-200 bg-slate-50"
                    >
                        <CircleAlert class="size-6 text-slate-500" />
                    </div>

                    <div class="min-w-0">
                        <h3 class="text-lg font-semibold">Unknown state</h3>
                        <p class="mt-1 break-all text-sm text-slate-500">
                            {{ entity.currentState }}
                        </p>
                    </div>
                </div>

                <div
                    class="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3 text-xs"
                >
                    <span class="text-slate-500">Last state change</span>
                    <time
                        class="font-medium text-slate-700"
                        :datetime="entity.currentStateLastChange || undefined"
                        :title="lastChangeTitle"
                    >
                        {{ lastChange }}
                    </time>
                </div>
            </div>
        </div>
    </section>
</template>
