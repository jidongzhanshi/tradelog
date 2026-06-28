<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { use, init, type ECharts } from 'echarts/core';
import { BarChart, LineChart, PieChart, ScatterChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

use([
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer,
]);

const props = defineProps<{ option: any }>();
const el = ref<HTMLDivElement>();
let chart: ECharts | null = null;

function render() {
  if (!el.value) return;
  if (!chart) chart = init(el.value);
  chart.setOption(props.option, true);
}

function resize() {
  chart?.resize();
}

onMounted(() => {
  render();
  window.addEventListener('resize', resize);
});
onUnmounted(() => {
  window.removeEventListener('resize', resize);
  chart?.dispose();
});
watch(() => props.option, render, { deep: true });
</script>

<template>
  <div ref="el" class="chart"></div>
</template>
