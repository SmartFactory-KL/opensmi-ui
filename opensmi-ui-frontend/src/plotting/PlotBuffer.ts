// import type { ModelUpdateMessage } from "@/stores/ModelStore";
// import type { DataValueData, VariantData } from "@/types/OPCTypes";
// import type { VariableValueUpdate } from "@/types/UpdateTypes";
// import type uPlot from "uplot";
//
// export type PlotType = "NumberPlot" | "ArrayPlot" | "ObjectPlot";
//
// export type PlotData = {
//   targetEntityId: string;
//   targetPlotReference: uPlot | null;
//   plotContent: Float64Array[];
//   plotDimension: number;
//   plotSeriesLabels: string[];
//   plotType: PlotType;
//   plotHistoryPending: boolean;
// };
//
// const MAX_PLOT_POINT_COUNT = 100;
//
// class PlotBuffer {
//   private plotMap: Map<string, PlotData>;
//
//   constructor() {
//     this.plotMap = new Map();
//   }
//
//   addPlotForEntity(
//     entityId: string,
//     initialValue: any,
//     initialTimestamp: number,
//   ): PlotData {
//     // first check the initial value for plotablility
//     // find out plotting series count:
//     let valueList = [] as number[];
//     let parsedValue = initialValue;
//     let plotSeriesLabels = [] as string[];
//     let plotType = "NumberPlot" as PlotType;
//
//     try {
//       if (typeof parsedValue === "string") {
//         parsedValue = JSON.parse(parsedValue);
//       }
//
//       if (Array.isArray(parsedValue)) {
//         valueList = parsedValue.map((el) => Number(el));
//         plotSeriesLabels = parsedValue.map((_, idx) => "#" + idx);
//         plotType = "ArrayPlot";
//       } else if (Number.isFinite(parsedValue)) {
//         valueList = [parsedValue];
//         plotSeriesLabels = ["Value"];
//         plotType = "NumberPlot";
//       } else if (
//         // that is pure js beauty <3
//         Object.prototype.toString.call(parsedValue) === "[object Object]"
//       ) {
//         valueList = Object.values(parsedValue).map((el) => Number(el));
//         plotSeriesLabels = Object.keys(parsedValue).map((el) => el.toString());
//         plotType = "ObjectPlot";
//       } else {
//         throw new Error(
//           "Type of value is non-plottable: " + typeof parsedValue,
//         );
//       }
//     } catch (e) {
//       console.error("Error while parsing for plot: ");
//       console.error((e as Error).message);
//
//       throw e;
//     }
//
//     // create the buffer for the plot
//     if (this.plotMap.has(entityId)) {
//       this.plotMap.delete(entityId);
//     }
//
//     const plotFloatData = new Array(valueList.length + 1) as Float64Array[];
//     plotFloatData[0] = new Float64Array(1);
//     plotFloatData[0][0] = initialTimestamp * 1000.0;
//     for (let k = 0; k < valueList.length; k++) {
//       plotFloatData[k + 1] = new Float64Array(1);
//       plotFloatData[k + 1][0] = valueList[k];
//     }
//
//     const newPlotData = {
//       targetEntityId: entityId,
//       plotContent: plotFloatData,
//       plotDimension: valueList.length,
//       plotSeriesLabels: plotSeriesLabels,
//       plotType: plotType,
//       targetPlotReference: null,
//       plotHistoryPending: true,
//     } as PlotData;
//
//     // this.addHistoryToPlot(newPlotData);
//
//     this.plotMap.set(entityId, newPlotData);
//
//     return newPlotData;
//   }
//
// //   async addHistoryToPlot(plotData: PlotData) {
// //     plotData.plotHistoryPending = true;
// //     try {
// //       const dataValueList = await simplyGet(
// //         "/api/server/node-history/" + plotData.targetEntityId,
// //       );
// //
// //       const bigValueList = [];
// //
// //       for (const dataValueItem of dataValueList) {
// //         bigValueList.push(
// //           this.createValueListFromDataValue(dataValueItem, plotData),
// //         );
// //       }
// //
// //       if (bigValueList.length == 0) {
// //         plotData.plotHistoryPending = false;
// //         return;
// //       }
// //
// //       const outputFloatArrays = new Array(
// //         plotData.plotDimension + 1,
// //       ) as Float64Array[];
// //
// //       // +1 for time
// //       for (let k = 0; k < plotData.plotDimension + 1; k++) {
// //         outputFloatArrays[k] = new Float64Array(bigValueList.length);
// //       }
// //
// //       for (let k = 0; k < bigValueList.length; k++) {
// //         for (let l = 0; l < plotData.plotDimension + 1; l++) {
// //           outputFloatArrays[l][k] = bigValueList[k][l];
// //         }
// //       }
// //
// //       plotData.plotContent = outputFloatArrays;
// //       plotData.targetPlotReference!.setData(plotData.plotContent);
// //     } catch (e) {
// //       console.log(
// //         "Error while collection history data for entityId " +
// //           plotData.targetEntityId,
// //       );
// //       console.log(e);
// //     } finally {
// //       plotData.plotHistoryPending = false;
// //     }
// //   }
//
//   createValueListFromDataValue(input: VariantData, plotData: PlotData) {
//     let valueList = [];
//
//     // Why add ms? -> Native timestamps in JS are in milliseconds
//     // but uPlot is expecting seconds and ms are added after decimal point.
//     // Issue regarding that: https://github.com/leeoniya/uPlot/issues/60
//     // what bewilders me: Why is getTime() returning seconds here? - turns out, it checks input length
//     // 10 digits -> seconds, 13 digits -> ms for getTime. Wild.
//     const msAddition = Math.abs(input.timestamp - Math.floor(input.timestamp));
//     const timestampValue =
//       new Date(this.secondizeTimestamp(input.timestamp)).getTime() + msAddition;
//
//     valueList.push(timestampValue);
//
//     switch (plotData.plotType) {
//       case "NumberPlot":
//         valueList = valueList.concat([Number(input.value.value)]);
//         break;
//       case "ArrayPlot":
//         if (!Array.isArray(input.value.value)) {
//           try {
//             valueList = valueList.concat(JSON.parse(input.value.value));
//           } catch (e) {
//             valueList = valueList.concat(
//               new Array(plotData.plotDimension).fill(0.0),
//             );
//           }
//         } else {
//           valueList = valueList.concat(input.value.value);
//         }
//         break;
//       case "ObjectPlot":
//         if (
//           Object.prototype.toString.call(input.value.value) ===
//           "[object Object]"
//         ) {
//           valueList = valueList.concat(
//             Object.values(input.value.value).map((el) => Number(el)),
//           );
//         } else {
//           try {
//             const obj = JSON.parse(input.value.value);
//             valueList = valueList.concat(
//               Object.values(obj).map((el) => Number(el)),
//             );
//           } catch (e) {
//             valueList = valueList.concat(
//               new Array(plotData.plotDimension).fill(0.0),
//             );
//           }
//         }
//         break;
//       default:
//         console.warn("invalid plotType. ignored.");
//         return [];
//     }
//
//     return valueList;
//   }
//
//   removePlotForEntity(entityId: string) {
//     this.plotMap.delete(entityId);
//   }
//
//   setPlotRenderForEntity(entityId: string, uPlotReference: uPlot) {
//     const target = this.plotMap.get(entityId);
//
//     if (target) {
//       target.targetPlotReference = uPlotReference;
//       target.targetPlotReference.setData(target.plotContent);
//     }
//   }
//
//   /**
//    * Checks if a timestamp is in milliseconds or seconds. returns a timestamp in seconds.
//    * @param ts timestamp to check
//    */
//   secondizeTimestamp(ts: number): number {
//     return ts <= 9_999_999_999 ? ts : Math.floor(ts / 1000.0);
//   }
//
//   handleVariableUpdate(update: ModelUpdateMessage) {
//     if (!update || !update.updateType) {
//       return;
//     }
//
//     if (!this.plotMap.has(update.entityId)) {
//       return;
//     }
//
//     // ignore updates while history is being processed.
//     // might loose some values here though.
//     if (this.plotMap.get(update.entityId)?.plotHistoryPending === true) {
//       return;
//     }
//
//     switch (update.updateType) {
//       case "VariableValueUpdate":
//         const updContent = update.updateContent as VariableValueUpdate;
//         const plotTarget = this.plotMap.get(update.entityId)!;
//
//         // convert incoming value according to plotType
//         const valueList = this.createValueListFromDataValue(
//           updContent.newValue,
//           plotTarget,
//         );
//
//         // use time array for determining size, as that should always be present
//         const startIndex =
//           plotTarget.plotContent[0].length > MAX_PLOT_POINT_COUNT
//             ? plotTarget.plotContent[0].length - MAX_PLOT_POINT_COUNT
//             : 0;
//
//         // the plot dimension only contains the values. add one to account for the time
//         const newPlotData = new Array(
//           plotTarget.plotDimension + 1,
//         ) as Float64Array[];
//
//         for (let k = 0; k < newPlotData.length; k++) {
//           newPlotData[k] = new Float64Array(
//             plotTarget.plotContent[0].length + 1 - startIndex,
//           );
//         }
//
//         // shift old data one to the left
//         for (let k = startIndex; k < newPlotData[0].length; k++) {
//           for (let l = 0; l < newPlotData.length; l++) {
//             newPlotData[l][k - startIndex] = plotTarget.plotContent[l][k];
//           }
//         }
//
//         // add the new values
//         for (let k = 0; k < plotTarget.plotDimension + 1; k++) {
//           newPlotData[k][newPlotData[0].length - 1] = valueList[k];
//         }
//         plotTarget.plotContent = newPlotData;
//
//         if (plotTarget.targetPlotReference) {
//           plotTarget.targetPlotReference.setData(plotTarget.plotContent, true);
//         }
//
//         break;
//       default:
//         // just ignore it, no logging here
//         break;
//     }
//   }
// }
//
// export default new PlotBuffer();
