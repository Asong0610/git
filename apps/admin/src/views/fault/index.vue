<template>
  <div class="fault-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>故障工单</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 160px;">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column label="工单ID" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ shortenId(row.id) }}
          </template>
        </el-table-column>
        <el-table-column prop="device_name" label="设备名称" min-width="150" />
        <el-table-column label="报修用户" min-width="140">
          <template #default="{ row }">
            {{ row.user_phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="故障描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="报修时间" min-width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleProcess(row)">
              <el-icon><Edit /></el-icon>
              处理
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

    <!-- 处理对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="处理工单"
      width="560px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="工单ID">
          <el-input :value="shortenId(currentRow?.id)" disabled />
        </el-form-item>
        <el-form-item label="设备名称">
          <el-input :value="currentRow?.device_name" disabled />
        </el-form-item>
        <el-form-item label="报修用户">
          <el-input :value="currentRow?.user_phone || '-'" disabled />
        </el-form-item>
        <el-form-item label="故障描述">
          <el-input :value="currentRow?.description" type="textarea" :rows="3" disabled />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择新状态" style="width: 100%;">
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="admin_remark">
          <el-input
            v-model="form.admin_remark"
            type="textarea"
            :rows="4"
            placeholder="请输入处理备注"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getFaultList, processFault } from '../../api/fault'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const currentRow = ref(null)

const searchForm = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  status: '',
  admin_remark: ''
})

const rules = {
  status: [
    { required: true, message: '请选择新状态', trigger: 'change' }
  ]
}

const statusMap = {
  pending: { text: '待处理', type: 'warning' },
  processing: { text: '处理中', type: 'primary' },
  resolved: { text: '已解决', type: 'success' },
  closed: { text: '已关闭', type: 'info' }
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
}

const getStatusText = (status) => {
  return statusMap[status]?.text || status
}

const shortenId = (id) => {
  if (!id) return ''
  return id.length > 12 ? `${id.slice(0, 12)}...` : id
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
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

    const res = await getFaultList(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载故障工单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
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

const handleProcess = (row) => {
  currentRow.value = { ...row }
  form.status = row.status === 'pending' ? 'processing' : row.status
  form.admin_remark = row.admin_remark || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value || !currentRow.value) return

  try {
    await formRef.value.validate()
    submitLoading.value = true

    await processFault(currentRow.value.id, {
      status: form.status,
      admin_remark: form.admin_remark
    })

    ElMessage.success('处理成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('处理失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const handleDialogClose = () => {
  currentRow.value = null
  form.status = ''
  form.admin_remark = ''
  formRef.value?.resetFields()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.fault-management {
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