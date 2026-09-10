<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  remoteVariable: RemoteVariableDto;
  enableWrites: boolean;
}>();

const step = computed(() => {
  if (
    (!props.remoteVariable.remoteVariableAnnotation.High &&
      props.remoteVariable.remoteVariableAnnotation.High != 0) ||
    (!props.remoteVariable.remoteVariableAnnotation.Low &&
      props.remoteVariable.remoteVariableAnnotation.Low != 0)
  ) {
    return 0.1;
  }

  return (
    (props.remoteVariable.remoteVariableAnnotation.High -
      props.remoteVariable.remoteVariableAnnotation.Low) /
    100.0
  );
});

const outOfRange = computed((): boolean => {
  if (
    (!props.remoteVariable.remoteVariableAnnotation.High &&
      props.remoteVariable.remoteVariableAnnotation.High != 0) ||
    (!props.remoteVariable.remoteVariableAnnotation.Low &&
      props.remoteVariable.remoteVariableAnnotation.Low != 0)
  ) {
    return false;
  }

  // should be true if it is out of range, not other way around
  return !(
    props.remoteVariable.tempDataContent.value.value >=
      props.remoteVariable.remoteVariableAnnotation.Low &&
    props.remoteVariable.tempDataContent.value.value <=
      props.remoteVariable.remoteVariableAnnotation.High
  );
});

// watch(
//   () => props.remoteVariable.tempValue,
//   (newValue) => {
//     if (
//       !props.remoteVariable.remoteVariableAnnotation.High ||
//       !props.remoteVariable.remoteVariableAnnotation.Low
//     ) {
//       return;
//     }

//     if (newValue < props.remoteVariable.remoteVariableAnnotation.Low) {
//       props.remoteVariable.tempValue =
//         props.remoteVariable.remoteVariableAnnotation.Low;
//       return;
//     }

//     if (newValue > props.remoteVariable.remoteVariableAnnotation.High) {
//       props.remoteVariable.tempValue =
//         props.remoteVariable.remoteVariableAnnotation.High;
//       return;
//     }
//   }
// );
</script>

<template>
  <div class="float-range-input" :class="{ 'out-of-range': outOfRange }">
    <!-- TODO: This sucks :)-->
    <div class="flex flex-row justify-between text-xs text-gray-400">
      <div>
        {{ remoteVariable.remoteVariableAnnotation.Low }}
      </div>
      <div>
        {{ remoteVariable.remoteVariableAnnotation.High }}
      </div>
    </div>
    <input
      type="range"
      v-model="remoteVariable.tempDataContent.value.value"
      :disabled="!enableWrites"
      :min="remoteVariable.remoteVariableAnnotation.Low"
      :max="remoteVariable.remoteVariableAnnotation.High"
      :step="step"
    />
    <input
      type="text"
      v-model="remoteVariable.tempDataContent.value.value"
      :disabled="!enableWrites"
    />
  </div>
</template>

<style scoped>
.float-range-input {
  @apply flex flex-col justify-center items-stretch gap-y-2;
  width: 100%;
}

.float-range-input input {
  width: 100%;
}

.out-of-range input {
  @apply accent-red-400;
}

.out-of-range {
  @apply bg-red-200;
}
</style>
