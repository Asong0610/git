<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="用户ID" width="320" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deposit_balance" label="押金余额" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.deposit_balance }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '已封禁' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="warning" link @click="handleAdjustDeposit(row)">
              <el-icon><Wallet /></el-icon>
              调账
            </el-button>
          </template>
        </el-table-column>
      </el-table>
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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// TODO: 实现用户管理逻辑
// 由于后端用户列表 API 暂未实现，此页面暂时显示占位内容
const tableData = ref([])
const loading = ref(false)
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
    // TODO: 调用后端 API
    ElMessage.success('调账成功')
    adjustVisible.value = false
  } catch (error) {
    ElMessage.error('调账失败')
  } finally {
    adjustLoading.value = false
  }
}
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
</style>
