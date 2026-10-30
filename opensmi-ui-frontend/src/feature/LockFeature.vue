<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import type { LockEntityData } from "@/types/EntityTypes";
import { computed, ref } from "vue";
import {
    LockKeyholeIcon,
    LockKeyholeOpenIcon,
    UserIcon,
    LaptopIcon,
} from "@lucide/vue";
import type { LockAction } from "@/types/UpdateTypes";
import { simplyPostToText } from "@/fetch/simplyFetch";
import { useServerStore } from "@/stores/ServerSessionStore";
import Toaster from "@/toast/Toaster";

const props = withDefaults(
    defineProps<{
        feature: FeatureNode;
        dark?: boolean;
    }>(),
    {
        dark: false,
    },
);

const serverStore = useServerStore();

type LOCKING_STATE = "open" | "lockedByUs" | "lockedByOthers";

// Neutral container, independent of the locking state
const CONTAINER_CLASSES = {
    light: "bg-gray-50 border-gray-200 text-gray-700",
    dark: "bg-gray-900 border-gray-700 text-gray-200",
};

// Only the circle carries the state color
const BUTTON_CLASSES: Record<LOCKING_STATE, string> = {
    open: "bg-red-500 hover:bg-red-600 focus-visible:ring-red-300",
    lockedByOthers:
        "bg-amber-500 hover:bg-amber-600 focus-visible:ring-amber-300",
    lockedByUs: "bg-green-500 hover:bg-green-600 focus-visible:ring-green-300",
};

const ACTIONS: Record<
    LOCKING_STATE,
    { action: LockAction["requestedAction"]; label: string }
> = {
    open: { action: "InitLock", label: "Lock" },
    lockedByOthers: { action: "BreakLock", label: "Break lock" },
    lockedByUs: { action: "ExitLock", label: "Release lock" },
};

const entity = computed(() => props.feature.entity as LockEntityData);
const isWorking = ref(false);

const isLocked = computed(() => entity.value.isLocked);

const lockingUser = computed(() => entity.value.lockingUser?.trim() || null);
const lockingClient = computed(
    () => entity.value.lockingClient?.trim() || null,
);

const lockingState = computed<LOCKING_STATE>(() => {
    if (!isLocked.value) {
        return "open";
    } else {
        if (lockingUser.value === serverStore.currentUsername) {
            return "lockedByUs";
        } else {
            return "lockedByOthers";
        }
    }
});

const containerClasses = computed(
    () => CONTAINER_CLASSES[props.dark ? "dark" : "light"],
);
const buttonClasses = computed(() => BUTTON_CLASSES[lockingState.value]);
const currentAction = computed(() => ACTIONS[lockingState.value]);

function requestCurrentAction() {
    requestAction(currentAction.value.action);
}

async function requestAction(requestedAction: LockAction["requestedAction"]) {
    try {
        if (isWorking.value === true) {
            return;
        }
        isWorking.value = true;

        const action = {
            entityId: props.feature.entityId,
            actionType: "LockAction",
            action: {
                requestedAction: requestedAction,
            } as LockAction,
        };

        await simplyPostToText("/api/opc-model/action", action);
    } catch (e) {
        console.error(e);
        Toaster.error("Failed to request Lock Action: " + e);
    } finally {
        isWorking.value = false;
    }
}
</script>

<template>
    <article
        class="flex h-16 w-fit items-center gap-3 rounded-xl border p-1 pl-5 shadow-sm transition-colors duration-150"
        :class="containerClasses"
    >
        <!-- Lock Information -->
        <div class="flex min-w-32 flex-col items-start justify-center">
            <div class="flex flex-row items-center gap-x-2 text-xs leading-4">
                <LockKeyholeIcon
                    v-if="isLocked"
                    :size="14"
                    :stroke-width="1.6"
                />
                <LockKeyholeOpenIcon v-else :size="14" :stroke-width="1.6" />
                <span>{{ isLocked ? "Locked" : "Open" }}</span>
            </div>

            <div class="flex flex-row items-center gap-x-2 text-xs leading-4">
                <UserIcon :size="14" :stroke-width="1.6" />
                <span>{{ lockingUser?.length ? lockingUser : "-" }}</span>
            </div>

            <div class="flex flex-row items-center gap-x-2 text-xs leading-4">
                <LaptopIcon :size="14" :stroke-width="1.6" />
                <span>{{ lockingClient?.length ? lockingClient : "-" }}</span>
            </div>
        </div>

        <!-- Lock action: circle fits the pill's right end -->
        <button
            type="button"
            class="flex size-14 shrink-0 items-center justify-center rounded-xl text-white shadow-sm transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-70 cursor-pointer"
            :class="buttonClasses"
            :disabled="isWorking"
            :title="currentAction.label"
            :aria-label="currentAction.label"
            @click="requestCurrentAction"
        >
            <LockKeyholeOpenIcon
                v-if="lockingState === 'lockedByUs'"
                :size="22"
                :stroke-width="1.8"
                :class="{ 'animate-spin': isWorking }"
            />
            <LockKeyholeIcon
                v-else
                :size="22"
                :stroke-width="1.8"
                :class="{ 'animate-spin': isWorking }"
            />
        </button>
    </article>
</template>
