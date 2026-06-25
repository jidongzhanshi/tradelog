<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { listUsers } from '../api/users';
import { useAuthStore } from '../stores/auth';
import type { User } from '../types';

const model = defineModel<number | undefined>();
const auth = useAuthStore();
const users = ref<User[]>([]);
const selected = computed({
  get: () => model.value ?? 0,
  set: (value: number) => {
    model.value = value === 0 ? undefined : value;
  },
});

onMounted(async () => {
  if (auth.isAdmin || auth.isViewer) {
    users.value = (await listUsers()).filter((item) => item.role === 'trader');
  }
});
</script>

<template>
  <div v-if="auth.isAdmin || auth.isViewer" class="scope-bar">
    <span>{{ auth.isViewer ? '观察范围' : '管理员视角' }}</span>
    <el-segmented
      v-model="selected"
      :options="[
        { label: '全部对比', value: 0 },
        ...users.map((user) => ({ label: user.display_name, value: user.id })),
      ]"
    />
  </div>
</template>
