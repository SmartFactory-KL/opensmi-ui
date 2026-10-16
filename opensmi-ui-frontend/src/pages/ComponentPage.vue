<script setup lang="ts">
import GenericFeature from "@/feature/GenericFeature.vue";
import { useModelStore } from "@/stores/ModelStore";
import { computed } from "vue";
import { useRoute } from "vue-router";

const modelStore = useModelStore();

const route = useRoute();

const component = computed(() => {
    const entityId = route.params.entityId;

    if (!entityId || Array.isArray(entityId)) {
        console.log("invalid component entity id:", entityId);
        return null;
    }

    if (!modelStore.entityIdComponentNodeMap.has(entityId)) {
        return null;
    }

    return modelStore.entityIdComponentNodeMap.get(entityId) ?? null;
});
</script>

<template>
    <main>
        <section v-if="component === null">
            Invalid Component or Entity ID not found
        </section>
        <section
            v-else
            class="flex flex-row flex-wrap justify-start items-start p-4 gap-4"
        >
            <GenericFeature
                v-for="feature in component.features"
                :feature="feature"
                :key="feature.entityId"
            >
            </GenericFeature>
        </section>
    </main>
</template>
