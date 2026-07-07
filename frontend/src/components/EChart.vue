<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { use, init, type ECharts } from 'echarts/core';
import { BarChart, LineChart, PieChart, ScatterChart } from 'echarts/charts';
import { GridComponent, LegendComponent, MarkLineComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

use([
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  GridComponent,
  MarkLineComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer,
]);

const props = defineProps<{ option: any }>();
const el = ref<HTMLDivElement>();
let chart: ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

function compactAxisValue(value: unknown) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return String(value ?? '');
  const absolute = Math.abs(value);
  if (absolute >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (absolute >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (absolute >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return `${value}`;
}

function normalizeAxis(axis: any) {
  if (!axis) return axis;
  const axes = Array.isArray(axis) ? axis : [axis];
  const normalized = axes.map((item) => ({
    ...item,
    axisLabel: {
      hideOverlap: true,
      margin: 10,
      ...(item.axisLabel || {}),
      ...(item.type === 'value'
        ? { formatter: item.axisLabel?.formatter || compactAxisValue }
        : {}),
    },
  }));
  return Array.isArray(axis) ? normalized : normalized[0];
}

function normalizeOption(option: any) {
  return {
    ...option,
    grid: Array.isArray(option.grid)
      ? option.grid.map((grid: any) => ({ containLabel: true, ...grid }))
      : { containLabel: true, ...(option.grid || {}) },
    xAxis: normalizeAxis(option.xAxis),
    yAxis: normalizeAxis(option.yAxis),
  };
}

function render() {
  if (!el.value) return;
  if (!chart) chart = init(el.value);
  chart.setOption(normalizeOption(props.option), true);
}

function resize() {
  chart?.resize();
}

onMounted(() => {
  render();
  if (el.value) {
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(el.value);
  }
  window.addEventListener('resize', resize);
});
onUnmounted(() => {
  resizeObserver?.disconnect();
  window.removeEventListener('resize', resize);
  chart?.dispose();
});
watch(() => props.option, render, { deep: true });
</script>

<template>
  <div ref="el" class="chart"></div>
</template>
