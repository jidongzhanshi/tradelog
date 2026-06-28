<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { locale, t } from '../i18n';

const zones = [
  ['timezone.beijing', 'Asia/Shanghai', 'CN'],
  ['timezone.newYork', 'America/New_York', 'US'],
  ['timezone.london', 'Europe/London', 'UK'],
  ['timezone.tokyo', 'Asia/Tokyo', 'JP'],
] as const;

const values = ref<{ label: string; flag: string; value: string }[]>([]);
let timer = 0;

function update() {
  values.value = zones.map(([labelKey, timeZone, flag]) => ({
    label: t(labelKey),
    flag,
    value: new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : 'en-GB', {
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
watch(locale, update);
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
