<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const auth = useAuthStore();
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

async function submit() {
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    ElMessage.success('登录成功');
    router.push('/dashboard');
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <section class="login-hero terminal-hero">
      <div class="market-terminal" aria-hidden="true">
        <div class="terminal-topline">
          <span>TRADELOG / CLOSED POSITIONS</span>
          <em>LIVE JOURNAL</em>
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
      <h1>TradeLog</h1>
      <p>把平仓后的交易变成可复盘的净值曲线、胜率和回撤，而不是散落在截图里的数字。</p>
    </section>

    <el-card class="login-card">
      <h2>登录系统</h2>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" size="large" type="password" show-password @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" class="full-button" @click="submit">
          进入系统
        </el-button>
        <p class="login-note">首次启动默认超级管理员：admin / admin123</p>
      </el-form>
    </el-card>
  </div>
</template>
