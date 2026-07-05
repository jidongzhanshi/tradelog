<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getCharts, getComparison, getOverview } from '../api/stats';
import MetricCard from '../components/MetricCard.vue';
import TimeZoneStrip from '../components/TimeZoneStrip.vue';
import UserScopeBar from '../components/UserScopeBar.vue';
import EChart from '../components/EChart.vue';
import { rangeOptions, t } from '../i18n';
import { useAuthStore } from '../stores/auth';
import { money, percent, rMultiple } from '../utils/format';
import type { OverviewStats } from '../types';

const route = useRoute();
const auth = useAuthStore();
const range = ref('all');
const scopeUserId = ref<number>();
const overview = ref<OverviewStats>();
const comparison = ref<{ users: OverviewStats[]; combined: OverviewStats }>();
const charts = ref<any>({});

function readRouteScope() {
  const raw = Number(route.query.user_id);
  scopeUserId.value = Number.isFinite(raw) && raw > 0 ? raw : undefined;
}

async function load() {
  const params = { range: range.value === 'all' ? undefined : range.value, user_id: scopeUserId.value };
  comparison.value = undefined;
  if (auth.isAdmin && !scopeUserId.value) {
    comparison.value = await getComparison(params);
    overview.value = comparison.value.combined;
  } else {
    overview.value = await getOverview(params);
  }
  charts.value = await getCharts(params);
}

const pageTitle = computed(() => {
  if (auth.isAdmin && scopeUserId.value && overview.value?.display_name) return t('dashboard.accountTitle', { name: overview.value.display_name });
  if (auth.isAdmin && !scopeUserId.value) return t('dashboard.adminTitle');
  return t('dashboard.title');
});

const equityOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: [t('chart.actualEquity'), t('chart.simulatedEquity')] },
  grid: { left: 48, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'category', data: (charts.value.equity_curve || []).map((p: any) => p.time?.slice(0, 10) || p.time) },
  yAxis: { type: 'value' },
  series: [
    { name: t('chart.actualEquity'), type: 'line', smooth: true, showSymbol: false, data: (charts.value.equity_curve || []).map((p: any) => p.equity), color: '#20c997' },
    { name: t('chart.simulatedEquity'), type: 'line', smooth: true, showSymbol: false, lineStyle: { type: 'dashed' }, data: (charts.value.equity_curve || []).map((p: any) => p.simulated_equity), color: '#6f8cff' },
  ],
}));

const monthOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: [t('chart.actualPnl'), t('chart.simulatedPnl')] },
  grid: { left: 48, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'category', data: (charts.value.monthly_pnl || []).map((p: any) => p.month) },
  yAxis: { type: 'value' },
  series: [
    { name: t('chart.actualPnl'), type: 'bar', data: (charts.value.monthly_pnl || []).map((p: any) => ({ value: p.pnl, itemStyle: { color: p.pnl >= 0 ? '#20c997' : '#ff5d73' } })) },
    { name: t('chart.simulatedPnl'), type: 'bar', data: (charts.value.monthly_pnl || []).map((p: any) => p.simulated_pnl), color: '#6f8cff' },
  ],
}));

onMounted(async () => {
  readRouteScope();
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
        <span class="eyebrow">{{ t('dashboard.eyebrow') }}</span>
        <h1>{{ pageTitle }}</h1>
      </div>
      <el-segmented v-model="range" :options="rangeOptions" />
    </header>

    <TimeZoneStrip />
    <UserScopeBar v-model="scopeUserId" />

    <section v-if="overview" class="metric-grid">
      <MetricCard :label="t('metric.initialCapital')" :value="money(overview.initial_capital)" tone="blue" />
      <MetricCard :label="t('metric.equity')" :value="money(overview.account_equity)" />
      <MetricCard :label="t('metric.simulatedEquity')" :value="money(overview.simulated_equity)" tone="blue" />
      <MetricCard :label="t('metric.pnl')" :value="money(overview.total_pnl)" :tone="overview.total_pnl >= 0 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.return')" :value="percent(overview.total_return)" :tone="overview.total_return >= 0 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.simulatedReturn')" :value="percent(overview.simulated_return)" :tone="overview.simulated_return >= 0 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.winRate')" :value="percent(overview.win_rate)" />
      <MetricCard :label="t('metric.drawdown')" :value="percent(overview.max_drawdown)" tone="red" />
      <MetricCard :label="t('metric.trades')" :value="overview.total_trades" />
      <MetricCard :label="t('metric.totalR')" :value="rMultiple(overview.total_r)" :tone="overview.total_r >= 0 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.averageR')" :value="rMultiple(overview.average_r)" :tone="overview.average_r >= 0 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.averageRisk')" :value="percent(overview.average_risk_percent)" :tone="overview.average_risk_percent <= 2 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.planAdherence')" :value="percent(overview.plan_adherence_rate)" />
      <MetricCard :label="t('metric.deviationCount')" :value="overview.deviation_count" :tone="overview.deviation_count ? 'red' : 'green'" />
      <MetricCard :label="t('metric.overRisk')" :value="overview.over_risk_count" :tone="overview.over_risk_count ? 'red' : 'green'" />
    </section>

    <section v-if="comparison && !scopeUserId" class="compare-grid">
      <div v-for="item in comparison.users" :key="item.user_id" class="compare-card">
        <strong>{{ item.display_name }}</strong>
        <span :class="item.total_pnl >= 0 ? 'positive' : 'negative'">{{ money(item.total_pnl) }}</span>
        <em>{{ t('metric.averageR') }} {{ rMultiple(item.average_r) }} · {{ t('metric.planAdherence') }} {{ percent(item.plan_adherence_rate) }}</em>
      </div>
    </section>

    <section class="chart-grid">
      <el-card class="panel-card" :header="t('dashboard.equityChart')"><EChart :option="equityOption" /></el-card>
      <el-card class="panel-card" :header="t('dashboard.monthChart')"><EChart :option="monthOption" /></el-card>
    </section>
  </div>
</template>
