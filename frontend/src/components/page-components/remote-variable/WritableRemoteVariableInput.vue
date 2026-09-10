<script setup lang="ts">
import { computed } from "vue";
import VariableEnumInput from "./writable-variable-input/VariableEnumInput.vue";
import VariableGenericInput from "./writable-variable-input/VariableGenericInput.vue";
import VariableBooleanInput from "./writable-variable-input/VariableBooleanInput.vue";
import VariableFloatRangeInput from "./writable-variable-input/VariableFloatRangeInput.vue";

const props = defineProps<{
  remoteVariable: RemoteVariableDto;
  enableWrites: boolean;
}>();

const inputComponent = computed(() => {
  switch (props.remoteVariable.remoteVariableType) {
    case "Enum":
      return VariableEnumInput;
    case "FloatRange":
      return VariableFloatRangeInput;
    case "Boolean":
      return VariableBooleanInput;
    case "Text":
      return VariableGenericInput;
  }
});
</script>

<template>
  <component
    :is="inputComponent"
    :remote-variable="remoteVariable"
    :enable-writes="enableWrites"
  ></component>
</template>

<style scoped>
.remote-variable {
  flex-basis: calc(33% - 5rem);
  max-width: 20rem;
}

.parameter-input {
  width: 7rem;
}

.parameter-value {
  width: 7rem;
}

.parameter-input input {
  width: 100%;
}
</style>
