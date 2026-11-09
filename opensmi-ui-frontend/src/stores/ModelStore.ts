import { simplyGetToText, simplyGetToJSON } from "@/fetch/simplyFetch";
import PlotBuffer from "@/plotting/PlotBuffer";
import type SocketClient from "@/socket/SocketClient";
import Toaster from "@/toast/Toaster";
import type {
  LockEntityData,
  MachineryItemStateEntityData,
  SkillControlEntityData,
  VariableEntityData,
} from "@/types/EntityTypes";
import type { ComponentNode, FeatureNode } from "@/types/NodeFeatureTypes";
import type {
  LockIsLockedUpdate,
  LockLockingClientUpdate,
  LockLockingUserUpdate,
  MachineryItemStateStateUpdate,
  SkillControlStateUpdate,
  VariableValueUpdate,
} from "@/types/UpdateTypes";
import { defineStore } from "pinia";

type ComponentNodeProcessItem = {
  componentNode: ComponentNode;
  parent: ComponentNode | null;
};

export interface ModelUpdateMessage {
  entityId: string;
  updateType: string;
  updateContent: any;
}

export const useModelStore = defineStore("model", {
  state: (): {
    requestData: {
      isPending: boolean;
      error: string | null;
    };

    isWorking: boolean;

    isDropdownVisible: boolean;
    currentMachine: ComponentNode | null;

    rootComponents: Map<string, ComponentNode>;
    entityIdComponentNodeMap: Map<string, ComponentNode>;
    entityIdFeatureNodeMap: Map<string, FeatureNode>;
  } => {
    return {
      requestData: {
        isPending: false,
        error: null,
      },

      isWorking: false,

      isDropdownVisible: false,
      currentMachine: null,

      rootComponents: new Map<string, ComponentNode>(),
      entityIdComponentNodeMap: new Map<string, ComponentNode>(),
      entityIdFeatureNodeMap: new Map<string, FeatureNode>(),
    };
  },
  getters: {},
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      socketClient.addChannelListener("Model", this.handleModelUpdate);
    },
    showDropdown() {
      this.isDropdownVisible = true;
    },
    toggleDropdown() {
      this.isDropdownVisible = !this.isDropdownVisible;
    },
    closeDropdown() {
      this.isDropdownVisible = false;
    },
    async requestBrowsing() {
      if (this.requestData.isPending == true || this.isWorking == true) {
        return;
      }

      Toaster.info("Loading Model ...");

      this.requestData.isPending = true;
      this.requestData.error = null;
      this.isWorking = true;

      try {
        await simplyGetToText("/api/opc-model/browse");

        Toaster.success(`Browsing successful!`);

        this.isWorking = false;
      } catch (e) {
        console.error(e);
        this.requestData.error = `Failed to browse: ${e}`;
        Toaster.error(this.requestData.error);
      } finally {
        this.requestData.isPending = false;
        this.isWorking = false;
      }
    },
    wipeModel() {
      this.currentMachine = null;

      this.rootComponents.clear();
      this.entityIdComponentNodeMap.clear();
      this.entityIdFeatureNodeMap.clear();
    },
    async loadModel() {
      if (this.requestData.isPending == true || this.isWorking == true) {
        return;
      }

      Toaster.info("Loading Model ...");

      this.requestData.isPending = true;
      this.requestData.error = null;
      this.isWorking = true;

      this.wipeModel();

      try {
        const rootComponentNodes = (await simplyGetToJSON(
          "/api/opc-model/",
        )) as ComponentNode[];

        if (!Array.isArray(rootComponentNodes)) {
          throw new Error(
            `Expected Model to ba Array, got ${typeof rootComponentNodes} instead`,
          );
        }

        // walk the component tree and map relevant entities within it
        for (const rootComponentNode of rootComponentNodes) {
          const componentsToProcess = [] as ComponentNodeProcessItem[];
          componentsToProcess.push({
            componentNode: rootComponentNode,
            parent: null,
          });

          let count = 0;
          while (componentsToProcess.length > 0) {
            count++;
            if (count > 100_000) {
              throw new Error("Count OVF when processing components.");
            }

            const componentItem = componentsToProcess.shift();
            if (
              !componentItem ||
              !componentItem.componentNode ||
              !componentItem.componentNode.entity
            ) {
              console.warn(
                "skipped incoming data because one of the null checks failed!",
              );
              console.log(componentItem);
              continue;
            } // this only exists to prevent null checks

            const component = componentItem.componentNode;

            this.entityIdComponentNodeMap.set(component.entityId, component);

            const featuresToProcess = [] as FeatureNode[];

            for (const feature of component.features) {
              featuresToProcess.push(feature);
            }

            let featureCount = 0;
            while (featuresToProcess.length > 0) {
              if (featureCount > 10_000) {
                console.warn("Feature Count Overflow");
                break;
              }
              featureCount++;

              const featureItem = featuresToProcess.shift();

              if (!featureItem) {
                continue;
              }

              this.entityIdFeatureNodeMap.set(
                featureItem.entityId,
                featureItem,
              );

              for (const childFeature of featureItem.features) {
                featuresToProcess.push(childFeature);
              }
            }

            if (componentItem.parent === null) {
              this.rootComponents.set(component.entityId, component);
            }

            for (const child of component.children) {
              componentsToProcess.push({
                componentNode: child,
                parent: component,
              });
            }
          }
        }

        if (this.rootComponents.size > 0) {
          for (const firstMachine of this.rootComponents.values()) {
            this.currentMachine = firstMachine;
            break;
          }
        }

        console.log(`Received ${this.rootComponents.size} root components`);
        Toaster.success(`Received ${this.rootComponents.size} root components`);
        this.isWorking = false;
      } catch (e) {
        console.error(e);
        this.requestData.error = `Failed to request model: ${e}`;
        Toaster.error(this.requestData.error);
      } finally {
        this.requestData.isPending = false;
        this.isWorking = false;
      }
    },
    getFeatureForEntity(entityId: string): FeatureNode | null {
      if (this.entityIdFeatureNodeMap.has(entityId)) {
        const feature = this.entityIdFeatureNodeMap.get(entityId)!;
        return feature;
      }

      return null;
    },
    handleModelUpdate(update: ModelUpdateMessage) {
      const targetFeature = this.getFeatureForEntity(update.entityId);

      if (targetFeature === null) {
        return;
      }

      switch (update.updateType) {
        case "VariableValueUpdate":
          {
            const typedUpdate = update.updateContent as VariableValueUpdate;
            const typedEntity = targetFeature.entity as VariableEntityData;
            typedEntity.value = typedUpdate.newValue;

            // PlotBuffer.handleVariableUpdate(update)
          }
          break;

        case "LockIsLockedUpdate":
          {
            const typedUpdate = update.updateContent as LockIsLockedUpdate;
            const typedEntity = targetFeature.entity as LockEntityData;

            typedEntity.isLocked = typedUpdate.newIsLocked;
            typedEntity.isLockedLastChange = typedUpdate.timestamp;
          }
          break;

        case "LockLockingUserUpdate":
          {
            const typedUpdate = update.updateContent as LockLockingUserUpdate;
            const typedEntity = targetFeature.entity as LockEntityData;

            typedEntity.lockingUser = typedUpdate.newUser;
            typedEntity.lockingUserLastChange = typedUpdate.timestamp;
          }
          break;

        case "LockLockingClientUpdate":
          {
            const typedUpdate = update.updateContent as LockLockingClientUpdate;
            const typedEntity = targetFeature.entity as LockEntityData;

            typedEntity.lockingClient = typedUpdate.newClient;
            typedEntity.lockingClientLastChange = typedUpdate.timestamp;
          }
          break;
        case "SkillControlStateUpdate":
          {
            const typedUpdate = update.updateContent as SkillControlStateUpdate;
            const typedEntity = targetFeature.entity as SkillControlEntityData;

            typedEntity.currentState = typedUpdate.newState;
            typedEntity.currentStateLastChange = typedUpdate.timestamp;
          }
          break;
        case "MachineryItemStateStateUpdate":
          {
            const typedUpdate =
              update.updateContent as MachineryItemStateStateUpdate;
            const typedEntity =
              targetFeature.entity as MachineryItemStateEntityData;

            typedEntity.currentState = typedUpdate.newState;
          }
          break;
        default:
          console.warn("unknown updateType", update.updateType);
          break;
      }
    },
  },
});
