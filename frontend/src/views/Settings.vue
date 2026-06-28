<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { changePassword } from '../api/auth';
import { getSettings, updateSettings } from '../api/settings';
import UserScopeBar from '../components/UserScopeBar.vue';
import TimeZoneStrip from '../components/TimeZoneStrip.vue';
import { t } from '../i18n';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const scopeUserId = ref<number>();
const capital = ref(0);
const oldPassword = ref('');
const newPassword = ref('');

async function load() {
  const data = await getSettings({ user_id: scopeUserId.value });
  capital.value = data.initial_capital;
}

async function saveCapital() {
  await updateSettings(capital.value, { user_id: scopeUserId.value });
  ElMessage.success(t('settings.capitalSaved'));
}

async function savePassword() {
  await changePassword(oldPassword.value, newPassword.value);
  oldPassword.value = '';
  newPassword.value = '';
  ElMessage.success(t('settings.passwordSaved'));
}

onMounted(() => {
  if (!auth.isAdmin) load();
});
watch(scopeUserId, (value) => {
  if (value) load();
});
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">{{ t('settings.eyebrow') }}</span>
        <h1>{{ t('settings.title') }}</h1>
      </div>
    </header>

    <TimeZoneStrip />
    <UserScopeBar v-if="auth.isAdmin" v-model="scopeUserId" :include-all="false" />

    <section class="settings-grid">
      <el-card class="panel-card" :header="t('settings.capital')">
        <el-form label-position="top">
          <el-form-item :label="t('settings.capitalLabel')">
            <el-input-number v-model="capital" :min="0" :precision="2" />
          </el-form-item>
          <el-button type="primary" @click="saveCapital">{{ t('common.save') }}</el-button>
        </el-form>
      </el-card>

      <el-card class="panel-card" :header="t('settings.security')">
        <el-form label-position="top">
          <el-form-item :label="t('common.oldPassword')"><el-input v-model="oldPassword" type="password" show-password /></el-form-item>
          <el-form-item :label="t('common.newPassword')"><el-input v-model="newPassword" type="password" show-password /></el-form-item>
          <el-button type="primary" @click="savePassword">{{ t('settings.changePassword') }}</el-button>
        </el-form>
      </el-card>

      <el-card class="panel-card" :header="t('settings.backup')">
        <p class="muted">{{ t('settings.backupLine1') }}</p>
        <p class="muted">{{ t('settings.backupLine2') }}</p>
      </el-card>
    </section>
  </div>
</template>
