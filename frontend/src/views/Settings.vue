<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { changePassword } from '../api/auth';
import { getSettings, updateSettings } from '../api/settings';
import UserScopeBar from '../components/UserScopeBar.vue';
import TimeZoneStrip from '../components/TimeZoneStrip.vue';
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
  ElMessage.success('资金设置已保存');
}

async function savePassword() {
  await changePassword(oldPassword.value, newPassword.value);
  oldPassword.value = '';
  newPassword.value = '';
  ElMessage.success('密码已修改');
}

onMounted(load);
watch(scopeUserId, load);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">Settings</span>
        <h1>系统设置</h1>
      </div>
    </header>

    <TimeZoneStrip />
    <UserScopeBar v-if="auth.isAdmin" v-model="scopeUserId" />

    <section class="settings-grid">
      <el-card class="panel-card" header="资金设置">
        <el-form label-position="top">
          <el-form-item label="总投入本金（USDT）">
            <el-input-number v-model="capital" :min="0" :precision="2" />
          </el-form-item>
          <el-button type="primary" :disabled="auth.isViewer" @click="saveCapital">保存</el-button>
        </el-form>
      </el-card>

      <el-card class="panel-card" header="账号安全">
        <el-form label-position="top">
          <el-form-item label="旧密码"><el-input v-model="oldPassword" type="password" show-password /></el-form-item>
          <el-form-item label="新密码"><el-input v-model="newPassword" type="password" show-password /></el-form-item>
          <el-button type="primary" @click="savePassword">修改密码</el-button>
        </el-form>
      </el-card>

      <el-card class="panel-card" header="备份说明">
        <p class="muted">SQLite 数据库会保存在服务器 data 目录。Docker 重建不会影响 data 目录。</p>
        <p class="muted">超级管理员可通过后端接口触发手动备份，自动备份策略后续可接入系统定时任务。</p>
      </el-card>
    </section>
  </div>
</template>
