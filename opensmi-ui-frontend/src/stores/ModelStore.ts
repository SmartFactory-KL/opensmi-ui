import { simplyGetToJSON } from "@/fetch/simplyFetch";
import type { SocketMessage } from "@/socket/SocketClient";
import type SocketClient from "@/socket/SocketClient";
import type { GenericUpdateMessage } from "@/types/GenericTypes";
import type {
  MachineDto,
  SkillDto,
  MethodDto,
  ComponentDto,
  RemoteVariableDto,
  ComponentEntityDto,
} from "@/types/ModuleTypes";
import type {
  MachineStateUpdate,
  MachineLockStateUpdate,
  MachineLockUserUpdate,
  MachineNewMessageUpdate,
  ComponentStateUpdate,
  SkillStateUpdate,
  VariableDataValueUpdate,
} from "@/types/UpdateTypes";
import { createDeepCopy } from "@/util/copy";
import { defineStore } from "pinia";

export const useModelStore = defineStore("model", {
  state: (): {
    requestData: {
      isPending: boolean;
      error: string | null;
    };

    isWorking: boolean;

    machines: Map<string, ComponentEntityDto>;

    skillEntityMap: Map<string, SkillDto>;
    methodEntityMap: Map<string, MethodDto>;
    componentEntityMap: Map<string, ComponentDto>;
    variableEntityMap: Map<string, RemoteVariableDto>;

    entityToParentMachineMap: Map<string, MachineDto>;

    nodeIdSkillMap: Map<string, SkillDto>;
    nodeIdMethodMap: Map<string, MethodDto>;
    nodeIdComponentMap: Map<string, ComponentDto>;
  } => {
    return {
      requestData: {
        isPending: false,
        error: null,
      },

      isWorking: false,

      machines: new Map<string, ComponentEntityDto>(),

      skillEntityMap: new Map<string, SkillDto>(),
      methodEntityMap: new Map<string, MethodDto>(),
      componentEntityMap: new Map<string, ComponentDto>(),
      variableEntityMap: new Map<string, RemoteVariableDto>(),

      entityToParentMachineMap: new Map<string, MachineDto>(),

      nodeIdSkillMap: new Map<string, SkillDto>(),
      nodeIdMethodMap: new Map<string, MethodDto>(),
      nodeIdComponentMap: new Map<string, ComponentDto>(),
    };
  },
  getters: {},
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      // add batch listener
      socketClient.addChannelListener("batch", this.handleBatchUpdate);

      // these channels are still listened to because direct messages might happen outside the batch
      socketClient.addChannelListener("Machine", this.handleMachineUpdate);
      socketClient.addChannelListener("Component", this.handleComponentUpdate);
      socketClient.addChannelListener("Skill", this.handleSkillUpdate);
      socketClient.addChannelListener("Method", this.handleMethodUpdate);
      socketClient.addChannelListener("Variable", this.handleVariableUpdate);
    },
    async refreshMachineData() {
      if (this.requestData.isPending == true || this.isWorking == true) {
        return;
      }

      this.requestData.isPending = true;
      this.requestData.error = null;
      this.isWorking = true;

      console.log("requesting machine data...");

      this.machines.clear();

      this.skillEntityMap.clear();
      this.methodEntityMap.clear();
      this.componentEntityMap.clear();
      this.variableEntityMap.clear();

      this.entityToParentMachineMap.clear();

      try {
        const result = (await simplyGetToJSON(
          "/api/opc-session/model",
        )) as ComponentEntityDto[];

        console.log(result);

        if (!Array.isArray(result)) {
          throw new Error(
            `Expected Model to ba Array, got ${typeof result} instead`,
          );
        }

        for (const rootComponent of result) {
          console.log("Handling Machine", rootComponent.data.name);

          // walk the component tree and map relevant entities within it
          const componentsToProcess = [rootComponent] as ComponentEntityDto[];

          let count = 0;
          while (componentsToProcess.length > 0) {
            count++;
            if (count > 100_000) {
              throw new Error("Count OVF when processing components.");
            }

            const nextComponentEntity = componentsToProcess.shift();
            if (!nextComponentEntity) {
              break;
            } // this only exists to prevent null checks

            for (const child of nextComponentEntity.children) {
              componentsToProcess.push(child);
            }
          }

          this.machines.set(rootComponent.entityId, rootComponent);
        }

        console.log(`Received ${this.machines.size} root components`);
        this.isWorking = false;
      } catch (e) {
        console.error(e);
        this.requestData.error = `Failed to request model: ${e}`;
      } finally {
        this.requestData.isPending = false;
        this.isWorking = false;
      }
    },
    /**
     * Handle a batch of updates by proxying them to the respective method
     * @param batchUpdate the list of updates to handle
     */
    handleBatchUpdate(batchUpdate: SocketMessage[]) {
      if (!batchUpdate?.length) {
        return;
      }

      for (const item of batchUpdate) {
        switch (item.channel) {
          case "Machine":
            this.handleMachineUpdate(item.data);
            break;
          case "Component":
            this.handleComponentUpdate(item.data);
            break;
          case "Skill":
            this.handleSkillUpdate(item.data);
            break;
          case "Method":
            this.handleMethodUpdate(item.data);
            break;
          case "Variable":
            this.handleVariableUpdate(item.data);
            break;
          default:
            console.warn("batch contained non-ok entityType in item", item);
        }
      }
    },
    /**
     * Handle a machine update
     * @param machineUpdate Update itself
     */
    handleMachineUpdate(machineUpdate: GenericUpdateMessage<any>) {
      if (!machineUpdate || !machineUpdate.updateType) {
        return;
      }
      switch (machineUpdate.updateType) {
        case "ComponentStateUpdate":
          const msg_state_update =
            machineUpdate.updateContent as MachineStateUpdate;
          const target_state_update = this.machines.get(machineUpdate.entityId);

          if (!target_state_update) {
            console.warn("Machine target not found for " + machineUpdate);
            return;
          }

          target_state_update.currentState = msg_state_update.newState;
          break;
        case "MachineLockStateUpdate":
          const msg_lock_state =
            machineUpdate.updateContent as MachineLockStateUpdate;
          const target_lock_state = this.machines.get(machineUpdate.entityId);

          if (!target_lock_state) {
            console.warn("Machine target not found for " + machineUpdate);
            return;
          }

          target_lock_state.lockingModule.isLockPending = false;
          target_lock_state.lockingModule.isLocked = msg_lock_state.isLocked;
          break;
        case "MachineLockUserUpdate":
          const msg_lock_user =
            machineUpdate.updateContent as MachineLockUserUpdate;
          const target_lock_user = this.machines.get(machineUpdate.entityId);

          if (!target_lock_user) {
            console.warn("Machine target not found for " + machineUpdate);
            return;
          }

          target_lock_user.lockingModule.isLockPending = false;
          target_lock_user.lockingModule.lockingUser =
            msg_lock_user.newLockingUser;
          break;
        case "ComponentNewMessageUpdate":
          const msg_message =
            machineUpdate.updateContent as MachineNewMessageUpdate;
          break;
        default:
          console.warn("Received invalid updateType for Machine:");
          console.warn(machineUpdate);
          break;
      }
    },
    /**
     * Handle a Component update
     * @param componentUpdate Update itself
     */
    handleComponentUpdate(componentUpdate: GenericUpdateMessage<any>) {
      const updateCheckResult = this.checkEntityUpdate(componentUpdate);
      if (!updateCheckResult.shouldBeHandled) {
        return;
      }

      const target = updateCheckResult.targetEntity;

      switch (componentUpdate.updateType) {
        case "ComponentStateUpdate":
          const msg_state_update =
            componentUpdate.updateContent as ComponentStateUpdate;
          target.currentState = msg_state_update.newState;
          break;
        case "ComponentNewMessageUpdate":
          const msg_message =
            componentUpdate.updateContent as MachineNewMessageUpdate;
          break;
        default:
          console.warn("Received invalid updateType for Component:");
          console.warn(componentUpdate);
          break;
      }
    },
    /**
     * Handle a Skill update
     * @param skillUpdate Update itself
     */
    handleSkillUpdate(skillUpdate: GenericUpdateMessage<any>) {
      const updateCheckResult = this.checkEntityUpdate(skillUpdate);
      if (!updateCheckResult.shouldBeHandled) {
        return;
      }

      const target = updateCheckResult.targetEntity;

      switch (skillUpdate.updateType) {
        case "SkillStateUpdate":
          const msg_state_update =
            skillUpdate.updateContent as SkillStateUpdate;
          target.currentState = msg_state_update.newState;
          break;
        default:
          console.warn("Received invalid updateType for Skill:");
          console.warn(skillUpdate);
          break;
      }
    },
    /**
     * Handle a Method Update
     * @param methodUpdate Update itself
     */
    handleMethodUpdate(methodUpdate: GenericUpdateMessage<any>) {
      const updateCheckResult = this.checkEntityUpdate(methodUpdate);
      if (!updateCheckResult.shouldBeHandled) {
        return;
      }

      // const target = updateCheckResult.targetEntity;

      switch (methodUpdate.updateType) {
        // For now, methods only have variable updates. This code is left anyway for documentation reasons
        default:
          console.warn("Received invalid updateType for Method:");
          console.warn(methodUpdate);
          break;
      }
    },
    /**
     * Handle a Variable update
     * @param variableUpdate Update itself
     */
    handleVariableUpdate(variableUpdate: GenericUpdateMessage<any>) {
      const updateCheckResult = this.checkEntityUpdate(variableUpdate);
      if (!updateCheckResult.shouldBeHandled) {
        return;
      }

      const target = updateCheckResult.targetEntity as RemoteVariableDto;

      switch (variableUpdate.updateType) {
        case "VariableDataValueUpdate":
          const value_msg =
            variableUpdate.updateContent as VariableDataValueUpdate;
          target.dataContent = value_msg;
          break;
        default:
          console.warn("Received invalid updateType for Variable:");
          console.warn(variableUpdate);
          break;
      }
    },
    /**
     * Check whether an update is generally good looking. shouldBeHandled is false if the update should not be handled.
     * @param update GenericUpdateMessage to check
     * @param entityId target entityId
     * @returns Object containing target and flag shouldBeHandled
     */
    checkEntityUpdate(update: GenericUpdateMessage<any>): {
      shouldBeHandled: boolean;
      targetEntity: any;
    } {
      const response = {
        shouldBeHandled: false,
        targetEntity: null as any,
      };

      // ignore updates while working on a refresh
      if (this.isWorking == true) {
        return response;
      }

      if (!update || !update.updateType) {
        return response;
      }

      switch (update.entityType) {
        case "Component":
          response.targetEntity =
            this.componentEntityMap.get(update.entityId) || null;
          break;
        case "Skill":
          response.targetEntity =
            this.skillEntityMap.get(update.entityId) || null;
          break;
        case "Method":
          response.targetEntity =
            this.methodEntityMap.get(update.entityId) || null;
          break;
        case "Variable":
          response.targetEntity =
            this.variableEntityMap.get(update.entityId) || null;
          break;
        default:
          // ignore these cases
          return response;
      }

      if (response.targetEntity !== null) {
        response.shouldBeHandled = true;
      } else {
        console.warn(
          "An update for non-existing entityId " +
            update.entityId +
            " was received. It was ignored.",
        );
      }

      return response;
    },
    /**
     * This method will mapify (entityId -> Dto) a component, its callables and its variables. It also sets default tempValues to parameters.
     * @param component The component to be initialized and mapified
     * @param parentMachine reference to the parentMachine
     */
    mapifyComponentEntities(
      component: ComponentDto,
      parentMachine: MachineDto,
    ) {
      this.applyTempValuesToParametersOfCallable(component);

      for (const _skill of component.skillSet || []) {
        this.applyTempValuesToParametersOfCallable(_skill);
        this.skillEntityMap.set(_skill.entityId, _skill);
        this.nodeIdSkillMap.set(
          _skill.nodeId.replace(".SkillExecution", ""),
          _skill,
        );
        this.entityToParentMachineMap.set(_skill.entityId, parentMachine);

        this.mapifyVariableTree(_skill.monitoring, parentMachine);
        this.mapifyVariableTree(_skill.parameterSet, parentMachine);
        this.mapifyVariableTree(_skill.finalResultData, parentMachine);
      }

      for (const _method of component.methods || []) {
        this.applyTempValuesToParametersOfCallable(_method);
        this.methodEntityMap.set(_method.entityId, _method);
        this.nodeIdMethodMap.set(_method.nodeId, _method);
        this.entityToParentMachineMap.set(_method.entityId, parentMachine);

        this.mapifyVariableTree(_method.monitoring, parentMachine);
        this.mapifyVariableTree(_method.parameterSet, parentMachine);
        this.mapifyVariableTree(_method.finalResultData, parentMachine);
      }

      this.mapifyVariableTree(component.monitoring, parentMachine);
      this.mapifyVariableTree(component.parameterSet, parentMachine);
      this.mapifyVariableTree(component.attributes, parentMachine);

      this.entityToParentMachineMap.set(component.entityId, parentMachine);
      this.nodeIdComponentMap.set(component.nodeId, component);
      this.componentEntityMap.set(component.entityId, component);
    },
    /**
     * Add all variables of this tree to the variableMap using entityId
     * @param rootElementList list of elements to use as root
     * @param parentMachine parentMachine to link these variables to
     * @returns -
     */
    mapifyVariableTree(
      rootElementList: RemoteVariableDto[],
      parentMachine: MachineDto,
    ) {
      if (!parentMachine) {
        return;
      }

      let count = 0;
      const entityList = [] as RemoteVariableDto[];

      if (!Array.isArray(rootElementList)) {
        return;
      }

      for (const entity of rootElementList) {
        entityList.push(entity);
      }

      while (entityList.length > 0 && count < 100_000) {
        count++;

        const curEntity = entityList.pop();
        if (!curEntity) {
          continue;
        }

        this.variableEntityMap.set(curEntity.entityId, curEntity);
        this.entityToParentMachineMap.set(curEntity.entityId, parentMachine);

        for (const childEntity of curEntity?.children || []) {
          entityList.push(childEntity);
        }
      }

      if (count >= 100_000) {
        console.error("COUNT OVF while mapifying variable tree!");
      }
    },
    /**
     * This will run through ParameterSet to set the temporary value (only used for display)
     * @param callableInput DTO of input
     */
    applyTempValuesToParametersOfCallable(
      callableInput: SkillDto | MethodDto | ComponentDto,
    ) {
      const itemsToProcess = [] as RemoteVariableDto[];

      if (!Array.isArray(callableInput.parameterSet)) {
        return;
      }

      for (const _item of callableInput.parameterSet) {
        itemsToProcess.push(_item);
      }

      let count = 0;
      while (itemsToProcess.length > 0) {
        count++;
        if (count > 100_000) {
          throw new Error(
            "Count OVF when processing remote variables within skill: " +
              callableInput.nodeId,
          );
        }

        const nextItem = itemsToProcess.shift();
        if (!nextItem) {
          continue;
        }

        nextItem.tempDataContent = createDeepCopy(nextItem.dataContent);

        for (const _child of nextItem.children) {
          itemsToProcess.push(_child);
        }
      }
    },
  },
});
