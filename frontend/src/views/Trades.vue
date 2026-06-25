<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import dayjs from 'dayjs';
import { createTrade, deleteTrade, listTrades, updateTrade } from '../api/trades';
import { exportTrades } from '../api/export';
import { listUsers } from '../api/users';
import UserScopeBar from '../components/UserScopeBar.vue';
import { useAuthStore } from '../stores/auth';
import { contractText, dateTime, directionText, duration, marginText, money, percent, statusText } from '../utils/format';
import type { Trade, User } from '../types';

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
    order_side: '买',
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

const canEdit = computed(() => !auth.isViewer);
const traderOptions = computed(() => users.value.filter((user) => user.role === 'trader').map((user) => ({ label: user.display_name, value: user.id })));

async function load() {
  const params = { ...filters, range: filters.range === 'all' ? undefined : filters.range, user_id: scopeUserId.value };
  trades.value = await listTrades(params);
}

function openCreate() {
  editing.value = null;
  Object.assign(form, blankTrade());
  if (scopeUserId.value) form.user_id = scopeUserId.value;
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
  ElMessage.success('交易已保存');
  dialog.value = false;
  await load();
}

async function remove(row: Trade) {
  await ElMessageBox.confirm(`确认删除 ${row.symbol} 这笔交易？`, '删除交易', { type: 'warning' });
  await deleteTrade(row.id);
  ElMessage.success('交易已删除');
  await load();
}

async function downloadExcel() {
  await exportTrades({ range: filters.range === 'all' ? undefined : filters.range, user_id: scopeUserId.value });
}

onMounted(async () => {
  if (auth.isAdmin || auth.isViewer) users.value = await listUsers();
  await load();
});
watch([scopeUserId, () => filters.range, () => filters.status, () => filters.direction], load);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <span class="eyebrow">Closed Trades</span>
        <h1>{{ auth.isViewer ? '交易记录查看' : '交易记录管理' }}</h1>
      </div>
      <div class="actions">
        <el-button @click="downloadExcel">导出 Excel</el-button>
        <el-button v-if="canEdit" type="primary" @click="openCreate">新增交易</el-button>
      </div>
    </header>

    <UserScopeBar v-model="scopeUserId" />

    <el-card class="panel-card">
      <div class="filter-row">
        <el-segmented v-model="filters.range" :options="[
          { label: '今日', value: 'today' }, { label: '本周', value: 'week' }, { label: '本月', value: 'month' },
          { label: '本年', value: 'year' }, { label: '全部', value: 'all' },
        ]" />
        <el-input v-model="filters.symbol" placeholder="交易对 SOLUSDT" clearable @change="load" />
        <el-select v-model="filters.direction" placeholder="方向" clearable>
          <el-option label="做多" value="long" />
          <el-option label="做空" value="short" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable>
          <el-option label="盈利" value="profit" />
          <el-option label="亏损" value="loss" />
          <el-option label="持平" value="flat" />
        </el-select>
      </div>

      <el-table :data="trades" class="trade-table" stripe>
        <el-table-column prop="close_time" label="平仓时间" min-width="160" sortable>
          <template #default="{ row }">{{ dateTime(row.close_time) }}</template>
        </el-table-column>
        <el-table-column prop="symbol" label="交易对" width="115" />
        <el-table-column label="方向" width="90">
          <template #default="{ row }"><el-tag :type="row.direction === 'long' ? 'success' : 'danger'">{{ directionText[row.direction] }}</el-tag></template>
        </el-table-column>
        <el-table-column label="模式" width="135">
          <template #default="{ row }">{{ contractText[row.contract_type] }} · {{ marginText[row.margin_mode] }} {{ row.leverage }}X</template>
        </el-table-column>
        <el-table-column label="盈亏" min-width="130" sortable>
          <template #default="{ row }"><strong :class="row.realized_pnl >= 0 ? 'positive' : 'negative'">{{ money(row.realized_pnl) }}</strong></template>
        </el-table-column>
        <el-table-column label="收益率" width="110" sortable>
          <template #default="{ row }"><span :class="row.roi_percent >= 0 ? 'positive' : 'negative'">{{ percent(row.roi_percent) }}</span></template>
        </el-table-column>
        <el-table-column label="开仓/平仓价" min-width="150">
          <template #default="{ row }">{{ row.avg_open_price }} / {{ row.avg_close_price }}</template>
        </el-table-column>
        <el-table-column label="持仓时长" min-width="130">
          <template #default="{ row }">{{ duration(row.holding_seconds) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">{{ statusText[row.status] }}</template>
        </el-table-column>
        <el-table-column v-if="canEdit" label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button text @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing ? '编辑交易' : '新增交易'" width="860px" class="trade-dialog">
      <p class="form-note">只记录平仓后的核心信息；状态会根据已实现盈亏自动判断。</p>
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item v-if="auth.isAdmin" label="归属用户">
            <el-select v-model="form.user_id">
              <el-option v-for="item in traderOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="交易对"><el-input v-model="form.symbol" /></el-form-item>
          <el-form-item label="方向">
            <el-select v-model="form.direction"><el-option label="做多" value="long" /><el-option label="做空" value="short" /></el-select>
          </el-form-item>
          <el-form-item label="合约类型">
            <el-select v-model="form.contract_type"><el-option label="永续" value="perpetual" /><el-option label="交割" value="delivery" /></el-select>
          </el-form-item>
          <el-form-item label="保证金模式">
            <el-select v-model="form.margin_mode"><el-option label="全仓" value="cross" /><el-option label="逐仓" value="isolated" /></el-select>
          </el-form-item>
          <el-form-item label="杠杆"><el-input-number v-model="form.leverage" :min="1" :precision="2" /></el-form-item>
          <el-form-item label="已实现盈亏"><el-input-number v-model="form.realized_pnl" :precision="4" /></el-form-item>
          <el-form-item label="收益率 %"><el-input-number v-model="form.roi_percent" :precision="4" /></el-form-item>
          <el-form-item label="平仓数量"><el-input-number v-model="form.position_size" :min="0" :precision="6" /></el-form-item>
          <el-form-item label="平均开仓价"><el-input-number v-model="form.avg_open_price" :min="0" :precision="8" /></el-form-item>
          <el-form-item label="平均平仓价"><el-input-number v-model="form.avg_close_price" :min="0" :precision="8" /></el-form-item>
          <el-form-item label="开仓时间"><el-date-picker v-model="form.open_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
          <el-form-item label="平仓时间"><el-date-picker v-model="form.close_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
          <el-form-item label="备注" class="wide"><el-input v-model="form.note" type="textarea" :rows="4" /></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="dialog = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>
