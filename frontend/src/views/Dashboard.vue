<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { getCharts, getComparison, getOverview } from '../api/stats';
import MetricCard from '../components/MetricCard.vue';
import TimeZoneStrip from '../components/TimeZoneStrip.vue';
import UserScopeBar from '../components/UserScopeBar.vue';
import EChart from '../components/EChart.vue';
import { useAuthStore } from '../stores/auth';
import { money, percent } from '../utils/format';
import type { OverviewStats } from '../types';

const auth = useAuthStore();
const range = ref('all');
const scopeUserId = ref<number>();
const overview = ref<OverviewStats>();
const comparison = ref<{ users: OverviewStats[]; combined: OverviewStats }>();
const charts = ref<any>({});
const ranges = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本年', value: 'year' },
  { label: '全部', value: 'all' },
];

async function load() {
  const params = { range: range.value === 'all' ? undefined : range.value, user_id: scopeUserId.value };
  if ((auth.isViewer || auth.isAdmin) && !scopeUserId.value) {
    comparison.value = await getComparison(params);
    overview.value = comparison.value.combined;
  } else {
    overview.value = await getOverview(params);
  }
  charts.value = await getCharts(params);
}

const equityOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'category', data: (charts.value.equity_curve || []).map((p: any) => p.time?.slice(0, 10) || p.time) },
  yAxis: { type: 'value' },
  series: [{ type: 'line', smooth: true, areaStyle: {}, data: (charts.value.equity_curve || []).map((p: any) => p.equity), color: '#20c997' }],
}));

const monthOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 24, top: 24, bottom: 36 },
  xAxis: { type: 'category', data: (charts.value.monthly_pnl || []).map((p: any) => p.month) },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: (charts.value.monthly_pnl || []).map((p: any) => ({ value: p.pnl, itemStyle: { color: p.pnl >= 0 ? '#20c997' : '#ff5d73' } })) }],
}));

onMounted(load);
watch([range, scopeUserId], load);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">Overview</span>
        <h1>{{ auth.isViewer && !scopeUserId ? '观察者对比总览' : '交易总览' }}</h1>
      </div>
      <el-segmented v-model="range" :options="ranges" />
    </header>

    <TimeZoneStrip />
    <UserScopeBar v-model="scopeUserId" />

    <section v-if="overview" class="metric-grid">
      <MetricCard label="总投入本金" :value="money(overview.initial_capital)" tone="blue" />
      <MetricCard label="当前账户净值" :value="money(overview.account_equity)" />
      <MetricCard label="累计盈亏" :value="money(overview.total_pnl)" :tone="overview.total_pnl >= 0 ? 'green' : 'red'" />
      <MetricCard label="累计收益率" :value="percent(overview.total_return)" :tone="overview.total_return >= 0 ? 'green' : 'red'" />
      <MetricCard label="胜率" :value="percent(overview.win_rate)" />
      <MetricCard label="最大回撤" :value="percent(overview.max_drawdown)" tone="red" />
      <MetricCard label="交易次数" :value="overview.total_trades" />
      <MetricCard label="期望值" :value="money(overview.expectancy)" />
    </section>

    <section v-if="comparison && !scopeUserId" class="compare-grid">
      <div v-for="item in comparison.users" :key="item.user_id" class="compare-card">
        <strong>{{ item.display_name }}</strong>
        <span :class="item.total_pnl >= 0 ? 'positive' : 'negative'">{{ money(item.total_pnl) }}</span>
        <em>胜率 {{ percent(item.win_rate) }} · {{ item.total_trades }} 笔</em>
      </div>
    </section>

    <section class="chart-grid">
      <el-card class="panel-card" header="权益曲线"><EChart :option="equityOption" /></el-card>
      <el-card class="panel-card" header="月度盈亏"><EChart :option="monthOption" /></el-card>
    </section>
  </div>
</template>
