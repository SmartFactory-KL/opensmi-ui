<script setup lang="ts">
import EntityBreadcrumbs from "@/components/EntityBreadcrumbs.vue";
import NullablePage from "@/components/NullablePage.vue";
import GenericEntityPageLink from "@/link/GenericEntityPageLink.vue";
import { useModelStore } from "@/stores/ModelStore";
import { computed } from "vue";
import { useRoute } from "vue-router";

const modelStore = useModelStore();

const route = useRoute();

const entityId = computed(() => {
    return route.params.entityId;
});

const component = computed(() => {
    const _entityId = entityId.value;

    if (!_entityId || Array.isArray(_entityId)) {
        console.log("invalid component entity id:", _entityId);
        return null;
    }

    if (!modelStore.entityIdComponentNodeMap.has(_entityId)) {
        return null;
    }

    return modelStore.entityIdComponentNodeMap.get(_entityId) ?? null;
});
</script>

<template>
    <NullablePage
        :item="component"
        :entityId="entityId"
        entity-type="Component"
        v-slot="{ item }"
    >
        <div class="flex flex-col justify-start items-start">
            <div
                class="sticky top-0 flex flex-row justify-between items-center w-full h-10 bg-slate-200 pr-4 pl-2"
            >
                <EntityBreadcrumbs
                    :node="item"
                    class="grow"
                ></EntityBreadcrumbs>

                <GenericEntityPageLink
                    tiny
                    :entityId="entityId"
                ></GenericEntityPageLink>
            </div>

            <section>
                {{ item.entityId }}

                <!-- Always add some spacing for that funky on-screen-display on the touchscreens -->
                <div class="on-screen-placeholder" style="height: 25vh"></div>
            </section>
        </div>
    </NullablePage>
</template>
