<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { gsap } from 'gsap';
import { DataAnalysis, Histogram, List, Moon, Setting, Sunny, SwitchButton, User, Monitor } from '@element-plus/icons-vue';
import en from 'element-plus/es/locale/lang/en';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { useAuthStore } from './stores/auth';
import { locale, localeLabel, roleLabel, t, toggleLocale } from './i18n';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const themeMode = ref(localStorage.getItem('tradelog_theme') || 'dark');
const sidebarCollapsed = ref(localStorage.getItem('tradelog_sidebar_collapsed') === '1');
const sidebarRef = ref<HTMLElement>();
const mainRef = ref<HTMLElement>();
const elementLocale = computed(() => (locale.value === 'zh' ? zhCn : en));
const reduceMotion = computed(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);

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

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}

function animateShell() {
  if (!sidebarRef.value || reduceMotion.value) return;
  const logo = sidebarRef.value.querySelector('.logo-block');
  const navItems = sidebarRef.value.querySelectorAll('.nav-item');
  const profile = sidebarRef.value.querySelector('.sidebar-tools');
  const timeline = gsap.timeline({ defaults: { ease: 'power3.out' } });

  if (logo) timeline.fromTo(logo, { autoAlpha: 0, y: -8 }, { autoAlpha: 1, y: 0, duration: 0.24 });
  if (navItems.length) timeline.fromTo(navItems, { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.24, stagger: 0.025 }, '-=0.1');
  if (profile) timeline.fromTo(profile, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.24 }, '-=0.08');
}

function animateSidebarFold() {
  if (!sidebarRef.value || reduceMotion.value) return;
  const navItems = sidebarRef.value.querySelectorAll('.nav-item');
  const labels = sidebarRef.value.querySelectorAll('.logo-copy, .nav-item span, .profile-info, .lang-button');
  const timeline = gsap.timeline({ defaults: { ease: 'power3.out', overwrite: 'auto' } });
  timeline.fromTo(
    labels,
    { autoAlpha: sidebarCollapsed.value ? 1 : 0, x: sidebarCollapsed.value ? 0 : -8 },
    { autoAlpha: sidebarCollapsed.value ? 0 : 1, x: 0, duration: 0.18, stagger: 0.012 },
    0,
  );
  gsap.fromTo(
    navItems,
    { autoAlpha: 0.7, x: sidebarCollapsed.value ? 6 : -6 },
    { autoAlpha: 1, x: 0, duration: 0.22, stagger: 0.018, ease: 'power3.out', overwrite: 'auto' },
  );
}

function animateRouteContent() {
  if (!mainRef.value || reduceMotion.value) return;
  const targets = mainRef.value.querySelectorAll('.page-header, .scope-bar, .timezone-strip, .metric-card, .compare-card, .user-score-card, .review-chip, .panel-card, .trade-table');
  if (!targets.length) return;
  gsap.fromTo(
    targets,
    { autoAlpha: 0, y: 14, filter: 'blur(4px)' },
    {
      autoAlpha: 1,
      y: 0,
      filter: 'blur(0px)',
      duration: 0.32,
      stagger: 0.022,
      ease: 'power3.out',
      clearProps: 'filter,transform,visibility,opacity',
      overwrite: 'auto',
    },
  );
}

watch(themeMode, (value) => {
  document.documentElement.dataset.theme = value;
  localStorage.setItem('tradelog_theme', value);
}, { immediate: true });

watch(sidebarCollapsed, (value) => {
  localStorage.setItem('tradelog_sidebar_collapsed', value ? '1' : '0');
  nextTick(animateSidebarFold);
});

watch(() => route.fullPath, () => {
  nextTick(animateRouteContent);
});

onMounted(() => {
  document.documentElement.dataset.theme = themeMode.value;
  nextTick(() => {
    animateShell();
    animateRouteContent();
  });
});
</script>

<template>
  <el-config-provider :locale="elementLocale">
    <router-view v-if="route.path === '/login'" />
    <div v-else class="app-frame" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <aside ref="sidebarRef" class="sidebar">
        <div class="logo-block">
          <div class="logo-mark">TL</div>
          <div class="logo-copy">
            <strong>{{ t('app.name') }}</strong>
            <span>{{ t('app.subtitle') }}</span>
          </div>
          <button class="sidebar-toggle" type="button" :aria-pressed="sidebarCollapsed" @click="toggleSidebar">
            <el-icon><List /></el-icon>
          </button>
        </div>

        <nav class="nav-list">
          <button
            v-for="item in menu"
            :key="item.path"
            class="nav-item"
            :class="{ active: route.path === item.path }"
            :title="item.label"
            @click="router.push(item.path)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </button>
        </nav>

        <div class="sidebar-tools">
          <div class="profile-card">
            <div class="profile-main">
              <div class="profile-avatar">{{ auth.user?.display_name?.slice(0, 1) }}</div>
              <div class="profile-info">
                <strong>{{ auth.user?.display_name }}</strong>
                <span>{{ roleLabel(auth.user?.role) }}</span>
              </div>
            </div>
            <div class="profile-actions">
              <el-button class="lang-button" text @click="toggleLocale">{{ localeLabel }}</el-button>
              <el-button :icon="themeMode === 'dark' ? Sunny : Moon" circle text @click="toggleTheme" />
              <el-button :icon="SwitchButton" circle text @click="logout" />
            </div>
          </div>
        </div>
      </aside>

      <main ref="mainRef" class="main-panel">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>
