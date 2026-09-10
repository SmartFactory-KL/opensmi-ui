<script setup lang="ts">
import { useMachineStore } from "../../../../stores/MachineStore";
import { usePageStore } from "../../../../stores/PageStore";

import NotFoundNotice from "../../../NotFoundNotice.vue";
import BlueButton from "../../../BlueButton.vue";

import { computed, ref } from "vue";
import { useServerStore } from "../../../../stores/ServerStore";
import { GenericActionDto } from "../../../../types/ActionTypes";

const machineStore = useMachineStore();
const pageStore = usePageStore();
const serverStore = useServerStore();

const pending = ref(false);

const props = defineProps<{
  component: ComponentDto;
}>();

const isMachineOfEntityLockedByUs = computed(() => {
  if (!props.component) {
    return;
  }
  const machineForSkill = machineStore.entityToParentMachineMap.get(
    props.component.entityId
  );

  if (!machineForSkill) {
    return false;
  }

  if (!machineForSkill.lockingModule.isLocked) {
    return false;
  }

  if (
    machineForSkill.lockingModule.lockingUser !=
    serverStore.connectionData.username
  ) {
    return false;
  }

  return true;
});

function getCoupleSkill() {
  if (!props.component) {
    return null;
  }

  const coupleSkill = props.component.skillSet.find((el) => {
    return el.name == "CoupleSkill";
  });

  return coupleSkill;
}

function requestCouple() {
  const skill = getCoupleSkill();

  if (!skill) {
    return;
  }

  pending.value = true;

  createSkillControlAction("reset", skill);

  const handle = setInterval(() => {
    if (skill.currentState == "Ready") {
      clearInterval(handle);
      createSkillControlAction("start", skill);
      pending.value = false;
    }
  }, 200);
}

function requestDecouple() {
  const skill = getCoupleSkill();

  if (!skill) {
    return;
  }

  pending.value = true;
  createSkillControlAction("halt", skill);
  pending.value = false;
}

function createSkillControlAction(
  type: "start" | "halt" | "reset" | "suspend" | string,
  skill: SkillDto
) {
  const skillAction: GenericActionDto = {
    entityId: skill?.entityId,
    entityType: "Skill",
    actionContent: null,
    actionType: "SkillStart",
  };

  switch (type) {
    case "start":
      skillAction.actionType = "SkillStart";
      break;
    case "halt":
      skillAction.actionType = "SkillHalt";
      break;
    case "reset":
      skillAction.actionType = "SkillReset";
      break;
    case "suspend":
      skillAction.actionType = "SkillSuspend";
      break;
  }

  machineStore.requestSkillAction(skillAction);
}

const areMagnetsClosed = computed(() => {
  if (!props.component) {
    return false;
  }

  const item =
    props.component.monitoring.find((el) => {
      return el.name == "MagnetsClosed";
    }) ?? null;

  if (!item) {
    return false;
  }

  return item.dataContent.value.value == true;
});
</script>

<template>
  <div v-if="!component"><NotFoundNotice></NotFoundNotice></div>
  <div v-else class="m-8">
    <div class="title-line">
      <div class="title">
        <div
          class="text-gray-800 flex flex-row gap-x-4 justify-start items-center"
        >
          <div class="flex flex-col justify-start items-start">
            <div class="text-3xl">
              <i class="fa-solid fa-toolbox fa-xs"></i> | {{ component.name }}
            </div>
            <div class="flex flex-col">
              <span class="text-sm" v-show="pageStore.showFlags.nodeIds">
                <span class="text-gray-400">NodeId</span> {{ component.nodeId }}
              </span>
              <span class="text-sm" v-show="pageStore.showFlags.entityIds">
                <span class="text-gray-400">EntityId</span>
                {{ component.entityId }}
              </span>
              <span class="text-sm">
                <span class="text-gray-400">Type</span> {{ component.type }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div>
      <div class="text-lg mt-10 flex flex-col">
        <span> Magnets are: </span>
        <span v-show="areMagnetsClosed" class="text-green-500">
          <i class="fa-solid fa-check"></i> closed
        </span>
        <span v-show="!areMagnetsClosed" class="text-red-500">
          <i class="fa-solid fa-x"></i> open
        </span>
      </div>
      <div class="mt-10 flex flex-col justify-start items-start">
        <BlueButton
          v-show="!areMagnetsClosed"
          @click="requestCouple()"
          :disabled="!isMachineOfEntityLockedByUs"
        >
          <span v-show="pending"
            ><i class="fa-solid fa-spinner fa-spin"></i
          ></span>
          Couple
        </BlueButton>
        <BlueButton
          v-show="areMagnetsClosed"
          @click="requestDecouple()"
          :disabled="!isMachineOfEntityLockedByUs"
        >
          <span v-show="pending"
            ><i class="fa-solid fa-spinner fa-spin"></i
          ></span>
          Decouple
        </BlueButton>
        <span v-show="!isMachineOfEntityLockedByUs" class="text-red-500"
          >Not locked</span
        >
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-line {
  @apply flex flex-row justify-between items-start;
}
</style>
