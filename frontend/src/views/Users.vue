<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { createUser, deleteUser, listUsers, resetPassword, updateUser } from '../api/users';
import { roleLabel, t } from '../i18n';
import type { Role, User } from '../types';

const users = ref<User[]>([]);
const dialog = ref(false);
const editing = ref<User | null>(null);
const form = reactive<{ username: string; display_name: string; role: Role; password: string; is_active: boolean }>({
  username: '',
  display_name: '',
  role: 'trader',
  password: '123456',
  is_active: true,
});

async function load() {
  users.value = await listUsers();
}

function openCreate() {
  editing.value = null;
  Object.assign(form, { username: '', display_name: '', role: 'trader', password: '123456', is_active: true });
  dialog.value = true;
}

function openEdit(row: User) {
  editing.value = row;
  Object.assign(form, { username: row.username, display_name: row.display_name, role: row.role, password: '', is_active: row.is_active });
  dialog.value = true;
}

async function save() {
  if (editing.value) await updateUser(editing.value.id, { display_name: form.display_name, role: form.role, is_active: form.is_active } as any);
  else await createUser(form);
  ElMessage.success(t('users.saved'));
  dialog.value = false;
  await load();
}

async function reset(row: User) {
  const result = await ElMessageBox.prompt(t('users.resetPrompt'), t('users.resetTitle', { name: row.display_name }), { inputValue: '123456' });
  await resetPassword(row.id, result.value);
  ElMessage.success(t('users.passwordReset'));
}

async function remove(row: User) {
  await ElMessageBox.confirm(t('users.deleteConfirm', { name: row.display_name }), t('users.deleteTitle'), { type: 'warning' });
  await deleteUser(row.id);
  ElMessage.success(t('users.deleted'));
  await load();
}

onMounted(load);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">{{ t('users.eyebrow') }}</span>
        <h1>{{ t('users.title') }}</h1>
      </div>
      <el-button type="primary" @click="openCreate">{{ t('users.add') }}</el-button>
    </header>

    <el-card class="panel-card">
      <el-table :data="users" stripe>
        <el-table-column prop="display_name" :label="t('common.displayName')" />
        <el-table-column prop="username" :label="t('common.username')" />
        <el-table-column :label="t('common.role')">
          <template #default="{ row }">
            <el-tag :type="row.role === 'super_admin' ? 'danger' : 'success'">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.status')">
          <template #default="{ row }">{{ row.is_active ? t('common.enabled') : t('common.disabled') }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="250">
          <template #default="{ row }">
            <el-button text @click="openEdit(row)">{{ t('common.edit') }}</el-button>
            <el-button text @click="reset(row)">{{ t('common.resetPassword') }}</el-button>
            <el-button text type="danger" @click="remove(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing ? t('users.editTitle') : t('users.createTitle')" width="520px">
      <el-form label-position="top">
        <el-form-item :label="t('common.username')"><el-input v-model="form.username" :disabled="Boolean(editing)" /></el-form-item>
        <el-form-item :label="t('common.displayName')"><el-input v-model="form.display_name" /></el-form-item>
        <el-form-item v-if="!editing" :label="t('common.initialPassword')"><el-input v-model="form.password" /></el-form-item>
        <el-form-item :label="t('common.role')">
          <el-select v-model="form.role">
            <el-option :label="t('role.trader')" value="trader" />
            <el-option :label="t('role.admin')" value="super_admin" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.enabled')"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog = false">{{ t('common.cancel') }}</el-button><el-button type="primary" @click="save">{{ t('common.save') }}</el-button></template>
    </el-dialog>
  </div>
</template>
