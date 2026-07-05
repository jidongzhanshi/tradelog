<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import dayjs from 'dayjs';
import { createTrade, deleteTrade, listTrades, updateTrade } from '../api/trades';
import { exportTrades } from '../api/export';
import { listUsers } from '../api/users';
import UserScopeBar from '../components/UserScopeBar.vue';
import { directionLabel, rangeOptions, statusLabel, t } from '../i18n';
import { useAuthStore } from '../stores/auth';
import { dateTime, duration, money, percent, price, rMultiple, rewardRisk } from '../utils/format';
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
const symbolOptions = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT', 'AVAXUSDT', 'MATICUSDT'];

function blankTrade() {
  const now = dayjs().format('YYYY-MM-DDTHH:mm:ss');
  return {
    user_id: undefined,
    symbol: 'SOLUSDT',
    base_asset: 'SOL',
    quote_asset: 'USDT',
    direction: 'long',
    realized_pnl: 0,
    avg_open_price: 0,
    avg_close_price: 0,
    stop_loss_price: 0,
    take_profit_price: 0,
    planned_risk_amount: 0,
    planned_profit_amount: 0,
    open_time: now,
    close_time: now,
    strategy_tag: '',
    exit_reason: 'manual',
    followed_plan: true,
    deviation_reason: '',
    deviation_note: '',
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
  if (form.planned_risk_amount <= 0 || form.planned_profit_amount <= 0) {
    ElMessage.warning(t('trades.planAmountRequired'));
    return;
  }
  if (!form.followed_plan && !form.deviation_reason) {
    ElMessage.warning(t('trades.deviationReasonRequired'));
    return;
  }
  form.symbol = form.symbol.toUpperCase();
  form.base_asset = form.symbol.replace('USDT', '') || form.base_asset;
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
watch(() => form.followed_plan, (followed) => {
  if (followed) {
    form.deviation_reason = '';
    form.deviation_note = '';
  }
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
        <el-table-column :label="t('trades.pnl')" min-width="130" sortable>
          <template #default="{ row }"><strong :class="row.realized_pnl >= 0 ? 'positive' : 'negative'">{{ money(row.realized_pnl) }}</strong></template>
        </el-table-column>
        <el-table-column :label="t('trades.rMultiple')" width="100" sortable>
          <template #default="{ row }"><strong :class="row.r_multiple >= 0 ? 'positive' : 'negative'">{{ rMultiple(row.r_multiple) }}</strong></template>
        </el-table-column>
        <el-table-column :label="t('trades.riskPercent')" width="115" sortable>
          <template #default="{ row }"><span :class="row.risk_percent > 2 ? 'negative' : ''">{{ percent(row.risk_percent) }}</span></template>
        </el-table-column>
        <el-table-column :label="t('trades.plannedRR')" width="105">
          <template #default="{ row }">{{ rewardRisk(row.planned_rr) }}</template>
        </el-table-column>
        <el-table-column :label="t('trades.planAmounts')" min-width="190">
          <template #default="{ row }">{{ money(row.planned_risk_amount) }} / {{ money(row.planned_profit_amount) }}</template>
        </el-table-column>
        <el-table-column :label="t('trades.simulatedPnl')" min-width="135" sortable>
          <template #default="{ row }"><span :class="row.simulated_pnl >= 0 ? 'positive' : 'negative'">{{ money(row.simulated_pnl) }}</span></template>
        </el-table-column>
        <el-table-column :label="t('trades.openClosePrice')" min-width="150">
          <template #default="{ row }">{{ price(row.avg_open_price) }} / {{ price(row.avg_close_price) }}</template>
        </el-table-column>
        <el-table-column :label="t('trades.stopTarget')" min-width="150">
          <template #default="{ row }">{{ row.stop_loss_price ? price(row.stop_loss_price) : '-' }} / {{ row.take_profit_price ? price(row.take_profit_price) : '-' }}</template>
        </el-table-column>
        <el-table-column :label="t('trades.duration')" min-width="130">
          <template #default="{ row }">{{ duration(row.holding_seconds) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="90">
          <template #default="{ row }">{{ statusLabel(row.status) }}</template>
        </el-table-column>
        <el-table-column :label="t('trades.followedPlan')" width="105">
          <template #default="{ row }"><el-tag :type="row.followed_plan ? 'success' : 'warning'">{{ row.followed_plan ? t('common.yes') : t('common.no') }}</el-tag></template>
        </el-table-column>
        <el-table-column v-if="canEdit" :label="t('common.actions')" fixed="right" width="150">
          <template #default="{ row }">
            <el-button text @click="openEdit(row)">{{ t('common.edit') }}</el-button>
            <el-button text type="danger" @click="remove(row)">{{ t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing ? t('trades.editTitle') : t('trades.createTitle')" width="820px" class="trade-dialog">
      <p class="form-note">{{ t('trades.formNote') }}</p>
      <el-form label-position="top">
        <div class="trade-form-sections">
          <section class="form-section">
            <h3>{{ t('trades.sectionPlan') }}</h3>
            <div class="form-grid compact">
              <el-form-item v-if="auth.isAdmin" :label="t('trades.owner')">
                <el-select v-model="form.user_id">
                  <el-option v-for="item in traderOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('trades.symbol')">
                <el-select v-model="form.symbol" filterable allow-create default-first-option>
                  <el-option v-for="symbol in symbolOptions" :key="symbol" :label="symbol" :value="symbol" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('trades.direction')">
                <el-select v-model="form.direction"><el-option :label="t('direction.long')" value="long" /><el-option :label="t('direction.short')" value="short" /></el-select>
              </el-form-item>
            </div>
          </section>
          <section class="form-section">
            <h3>{{ t('trades.sectionPrice') }}</h3>
            <div class="form-grid compact">
              <el-form-item :label="t('trades.avgOpen')"><el-input-number v-model="form.avg_open_price" :min="0" :precision="8" /></el-form-item>
              <el-form-item :label="t('trades.avgClose')"><el-input-number v-model="form.avg_close_price" :min="0" :precision="8" /></el-form-item>
              <el-form-item :label="t('trades.stopLoss')"><el-input-number v-model="form.stop_loss_price" :min="0" :precision="8" /></el-form-item>
              <el-form-item :label="t('trades.takeProfit')"><el-input-number v-model="form.take_profit_price" :min="0" :precision="8" /></el-form-item>
              <el-form-item :label="t('trades.plannedRiskAmount')"><el-input-number v-model="form.planned_risk_amount" :min="0" :precision="2" /></el-form-item>
              <el-form-item :label="t('trades.plannedProfitAmount')"><el-input-number v-model="form.planned_profit_amount" :min="0" :precision="2" /></el-form-item>
            </div>
          </section>
          <section class="form-section">
            <h3>{{ t('trades.sectionResult') }}</h3>
            <div class="form-grid compact">
              <el-form-item :label="t('trades.realizedPnl')"><el-input-number v-model="form.realized_pnl" :precision="2" /></el-form-item>
              <el-form-item :label="t('trades.openTime')"><el-date-picker v-model="form.open_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
              <el-form-item :label="t('trades.closeTime')"><el-date-picker v-model="form.close_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
              <el-form-item :label="t('trades.strategyTag')"><el-input v-model="form.strategy_tag" /></el-form-item>
              <el-form-item :label="t('trades.exitReason')">
                <el-select v-model="form.exit_reason">
                  <el-option :label="t('exitReason.takeProfit')" value="take_profit" />
                  <el-option :label="t('exitReason.stopLoss')" value="stop_loss" />
                  <el-option :label="t('exitReason.manual')" value="manual" />
                  <el-option :label="t('exitReason.other')" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('trades.followedPlan')">
                <el-switch v-model="form.followed_plan" />
              </el-form-item>
              <el-form-item :label="t('trades.deviationReason')" :class="{ 'plan-field-disabled': form.followed_plan }">
                <el-select v-model="form.deviation_reason" :disabled="form.followed_plan" clearable>
                  <el-option :label="t('deviation.earlyTakeProfit')" value="early_take_profit" />
                  <el-option :label="t('deviation.earlyStop')" value="early_stop" />
                  <el-option :label="t('deviation.delayedExit')" value="delayed_exit" />
                  <el-option :label="t('deviation.missedStop')" value="missed_stop" />
                  <el-option :label="t('deviation.addedPosition')" value="added_position" />
                  <el-option :label="t('deviation.oversizedRisk')" value="oversized_risk" />
                  <el-option :label="t('deviation.emotionalTrade')" value="emotional_trade" />
                  <el-option :label="t('deviation.other')" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('trades.deviationNote')" class="wide" :class="{ 'plan-field-disabled': form.followed_plan }">
                <el-input v-model="form.deviation_note" type="textarea" :rows="2" :disabled="form.followed_plan" />
              </el-form-item>
              <el-form-item :label="t('trades.note')" class="wide"><el-input v-model="form.note" type="textarea" :rows="3" /></el-form-item>
            </div>
          </section>
        </div>
      </el-form>
      <template #footer><el-button @click="dialog = false">{{ t('common.cancel') }}</el-button><el-button type="primary" @click="save">{{ t('common.save') }}</el-button></template>
    </el-dialog>
  </div>
</template>
