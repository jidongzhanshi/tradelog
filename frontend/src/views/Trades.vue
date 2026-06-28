<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import dayjs from 'dayjs';
import { createTrade, deleteTrade, listTrades, updateTrade } from '../api/trades';
import { exportTrades } from '../api/export';
import { listUsers } from '../api/users';
import UserScopeBar from '../components/UserScopeBar.vue';
import { contractLabel, directionLabel, marginLabel, rangeOptions, statusLabel, t } from '../i18n';
import { useAuthStore } from '../stores/auth';
import { dateTime, duration, money, percent } from '../utils/format';
import type { Trade, User } from '../types';

const route = useRoute();
const auth = useAuthStore();
const trades = ref<Trade[]>([]);
const users = ref<User[]>([]);
const scopeUserId = ref<number>();
const dialog = ref(false);
const editing = ref<Trade | null>(null);
const filters = reactive({ range: 'all', symbol: '', status: '', direction: '' });
const form = reactive<any>(blankTrade());

function blankTrade() {
  const now = dayjs().format('YYYY-MM-DDTHH:mm:ss');
  return {
    user_id: undefined,
    symbol: 'SOLUSDT',
    base_asset: 'SOL',
    quote_asset: 'USDT',
    direction: 'long',
    order_side: 'buy',
    contract_type: 'perpetual',
    margin_mode: 'cross',
    leverage: 100,
    realized_pnl: 0,
    roi_percent: 0,
    position_size: 0,
    max_position_size: 0,
    avg_open_price: 0,
    avg_close_price: 0,
    open_time: now,
    close_time: now,
    fee: 0,
    status: 'flat',
    note: '',
  };
}

const canEdit = computed(() => true);
const traderOptions = computed(() => users.value.filter((user) => user.role === 'trader').map((user) => ({ label: user.display_name, value: user.id })));
const currentAccountName = computed(() => traderOptions.value.find((item) => item.value === scopeUserId.value)?.label);
const pageTitle = computed(() => currentAccountName.value ? t('trades.accountTitle', { name: currentAccountName.value }) : t('trades.title'));

function readRouteScope() {
  const raw = Number(route.query.user_id);
  scopeUserId.value = Number.isFinite(raw) && raw > 0 ? raw : undefined;
}

async function load() {
  const params = { ...filters, range: filters.range === 'all' ? undefined : filters.range, user_id: scopeUserId.value };
  trades.value = await listTrades(params);
}

function openCreate() {
  editing.value = null;
  Object.assign(form, blankTrade());
  if (auth.isAdmin) form.user_id = scopeUserId.value || traderOptions.value[0]?.value;
  dialog.value = true;
}

function openEdit(row: Trade) {
  editing.value = row;
  Object.assign(form, row);
  dialog.value = true;
}

async function save() {
  form.symbol = form.symbol.toUpperCase();
  form.base_asset = form.symbol.replace('USDT', '') || form.base_asset;
  form.max_position_size = form.position_size || 0;
  form.fee = 0;
  form.status = form.realized_pnl > 0 ? 'profit' : form.realized_pnl < 0 ? 'loss' : 'flat';
  if (editing.value) await updateTrade(editing.value.id, form);
  else await createTrade(form);
  ElMessage.success(t('trades.saved'));
  dialog.value = false;
  await load();
}

async function remove(row: Trade) {
  await ElMessageBox.confirm(t('trades.deleteConfirm', { symbol: row.symbol }), t('trades.deleteTitle'), { type: 'warning' });
  await deleteTrade(row.id);
  ElMessage.success(t('trades.deleted'));
  await load();
}

async function downloadExcel() {
  await exportTrades({ range: filters.range === 'all' ? undefined : filters.range, user_id: scopeUserId.value });
}

