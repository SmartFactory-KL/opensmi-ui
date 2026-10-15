import { simplyGetToJSON } from "@/fetch/simplyFetch";
import type { SocketMessage } from "@/socket/SocketClient";
import type SocketClient from "@/socket/SocketClient";
import type { ComponentEntityData } from "@/types/EntityTypes";
import type { GenericUpdateMessage } from "@/types/GenericTypes";
import type { ComponentNodeData } from "@/types/NodeFeatureTypes";
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

type ComponentNodeProcessItem = {
  componentNode: ComponentNodeData;
  parent: ComponentNodeData | null;
};

export const useModelStore = defineStore("model", {
  state: (): {
    requestData: {
      isPending: boolean;
      error: string | null;
    };

    isWorking: boolean;

    rootComponents: Map<string, ComponentNodeData>;
    entityIdComponentNodeMap: Map<string, ComponentNodeData>;
  } => {
    return {
      requestData: {
        isPending: false,
        error: null,
      },

      isWorking: false,

      rootComponents: new Map<string, ComponentNodeData>(),
      entityIdComponentNodeMap: new Map<string, ComponentNodeData>(),
    };
  },
  getters: {},
  actions: {
    attachToSocketClient(socketClient: SocketClient) {
      // add batch listener
      //       socketClient.addChannelListener("batch", this.handleBatchUpdate);
      //
      // these channels are still listened to because direct messages might happen outside the batch
      //       socketClient.addChannelListener("Machine", this.handleMachineUpdate);
      //       socketClient.addChannelListener("Component", this.handleComponentUpdate);
      //       socketClient.addChannelListener("Skill", this.handleSkillUpdate);
      //       socketClient.addChannelListener("Method", this.handleMethodUpdate);
      //       socketClient.addChannelListener("Variable", this.handleVariableUpdate);
    },
    async refreshMachineData() {
      if (this.requestData.isPending == true || this.isWorking == true) {
        return;
      }

      this.requestData.isPending = true;
      this.requestData.error = null;
      this.isWorking = true;

      console.log("requesting machine data...");

      this.rootComponents.clear();
      this.entityIdComponentNodeMap.clear();

      try {
        const rootComponentNodes = (await simplyGetToJSON(
          "/api/opc-model/browse",
        )) as ComponentNodeData[];

        if (!Array.isArray(rootComponentNodes)) {
          throw new Error(
            `Expected Model to ba Array, got ${typeof rootComponentNodes} instead`,
          );
        }

        console.log(rootComponentNodes);

        // walk the component tree and map relevant entities within it
        for (const rootComponentNode of rootComponentNodes) {
          const nodesToProcess = [] as ComponentNodeProcessItem[];
          nodesToProcess.push({
            componentNode: rootComponentNode,
            parent: null,
          });

          let count = 0;
          while (nodesToProcess.length > 0) {
            count++;
            if (count > 100_000) {
              throw new Error("Count OVF when processing components.");
            }

            const item = nodesToProcess.shift();
            if (!item || !item.componentNode || !item.componentNode.entity) {
              break;
            } // this only exists to prevent null checks

            const component = item.componentNode;
            const entity = component.entity as ComponentEntityData;

            this.entityIdComponentNodeMap.set(entity.entityId, component);

            for (const feature of component.features) {
              // console.log(feature);
            }

            if (item.parent === null) {
              this.rootComponents.set(entity.entityId, component);
            }

            for (const child of component.children) {
              nodesToProcess.push({
                componentNode: child,
                parent: component,
              });
            }
          }
        }

        console.log(`Received ${this.rootComponents.size} root components`);
        this.isWorking = false;
      } catch (e) {
        console.error(e);
        this.requestData.error = `Failed to request model: ${e}`;
      } finally {
        this.requestData.isPending = false;
        this.isWorking = false;
      }
    },
  },
});
