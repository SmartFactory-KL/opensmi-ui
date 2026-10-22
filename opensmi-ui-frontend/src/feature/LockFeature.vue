```vue
<script setup lang="ts">
import type { FeatureNode } from "@/types/NodeFeatureTypes";
import type { LockEntityData } from "@/types/EntityTypes";
import { computed } from "vue";
import {
    LockKeyhole,
    LockKeyholeOpen,
    UserRound,
    Monitor,
    ShieldCheck,
} from "@lucide/vue";
import type { GenericAction, LockAction } from "@/types/UpdateTypes";
import { simplyPostToText } from "@/fetch/simplyFetch";
import IconButton from "@/components/IconButton.vue";

const props = defineProps<{
    feature: FeatureNode;
}>();

const entity = computed(() => props.feature.entity as LockEntityData);

const isLocked = computed(() => entity.value.isLocked);

const lockingUser = computed(() => entity.value.lockingUser?.trim() || null);

const lockingClient = computed(
    () => entity.value.lockingClient?.trim() || null,
);

function requestInitLock() {
    const action = {
        entityId: props.feature.entityId,
        actionType: "LockAction",
        action: {
            requestedAction: "InitLock",
        } as LockAction,
    };

    requestAction(action);
}

function requestBreakLock() {
    const action = {
        entityId: props.feature.entityId,
        actionType: "LockAction",
        action: {
            requestedAction: "BreakLock",
        } as LockAction,
    };

    requestAction(action);
}

function requestExitLock() {
    const action = {
        entityId: props.feature.entityId,
        actionType: "LockAction",
        action: {
            requestedAction: "ExitLock",
        } as LockAction,
    };

    requestAction(action);
}

async function requestAction(action: GenericAction) {
    try {
        await simplyPostToText("/api/opc-model/action", action);
    } catch (e) {
        console.error(e);
    }
}
</script>

<template>
    <article
        class="flex w-full flex-col gap-4 shadow-sm border bg-white p-4 text-gray-900 transition-colors"
        :class="
            isLocked
                ? 'border-amber-200 hover:border-amber-300'
                : 'border-gray-200 hover:border-gray-300'
        "
    >
        <!-- Header -->
        <div class="flex items-center gap-3">
            <div
                class="flex size-11 shrink-0 items-center justify-center rounded-lg"
                :class="
                    isLocked
                        ? 'bg-amber-50 text-amber-600'
                        : 'bg-gray-100 text-gray-500'
                "
            >
                <LockKeyhole v-if="isLocked" :size="22" :stroke-width="1.8" />
                <LockKeyholeOpen v-else :size="22" :stroke-width="1.8" />
            </div>

            <div class="min-w-0 flex-1">
                <h3 class="truncate text-sm font-semibold tracking-tight">
                    {{ feature.entityType }}
                </h3>
            </div>

            <div class="min-w-0 flex-1">
                <IconButton @click="requestInitLock">Init Lock</IconButton>
                <IconButton @click="requestBreakLock">Break Lock</IconButton>
                <IconButton @click="requestExitLock">Exit Lock</IconButton>
            </div>

            <span
                class="inline-flex shrink-0 items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium"
                :class="
                    isLocked
                        ? 'bg-amber-50 text-amber-700'
                        : 'bg-gray-100 text-gray-600'
                "
            >
                {{ isLocked ? "Locked" : "Unlocked" }}
            </span>
        </div>

        <div class="text-xs text-stone-400">
            since: {{ entity.isLockedLastChange }}
        </div>

        <!-- Lock details -->
        <div class="flex flex-col gap-3 border-t border-gray-100 pt-4">
            <div class="flex items-start gap-3">
                <div class="mt-0.5 text-gray-400">
                    <UserRound :size="16" />
                </div>

                <div class="min-w-0 flex-1">
                    <p class="text-xs font-medium text-gray-500">
                        Locking user
                    </p>

                    <p
                        class="mt-1 wrap-break-word text-sm font-medium text-gray-800"
                    >
                        {{ lockingUser || "-" }}
                    </p>
                    <span class="text-xs text-stone-500">
                        since {{ entity.lockingUserLastChange }}
                    </span>
                </div>
            </div>

            <div class="flex items-start gap-3">
                <div class="mt-0.5 text-gray-400">
                    <Monitor :size="16" />
                </div>

                <div class="min-w-0 flex-1">
                    <p class="text-xs font-medium text-gray-500">
                        Locking client
                    </p>

                    <p
                        class="mt-1 wrap-break-word text-sm font-medium text-gray-800"
                    >
                        {{ lockingClient || "-" }}
                    </p>
                    <span class="text-xs text-stone-500">
                        since {{ entity.lockingClientLastChange }}
                    </span>
                </div>
            </div>
        </div>
    </article>
</template>
```
