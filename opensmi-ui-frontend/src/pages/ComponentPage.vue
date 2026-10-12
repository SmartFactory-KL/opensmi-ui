<script setup lang="ts">
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

    if (!modelStore.entityIdComponentMap.has(entityId)) {
        return null;
    }

    return modelStore.entityIdComponentMap.get(entityId) ?? null;
});
</script>

<template>
    <main>
        <section v-if="component === null">
            Invalid Component or Entity ID not found
        </section>
        <section v-else>
            {{ component.entityId }}
            {{ component.entityType }}

            <div v-for="feature in component.features">
                {{ feature }}
            </div>
        </section>
    </main>
</template>
