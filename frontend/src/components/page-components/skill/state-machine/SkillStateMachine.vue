<script lang="ts" setup>
import { computed } from "vue";
import SkillContinuousStateMachineDisplay from "./SkillContinuousStateMachineDisplay.vue";
import SkillFiniteStateMachineDisplay from "./SkillFiniteStateMachineDisplay.vue";
import NotFoundNotice from "../../../NotFoundNotice.vue";

const props = defineProps<{
  state: string;
  type: "Finite" | "Continuous" | string;
}>();

const stateMachineComponent = computed(() => {
  switch (props.type) {
    case "Continuous":
      return SkillContinuousStateMachineDisplay;
    case "Finite":
      return SkillFiniteStateMachineDisplay;
    default:
      return NotFoundNotice;
  }
});
</script>

<template>
  <component :is="stateMachineComponent" :state="state"></component>
</template>
