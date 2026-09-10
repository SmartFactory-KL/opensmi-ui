<script lang="ts" setup>
import { computed, ref } from "vue";
import { useMachineStore } from "../../../stores/MachineStore";
import { usePageStore } from "../../../stores/PageStore";

import SkillLink from "./SkillLink.vue";

const pageStore = usePageStore();
const machineStore = useMachineStore();

const showOthers = ref(false);

const props = defineProps<{
  skillIdList: string[];
}>();

const firstFive = computed(() => {
  return props.skillIdList.slice(0, 5);
});

const allOthers = computed(() => {
  return props.skillIdList.slice(5, props.skillIdList.length);
});
</script>

<template>
  <div class="flex flex-col justify-start items-start">
    <span v-show="!skillIdList.length" class="text-gray-400"> no items </span>
    <div v-for="skillNodeId of firstFive">
      <div v-show="pageStore.showFlags.nodeIds" class="text-xs text-gray-400">
        {{ skillNodeId }}
      </div>
      <SkillLink
        :skill="machineStore.nodeIdSkillMap.get(skillNodeId)"
        :node-id="skillNodeId"
      ></SkillLink>
    </div>
    <div v-for="skillNodeId of allOthers" v-show="showOthers">
      <div v-show="pageStore.showFlags.nodeIds" class="text-xs text-gray-400">
        {{ skillNodeId }}
      </div>
      <SkillLink
        :skill="machineStore.nodeIdSkillMap.get(skillNodeId)"
        :node-id="skillNodeId"
      ></SkillLink>
    </div>
    <div class="flex flex-row justify-start items-center">
      <span
        class="action-button"
        v-show="allOthers.length > 0 && showOthers == false"
        @click="showOthers = true"
      >
        Show more <i class="fa-solid fa-caret-down"></i>
      </span>
      <span
        class="action-button"
        v-show="allOthers.length > 0 && showOthers == true"
        @click="showOthers = false"
      >
        Hide others <i class="fa-solid fa-caret-up"></i>
      </span>
    </div>
  </div>
</template>

<style scoped>
.action-button {
  @apply text-pink-500 hover:underline hover:scale-105 hover:text-gray-400 cursor-pointer;
}
</style>
