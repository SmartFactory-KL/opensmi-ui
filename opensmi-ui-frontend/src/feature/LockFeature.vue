```vue
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
import IconButton from "@/components/IconButton.vue";
import { useServerStore } from "@/stores/ServerSessionStore";
import Toaster from "@/toast/Toaster";

const props = defineProps<{
    feature: FeatureNode;
}>();

const serverStore = useServerStore();

type LOCKING_STATE = "open" | "lockedByUs" | "lockedByOthers";

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

function requestInitLock() {
    requestAction("InitLock");
}

function requestBreakLock() {
    requestAction("BreakLock");
}

function requestExitLock() {
    requestAction("ExitLock");
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
      Toaster.error("Failed to request Lock Action: " + e)
    } finally {
        isWorking.value = false;
    }
}
</script>

<template>
    <article
        class="flex flex-col gap-4 shadow-sm border px-4 py-2 transition-colors duration-150"
        :class="{
            'bg-red-50 border-red-600 text-red-800': lockingState === 'open',
            'bg-amber-50 border-amber-600 text-amber-800':
                lockingState === 'lockedByOthers',
            'bg-green-50 border-green-600 text-green-800':
                lockingState === 'lockedByUs',
        }"
    >
        <!-- Header -->
        <div class="flex items-center gap-2">
            <div class="min-w-40 flex flex-col justify-between items-start">
                <div
                    class="flex flex-row justify-start items-center gap-x-2 text-sm"
                >
                    <div>
                        <LockKeyholeIcon
                            v-if="isLocked"
                            :size="16"
                            :stroke-width="1.6"
                        />
                        <LockKeyholeOpenIcon
                            v-else
                            :size="16"
                            :stroke-width="1.6"
                        />
                    </div>

                    <div>
                        {{ isLocked ? "Locked" : "Open" }}
                    </div>
                </div>

                <div
                    class="flex flex-row justify-start items-center gap-x-2 text-sm"
                >
                    <div>
                        <UserIcon :size="16" :stroke-width="1.6" />
                    </div>

                    <div>
                        {{ lockingUser?.length ? lockingUser : "-" }}
                    </div>
                </div>

                <div
                    class="flex flex-row justify-start items-center gap-x-2 text-sm"
                >
                    <div>
                        <LaptopIcon :size="16" :stroke-width="1.6" />
                    </div>

                    <div>
                        {{ lockingClient?.length ? lockingClient : "-" }}
                    </div>
                </div>
            </div>

            <div class="">
                <IconButton
                    @click="requestInitLock"
                    :disabled="isWorking"
                    :class="[isWorking ? 'animate-spin' : '']"
                    v-show="lockingState === 'open'"
                >
                    <LockKeyholeIcon></LockKeyholeIcon>
                </IconButton>
                <IconButton
                    @click="requestBreakLock"
                    :disabled="isWorking"
                    :class="[isWorking ? 'animate-spin' : '']"
                    v-show="lockingState === 'lockedByOthers'"
                >
                    <LockKeyholeIcon></LockKeyholeIcon>
                </IconButton>
                <IconButton
                    @click="requestExitLock"
                    :disabled="isWorking"
                    :class="[isWorking ? 'animate-spin' : '']"
                    v-show="lockingState === 'lockedByUs'"
                >
                    <LockKeyholeOpenIcon></LockKeyholeOpenIcon>
                </IconButton>
            </div>
        </div>
    </article>
</template>
```
