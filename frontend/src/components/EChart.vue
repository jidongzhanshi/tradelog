<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{ option: any }>();
const el = ref<HTMLDivElement>();
let chart: echarts.ECharts | null = null;

function render() {
  if (!el.value) return;
  if (!chart) chart = echarts.init(el.value);
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
