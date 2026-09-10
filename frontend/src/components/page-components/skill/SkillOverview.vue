<script setup lang="ts">
import { useRoute } from "vue-router";
import { useMachineStore } from "../../../stores/MachineStore";

import RemoteVariableList from "../remote-variable/RemoteVariableList.vue";
import WritableRemoteVariableList from "../remote-variable/WritableRemoteVariableList.vue";
import SkillControlBoard from "./SkillControlBoard.vue";
import GenericStateDisplay from "../../GenericStateDisplay.vue";

import { WriteParameterDto } from "../../../types/ActionTypes";
import { usePageStore } from "../../../stores/PageStore";
import SkillNameDisplay from "./SkillNameDisplay.vue";
import NotFoundNotice from "../../NotFoundNotice.vue";
import SkillStateMachineDisplay from "./state-machine/SkillStateMachine.vue";
import { ref } from "vue";
import SkillLimitedLinkList from "./SkillLimitedLinkList.vue";
import NodeBreadcrumbContainer from "../../NodeBreadcrumbContainer.vue";

const route = useRoute();

const machineStore = useMachineStore();
const pageStore = usePageStore();

const isStateMachineVisisble = ref(true);

function createSingleWriteSkillAction(remoteVariable: RemoteVariableDto) {
  if (!skill) {
    return;
  }

  const skillAction: WriteParameterDto = {
    entityType: "Skill",
    entityId: skill?.entityId,
    actionType: "WriteParameter",
    actionContent: {
      parameterNodeId: remoteVariable.nodeId,
      parameterName: remoteVariable.name,
      parameterNewValue: String(remoteVariable.tempDataContent.value.value),
    },
  };

  console.log(skillAction);

  machineStore.requestSkillAction(skillAction);
}

const skill = machineStore.skillEntityMap.get(
  route.params.skillEntityId as string,
);
</script>

<template>
  <div v-if="!skill"><NotFoundNotice></NotFoundNotice></div>
  <div v-else class="m-8">
    <div class="mb-2">
      <NodeBreadcrumbContainer
        :parent-node-id-list="skill.parentNodeIdList"
      ></NodeBreadcrumbContainer>
    </div>
    <div class="title-line">
      <div class="title">
        <div
          class="text-gray-800 flex flex-row gap-x-4 justify-start items-center"
        >
          <div class="flex flex-col justify-start items-start">
            <div class="text-3xl">
              <i
                class="fa-solid fa-rotate fa-xs"
                v-if="skill.type == 'Continuous'"
              ></i>
              <i class="fa-solid fa-bolt fa-xs" v-else></i>
              <span>
                | <SkillNameDisplay :skill="skill"></SkillNameDisplay>
              </span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm" v-show="pageStore.showFlags.nodeIds">
                <span class="text-gray-400">NodeId</span> {{ skill.nodeId }}
              </span>
              <span class="text-sm" v-show="pageStore.showFlags.entityIds">
                <span class="text-gray-400">EntityId</span> {{ skill.entityId }}
              </span>
              <span class="text-sm">
                <span class="text-gray-400">Type</span> {{ skill.type }}
              </span>
              <span class="text-sm">
                <span class="text-gray-400">Min. Access Level</span>
                {{ skill.minAccessLevel }}
              </span>

              <div
                class="state-line text-lg my-4 flex flex-row justify-start items-center gap-x-4"
              >
                <GenericStateDisplay
                  :state="skill.currentState!"
                ></GenericStateDisplay>

                <div>|</div>

                <div
                  @click="isStateMachineVisisble = !isStateMachineVisisble"
                  class="text-gray-600 hover:scale-105 cursor-pointer hover:text-gray-900"
                >
                  State Machine
                  <i
                    class="fa-solid fa-caret-down"
                    v-show="!isStateMachineVisisble"
                  ></i>
                  <i
                    class="fa-solid fa-caret-up"
                    v-show="isStateMachineVisisble"
                  ></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div>
        <SkillControlBoard
          :skill="skill"
          :show-as-tiny="false"
        ></SkillControlBoard>
      </div>
    </div>

    <div
      style="width: 48rem; height: 12rem"
      v-show="isStateMachineVisisble"
      class="mb-4 border-slate-500 shadow-lg border"
    >
      <SkillStateMachineDisplay
        :state="skill.currentState || ''"
        :type="skill.type"
      ></SkillStateMachineDisplay>
    </div>

    <div
      class="text-gray-600 text-sm flex flex-row justify-around items-start mb-4"
    >
      <div class="flex flex-col justify-start items-start">
        Dependency of:
        <SkillLimitedLinkList
          :skill-id-list="skill.dependencyOf"
        ></SkillLimitedLinkList>
      </div>
      <div class="flex flex-col justify-start items-start">
        Depends on:
        <SkillLimitedLinkList
          :skill-id-list="skill.dependsOn"
        ></SkillLimitedLinkList>
      </div>
    </div>

    <hr class="border-primary" />

    <div class="flex flex-row justify-start w-full gap-x-8 my-4">
      <WritableRemoteVariableList
        :remote-variable-list="skill.parameterSet"
        :parent-entity-id="skill.entityId"
        label="ParameterSet"
        @single-write="createSingleWriteSkillAction"
      ></WritableRemoteVariableList>
    </div>

    <hr class="border-primary" />

    <div class="stats-line flex flex-row flex-wrap justify-start gap-x-8 mt-4">
      <div class="monitoring basis-5/12">
        <RemoteVariableList
          :remote-variable-list="skill.monitoring"
          label="Monitoring"
        ></RemoteVariableList>
      </div>
      <div class="attributes basis-5/12">
        <RemoteVariableList
          :remote-variable-list="skill.finalResultData"
          label="Final Result Data"
        ></RemoteVariableList>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-line {
  @apply flex flex-row justify-between items-start;
}
</style>
