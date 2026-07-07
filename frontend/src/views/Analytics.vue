<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getCharts, getComparison } from '../api/stats';
import { listUsers } from '../api/users';
import EChart from '../components/EChart.vue';
import UserScopeBar from '../components/UserScopeBar.vue';
import { directionLabel, rangeOptions, t } from '../i18n';
import { useAuthStore } from '../stores/auth';
import { money, percent, rMultiple } from '../utils/format';
import type { User } from '../types';

const route = useRoute();
const auth = useAuthStore();
const range = ref('all');
const scopeUserId = ref<number>();
const charts = ref<any>({});
const comparison = ref<any>();
const users = ref<User[]>([]);
const selectedAccountName = computed(() => users.value.find((user) => user.id === scopeUserId.value)?.display_name);

function bucketLabel(bucket: string) {
  const keys = {
    lte_minus_1: 'rBucket.lte_minus_1',
    minus_1_to_0: 'rBucket.minus_1_to_0',
    '0_to_1': 'rBucket.0_to_1',
    '1_to_2': 'rBucket.1_to_2',
    gte_2: 'rBucket.gte_2',
  } as const;
  return t(keys[bucket as keyof typeof keys] || 'rBucket.0_to_1');
}

function deviationLabel(reason: string) {
  const keys = {
    early_take_profit: 'deviation.earlyTakeProfit',
    early_stop: 'deviation.earlyStop',
    delayed_exit: 'deviation.delayedExit',
    missed_stop: 'deviation.missedStop',
    added_position: 'deviation.addedPosition',
    oversized_risk: 'deviation.oversizedRisk',
    emotional_trade: 'deviation.emotionalTrade',
    other: 'deviation.other',
  } as const;
  return t(keys[reason as keyof typeof keys] || 'deviation.other');
}

function planGroupLabel(group: string) {
  return group === 'followed' ? t('planGroup.followed') : t('planGroup.deviated');
}

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
    formatter: (p: any) => `${p.data[3]}<br/>${t('analytics.holdingHours')} ${p.data[0].toFixed(1)}<br/>${t('trades.rMultiple')} ${rMultiple(p.data[1])}<br/>${t('trades.pnl')} ${money(p.data[2])}`,
  },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'value', name: t('analytics.holdingHours') },
  yAxis: { type: 'value', name: t('analytics.rMultiple') },
  series: [{
    type: 'scatter',
    symbolSize: (d: number[]) => Math.max(8, Math.min(28, Math.abs(d[2]) / 20)),
    data: (charts.value.scatter || []).map((item: any) => [
      (item.holding_seconds || 0) / 3600,
      item.r_multiple,
      item.pnl,
      item.symbol,
    ]),
    itemStyle: { color: (p: any) => p.data[2] >= 0 ? '#20c997' : '#ff5d73' },
  }],
}));

const rCurveOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.r_curve || []).map((p: any) => p.time?.slice(0, 10) || p.time) },
  yAxis: { type: 'value', name: 'R' },
  series: [{
    name: t('metric.totalR'),
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: (charts.value.r_curve || []).map((p: any) => p.cumulative_r),
    color: '#6f8cff',
  }],
}));

const rDistributionOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.r_distribution || []).map((p: any) => bucketLabel(p.bucket)) },
  yAxis: { type: 'value', minInterval: 1 },
  series: [{
    type: 'bar',
    barMaxWidth: 42,
    data: (charts.value.r_distribution || []).map((p: any, index: number) => ({
      value: p.count,
      itemStyle: { color: index < 2 ? '#ff5d73' : index === 2 ? '#94a3b8' : '#20c997' },
    })),
  }],
}));

const rollingROption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.rolling_average_r || []).map((p: any) => p.time?.slice(0, 10)) },
  yAxis: { type: 'value', name: 'R' },
  series: [{
    name: t('metric.averageR'),
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: (charts.value.rolling_average_r || []).map((p: any) => p.average_r),
    color: '#20c997',
    markLine: { silent: true, data: [{ yAxis: 0 }], lineStyle: { color: '#64748b' } },
  }],
}));

const equityOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: [t('chart.actualEquity'), t('chart.simulatedEquity')] },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.equity_curve || []).map((p: any) => p.time?.slice(0, 10) || p.time) },
  yAxis: { type: 'value' },
  series: [
    {
      name: t('chart.actualEquity'),
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: (charts.value.equity_curve || []).map((p: any) => p.equity),
      color: '#20c997',
    },
    {
      name: t('chart.simulatedEquity'),
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: { type: 'dashed', width: 2 },
      data: (charts.value.equity_curve || []).map((p: any) => p.simulated_equity),
      color: '#6f8cff',
    },
  ],
}));

const monthOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: [t('chart.actualPnl'), t('chart.simulatedPnl')] },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.monthly_pnl || []).map((p: any) => p.month) },
  yAxis: { type: 'value' },
  series: [
    {
      name: t('chart.actualPnl'),
      type: 'bar',
      barMaxWidth: 32,
      data: (charts.value.monthly_pnl || []).map((p: any) => ({ value: p.pnl, itemStyle: { color: p.pnl >= 0 ? '#20c997' : '#ff5d73' } })),
    },
    {
      name: t('chart.simulatedPnl'),
      type: 'bar',
      barMaxWidth: 32,
      data: (charts.value.monthly_pnl || []).map((p: any) => p.simulated_pnl),
      color: '#6f8cff',
    },
  ],
}));

const riskTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.risk_percent_trend || []).map((p: any) => p.time?.slice(0, 10)) },
  yAxis: { type: 'value', name: '%' },
  series: [{
    name: t('chart.riskPercent'),
    type: 'line',
    smooth: true,
    data: (charts.value.risk_percent_trend || []).map((p: any) => ({
      value: p.risk_percent,
      itemStyle: { color: p.risk_percent > 2 ? '#ff5d73' : '#20c997' },
    })),
    color: '#20c997',
    markLine: { silent: true, data: [{ yAxis: 2 }], lineStyle: { color: '#ffb020', type: 'dashed' } },
  }],
}));

const planComparisonOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'category', data: (charts.value.plan_execution_comparison || []).map((p: any) => planGroupLabel(p.group)) },
  yAxis: { type: 'value', name: 'R' },
  series: [{
    type: 'bar',
    barMaxWidth: 52,
    data: (charts.value.plan_execution_comparison || []).map((p: any) => ({
      value: p.average_r,
      itemStyle: { color: p.group === 'followed' ? '#20c997' : '#ffb020' },
    })),
  }],
}));

const deviationReasonsOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 92, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'value', minInterval: 1 },
  yAxis: { type: 'category', data: (charts.value.deviation_reason_distribution || []).map((p: any) => deviationLabel(p.reason)).reverse() },
  series: [{
    type: 'bar',
    barMaxWidth: 32,
    data: (charts.value.deviation_reason_distribution || []).map((p: any) => p.count).reverse(),
    color: '#ffb020',
  }],
}));

const rankingOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 72, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: (charts.value.symbol_ranking || []).map((i: any) => i.symbol).reverse() },
  series: [{
    type: 'bar',
    data: (charts.value.symbol_ranking || []).map((i: any) => i.total_r).reverse(),
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
      value: i.average_r,
      itemStyle: { color: i.average_r >= 0 ? '#20c997' : '#ff5d73' },
    })),
  }],
  xAxis: { type: 'category', data: (charts.value.direction_comparison || []).map((i: any) => directionLabel(i.direction)) },
  yAxis: { type: 'value' },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
}));

const directionSummary = computed(() => (charts.value.direction_comparison || []).map((i: any) => ({
  label: directionLabel(i.direction),
  pnl: i.pnl,
  averageR: i.average_r,
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
        <em>{{ t('metric.totalR') }} {{ rMultiple(item.total_r) }} · {{ t('metric.winRate') }} {{ percent(item.win_rate) }}</em>
      </div>
    </section>

    <section class="review-strip">
      <div v-for="item in directionSummary" :key="item.label" class="review-chip">
        <span>{{ item.label }}</span>
        <strong :class="item.pnl >= 0 ? 'positive' : 'negative'">{{ money(item.pnl) }}</strong>
        <em>{{ item.count }} {{ t('metric.trades') }} · {{ t('metric.averageR') }} {{ rMultiple(item.averageR) }}</em>
      </div>
    </section>

    <section class="chart-grid review">
      <el-card class="panel-card wide" :header="t('analytics.equity')"><EChart :option="equityOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.rCurve')"><EChart :option="rCurveOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.month')"><EChart :option="monthOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.planComparison')"><EChart :option="planComparisonOption" /></el-card>
      <el-card class="panel-card" :header="t('analytics.riskTrend')"><EChart :option="riskTrendOption" /></el-card>
      <el-card class="panel-card wide" :header="t('analytics.scatter')"><EChart :option="scatterOption" /></el-card>
    </section>
  </div>
</template>
