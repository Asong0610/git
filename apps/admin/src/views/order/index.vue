<template>
  <div class="order-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单ID">
          <el-input v-model="searchForm.orderId" placeholder="请输入订单ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="进行中" value="active" />
            <el-option label="已归还" value="returned" />
            <el-option label="已取消" value="cancelled" />
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

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="订单ID" width="320" show-overflow-tooltip />
        <el-table-column prop="device_code" label="设备码" width="120" />
        <el-table-column prop="device_name" label="设备名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="borrowed_at" label="借出时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.borrowed_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="due_at" label="免费截止" width="180">
          <template #default="{ row }">
            {{ formatTime(row.due_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="returned_at" label="归还时间" width="180">
          <template #default="{ row }">
            {{ row.returned_at ? formatTime(row.returned_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="usage_fee" label="使用费(元)" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.usage_fee || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="600px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单ID" :span="2">
          {{ currentOrder.id }}
        </el-descriptions-item>
        <el-descriptions-item label="设备码">
          {{ currentOrder.device_code }}
        </el-descriptions-item>
        <el-descriptions-item label="设备名称">
          {{ currentOrder.device_name }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="使用费">
          ¥{{ currentOrder.usage_fee || '0.00' }}
        </el-descriptions-item>
        <el-descriptions-item label="借出时间">
          {{ formatTime(currentOrder.borrowed_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="免费截止">
          {{ formatTime(currentOrder.due_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="归还时间" :span="2">
          {{ currentOrder.returned_at ? formatTime(currentOrder.returned_at) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOrderList, getOrderDetail } from '../../api/order'

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const currentOrder = ref(null)

const searchForm = reactive({
  orderId: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const getStatusType = (status) => {
  const map = {
    active: 'warning',
    returned: 'success',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    active: '进行中',
    returned: '已归还',
    cancelled: '已取消'
  }
  return map[status] || status
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchForm.status) params.status = searchForm.status

    const res = await getOrderList(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载订单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.orderId = ''
  searchForm.status = ''
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

const handleView = async (row) => {
  try {
    const res = await getOrderDetail(row.id)
    currentOrder.value = res
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载订单详情失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.order-management {
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
