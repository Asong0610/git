<template>
  <div class="device-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加设备
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="设备码">
          <el-input v-model="searchForm.deviceCode" placeholder="请输入设备码" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="可用" value="available" />
            <el-option label="已借出" value="borrowed" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="searchForm.category" placeholder="请输入分类" clearable />
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
        <el-table-column prop="device_code" label="设备码" width="120" />
        <el-table-column prop="name" label="设备名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="location" label="位置" min-width="150" />
        <el-table-column prop="hourly_rate" label="费率(元/小时)" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.hourly_rate }}
          </template>
        </el-table-column>
        <el-table-column prop="deposit_amount" label="押金(元)" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.deposit_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="free_hours" label="免费时长(小时)" width="130" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="二维码" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="showQRCode(row.device_code)">
              <el-icon><Picture /></el-icon>
              二维码
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="设备码" prop="device_code">
          <el-input v-model="form.device_code" placeholder="请输入设备码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="form.category" placeholder="请输入分类" />
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入位置" />
        </el-form-item>
        <el-form-item label="费率(元/小时)" prop="hourly_rate">
          <el-input-number v-model="form.hourly_rate" :min="0" :precision="2" :step="0.5" />
        </el-form-item>
        <el-form-item label="押金(元)" prop="deposit_amount">
          <el-input-number v-model="form.deposit_amount" :min="0" :precision="2" :step="10" />
        </el-form-item>
        <el-form-item label="免费时长(小时)" prop="free_hours">
          <el-input-number v-model="form.free_hours" :min="0" :step="1" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="可用" value="available" />
            <el-option label="已借出" value="borrowed" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 二维码弹窗 -->
    <el-dialog
      v-model="qrDialogVisible"
      title="设备二维码"
      width="320px"
      center
    >
      <div style="text-align: center;">
        <img :src="qrCodeUrl" alt="二维码" style="width: 240px; height: 240px;" />
        <div style="margin-top: 16px; font-size: 18px; font-weight: bold;">{{ currentDeviceCode }}</div>
        <div style="margin-top: 8px; font-size: 14px; color: #666;">扫码可直接进入借出页面</div>
      </div>
      <template #footer>
        <el-button @click="qrDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { getDeviceList, createDevice, updateDevice, deleteDevice } from '../../api/device'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加设备')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

// QR Code
const qrDialogVisible = ref(false)
const currentDeviceCode = ref('')
const qrCodeUrl = ref('')

const showQRCode = (deviceCode) => {
  currentDeviceCode.value = deviceCode
  qrCodeUrl.value = `/api/v1/devices/${deviceCode}/qrcode`
  qrDialogVisible.value = true
}

const searchForm = reactive({
  deviceCode: '',
  status: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  device_code: '',
  name: '',
  category: '',
  location: '',
  hourly_rate: 0,
  deposit_amount: 0,
  free_hours: 2,
  status: 'available'
})

const rules = {
  device_code: [
    { required: true, message: '请输入设备码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' }
  ],
  hourly_rate: [
    { required: true, message: '请输入费率', trigger: 'blur' }
  ],
  deposit_amount: [
    { required: true, message: '请输入押金', trigger: 'blur' }
  ]
}

const getStatusType = (status) => {
  const map = {
    available: 'success',
    borrowed: 'warning',
    maintenance: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    available: '可用',
    borrowed: '已借出',
    maintenance: '维护中'
  }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchForm.deviceCode) params.device_code = searchForm.deviceCode
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.category) params.category = searchForm.category

    const res = await getDeviceList(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载设备列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.deviceCode = ''
  searchForm.status = ''
  searchForm.category = ''
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

const handleAdd = () => {
  dialogTitle.value = '添加设备'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑设备'
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除设备 "${row.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteDevice(row.device_code)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitLoading.value = true

    if (isEdit.value) {
      await updateDevice(form.device_code, form)
      ElMessage.success('更新成功')
    } else {
      await createDevice(form)
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadData()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  form.device_code = ''
  form.name = ''
  form.category = ''
  form.location = ''
  form.hourly_rate = 0
  form.deposit_amount = 0
  form.free_hours = 2
  form.status = 'available'
  formRef.value?.resetFields()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.device-management {
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
