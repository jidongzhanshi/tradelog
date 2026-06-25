<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  sub?: string;
  tone?: 'green' | 'red' | 'blue' | 'neutral';
}>();
</script>

<template>
  <div class="metric-card" :class="tone">
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
    <small v-if="sub">{{ sub }}</small>
  </div>
</template>
