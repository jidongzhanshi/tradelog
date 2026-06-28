<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { gsap } from 'gsap';
import { useAuthStore } from '../stores/auth';
import { localeLabel, t, toggleLocale } from '../i18n';

const router = useRouter();
const auth = useAuthStore();
const pageRoot = ref<HTMLElement>();
const loading = ref(false);
const form = reactive({ username: 'admin', password: 'admin123' });
const coins = [
  { symbol: 'BTC', glyph: '₿', tone: 'gold' },
  { symbol: 'ETH', glyph: 'Ξ', tone: 'violet' },
  { symbol: 'SOL', glyph: 'S', tone: 'mint' },
  { symbol: 'BNB', glyph: '◆', tone: 'amber' },
  { symbol: 'XRP', glyph: 'X', tone: 'steel' },
];
const candles = Array.from({ length: 34 }, (_, index) => ({
  height: 28 + ((index * 17) % 86),
  wick: 46 + ((index * 23) % 120),
  up: index % 4 !== 1,
}));
let motion: ReturnType<typeof gsap.matchMedia> | undefined;

async function submit() {
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    ElMessage.success(t('login.success'));
    router.push(auth.isAdmin ? '/admin' : '/dashboard');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (!pageRoot.value) return;
  const loginCard = gsap.utils.toArray<HTMLElement>('.login-card', pageRoot.value);
  gsap.set(loginCard, { clearProps: 'opacity,visibility,transform' });
  motion = gsap.matchMedia();
  motion.add(
    {
      animate: '(prefers-reduced-motion: no-preference)',
      compact: '(max-width: 760px)',
    },
    (context) => {
      if (!context.conditions?.animate || !pageRoot.value) return;
      const q = gsap.utils.selector(pageRoot.value);
      const candles = gsap.utils.toArray<HTMLElement>('.candle', pageRoot.value);
      const timeline = gsap.timeline({
        defaults: { duration: 0.55, ease: 'power3.out' },
      });

      gsap.set(loginCard, {
        x: context.conditions.compact ? 0 : 28,
        y: context.conditions.compact ? 18 : 0,
      });
      gsap.set(q('.signal-line path'), { strokeDasharray: 720, strokeDashoffset: 720 });
      timeline
        .to(loginCard, {
          x: 0,
          y: 0,
          duration: 0.48,
          clearProps: 'transform',
        }, 0.08)
        .from(q('.market-terminal'), { autoAlpha: 0, y: context.conditions.compact ? 14 : 24, scale: 0.985 })
        .from(q('.terminal-topline > *'), { autoAlpha: 0, y: 8, stagger: 0.08 }, '-=0.25')
        .from(q('.coin-chip'), { autoAlpha: 0, y: 10, stagger: 0.055 }, '-=0.3')
        .from(candles, {
          autoAlpha: 0,
          scaleY: 0.08,
          transformOrigin: '50% 100%',
          duration: 0.42,
          stagger: { amount: 0.48, from: 'start' },
        }, '-=0.3')
        .to(q('.signal-line path'), { strokeDashoffset: 0, duration: 1.1, ease: 'power2.inOut' }, '-=0.45')
        .from(q('.terminal-stats span'), { autoAlpha: 0, y: 10, stagger: 0.08 }, '-=0.5')
        .from(q('.login-hero-copy > *'), { autoAlpha: 0, y: 18, stagger: 0.08 }, '-=0.42');
    },
    pageRoot.value,
  );
});

onUnmounted(() => motion?.revert());
</script>

<template>
  <div ref="pageRoot" class="login-page">
    <button class="login-language" type="button" @click="toggleLocale">
      {{ localeLabel }}
    </button>
    <section class="login-hero terminal-hero">
      <div class="market-terminal" aria-hidden="true">
        <div class="terminal-topline">
          <span>TRADELOG / {{ t('login.closedPositions').toUpperCase() }}</span>
          <em>{{ t('login.privateJournal').toUpperCase() }}</em>
        </div>
        <div class="coin-row">
          <div v-for="coin in coins" :key="coin.symbol" class="coin-chip" :class="coin.tone">
            <strong>{{ coin.glyph }}</strong>
            <span>{{ coin.symbol }}</span>
          </div>
        </div>
        <div class="kline-board">
          <div class="price-grid"></div>
          <div class="candle-track">
            <span
              v-for="(item, index) in candles"
              :key="index"
              class="candle"
              :class="{ up: item.up, down: !item.up }"
              :style="{ '--body': `${item.height}px`, '--wick': `${item.wick}px`, '--delay': `${index * 42}ms` }"
            ></span>
          </div>
          <svg class="signal-line" viewBox="0 0 640 180" preserveAspectRatio="none">
            <path d="M0 120 C80 64 114 148 178 100 C244 52 292 78 344 66 C430 46 450 138 526 92 C576 62 604 70 640 44" />
          </svg>
        </div>
        <div class="terminal-stats">
          <span><em>Win rate</em><strong>68.4%</strong></span>
          <span><em>Drawdown</em><strong>-7.9%</strong></span>
          <span><em>Equity</em><strong>+24.6%</strong></span>
        </div>
      </div>
      <div class="login-hero-copy">
        <h1>TradeLog</h1>
        <p>{{ t('login.hero') }}</p>
      </div>
    </section>

    <el-card class="login-card">
      <h2>{{ t('login.title') }}</h2>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item :label="t('common.username')">
          <el-input v-model="form.username" size="large" />
        </el-form-item>
        <el-form-item :label="t('common.password')">
          <el-input v-model="form.password" size="large" type="password" show-password @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" class="full-button" @click="submit">
          {{ t('login.enter') }}
        </el-button>
        <p class="login-note">{{ t('login.defaultAccount') }}</p>
      </el-form>
    </el-card>
  </div>
</template>
