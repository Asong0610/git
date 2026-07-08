<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="输入学号/姓名/手机号"
            clearable
            style="width: 260px;"
          />
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
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出用户表
          </el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="student_id" label="学号" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="phone" label="手机号" min-width="130">
          <template #default="{ row }">
            {{ maskPhone(row.phone) }}
          </template>
        </el-table-column>
        <el-table-column prop="deposit_balance" label="押金余额" min-width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.deposit_balance }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '冻结' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              :type="row.status === 'active' ? 'danger' : 'success'"
              link
              @click="handleFreeze(row)"
            >
              <el-icon>
                <component :is="row.status === 'active' ? Lock : Unlock" />
              </el-icon>
              {{ row.status === 'active' ? '冻结' : '解冻' }}
            </el-button>
            <el-button type="warning" link @click="handleResetSms(row)">
              <el-icon><Refresh /></el-icon>
              重置验证码
            </el-button>
            <el-button type="primary" link @click="handleAdjustDeposit(row)">
              <el-icon><Wallet /></el-icon>
              调账
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

    <!-- 调账对话框 -->
    <el-dialog v-model="adjustVisible" title="押金调账" width="500px">
      <el-form :model="adjustForm" label-width="100px">
        <el-form-item label="当前余额">
          <span>¥{{ currentUser?.deposit_balance }}</span>
        </el-form-item>
        <el-form-item label="调整金额">
          <el-input-number v-model="adjustForm.amount" :precision="2" :step="10" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="adjustForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" :loading="adjustLoading" @click="handleSubmitAdjust">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Wallet, Lock, Unlock } from '@element-plus/icons-vue'
import {
  getUserList,
  freezeUser,
  resetUserSms,
  exportUsers,
  adjustUserDeposit
} from '../../api/user'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const maskPhone = (phone) => {
  if (!phone || phone.length < 7) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const formatDateTime = (value) => {
  if (!value) return ''
  const date = new Date(value)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    const res = await getUserList(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
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

const handleFreeze = async (row) => {
  const isActive = row.status === 'active'
  const action = isActive ? 'freeze' : 'unfreeze'
  const message = isActive ? `确定要冻结用户 "${row.name || row.phone}" 吗？` : `确定要解冻用户 "${row.name || row.phone}" 吗？`

  try {
    await ElMessageBox.confirm(message, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await freezeUser(row.id, action)
    ElMessage.success(isActive ? '冻结成功' : '解冻成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(isActive ? '冻结失败' : '解冻失败')
    }
  }
}

const handleResetSms = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要重置用户 "${row.name || row.phone}" 的验证码吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await resetUserSms(row.id)
    ElMessage.success('验证码已重置')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置验证码失败')
    }
  }
}

const handleExport = async () => {
  try {
    const blob = await exportUsers()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `users_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 调账
const adjustVisible = ref(false)
const adjustLoading = ref(false)
const currentUser = ref(null)
const adjustForm = reactive({
  amount: 0,
  remark: ''
})

const handleAdjustDeposit = (row) => {
  currentUser.value = row
  adjustForm.amount = 0
  adjustForm.remark = ''
  adjustVisible.value = true
}

const handleSubmitAdjust = async () => {
  try {
    adjustLoading.value = true
    await adjustUserDeposit(currentUser.value.id, adjustForm.amount, adjustForm.remark)
    ElMessage.success('调账成功')
    adjustVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('调账失败')
  } finally {
    adjustLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.user-management {
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