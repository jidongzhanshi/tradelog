<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { createUser, deleteUser, listUsers, resetPassword, updateUser } from '../api/users';
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
  ElMessage.success('用户已保存');
  dialog.value = false;
  await load();
}

async function reset(row: User) {
  const result = await ElMessageBox.prompt('输入新密码', `重置 ${row.display_name} 的密码`, { inputValue: '123456' });
  await resetPassword(row.id, result.value);
  ElMessage.success('密码已重置');
}

async function remove(row: User) {
  await ElMessageBox.confirm(`确认删除账号 ${row.display_name}？`, '删除用户', { type: 'warning' });
  await deleteUser(row.id);
  ElMessage.success('用户已删除');
  await load();
}

onMounted(load);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">Accounts</span>
        <h1>用户管理</h1>
      </div>
      <el-button type="primary" @click="openCreate">新增账号</el-button>
    </header>

    <el-card class="panel-card">
      <el-table :data="users" stripe>
        <el-table-column prop="display_name" label="显示名称" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'super_admin' ? 'danger' : row.role === 'viewer' ? 'warning' : 'success'">
              {{ row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="{ row }">{{ row.is_active ? '启用' : '禁用' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="230">
          <template #default="{ row }">
            <el-button text @click="openEdit(row)">编辑</el-button>
            <el-button text @click="reset(row)">重置密码</el-button>
            <el-button text type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing ? '编辑用户' : '新增用户'" width="520px">
      <el-form label-position="top">
        <el-form-item label="用户名"><el-input v-model="form.username" :disabled="Boolean(editing)" /></el-form-item>
        <el-form-item label="显示名称"><el-input v-model="form.display_name" /></el-form-item>
        <el-form-item v-if="!editing" label="初始密码"><el-input v-model="form.password" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="交易用户" value="trader" />
            <el-option label="只读观察" value="viewer" />
            <el-option label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用账号"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>
