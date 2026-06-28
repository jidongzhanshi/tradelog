<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getCharts, getComparison } from '../api/stats';
import { listUsers } from '../api/users';
import EChart from '../components/EChart.vue';
import UserScopeBar from '../components/UserScopeBar.vue';
import { directionLabel, rangeOptions, t, statusLabel } from '../i18n';
import { useAuthStore } from '../stores/auth';
import { money, percent } from '../utils/format';
import type { User } from '../types';

const route = useRoute();
const auth = useAuthStore();
const range = ref('all');
const scopeUserId = ref<number>();
const charts = ref<any>({});
const comparison = ref<any>();
const users = ref<User[]>([]);
const selectedAccountName = computed(() => users.value.find((user) => user.id === scopeUserId.value)?.display_name);

function readRouteScope() {
  const raw = Number(route.query.user_id);
  scopeUserId.value = Number.isFinite(raw) && raw > 0 ? raw : undefined;
}

async function load() {
  const params = { range: range.value === 'all' ? undefined : range.value, user_id: scopeUserId.value };
  charts.value = await getCharts(params);
  comparison.value = auth.isAdmin && !scopeUserId.value ? await getComparison(params) : undefined;
}

const pageTitle = computed(() => {
  if (auth.isAdmin && scopeUserId.value) {
    return t('analytics.accountTitle', { name: selectedAccountName.value || t('role.trader') });
  }
  if (auth.isAdmin && !scopeUserId.value) return t('analytics.adminTitle');
  return t('analytics.title');
});

const scatterOption = computed(() => ({
  tooltip: {
    formatter: (p: any) => `${p.data[3]}<br/>${t('analytics.holdingHours')} ${p.data[0].toFixed(1)}<br/>${t('trades.roi')} ${percent(p.data[1])}<br/>${t('trades.pnl')} ${money(p.data[2])}`,
  },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'value', name: t('analytics.holdingHours') },
  yAxis: { type: 'value', name: t('analytics.roi') },
  series: [{
    type: 'scatter',
    symbolSize: (d: number[]) => Math.max(8, Math.min(28, Math.abs(d[2]) / 20)),
    data: (charts.value.scatter || []).map((item: any) => [
      (item.holding_seconds || 0) / 3600,
      item.roi,
      item.pnl,
      item.symbol,
    ]),
    itemStyle: { color: (p: any) => p.data[2] >= 0 ? '#20c997' : '#ff5d73' },
  }],
}));

const equityOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.equity_curve || []).map((p: any) => p.time?.slice(0, 10) || p.time) },
  yAxis: { type: 'value' },
  series: [{
    name: t('chart.accountEquity'),
    type: 'line',
    smooth: true,
    showSymbol: false,
    areaStyle: { opacity: 0.16 },
    data: (charts.value.equity_curve || []).map((p: any) => p.equity),
    color: '#20c997',
  }],
}));

const monthOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.monthly_pnl || []).map((p: any) => p.month) },
  yAxis: { type: 'value' },
  series: [{
    name: t('chart.monthlyPnl'),
    type: 'bar',
    barMaxWidth: 38,
    data: (charts.value.monthly_pnl || []).map((p: any) => ({ value: p.pnl, itemStyle: { color: p.pnl >= 0 ? '#20c997' : '#ff5d73' } })),
  }],
}));

const rankingOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 72, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: (charts.value.symbol_ranking || []).map((i: any) => i.symbol).reverse() },
  series: [{
    type: 'bar',
    data: (charts.value.symbol_ranking || []).map((i: any) => i.pnl).reverse(),
    itemStyle: { color: (p: any) => p.value >= 0 ? '#20c997' : '#ff5d73' },
  }],
}));

const directionOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'bar',
    barMaxWidth: 42,
    data: (charts.value.direction_comparison || []).map((i: any) => ({
      name: directionLabel(i.direction),
      value: i.pnl,
      itemStyle: { color: i.pnl >= 0 ? '#20c997' : '#ff5d73' },
    })),
  }],
  xAxis: { type: 'category', data: (charts.value.direction_comparison || []).map((i: any) => directionLabel(i.direction)) },
  yAxis: { type: 'value' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
}));

const winLossOption = computed(() => {
  const points = charts.value.scatter || [];
  const wins = points.filter((item: any) => item.pnl > 0).length;
  const losses = points.filter((item: any) => item.pnl < 0).length;
  const flats = points.length - wins - losses;
  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['56%', '78%'],
      data: [
        { name: statusLabel('profit'), value: wins },
        { name: statusLabel('loss'), value: losses },
        { name: statusLabel('flat'), value: flats },
      ],
      color: ['#20c997', '#ff5d73', '#94a3b8'],
    }],
  };
});

const directionSummary = computed(() => (charts.value.direction_comparison || []).map((i: any) => ({
  label: directionLabel(i.direction),
  pnl: i.pnl,
  count: i.count,
  winRate: i.win_rate,
})));

onMounted(async () => {
  readRouteScope();
  if (auth.isAdmin) users.value = await listUsers();
  await load();
});
watch([range, scopeUserId], load);
watch(() => route.query.user_id, async () => {
  readRouteScope();
  await load();
});
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">{{ t('analytics.eyebrow') }}</span>
        <h1>{{ pageTitle }}</h1>
      </div>
      <el-segmented v-model="range" :options="rangeOptions" />
    </header>
    <UserScopeBar v-model="scopeUserId" />

    <section v-if="comparison && !scopeUserId" class="comparison-board">
      <div v-for="item in comparison.users" :key="item.user_id" class="user-score-card">
        <span>{{ item.display_name }}</span>
        <strong :class="item.total_pnl >= 0 ? 'positive' : 'negative'">{{ money(item.total_pnl) }}</strong>
        <em>{{ t('metric.return') }} {{ percent(item.total_return) }} · {{ t('metric.winRate') }} {{ percent(item.win_rate) }}</em>
      </div>
    </section>

    <section class="review-strip">
      <div v-for="item in directionSummary" :key="item.label" class="review-chip">
        <span>{{ item.label }}</span>
        <strong :class="item.pnl >= 0 ? 'positive' : 'negative'">{{ money(item.pnl) }}</strong>
        <em>{{ item.count }} {{ t('metric.trades') }} · {{ t('metric.winRate') }} {{ percent(item.winRate) }}</em>
      </div>
    </section>

    <section class="chart-grid review">
      <el-card class="panel-card wide" :header="t('analytics.equity')"><EChart :option="equityOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.winLoss')"><EChart :option="winLossOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.month')"><EChart :option="monthOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.symbol')"><EChart :option="rankingOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.direction')"><EChart :option="directionOption" /></el-card>
      <el-card class="panel-card wide" :header="t('analytics.scatter')"><EChart :option="scatterOption" /></el-card>
    </section>
  </div>
</template>
