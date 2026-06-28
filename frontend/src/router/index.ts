import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const Login = () => import('../views/Login.vue');
const AdminHome = () => import('../views/AdminHome.vue');
const Dashboard = () => import('../views/Dashboard.vue');
const Trades = () => import('../views/Trades.vue');
const Analytics = () => import('../views/Analytics.vue');
const Users = () => import('../views/Users.vue');
const Settings = () => import('../views/Settings.vue');

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/', redirect: '/admin' },
    { path: '/admin', component: AdminHome, meta: { auth: true, admin: true } },
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
  if (to.path === '/login' && auth.user) return auth.isAdmin ? '/admin' : '/dashboard';
  return true;
});

export default router;
