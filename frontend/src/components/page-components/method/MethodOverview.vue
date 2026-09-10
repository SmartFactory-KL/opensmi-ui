<script setup lang="ts">
import { useRoute } from "vue-router";
import { useMachineStore } from "../../../stores/MachineStore";

import RemoteVariableList from "../remote-variable/RemoteVariableList.vue";
import WritableRemoteVariableList from "../remote-variable/WritableRemoteVariableList.vue";
import MethodControlBoard from "./MethodControlBoard.vue";
import GenericStateDisplay from "../../GenericStateDisplay.vue";

import { WriteParameterDto } from "../../../types/ActionTypes";
import { usePageStore } from "../../../stores/PageStore";

import NotFoundNotice from "../../NotFoundNotice.vue";
import NodeBreadcrumbContainer from "../../NodeBreadcrumbContainer.vue";

const route = useRoute();

const machineStore = useMachineStore();
const pageStore = usePageStore();


function createSingleWriteSkillAction(remoteVariable: RemoteVariableDto) {
  if (!method) {
    return;
  }

  const methodAction: WriteParameterDto = {
    actionType: "WriteParameter",
    actionContent: {
      parameterNodeId: remoteVariable.nodeId,
      parameterName: remoteVariable.name,
      parameterNewValue: String(remoteVariable.tempDataContent.value.value),
    },
    entityId: method?.entityId,
    entityType: "Method",
  };

  console.log(methodAction);

  machineStore.requestMethodAction(methodAction);
}

const method = machineStore.methodEntityMap.get(
  route.params.methodEntityId as string
);
</script>

<template>
  <div v-if="!method"><NotFoundNotice></NotFoundNotice></div>
  <div v-else class="m-8">
    <div class="mb-2">
      <NodeBreadcrumbContainer
        :parent-node-id-list="method.parentNodeIdList"
      ></NodeBreadcrumbContainer>
    </div>
    <div class="title-line">
      <div class="title">
        <div
          class="text-gray-800 flex flex-row gap-x-4 justify-start items-center"
        >
          <div class="flex flex-col justify-start items-start">
            <div class="text-3xl">
              <i class="fa-solid fa-meteor fa-xs"></i>
              <span> | {{ method.name }} </span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm" v-show="pageStore.showFlags.nodeIds">
                <span class="text-gray-400">NodeId</span> {{ method.nodeId }}
              </span>
              <span class="text-sm" v-show="pageStore.showFlags.entityIds">
                <span class="text-gray-400">EntityId</span>
                {{ method.entityId }}
              </span>
              <span class="text-sm">
                <span class="text-gray-400">Type</span> {{ method.type }}
              </span>
              <span class="text-sm">
                <span class="text-gray-400">Min. Access Level</span> {{ method.minAccessLevel }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div>
        <MethodControlBoard
          :method="method"
          :show-as-tiny="false"
        ></MethodControlBoard>
      </div>
    </div>

    <div class="state-line text-lg my-4">
      <GenericStateDisplay state="no state"></GenericStateDisplay>
    </div>

    <hr class="border-primary" />

    <div class="flex flex-row justify-start w-full gap-x-8 my-4">
      <WritableRemoteVariableList
        :remote-variable-list="method.parameterSet"
        :parent-entity-id="method.entityId"
        label="ParameterSet"
        @single-write="createSingleWriteSkillAction"
      ></WritableRemoteVariableList>
    </div>

    <hr class="border-primary" />

    <div class="stats-line flex flex-row flex-wrap justify-start gap-x-8 mt-4">
      <div class="monitoring basis-5/12">
        <RemoteVariableList
          :remote-variable-list="method.monitoring"
          label="Monitoring"
        ></RemoteVariableList>
      </div>
      <div class="attributes basis-5/12">
        <RemoteVariableList
          :remote-variable-list="method.finalResultData"
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
