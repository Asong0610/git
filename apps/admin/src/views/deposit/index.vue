<template>
  <div class="deposit-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>押金流水</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户">
          <el-input v-model="searchForm.keyword" placeholder="手机号 / 昵称" clearable />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.entryType" placeholder="全部" clearable>
            <el-option label="充值" value="topup" />
            <el-option label="冻结" value="freeze" />
            <el-option label="退还" value="refund" />
            <el-option label="调账" value="adjust" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="entry_type" label="类型" width="100" align="center">
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
import { getAdminDepositLedger } from '../../api/user'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  keyword: '',
  entryType: ''
})

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
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.entryType) params.entry_type = searchForm.entryType

    const res = await getAdminDepositLedger(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载流水失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.entryType = ''
  handleSearch()
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

.search-form {
  margin-bottom: 20px;
}
</style>