onMounted(async () => {
  readRouteScope();
  if (auth.isAdmin) users.value = await listUsers();
  await load();
});
watch([scopeUserId, () => filters.range, () => filters.status, () => filters.direction], load);
watch(() => route.query.user_id, async () => {
  readRouteScope();
  await load();
});
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">{{ t('trades.eyebrow') }}</span>
        <h1>{{ pageTitle }}</h1>
      </div>
      <div class="actions">
        <el-button @click="downloadExcel">{{ t('common.exportExcel') }}</el-button>
        <el-button v-if="canEdit" type="primary" @click="openCreate">{{ t('common.addTrade') }}</el-button>
      </div>
    </header>

    <UserScopeBar v-model="scopeUserId" />

    <el-card class="panel-card">
      <div class="filter-row">
        <el-segmented v-model="filters.range" :options="rangeOptions" />
        <el-input v-model="filters.symbol" :placeholder="t('trades.symbolPlaceholder')" clearable @change="load" />
        <el-select v-model="filters.direction" :placeholder="t('trades.direction')" clearable>
          <el-option :label="t('direction.long')" value="long" />
          <el-option :label="t('direction.short')" value="short" />
        </el-select>
        <el-select v-model="filters.status" :placeholder="t('common.status')" clearable>
          <el-option :label="t('status.profit')" value="profit" />
          <el-option :label="t('status.loss')" value="loss" />
          <el-option :label="t('status.flat')" value="flat" />
        </el-select>
      </div>

      <el-table :data="trades" class="trade-table" stripe>
        <el-table-column prop="close_time" :label="t('trades.closeTime')" min-width="160" sortable>
          <template #default="{ row }">{{ dateTime(row.close_time) }}</template>
        </el-table-column>
        <el-table-column prop="symbol" :label="t('trades.symbol')" width="115" />
        <el-table-column :label="t('trades.direction')" width="90">
          <template #default="{ row }"><el-tag :type="row.direction === 'long' ? 'success' : 'danger'">{{ directionLabel(row.direction) }}</el-tag></template>
        </el-table-column>
        <el-table-column :label="t('trades.mode')" width="150">
          <template #default="{ row }">{{ contractLabel(row.contract_type) }} · {{ marginLabel(row.margin_mode) }} {{ row.leverage }}X</template>
        </el-table-column>
        <el-table-column :label="t('trades.pnl')" min-width="130" sortable>
          <template #default="{ row }"><strong :class="row.realized_pnl >= 0 ? 'positive' : 'negative'">{{ money(row.realized_pnl) }}</strong></template>
        </el-table-column>
        <el-table-column :label="t('trades.roi')" width="110" sortable>
          <template #default="{ row }"><span :class="row.roi_percent >= 0 ? 'positive' : 'negative'">{{ percent(row.roi_percent) }}</span></template>
        </el-table-column>
        <el-table-column :label="t('trades.openClosePrice')" min-width="150">
          <template #default="{ row }">{{ row.avg_open_price }} / {{ row.avg_close_price }}</template>
        </el-table-column>
        <el-table-column :label="t('trades.duration')" min-width="130">
          <template #default="{ row }">{{ duration(row.holding_seconds) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="90">
          <template #default="{ row }">{{ statusLabel(row.status) }}</template>
        </el-table-column>
        <el-table-column v-if="canEdit" :label="t('common.actions')" fixed="right" width="150">
          <template #default="{ row }">
            <el-button text @click="openEdit(row)">{{ t('common.edit') }}</el-button>
            <el-button text type="danger" @click="remove(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing ? t('trades.editTitle') : t('trades.createTitle')" width="860px" class="trade-dialog">
      <p class="form-note">{{ t('trades.formNote') }}</p>
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item v-if="auth.isAdmin" :label="t('trades.owner')">
            <el-select v-model="form.user_id">
              <el-option v-for="item in traderOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('trades.symbol')"><el-input v-model="form.symbol" /></el-form-item>
          <el-form-item :label="t('trades.direction')">
            <el-select v-model="form.direction"><el-option :label="t('direction.long')" value="long" /><el-option :label="t('direction.short')" value="short" /></el-select>
          </el-form-item>
          <el-form-item :label="t('trades.contractType')">
            <el-select v-model="form.contract_type"><el-option :label="t('contract.perpetual')" value="perpetual" /><el-option :label="t('contract.delivery')" value="delivery" /></el-select>
          </el-form-item>
          <el-form-item :label="t('trades.marginMode')">
            <el-select v-model="form.margin_mode"><el-option :label="t('margin.cross')" value="cross" /><el-option :label="t('margin.isolated')" value="isolated" /></el-select>
          </el-form-item>
          <el-form-item :label="t('trades.leverage')"><el-input-number v-model="form.leverage" :min="1" :precision="2" /></el-form-item>
          <el-form-item :label="t('trades.realizedPnl')"><el-input-number v-model="form.realized_pnl" :precision="4" /></el-form-item>
          <el-form-item :label="t('trades.roi')"><el-input-number v-model="form.roi_percent" :precision="4" /></el-form-item>
          <el-form-item :label="t('trades.positionSize')"><el-input-number v-model="form.position_size" :min="0" :precision="6" /></el-form-item>
          <el-form-item :label="t('trades.avgOpen')"><el-input-number v-model="form.avg_open_price" :min="0" :precision="8" /></el-form-item>
          <el-form-item :label="t('trades.avgClose')"><el-input-number v-model="form.avg_close_price" :min="0" :precision="8" /></el-form-item>
          <el-form-item :label="t('trades.openTime')"><el-date-picker v-model="form.open_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
          <el-form-item :label="t('trades.closeTime')"><el-date-picker v-model="form.close_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
          <el-form-item :label="t('trades.note')" class="wide"><el-input v-model="form.note" type="textarea" :rows="4" /></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="dialog = false">{{ t('common.cancel') }}</el-button><el-button type="primary" @click="save">{{ t('common.save') }}</el-button></template>
    </el-dialog>
  </div>
</template>
