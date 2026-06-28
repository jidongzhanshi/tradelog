<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { listUsers } from '../api/users';
import { t } from '../i18n';
import { useAuthStore } from '../stores/auth';
import type { User } from '../types';

const model = defineModel<number | undefined>();
const props = withDefaults(defineProps<{ includeAll?: boolean }>(), {
  includeAll: true,
});
const auth = useAuthStore();
const users = ref<User[]>([]);
const selected = computed({
  get: () => model.value ?? 0,
  set: (value: number) => {
    model.value = value === 0 ? undefined : value;
  },
});
const options = computed(() => [
  ...(props.includeAll ? [{ label: t('common.totalComparison'), value: 0 }] : []),
  ...users.value.map((user) => ({ label: user.display_name, value: user.id })),
]);

onMounted(async () => {
  if (auth.isAdmin) {
    users.value = (await listUsers()).filter((item) => item.role === 'trader');
    if (!props.includeAll && !model.value && users.value.length) {
      model.value = users.value[0].id;
    }
  }
});
</script>

<template>
  <div v-if="auth.isAdmin" class="scope-bar">
    <span>{{ t('common.adminScope') }}</span>
    <el-segmented
      v-model="selected"
      :options="options"
    />
  </div>
</template>
