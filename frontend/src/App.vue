<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { DataAnalysis, Fold, Histogram, List, Moon, Setting, Sunny, SwitchButton, User } from '@element-plus/icons-vue';
import { useAuthStore } from './stores/auth';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const themeMode = ref(localStorage.getItem('tradelog_theme') || 'dark');

const menu = computed(() => {
  const items = [
    { path: '/dashboard', label: '总览', icon: Histogram },
    { path: '/trades', label: auth.isViewer ? '交易查看' : '交易记录', icon: List },
    { path: '/analytics', label: auth.isViewer ? '对比分析' : '图表分析', icon: DataAnalysis },
    { path: '/settings', label: '系统设置', icon: Setting },
  ];
  if (auth.isAdmin) items.splice(3, 0, { path: '/users', label: '用户管理', icon: User });
  return items;
});

function logout() {
  auth.logout();
  router.push('/login');
}

function toggleTheme() {
  themeMode.value = themeMode.value === 'dark' ? 'light' : 'dark';
}

watch(themeMode, (value) => {
  document.documentElement.dataset.theme = value;
  localStorage.setItem('tradelog_theme', value);
}, { immediate: true });

onMounted(() => {
  document.documentElement.dataset.theme = themeMode.value;
});
</script>

<template>
  <router-view v-if="route.path === '/login'" />
  <div v-else class="app-frame">
    <aside class="sidebar">
      <div class="logo-block">
        <div class="logo-mark">TL</div>
        <div>
          <strong>TradeLog</strong>
          <span>Private Journal</span>
        </div>
      </div>

      <nav class="nav-list">
        <button
          v-for="item in menu"
          :key="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
          @click="router.push(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="profile-card">
        <div class="profile-avatar">{{ auth.user?.display_name?.slice(0, 1) }}</div>
        <div class="profile-info">
          <strong>{{ auth.user?.display_name }}</strong>
          <span>{{ auth.user?.role }}</span>
        </div>
        <el-button :icon="themeMode === 'dark' ? Sunny : Moon" circle text @click="toggleTheme" />
        <el-button :icon="SwitchButton" circle text @click="logout" />
      </div>
    </aside>

    <main class="main-panel">
      <router-view />
    </main>

    <button class="mobile-menu">
      <el-icon><Fold /></el-icon>
    </button>
  </div>
</template>
