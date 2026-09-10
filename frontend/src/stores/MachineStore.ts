import { defineStore } from "pinia";
import { simplyGet, simplyPost } from "../util/SimplyFetch";
import SocketClient, { SocketMessage } from "../util/SocketClient";
import Notify from "../util/Notify";
import {
  ComponentStateUpdate,
  GenericUpdateMessage,
  MachineLockStateUpdate,
  MachineLockUserUpdate,
  MachineNewMessageUpdate,
  MachineStateUpdate,
  SkillStateUpdate,
  VariableDataValueUpdate,
} from "../types/UpdateTypes";
import { GenericActionDto } from "../types/ActionTypes";
import { createDeepCopy } from "../util/DeepClone";

export const useMachineStore = defineStore("machine", {
  state: (): {
    machines: Map<string, MachineDto>;
    refreshPending: boolean;

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
      machines: new Map<string, MachineDto>(),
      refreshPending: true,

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
  actions: {
    attachToSocketClient() {
      // add batch listener
      SocketClient.addChannelListener("batch", this.handleBatchUpdate);

      // these channels are still listened to because direct messages might happen outside the batch
      SocketClient.addChannelListener("Machine", this.handleMachineUpdate);
      SocketClient.addChannelListener("Component", this.handleComponentUpdate);
      SocketClient.addChannelListener("Skill", this.handleSkillUpdate);
      SocketClient.addChannelListener("Method", this.handleMethodUpdate);
      SocketClient.addChannelListener("Variable", this.handleVariableUpdate);

      // refresh signal
      SocketClient.addChannelListener("refresh", this.handleRefresh);
    },
    handleRefresh() {
      this.refreshMachineData();
    },
    async refreshMachineData() {
      try {
        this.refreshPending = true;
        console.log("requesting machine data...");

        this.machines.clear();

        this.skillEntityMap.clear();
        this.methodEntityMap.clear();
        this.componentEntityMap.clear();
        this.variableEntityMap.clear();

        this.entityToParentMachineMap.clear();

        const result = (await simplyGet("/api/machine/")) as MachineDto[];

        for (const [index, machine] of result.entries()) {
          console.log("Receiving machine " + index + ": " + machine.entityId);
          // this is to prevent double machines being within the result
          if (this.machines.has(machine.entityId)) {
            console.error(
              "Machine with nodeId " + machine.entityId + " already present",
            );
            continue;
          }

          // walk the component tree and map relevant entities within it
          const componentsToProcess = [] as ComponentDto[];
          for (const _component of machine.components) {
            componentsToProcess.push(_component);
          }
          componentsToProcess.push(machine); // dont forget the machine itself <3

          console.log(
            "Mapping out machine entities for machine " + machine.name,
          );
          let count = 0;
          while (componentsToProcess.length > 0) {
            count++;
            if (count > 100_000) {
              throw new Error("Count OVF when processing components.");
            }

            const nextComponent = componentsToProcess.shift();
            if (!nextComponent) {
              break;
            } // just to satisfy the typescript gods

            console.log(" + Component: " + nextComponent?.name);
            this.mapifyComponentEntities(nextComponent, machine);

            for (const _childComponent of nextComponent.components) {
              componentsToProcess.push(_childComponent);
            }
          }

          if (index == 0) {
            // only use the first machine as part of the document title
            document.title = machine.name + " - Module UI";
          }

          // add the pending, as the lock is not using its own store or anything
          machine.lockingModule.isLockPending = false;
          this.machines.set(machine.entityId, machine);
        }

        console.log("machine data received!");

        setTimeout(() => {
          this.refreshPending = false;
        }, 1_000);
      } catch (e) {
        Notify.notify("error", "MachineStore Error: " + (e as Error).message);
        console.error(e);
        this.refreshPending = false;
      }
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
            console.warn("batch containt non-ok entityType in item", item);
        }
      }
    },
    /**
     * Handle a machine update
     * @param machineUpdate Update itself
     */
    handleMachineUpdate(machineUpdate: GenericUpdateMessage) {
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
          Notify.notify(
            msg_message.severity,
            `Machine Message: ${msg_message.severity} ${msg_message.code}: ${msg_message.text}`,
          );
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
    handleComponentUpdate(componentUpdate: GenericUpdateMessage) {
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
          Notify.notify(
            "info",
            `Component Message: ${msg_message.severity} ${msg_message.code}: ${msg_message.text}`,
          );
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
    handleSkillUpdate(skillUpdate: GenericUpdateMessage) {
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
    handleMethodUpdate(methodUpdate: GenericUpdateMessage) {
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
    handleVariableUpdate(variableUpdate: GenericUpdateMessage) {
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
    checkEntityUpdate(update: GenericUpdateMessage): {
      shouldBeHandled: boolean;
      targetEntity: any;
    } {
      const response = {
        shouldBeHandled: false,
        targetEntity: null as any,
      };

      if (this.refreshPending == true) {
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
    async requestLockToggleForMachine(machineEntityId: string) {
      try {
        if (this.machines.has(machineEntityId)) {
          this.machines.get(machineEntityId)!.lockingModule.isLockPending =
            true;
        }

        await simplyGet("/api/machine/lock/" + machineEntityId + "/toggle");
      } catch (e) {
        Notify.notify("error", "MachineStore Error: " + (e as Error).message);
        console.error(e);
      } finally {
        if (this.machines.has(machineEntityId)) {
          this.machines.get(machineEntityId)!.lockingModule.isLockPending =
            false;
        }
      }
    },
    async requestLockBreakForMachine(machineEntityId: string) {
      try {
        if (this.machines.has(machineEntityId)) {
          this.machines.get(machineEntityId)!.lockingModule.isLockPending =
            true;
        }

        await simplyGet("/api/machine/lock/" + machineEntityId + "/break");
      } catch (e) {
        Notify.notify("error", "MachineStore Error: " + (e as Error).message);
        console.error(e);
      }
    },
    async requestSkillAction(action: GenericActionDto) {
      try {
        await simplyPost("/api/server/action", action);
      } catch (e) {
        Notify.notify("error", "MachineStore Error: " + (e as Error).message);
        console.error(e);
      }
    },
    async requestMethodAction(action: GenericActionDto) {
      try {
        await simplyPost("/api/server/action", action);
      } catch (e) {
        Notify.notify("error", "MachineStore Error: " + (e as Error).message);
        console.error(e);
      }
    },
  },
});
