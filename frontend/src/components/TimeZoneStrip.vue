<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

const zones = [
  ['北京时间', 'Asia/Shanghai', ''],
  ['纽约时间', 'America/New_York', '🇺🇸'],
  ['伦敦时间', 'Europe/London', '🇬🇧'],
  ['东京时间', 'Asia/Tokyo', '🇯🇵'],
];

const values = ref<{ label: string; flag: string; value: string }[]>([]);
let timer = 0;

function update() {
  values.value = zones.map(([label, timeZone, flag]) => ({
    label,
    flag,
    value: new Intl.DateTimeFormat('zh-CN', {
      timeZone,
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).format(new Date()),
  }));
}

onMounted(() => {
  update();
  timer = window.setInterval(update, 1000);
});
onUnmounted(() => window.clearInterval(timer));
</script>

<template>
  <div class="timezone-strip">
    <div v-for="item in values" :key="item.label" class="time-chip">
      <span>{{ item.flag }}</span>
      <em>{{ item.label }}</em>
      <strong>{{ item.value }}</strong>
    </div>
  </div>
</template>
