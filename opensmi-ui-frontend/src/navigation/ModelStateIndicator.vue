<script setup lang="ts">
import { computed, type Component } from "vue";
import {
    BellRingIcon,
    CheckIcon,
    CircleDotIcon,
    EraserIcon,
    EyeIcon,
    FolderOpenIcon,
    NetworkIcon,
    XIcon,
} from "@lucide/vue";
import type { OPCModelState } from "@/stores/ModelStore";

interface StateConfig {
    label: string;
    description: string;
    badgeIcon: Component;
    classes: string;
    iconClasses: string;
    badgeClasses: string;
    animate: boolean;
}

const props = defineProps<{
    state: OPCModelState;
}>();

const idleConfig = {
    classes: "bg-stone-200 border-stone-200 text-stone-600",
    iconClasses: "text-stone-500",
    badgeClasses: "bg-stone-500 text-white",
};

const workingConfig = {
    classes: "bg-violet-200 border-violet-200 text-violet-700",
    iconClasses: "text-violet-600",
    badgeClasses: "bg-violet-600 text-white",
    animate: true,
};

const STATE_CONFIG: Record<OPCModelState, StateConfig> = {
    open: {
        label: "Open",
        description: "The model is open.",
        badgeIcon: CircleDotIcon,
        ...idleConfig,
        animate: false,
    },
    browsing_cleanup: {
        label: "Cleaning up",
        description: "Cleaning up before browsing the model.",
        badgeIcon: EraserIcon,
        ...workingConfig,
    },
    browsing_model: {
        label: "Browsing model",
        description: "Browsing the model structure.",
        badgeIcon: NetworkIcon,
        ...workingConfig,
    },
    browsing_subscriptions: {
        label: "Browsing subscriptions",
        description: "Browsing the model subscriptions.",
        badgeIcon: BellRingIcon,
        ...workingConfig,
    },
    browsing_value_read: {
        label: "Reading values",
        description: "Reading the model values.",
        badgeIcon: EyeIcon,
        ...workingConfig,
    },
    ready: {
        label: "Ready",
        description: "The model is ready.",
        badgeIcon: CheckIcon,
        classes: "bg-teal-200 border-teal-200 text-teal-700",
        iconClasses: "text-teal-600",
        badgeClasses: "bg-teal-600 text-white",
        animate: false,
    },
    error: {
        label: "Error",
        description: "An error occurred while processing the model.",
        badgeIcon: XIcon,
        classes: "bg-rose-200 border-rose-200 text-rose-700",
        iconClasses: "text-rose-500",
        badgeClasses: "bg-rose-600 text-white",
        animate: false,
    },
};

const stateConfig = computed(() => STATE_CONFIG[props.state]);
</script>

<template>
    <div
        :class="[
            'flex size-11 items-center justify-center rounded-md border shadow-sm',
            'transition-colors duration-100',
            stateConfig.classes,
        ]"
        :title="`${stateConfig.label}: ${stateConfig.description}`"
        :aria-label="stateConfig.label"
    >
        <div class="relative size-6">
            <FolderOpenIcon
                :class="['size-6', stateConfig.iconClasses]"
                :stroke-width="2"
            />

            <!-- Only the badge spins; it rotates around its own center -->
            <span
                :class="[
                    'absolute -bottom-1 -right-1 flex size-3.5 items-center justify-center rounded-full',
                    'transition-colors duration-100',
                    stateConfig.badgeClasses,
                    { 'animate-spin': stateConfig.animate },
                ]"
            >
                <component
                    :is="stateConfig.badgeIcon"
                    class="size-2.5"
                    :stroke-width="3"
                />
            </span>
        </div>
    </div>
</template>
