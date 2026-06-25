<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { getCharts, getComparison } from '../api/stats';
import EChart from '../components/EChart.vue';
import UserScopeBar from '../components/UserScopeBar.vue';
import { useAuthStore } from '../stores/auth';
import { money, percent } from '../utils/format';

const auth = useAuthStore();
const range = ref('all');
const scopeUserId = ref<number>();
const charts = ref<any>({});
const comparison = ref<any>();

async function load() {
  const params = { range: range.value === 'all' ? undefined : range.value, user_id: scopeUserId.value };
  charts.value = await getCharts(params);
  if ((auth.isViewer || auth.isAdmin) && !scopeUserId.value) comparison.value = await getComparison(params);
}

const scatterOption = computed(() => ({
  tooltip: {
    formatter: (p: any) => `${p.data[3]}<br/>持仓 ${p.data[0].toFixed(1)}h<br/>收益率 ${percent(p.data[1])}<br/>盈亏 ${money(p.data[2])}`,
  },
  grid: { left: 52, right: 24, top: 24, bottom: 42 },
  xAxis: { type: 'value', name: '持仓小时' },
  yAxis: { type: 'value', name: '收益率%' },
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
    name: '账户净值',
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
    name: '月度盈亏',
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
      name: i.direction === 'long' ? '做多' : '做空',
      value: i.pnl,
      itemStyle: { color: i.pnl >= 0 ? '#20c997' : '#ff5d73' },
    })),
  }],
  xAxis: { type: 'category', data: (charts.value.direction_comparison || []).map((i: any) => i.direction === 'long' ? '做多' : '做空') },
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
        { name: '盈利', value: wins },
        { name: '亏损', value: losses },
        { name: '持平', value: flats },
      ],
      color: ['#20c997', '#ff5d73', '#94a3b8'],
    }],
  };
});

const directionSummary = computed(() => (charts.value.direction_comparison || []).map((i: any) => ({
  label: i.direction === 'long' ? '做多' : '做空',
  pnl: i.pnl,
  count: i.count,
  winRate: i.win_rate,
})));

/*
const oldDirectionOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    radius: ['48%', '72%'],
    data: (charts.value.direction_comparison || []).map((i: any) => ({ name: i.direction === 'long' ? '做多' : '做空', value: i.pnl })),
    color: ['#20c997', '#ff5d73'],
  }],
}));
*/

onMounted(load);
watch([range, scopeUserId], load);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">Analytics</span>
        <h1>{{ auth.isViewer && !scopeUserId ? '多用户对比分析' : '交易图表分析' }}</h1>
      </div>
      <el-segmented v-model="range" :options="[
        { label: '今日', value: 'today' }, { label: '本周', value: 'week' }, { label: '本月', value: 'month' },
        { label: '本年', value: 'year' }, { label: '全部', value: 'all' },
      ]" />
    </header>
    <UserScopeBar v-model="scopeUserId" />

    <section v-if="comparison && !scopeUserId" class="comparison-board">
      <div v-for="item in comparison.users" :key="item.user_id" class="user-score-card">
        <span>{{ item.display_name }}</span>
        <strong :class="item.total_pnl >= 0 ? 'positive' : 'negative'">{{ money(item.total_pnl) }}</strong>
        <em>收益率 {{ percent(item.total_return) }} · 胜率 {{ percent(item.win_rate) }}</em>
      </div>
    </section>

    <section class="review-strip">
      <div v-for="item in directionSummary" :key="item.label" class="review-chip">
        <span>{{ item.label }}</span>
        <strong :class="item.pnl >= 0 ? 'positive' : 'negative'">{{ money(item.pnl) }}</strong>
        <em>{{ item.count }} 笔 · 胜率 {{ percent(item.winRate) }}</em>
      </div>
    </section>

    <section class="chart-grid review">
      <el-card class="panel-card wide" header="权益曲线：看账户是否稳定向上"><EChart :option="equityOption" /></el-card>
      <el-card class="panel-card" header="胜负结构"><EChart :option="winLossOption" /></el-card>
      <el-card class="panel-card" header="月度盈亏：看周期表现"><EChart :option="monthOption" /></el-card>
      <el-card class="panel-card" header="币种贡献：看主要利润来源"><EChart :option="rankingOption" /></el-card>
      <el-card class="panel-card" header="多空盈亏：看方向偏差"><EChart :option="directionOption" /></el-card>
      <el-card class="panel-card wide" header="持仓时长 vs 收益率：看交易节奏"><EChart :option="scatterOption" /></el-card>
    </section>
  </div>
</template>
