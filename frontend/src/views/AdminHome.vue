<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { getComparison } from '../api/stats';
import { listUsers } from '../api/users';
import MetricCard from '../components/MetricCard.vue';
import TimeZoneStrip from '../components/TimeZoneStrip.vue';
import { rangeOptions, t } from '../i18n';
import { money, percent } from '../utils/format';
import type { AccountOverview, OverviewStats, User } from '../types';

const router = useRouter();
const pageRoot = ref<HTMLElement>();
const range = ref('all');
const loading = ref(false);
const users = ref<User[]>([]);
const comparison = ref<{ users: AccountOverview[]; combined: OverviewStats }>();
let animationContext: ReturnType<typeof gsap.context> | undefined;

const traderUsers = computed(() => users.value.filter((user) => user.role === 'trader'));
const activeTraderCount = computed(() => traderUsers.value.filter((user) => user.is_active).length);
const traderStatus = computed(() => new Map(traderUsers.value.map((user) => [user.id, user.is_active])));

function routeTo(path: string, userId?: number) {
  router.push({ path, query: userId ? { user_id: userId } : {} });
}

async function load() {
  loading.value = true;
  try {
    const params = { range: range.value === 'all' ? undefined : range.value };
    const [userRows, comparisonRows] = await Promise.all([listUsers(), getComparison(params)]);
    users.value = userRows;
    comparison.value = comparisonRows;
    await animateContent();
  } finally {
    loading.value = false;
  }
}

async function animateContent() {
  await nextTick();
  if (!pageRoot.value) return;
  animationContext?.revert();
  animationContext = gsap.context(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const metricCards = gsap.utils.toArray<HTMLElement>('.admin-summary .metric-card', pageRoot.value);
    const accountCards = gsap.utils.toArray<HTMLElement>('.account-command-card', pageRoot.value);
    const staggerAmount = gsap.utils.clamp(0.16, 0.42, metricCards.length * 0.055);
    const timeline = gsap.timeline({
      defaults: { duration: 0.48, ease: 'power3.out' },
    });

    timeline
      .from('.admin-heading > *', { autoAlpha: 0, y: 16, stagger: 0.08 })
      .from('.timezone-strip .time-chip', { autoAlpha: 0, y: 10, stagger: 0.045 }, '-=0.24')
      .from(metricCards, {
        autoAlpha: 0,
        y: 18,
        stagger: { amount: staggerAmount, from: 'start' },
      }, '-=0.26');

    accountCards.forEach((card, index) => {
      gsap.from(card, {
        autoAlpha: 0,
        y: 22,
        duration: 0.52,
        delay: Math.min(index * 0.035, 0.16),
        ease: 'power3.out',
        scrollTrigger: {
          trigger: card,
          start: 'top 94%',
          once: true,
        },
      });
    });
  }, pageRoot.value);
  ScrollTrigger.refresh();
}

onMounted(load);
watch(range, load);
onUnmounted(() => animationContext?.revert());
</script>

<template>
  <div ref="pageRoot" v-loading="loading" class="page-stack admin-page">
    <header class="page-header admin-heading">
      <div>
        <span class="eyebrow">{{ t('admin.eyebrow') }}</span>
        <h1>{{ t('admin.title') }}</h1>
        <p>{{ t('admin.subtitle') }}</p>
      </div>
      <div class="actions">
        <el-segmented v-model="range" :options="rangeOptions" />
        <el-button type="primary" @click="router.push('/users')">{{ t('admin.manageUsers') }}</el-button>
      </div>
    </header>

    <TimeZoneStrip />

    <section v-if="comparison" class="admin-summary">
      <MetricCard :label="t('metric.initialCapital')" :value="money(comparison.combined.initial_capital)" tone="blue" />
      <MetricCard :label="t('metric.equity')" :value="money(comparison.combined.account_equity)" />
      <MetricCard :label="t('metric.pnl')" :value="money(comparison.combined.total_pnl)" :tone="comparison.combined.total_pnl >= 0 ? 'green' : 'red'" />
      <MetricCard :label="t('metric.winRate')" :value="percent(comparison.combined.win_rate)" />
      <MetricCard :label="t('metric.trades')" :value="comparison.combined.total_trades" />
      <MetricCard :label="t('admin.activeAccounts')" :value="`${activeTraderCount}/${traderUsers.length}`" />
    </section>

    <section v-if="comparison" class="account-command-grid">
      <article class="account-command-card combined">
        <div class="account-card-head">
          <div>
            <span>{{ t('common.totalComparison') }}</span>
            <h2>{{ t('admin.combined') }}</h2>
          </div>
          <em>{{ comparison.users.length }} {{ t('common.accounts') }}</em>
        </div>
        <div class="account-balance">
          <small>{{ t('metric.pnl') }}</small>
          <strong :class="comparison.combined.total_pnl >= 0 ? 'positive' : 'negative'">
            {{ money(comparison.combined.total_pnl) }}
          </strong>
        </div>
        <div class="mini-metrics">
          <span>{{ t('metric.return') }} <b>{{ percent(comparison.combined.total_return) }}</b></span>
          <span>{{ t('metric.trades') }} <b>{{ comparison.combined.total_trades }}</b></span>
          <span>{{ t('metric.winRate') }} <b>{{ percent(comparison.combined.win_rate) }}</b></span>
        </div>
        <div class="account-actions">
          <el-button @click="routeTo('/dashboard')">{{ t('admin.openCombined') }}</el-button>
          <el-button @click="routeTo('/analytics')">{{ t('admin.viewAnalytics') }}</el-button>
          <el-button @click="routeTo('/trades')">{{ t('admin.viewTrades') }}</el-button>
        </div>
      </article>

      <article v-for="item in comparison.users" :key="item.user_id" class="account-command-card">
        <div class="account-card-head">
          <div>
            <span>{{ t('role.trader') }}</span>
            <h2>{{ item.display_name }}</h2>
          </div>
          <em class="account-state" :class="{ offline: !traderStatus.get(item.user_id) }">
            <i></i>
            {{ traderStatus.get(item.user_id) ? t('common.enabled') : t('common.disabled') }}
          </em>
        </div>
        <div class="account-balance">
          <small>{{ t('metric.pnl') }}</small>
          <strong :class="item.total_pnl >= 0 ? 'positive' : 'negative'">{{ money(item.total_pnl) }}</strong>
        </div>
        <div class="mini-metrics">
          <span>{{ t('metric.return') }} <b>{{ percent(item.total_return) }}</b></span>
          <span>{{ t('metric.winRate') }} <b>{{ percent(item.win_rate) }}</b></span>
          <span>{{ t('metric.equity') }} <b>{{ money(item.account_equity) }}</b></span>
          <span>{{ t('metric.drawdown') }} <b>{{ percent(item.max_drawdown) }}</b></span>
          <span>{{ t('metric.trades') }} <b>{{ item.total_trades }}</b></span>
        </div>
        <div class="account-actions">
          <el-button @click="routeTo('/dashboard', item.user_id)">{{ t('admin.viewDashboard') }}</el-button>
          <el-button @click="routeTo('/trades', item.user_id)">{{ t('admin.viewTrades') }}</el-button>
          <el-button @click="routeTo('/analytics', item.user_id)">{{ t('admin.viewAnalytics') }}</el-button>
        </div>
      </article>
    </section>

    <el-empty v-if="comparison && !comparison.users.length" :description="t('admin.noTrader')">
      <p class="muted">{{ t('admin.noTraderHint') }}</p>
      <el-button type="primary" @click="router.push('/users')">{{ t('users.add') }}</el-button>
    </el-empty>
  </div>
</template>
