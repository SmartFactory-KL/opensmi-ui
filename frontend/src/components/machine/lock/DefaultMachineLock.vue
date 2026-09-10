<script setup lang="ts">
import { computed } from "vue";
import BlueButton from "../../BlueButton.vue";

interface Props {
  lockingModule: LockingModuleDto;
  serverUserName: string;
  enableTitle?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  enableTitle: false,
});

const emit = defineEmits(["lock-request", "break-request"]);

function emitLockingRequest() {
  if (isLockedByOthers.value == true) {
    emit("break-request");
  } else {
    emit("lock-request");
  }
}

const isLockedByUser = computed(() => {
  return (
    props.lockingModule.isLocked == true &&
    props.lockingModule.lockingUser == props.serverUserName
  );
});

const isLockedByOthers = computed(() => {
  return (
    props.lockingModule.isLocked == true &&
    props.lockingModule.lockingUser != props.serverUserName
  );
});

const isLocked = computed(() => {
  return props.lockingModule.isLocked == true;
});

const lockTitleString = computed(() => {
  if (isLockedByUser.value) {
    return "Locked by " + props.lockingModule.lockingUser;
  } else if (isLockedByOthers.value) {
    return "Locked by " + props.lockingModule.lockingUser;
  } else {
    return "Not locked";
  }
});
</script>

<template>
  <div class="flex flex-col">
    <div
      class="locking-display cursor-pointer hover:scale-105"
      @click="emitLockingRequest"
      :title="lockTitleString"
    >
      <i
        class="fa-solid fa-lock-open"
        v-show="!isLocked"
        :class="{ 'animate-spin': lockingModule.isLockPending }"
      ></i>
      <i
        class="fa-solid fa-lock"
        :class="{
          'text-green-400': isLockedByUser,
          'text-yellow-400': isLockedByOthers,
          'animate-spin': lockingModule.isLockPending,
        }"
        v-show="isLocked"
      ></i>

      <i
        class="fa-solid fa-user-lock text-green-400"
        v-show="isLockedByUser"
      ></i>
      <i
        class="fa-solid fa-plane-lock text-yellow-400"
        v-show="isLockedByOthers"
      ></i>
      <i class="fa-solid fa-circle-notch fa-2xs" v-show="!isLocked"></i>
    </div>
    <div v-if="enableTitle == true" class="text-base flex flex-col">
      {{ lockTitleString }}

      <BlueButton v-show="isLockedByOthers" @click="emitLockingRequest">
        Break
      </BlueButton>
    </div>
  </div>
</template>

<style scoped>
.locking-display {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  column-gap: 0.5rem;
}
</style>
