import { defineStore } from 'pinia';
import { getMe, login as loginApi } from '../api/auth';
import type { User } from '../types';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('tradelog_token') || '',
    user: null as User | null,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.user),
    isAdmin: (state) => state.user?.role === 'super_admin',
    isTrader: (state) => state.user?.role === 'trader',
  },
  actions: {
    async login(username: string, password: string) {
      const token = await loginApi(username, password);
      this.token = token.access_token;
      localStorage.setItem('tradelog_token', token.access_token);
      await this.loadMe();
    },
    async loadMe() {
      if (!this.token) return;
      this.user = await getMe();
    },
    logout() {
      this.token = '';
      this.user = null;
      localStorage.removeItem('tradelog_token');
    },
  },
});
