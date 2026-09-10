<script setup lang="ts">
import { computed } from "vue";
import SkillControlKnob from "./SkillControlKnob.vue";

import { useServerStore } from "../../../stores/ServerStore";
import { useMachineStore } from "../../../stores/MachineStore";
import { GenericActionDto } from "../../../types/ActionTypes";
import { usePinGuardStore } from "../../../stores/PinStore";

const machineStore = useMachineStore();
const serverStore = useServerStore();
const pinGuardStore = usePinGuardStore();

const props = defineProps<{
  skill: SkillDto;
  showAsTiny: boolean;
}>();

const canExecuteSkillAction = computed(() => {
  if (pinGuardStore.isLocked) {
    return false;
  }

  const machineForSkill = machineStore.entityToParentMachineMap.get(
    props.skill.entityId
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

function createSkillControlAction(
  type: "start" | "halt" | "reset" | "suspend" | string
) {
  const skillAction: GenericActionDto = {
    entityId: props.skill?.entityId,
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

const buttonIsActive = computed(() => {
  const activeButtons = {
    reset: false,
    start: false,
    halt: false,
    suspend: false,
  };

  const currentState = props.skill.currentState;

  switch (currentState) {
    case "Halted":
      activeButtons.reset = true;
      break;
    case "Ready":
      activeButtons.start = true;
      activeButtons.halt = true;
      break;
    case "Running":
      activeButtons.halt = true;
      activeButtons.suspend = props.skill.isSuspendable;
      break;
    case "Suspended":
      activeButtons.reset = true;
      activeButtons.halt = true;
      activeButtons.start = true;
      break;
    case "Completed":
      activeButtons.reset = true;
      activeButtons.halt = true;
      break;
    case "Starting":
      activeButtons.halt = true;
      break;
    case "Halting":
      activeButtons.halt = true;
      break;
    case "Completing":
      activeButtons.halt = true;
      break;
  }

  return activeButtons;
});
</script>

<template>
  <div
    class="skill-control-board"
    :class="[{ inactive: !canExecuteSkillAction, tiny: showAsTiny }]"
  >
    <div class="control-knob-list">
      <SkillControlKnob
        label="Reset"
        :is-active="buttonIsActive['reset'] && canExecuteSkillAction"
        :is-tiny="showAsTiny"
        @control-click="createSkillControlAction('reset')"
        symbol="fa-reply"
      ></SkillControlKnob>
      <SkillControlKnob
        label="Start"
        :is-active="buttonIsActive['start'] && canExecuteSkillAction"
        :is-tiny="showAsTiny"
        @control-click="createSkillControlAction('start')"
        symbol="fa-play"
      ></SkillControlKnob>
      <SkillControlKnob
        label="Halt"
        :is-active="buttonIsActive['halt'] && canExecuteSkillAction"
        :is-tiny="showAsTiny"
        @control-click="createSkillControlAction('halt')"
        symbol="fa-power-off"
      ></SkillControlKnob>
      <SkillControlKnob
        label="Suspend"
        :is-active="buttonIsActive['suspend'] && canExecuteSkillAction"
        :is-tiny="showAsTiny"
        @control-click="createSkillControlAction('suspend')"
        symbol="fa-pause"
      ></SkillControlKnob>
    </div>
    <div v-show="!showAsTiny">
      <span
        class="text-red-400 flex flex-row justify-center items-center text-xs pt-2"
        v-show="!canExecuteSkillAction"
      >
        Either the machine is not locked or the PinGuard is locked.
      </span>
    </div>
  </div>
</template>

<style scoped>
.skill-control-board {
  @apply border-2 border-secondary p-4;
}

.skill-control-board.tiny {
  @apply border-0 p-0;
}

.skill-control-board.inactive {
  @apply border-gray-400;
}

.control-knob-list {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  column-gap: 1.5rem;
  align-items: center;
}

.tiny .control-knob-list {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  column-gap: 0;
}

.skill-control-knob {
  @apply border border-primary;
  width: 3rem;
  height: 3rem;
}
</style>
