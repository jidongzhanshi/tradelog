import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Login from '../views/Login.vue';
import Dashboard from '../views/Dashboard.vue';
import Trades from '../views/Trades.vue';
import Analytics from '../views/Analytics.vue';
import Users from '../views/Users.vue';
import Settings from '../views/Settings.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: Dashboard, meta: { auth: true } },
    { path: '/trades', component: Trades, meta: { auth: true } },
    { path: '/analytics', component: Analytics, meta: { auth: true } },
    { path: '/users', component: Users, meta: { auth: true, admin: true } },
    { path: '/settings', component: Settings, meta: { auth: true } },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (auth.token && !auth.user) {
    try {
      await auth.loadMe();
    } catch {
      auth.logout();
    }
  }
  if (to.meta.auth && !auth.user) return '/login';
  if (to.meta.admin && auth.user?.role !== 'super_admin') return '/dashboard';
  if (to.path === '/login' && auth.user) return '/dashboard';
  return true;
});

export default router;
