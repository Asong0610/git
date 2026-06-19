<template>
  <div class="deposit-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>押金流水</span>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="entry_type" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.entry_type)">
              {{ getTypeText(row.entry_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额(元)" width="120" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.amount >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ row.amount >= 0 ? '+' : '' }}¥{{ Math.abs(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance_after" label="余额(元)" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.balance_after }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDepositLedger } from '../../api/user'

const loading = ref(false)
const tableData = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const getTypeColor = (type) => {
  const map = {
    topup: 'success',
    freeze: 'warning',
    refund: 'primary',
    adjust: 'danger'
  }
  return map[type] || 'info'
}

const getTypeText = (type) => {
  const map = {
    topup: '充值',
    freeze: '冻结',
    refund: '退还',
    adjust: '调账'
  }
  return map[type] || type
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDepositLedger({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载流水失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.deposit-management {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
