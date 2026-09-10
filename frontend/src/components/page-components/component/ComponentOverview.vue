<script setup lang="ts">
import { useRoute } from "vue-router";
import { useMachineStore } from "../../../stores/MachineStore";
import { usePageStore } from "../../../stores/PageStore";
import { computed } from "vue";

import NotFoundNotice from "../../NotFoundNotice.vue";
import GenericComponentOverview from "./GenericComponentOverview.vue";

import StorageComponentOverview from "./special/StorageComponentOverview.vue";
// import PortComponentOverview from "./special/PortComponentOverview.vue";

const route = useRoute();

const machineStore = useMachineStore();
const pageStore = usePageStore();

const component = machineStore.componentEntityMap.get(
  route.params.componentEntityId as string
);

const componentViewType = computed(() => {
  if (!component) {
    return NotFoundNotice;
  }

  if (!pageStore.showFlags.specializedPages) {
    return GenericComponentOverview;
  }

  switch (component.type) {
    // case "Port":
    //   return PortComponentOverview;
    case "Storage":
      return StorageComponentOverview;
    default:
      return GenericComponentOverview;
  }
});
</script>

<template>
  <div v-if="!component"><NotFoundNotice></NotFoundNotice></div>
  <component v-else :is="componentViewType" :component="component"></component>
</template>
