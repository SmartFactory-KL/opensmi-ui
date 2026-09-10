<script lang="ts" setup>
import { onBeforeUnmount, onMounted, ref, useTemplateRef } from "vue";
import PlotBuffer, { PlotData } from "../../../../plotting/PlotBuffer";
import uPlot from "uplot";
import ColorPick from "../../../../util/ColorPick";

const props = defineProps<{
  entityId: string;
  initialValue: any;
  initialTimestamp: number;
}>();

const isPlottable = ref(true);

const plotDiv = useTemplateRef("my-plot");

let plotData: PlotData | null = null;
let plotRender: uPlot | null = null;

onMounted(() => {
  try {
    plotData = PlotBuffer.addPlotForEntity(
      props.entityId,
      props.initialValue,
      props.initialTimestamp
    );
  } catch (e) {
    isPlottable.value = false;
    console.warn("Not plottable:");
    console.warn(plotData, props.initialValue, props.initialTimestamp);
    return;
  }

  const plotDivSize = {
    width: plotDiv.value?.clientWidth || 800,
    height: 0,
  };
  plotDivSize.height = Math.floor(plotDivSize.width / 2.0);

  // the {} empty line is there since otherwise the plot looks weird?
  const seriesInput = [{}] as uPlot.Series[];
  for (let k = 0; k < plotData.plotDimension; k++) {
    seriesInput.push({
      label: plotData.plotSeriesLabels[k] || "value",
      stroke: ColorPick.getIndexedColor(k),
    });
  }

  const plotOptions = {
    width: plotDivSize.width,
    height: plotDivSize.height,
    axes: [
      // first index of the data is always the x axis, in this case: time
      {
        // label: "Time",
      },
      // second index of the data is y axis: value.
      {
        // label: "Value",
      },
    ],
    series: seriesInput,
  } as uPlot.Options;

  plotRender = new uPlot(
    plotOptions,
    plotData.plotContent,
    plotDiv.value as HTMLElement
  );
  PlotBuffer.setPlotRenderForEntity(props.entityId, plotRender);
});

onBeforeUnmount(() => {
  console.log("Plot destroy");
  PlotBuffer.removePlotForEntity(props.entityId);
  plotRender?.destroy();
});
</script>

<template>
  <div class="variable-plot">
    <div
      v-show="!isPlottable"
      class="bg-red-200 border border-red-600 m-2 p-4 text-red-900 flex flex-row justify-start items-center gap-x-2"
    >
      <div>
        <i class="fa-solid fa-circle-exclamation fa-xl"></i>
      </div>
      <div class="text-xs">This value seems to be non-plottable.</div>
    </div>
    <div ref="my-plot"></div>
  </div>
</template>

<style scoped></style>
