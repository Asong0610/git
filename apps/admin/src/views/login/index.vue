<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <el-icon size="32" color="#409EFF"><Monitor /></el-icon>
          <h2>校园设备管理系统</h2>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        size="large"
      >
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            :prefix-icon="Phone"
          />
        </el-form-item>

        <el-form-item prop="smsCode">
          <div class="code-input">
            <el-input
              v-model="form.smsCode"
              placeholder="请输入验证码"
              :prefix-icon="Message"
            />
            <el-button
              type="primary"
              :disabled="countdown > 0"
              :loading="sendingCode"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? `${countdown}s 后重试` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="tips">
        <p>测试账号：13800138000</p>
        <p>验证码：发送后自动填入</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { sendSmsCode } from '../../api/auth'
import { ElMessage } from 'element-plus'
import { Phone, Message } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let countdownTimer = null

const form = reactive({
  phone: '13800138000',
  smsCode: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  smsCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为 6 位', trigger: 'blur' }
  ]
}

const handleSendCode = async () => {
  if (!form.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }

  try {
    sendingCode.value = true
    const res = await sendSmsCode(form.phone)
    console.log('sms response:', res)
    console.log('debug_code:', res.debug_code)
    
    // 开发环境自动填入验证码
    if (res.debug_code) {
      form.smsCode = res.debug_code
      ElMessage.success(`验证码已发送: ${res.debug_code}`)
    } else {
      ElMessage.success('验证码已发送')
    }

    // 开始倒计时
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error('发送验证码失败')
  } finally {
    sendingCode.value = false
  }
}

const handleLogin = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true
    
    await authStore.login(form.phone, form.smsCode)
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '登录失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.code-input {
  display: flex;
  gap: 12px;
  width: 100%;
}

.code-input .el-input {
  flex: 1;
}

.login-button {
  width: 100%;
}

.tips {
  margin-top: 20px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #909399;
}

.tips p {
  margin: 4px 0;
}
</style>
