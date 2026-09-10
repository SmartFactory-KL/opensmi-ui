<script setup lang="ts">
import { useRoute } from "vue-router";
import { useMachineStore } from "../../../stores/MachineStore";
import { useServerStore } from "../../../stores/ServerStore";

import MachineLockDisplay from "../../machine/MachineLockDisplay.vue";
import RemoteVariableList from "../remote-variable/RemoteVariableList.vue";
import WritableRemoteVariableList from "../remote-variable/WritableRemoteVariableList.vue";
import ComponentTreeLink from "../navigation/ComponentTreeLink.vue";
import { usePageStore } from "../../../stores/PageStore";
import SkillLink from "../skill/SkillLink.vue";

import SkillControlBoard from "../skill/SkillControlBoard.vue";
import MethodLink from "../method/MethodLink.vue";
import NotFoundNotice from "../../NotFoundNotice.vue";

import { WriteParameterDto } from "../../../types/ActionTypes";

const route = useRoute();

const machineStore = useMachineStore();
const serverStore = useServerStore();
const pageStore = usePageStore();

// Copy & Paste for the 4th(?) time :D  - CaHa
// They used to be different per entityType until recently - KuZo
function createSingleWriteSkillAction(remoteVariable: RemoteVariableDto) {
  if (!machine) {
    return;
  }

  const skillAction: WriteParameterDto = {
    entityType: "Machine",
    entityId: machine?.entityId,
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

const machine = machineStore.machines.get(
  route.params.machineEntityId as string
);

function lockRequest() {
  machineStore.requestLockToggleForMachine(
    route.params.machineEntityId as string
  );
}

function breakLockRequest() {
  machineStore.requestLockBreakForMachine(
    route.params.machineEntityId as string
  );
}
</script>

<template>
  <div v-if="!machine">
    <NotFoundNotice></NotFoundNotice>
  </div>
  <div v-else class="m-8">
    <div class="title-line">
      <div class="title">
        <div class="text-gray-800 flex flex-row gap-x-4 justify-start items-center">
          <div class="text-4xl">
            <MachineLockDisplay :lockingModule="machine.lockingModule"
              :server-user-name="serverStore.connectionData.username" :enable-title="true" @lock-request="lockRequest"
              @break-request="breakLockRequest"></MachineLockDisplay>
          </div>
          <div>|</div>
          <div class="flex flex-col justify-start items-start">
            <div class="text-3xl">
              {{ machine.name }}
            </div>
            <div class="h-4">
              <span class="text-sm text-gray-500 leading-2">
                <span v-show="pageStore.showFlags.nodeIds">
                  {{ machine.nodeId }}
                </span>
                <span v-show="pageStore.showFlags.entityIds">
                  | {{ machine.entityId }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="state-line text-lg my-4">
      {{ machine.currentState }}
    </div>

    <hr class="border-primary" />

    <div class="my-4 flex flex-row justify-between items-start" style="max-width: 100%">
      <div>
        <span v-show="!machine.components?.length" class="text-base text-gray-500">
          No child components
        </span>
        <div v-show="machine.components?.length">
          <div class="mb-2 text-lg text-primary">Component Tree</div>
          <ComponentTreeLink :component="childComponent" :hide-skills="true"
            v-for="childComponent of machine.components"></ComponentTreeLink>
        </div>
      </div>

      <div>
        <span v-show="!machine.skillSet?.length" class="text-base text-gray-500">
          No skills
        </span>
        <div v-show="machine.skillSet?.length">
          <div class="mb-2 text-lg text-primary">Skillset</div>
          <div v-for="skill of machine.skillSet" class="flex flex-row justify-start gap-x-4 items-center">
            <SkillControlBoard :skill="skill" :show-as-tiny="true"></SkillControlBoard>

            <SkillLink :skill="skill"></SkillLink>
          </div>
        </div>
      </div>

      <div>
        <span v-show="!machine.methods?.length" class="text-base text-gray-500">
          No methods
        </span>
        <div v-show="machine.methods?.length">
          <div class="mb-2 text-lg text-primary">Methods</div>
          <div v-for="method of machine.methods" class="flex flex-row justify-start gap-x-4 items-center">
            <MethodLink :method="method"></MethodLink>
          </div>
        </div>
      </div>
    </div>

    <hr class="border-primary" />

    <div class="flex flex-row justify-start w-full gap-x-8 my-4">
      <WritableRemoteVariableList :remote-variable-list="machine.parameterSet" :parent-entity-id="machine.entityId"
        label="ParameterSet" @single-write="createSingleWriteSkillAction"></WritableRemoteVariableList>
    </div>

    <hr class="border-primary" />

    <div class="stats-line flex flex-row justify-start gap-x-8 mt-4">
      <div class="monitoring basis-1/2">
        <RemoteVariableList :remote-variable-list="machine.monitoring" label="Monitoring"></RemoteVariableList>
      </div>
      <div class="attributes basis-1/2">
        <RemoteVariableList :remote-variable-list="machine.attributes" label="Attributes"></RemoteVariableList>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-line {
  @apply flex flex-row justify-between items-start;
}
</style>
