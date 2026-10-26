<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import NullablePage from "@/components/NullablePage.vue";
import OPCNodeInfo from "@/components/OPCNodeInfo.vue";
import SectionBar from "@/components/SectionBar.vue";
import GenericFeature from "@/feature/GenericFeature.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import {
    CheckIcon,
    ChevronDownIcon,
    CopyIcon,
    RefreshCwIcon,
} from "@lucide/vue";
import { computed, ref, toRaw, watch } from "vue";
import { useRoute } from "vue-router";

const modelStore = useModelStore();

const route = useRoute();
const routeEntityId = computed(() => {
    return route.params.entityId;
});

const entity = computed<FeatureNode | ComponentNode | null>(() => {
    const entityId = routeEntityId.value;

    if (!entityId || Array.isArray(entityId)) {
        console.log("invalid component entity id:", entityId);
        return null;
    }

    let result = null;

    if (modelStore.entityIdComponentNodeMap.has(entityId)) {
        result = modelStore.entityIdComponentNodeMap.get(entityId);
    }

    if (result == null && modelStore.entityIdFeatureNodeMap.has(entityId)) {
        result = modelStore.entityIdFeatureNodeMap.get(entityId);
    }

    return result ?? null;
});

const showJSON = ref(false);
const copied = ref(false);

const snapshot = ref<string | null>(null);
const snapshotTime = ref<Date | null>(null);

watch(routeEntityId, () => {
    snapshot.value = null;
    snapshotTime.value = null;
});

function serialize(value: unknown): string {
    try {
        // toRaw avoids walking Vue's reactive proxies; JSON.stringify
        // reads the data once and doesn't create subscriptions in an event handler
        return JSON.stringify(toRaw(value), null, 2);
    } catch (e) {
        // e.g. circular references
        return `Could not serialize item: ${String(e)}`;
    }
}

function takeSnapshot() {
    if (!entity.value) return;
    snapshot.value = serialize(entity.value);
    snapshotTime.value = new Date();
}

function toggleJson() {
    showJSON.value = !showJSON.value;

    // Take the first snapshot when the block is opened
    if (showJSON.value && snapshot.value === null) {
        takeSnapshot();
    }
}

async function copyJson() {
    // Copy what is shown; if nothing was taken yet, take a fresh one
    if (snapshot.value === null) takeSnapshot();

    try {
        await navigator.clipboard.writeText(snapshot.value ?? "");
        copied.value = true;
        setTimeout(() => (copied.value = false), 1500);
    } catch (e) {
        console.error(e);
    }
}
</script>

<template>
    <NullablePage
        :item="entity"
        :entityId="routeEntityId"
        entity-type="Entity"
        v-slot="{ item }"
    >
        <div class="flex flex-col justify-start items-start">
            <EntityBreadcrumbs
                :node="item"
                class="sticky top-0 bg-slate-200 h-10 w-full pl-2"
            ></EntityBreadcrumbs>

            <section class="flex flex-col p-4 justify-start items-start w-full gap-4">
                <SectionBar
                    >Rendered Feature
                    <span class="text-stone-400"
                        >(might not work)</span
                    ></SectionBar
                >
                <GenericFeature :feature="item" flat></GenericFeature>

                <SectionBar>Raw JSON Content</SectionBar>

                <div class="w-full">
                    <div class="flex items-center justify-center gap-2">
                        <button
                            type="button"
                            class="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-indigo-500"
                            :aria-expanded="showJSON"
                            @click="toggleJson"
                        >
                            <ChevronDownIcon
                                class="size-4 transition-transform duration-200"
                                :class="showJSON && 'rotate-180'"
                                aria-hidden="true"
                            />
                            {{ showJSON ? "Hide JSON" : "Show JSON" }}
                        </button>

                        <button
                            v-if="showJSON"
                            type="button"
                            class="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-indigo-500"
                            @click="takeSnapshot"
                        >
                            <RefreshCwIcon class="size-4" aria-hidden="true" />
                            Refresh
                        </button>

                        <button
                            type="button"
                            class="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-indigo-500"
                            @click="copyJson"
                        >
                            <CheckIcon
                                v-if="copied"
                                class="size-4 text-emerald-600"
                                aria-hidden="true"
                            />
                            <CopyIcon
                                v-else
                                class="size-4"
                                aria-hidden="true"
                            />
                            {{ copied ? "Copied" : "Copy JSON" }}
                        </button>
                    </div>

                    <p
                        v-if="showJSON && snapshotTime"
                        class="mt-2 text-center text-xs text-slate-400"
                    >
                        Snapshot taken {{ snapshotTime.toLocaleTimeString() }}
                    </p>

                    <pre
                        v-if="showJSON && snapshot !== null"
                        class="mt-2 max-h-96 overflow-auto rounded-md bg-slate-200 p-4 text-xs leading-relaxed text-slate-800 shadow-inner"
                        >{{ snapshot }}</pre
                    >
                </div>

                <SectionBar>OPC Node Data</SectionBar>

                <OPCNodeInfo :node="item.opcNode"></OPCNodeInfo>

                <template v-if="'children' in item">
                    <SectionBar>Contained Components</SectionBar>

                    <span v-show="!item.children?.length" class="text-stone-500"
                        >No Components</span
                    >

                    <div
                        v-for="component in item.children ?? []"
                        class="flex flex-row justify-start items-center gap-x-2"
                    >
                        {{ component.entity.name }}

                        <GenericEntityPageLink
                            :entityId="component.entityId"
                            :entityType="component.entityType"
                        ></GenericEntityPageLink>
                    </div>
                </template>

                <SectionBar>Contained Features</SectionBar>

                <span v-show="!item.features?.length" class="text-stone-500"
                    >No Features</span
                >

                <div
                    class="flex flex-col flex-wrap gap-2 justify-start items-start"
                >
                    <GenericFeature
                        v-for="feature in item.features"
                        :feature="feature"
                        :key="feature.entityId"
                    >
                    </GenericFeature>
                </div>

                <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                <div class="on-screen-placeholder" style="height: 25vh"></div>
            </section>
        </div>
    </NullablePage>
</template>
