<script setup lang="ts">
import { computed, ref } from "vue";

import SkillLink from "../skill/SkillLink.vue";
import MethodLink from "../method/MethodLink.vue";
import ComponentLink from "../component/ComponentLink.vue";

const props = defineProps<{
  component: ComponentDto;
  hideSkills?: boolean;
}>();

const childElementVisible = ref(false);

const hasChildren = computed(() => {
  if (props.hideSkills) {
    return props.component?.components.length;
  } else {
    return (
      props.component?.components?.length || props.component?.skillSet.length
    );
  }
});
</script>

<template>
  <div class="component-tree-link">
    <div class="link-content my-1">
      <div
        v-show="hasChildren"
        @click="childElementVisible = !childElementVisible"
        class="cursor-pointer hover:text-secondary hover:scale-105"
      >
        <i class="fa-solid fa-caret-right" v-show="!childElementVisible"></i>
        <i class="fa-solid fa-caret-down" v-show="childElementVisible"></i>
      </div>
      <div v-show="!hasChildren">
        <i class="fa-solid fa-minus fa-2xs text-gray-600"></i>
      </div>

      <ComponentLink :component="component"></ComponentLink>
    </div>
    <div class="link-children ml-4" v-show="childElementVisible">
      <div v-if="hideSkills !== true">
        <SkillLink
          :skill="skill"
          v-for="skill of component.skillSet"
          class="my-2"
        ></SkillLink>
      </div>
      <div v-if="hideSkills !== true">
        <MethodLink
          :method="method"
          v-for="method of component.methods"
          class="my-2"
        ></MethodLink>
      </div>
      <ComponentTreeLink
        :component="component"
        :hide-skills="hideSkills"
        v-for="component of component.components"
      >
      </ComponentTreeLink>
    </div>
  </div>
</template>

<style scoped>
.link-content {
  display: flex;
  flex-direction: row;
  column-gap: 0.5rem;
  justify-content: start;
  align-items: center;
}
</style>
