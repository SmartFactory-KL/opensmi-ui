import { simplyGetToText, simplyGetToJSON } from "@/fetch/simplyFetch";
import type SocketClient from "@/socket/SocketClient";
import Toaster from "@/toast/Toaster";
import type { ComponentNode } from "@/types/NodeFeatureTypes";
import { defineStore } from "pinia";

type ComponentNodeProcessItem = {
  componentNode: ComponentNode;
  parent: ComponentNode | null;
};

export const useModelStore = defineStore("model", {
  state: (): {
    requestData: {
      isPending: boolean;
      error: string | null;
    };

    isWorking: boolean;

    rootComponents: Map<string, ComponentNode>;
    entityIdComponentNodeMap: Map<string, ComponentNode>;
  } => {
    return {
      requestData: {
        isPending: false,
        error: null,
      },

      isWorking: false,

      rootComponents: new Map<string, ComponentNode>(),
      entityIdComponentNodeMap: new Map<string, ComponentNode>(),
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
    async loadModel() {
      if (this.requestData.isPending == true || this.isWorking == true) {
        return;
      }

      Toaster.info("Loading Model ...");

      this.requestData.isPending = true;
      this.requestData.error = null;
      this.isWorking = true;

      this.rootComponents.clear();
      this.entityIdComponentNodeMap.clear();

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
              console.warn(
                "skipped incoming data because one of the null checks failed!",
              );
              console.log(item);
              continue;
            } // this only exists to prevent null checks

            const component = item.componentNode;

            this.entityIdComponentNodeMap.set(component.entityId, component);

            for (const feature of component.features) {
              console.log(feature);
            }

            if (item.parent === null) {
              this.rootComponents.set(component.entityId, component);
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
  },
});
