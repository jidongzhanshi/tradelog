<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { DataAnalysis, Histogram, List, Moon, Setting, Sunny, SwitchButton, User, Monitor } from '@element-plus/icons-vue';
import en from 'element-plus/es/locale/lang/en';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { useAuthStore } from './stores/auth';
import { locale, localeLabel, roleLabel, t, toggleLocale } from './i18n';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const themeMode = ref(localStorage.getItem('tradelog_theme') || 'dark');
const elementLocale = computed(() => (locale.value === 'zh' ? zhCn : en));

const menu = computed(() => {
  const items = [
    ...(auth.isAdmin ? [{ path: '/admin', label: t('nav.admin'), icon: Monitor }] : []),
    { path: '/dashboard', label: t('nav.dashboard'), icon: Histogram },
    { path: '/trades', label: t('nav.trades'), icon: List },
    { path: '/analytics', label: t('nav.analytics'), icon: DataAnalysis },
    ...(auth.isAdmin ? [{ path: '/users', label: t('nav.users'), icon: User }] : []),
    { path: '/settings', label: t('nav.settings'), icon: Setting },
  ];
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
  <el-config-provider :locale="elementLocale">
    <router-view v-if="route.path === '/login'" />
    <div v-else class="app-frame">
      <aside class="sidebar">
        <div class="logo-block">
          <div class="logo-mark">TL</div>
          <div>
            <strong>{{ t('app.name') }}</strong>
            <span>{{ t('app.subtitle') }}</span>
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
            <span>{{ roleLabel(auth.user?.role) }}</span>
          </div>
          <el-button class="lang-button" text @click="toggleLocale">{{ localeLabel }}</el-button>
          <el-button :icon="themeMode === 'dark' ? Sunny : Moon" circle text @click="toggleTheme" />
          <el-button :icon="SwitchButton" circle text @click="logout" />
        </div>
      </aside>

      <main class="main-panel">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>
