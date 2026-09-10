<script setup lang="ts">
import { useRoute } from "vue-router";
import { useMachineStore } from "../../../stores/MachineStore";
import { usePageStore } from "../../../stores/PageStore";

import RemoteVariableList from "../remote-variable/RemoteVariableList.vue";
import ComponentTreeLink from "../navigation/ComponentTreeLink.vue";
import GenericStateDisplay from "../../GenericStateDisplay.vue";
import SkillControlBoard from "../skill/SkillControlBoard.vue";
import SkillLink from "../skill/SkillLink.vue";
import MethodLink from "../method/MethodLink.vue";
import NotFoundNotice from "../../NotFoundNotice.vue";
import WritableRemoteVariableList from "../remote-variable/WritableRemoteVariableList.vue";

import { WriteParameterDto } from "../../../types/ActionTypes";
import NodeBreadcrumbContainer from "../../NodeBreadcrumbContainer.vue";

const route = useRoute();

const machineStore = useMachineStore();
const pageStore = usePageStore();

function createSingleWriteSkillAction(remoteVariable: RemoteVariableDto) {
  if (!component) {
    return;
  }

  const skillAction: WriteParameterDto = {
    entityType: "Component",
    entityId: component?.entityId,
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

const component = machineStore.componentEntityMap.get(
  route.params.componentEntityId as string,
);
</script>

<template>
  <div v-if="!component"><NotFoundNotice></NotFoundNotice></div>
  <div v-else class="m-8">
    <NodeBreadcrumbContainer
      :parent-node-id-list="component.parentNodeIdList"
      class="mb-2"
    ></NodeBreadcrumbContainer>
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

    <div class="state-line text-lg my-4">
      <GenericStateDisplay
        :state="component.currentState!"
      ></GenericStateDisplay>
    </div>

    <hr class="border-primary" />

    <div
      class="my-4 flex flex-row justify-between items-start"
      style="max-width: 100%"
    >
      <div>
        <span
          v-show="!component.components?.length"
          class="text-base text-gray-500"
        >
          No child components
        </span>
        <div v-show="component.components?.length">
          <div class="mb-2 text-lg text-primary">Component Tree</div>
          <ComponentTreeLink
            :component="childComponent"
            v-for="childComponent of component.components"
          ></ComponentTreeLink>
        </div>
      </div>

      <div>
        <span
          v-show="!component.skillSet?.length"
          class="text-base text-gray-500"
        >
          No skills
        </span>
        <div v-show="component.skillSet?.length">
          <div class="mb-2 text-lg text-primary">Skillset</div>
          <div
            v-for="skill of component.skillSet"
            class="flex flex-row justify-start gap-x-4 items-center"
          >
            <SkillControlBoard
              :skill="skill"
              :show-as-tiny="true"
            ></SkillControlBoard>
            <SkillLink :skill="skill"></SkillLink>
          </div>
        </div>
      </div>

      <div>
        <span
          v-show="!component.methods?.length"
          class="text-base text-gray-500"
        >
          No methods
        </span>
        <div v-show="component.methods?.length">
          <div class="mb-2 text-lg text-primary">Methods</div>
          <div
            v-for="method of component.methods"
            class="flex flex-row justify-start gap-x-4 items-center"
          >
            <MethodLink :method="method"></MethodLink>
          </div>
        </div>
      </div>
    </div>

    <hr class="border-primary" />

    <div class="flex flex-row justify-start w-full gap-x-8 my-4">
      <WritableRemoteVariableList
        :remote-variable-list="component.parameterSet"
        :parent-entity-id="component.entityId"
        label="ParameterSet"
        @single-write="createSingleWriteSkillAction"
      ></WritableRemoteVariableList>
    </div>

    <hr class="border-primary" />

    <div class="stats-line flex flex-row justify-start gap-x-8 mt-4">
      <div class="monitoring basis-1/2">
        <RemoteVariableList
          :remote-variable-list="component.monitoring"
          label="Monitoring"
        ></RemoteVariableList>
      </div>
      <div class="attributes basis-1/2">
        <RemoteVariableList
          :remote-variable-list="component.attributes"
          label="Attributes"
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
