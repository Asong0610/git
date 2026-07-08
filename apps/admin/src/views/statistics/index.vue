<template>
  <div class="statistics-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单数据统计</span>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :shortcuts="dateShortcuts"
          />
        </el-form-item>
        <el-form-item label="统计维度">
          <el-select v-model="searchForm.groupBy" style="width: 120px">
            <el-option label="按日" value="day" />
            <el-option label="按周" value="week" />
            <el-option label="按月" value="month" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出 Excel
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 时间趋势图表 -->
    <el-card class="chart-card">
      <template #header>
        <span>时间趋势</span>
      </template>
      <div ref="chartRef" class="chart-container" />
    </el-card>

    <!-- 按时间汇总表 -->
    <el-card class="table-card">
      <template #header>
        <span>按时间汇总</span>
      </template>
      <el-table :data="timeStats" border stripe show-summary :summary-method="getTimeSummary">
        <el-table-column prop="period" label="统计周期" min-width="140" />
        <el-table-column prop="borrow_count" label="借用次数" min-width="120" align="center" />
        <el-table-column prop="total_hours" label="累计时长(小时)" min-width="160" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.total_hours) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_revenue" label="营收(元)" min-width="140" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.total_revenue) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 按设备汇总表 -->
    <el-card class="table-card">
      <template #header>
        <span>按设备汇总</span>
      </template>
      <el-table :data="deviceStats" border stripe>
        <el-table-column prop="device_code" label="设备编号" min-width="120" />
        <el-table-column prop="device_name" label="设备名称" min-width="160" />
        <el-table-column prop="category" label="分类" min-width="100" />
        <el-table-column prop="borrow_count" label="借用次数" min-width="120" align="center" sortable />
        <el-table-column prop="total_hours" label="累计时长(小时)" min-width="160" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.total_hours) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_revenue" label="营收(元)" min-width="140" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.total_revenue) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import { getTimeStats, getDeviceStats, exportStatistics } from '../../api/order'

const chartRef = ref(null)
let chartInstance = null

const dateRange = ref([])
const searchForm = reactive({
  groupBy: 'day'
})

const timeStats = ref([])
const deviceStats = ref([])
const loading = ref(false)

const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [formatDate(start), formatDate(end)]
    }
  },
  {
    text: '最近一月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [formatDate(start), formatDate(end)]
    }
  },
  {
    text: '最近三月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 60 * 60 * 1000)
      return [formatDate(start), formatDate(end)]
    }
  }
]

function formatDate(date) {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatNumber(value) {
  if (value === undefined || value === null) return '0.00'
  return Number(value).toFixed(2)
}

function initChart() {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
  }
}

function resizeChart() {
  chartInstance?.resize()
}

function renderChart() {
  if (!chartInstance) return

  const periods = timeStats.value.map(item => item.period)
  const counts = timeStats.value.map(item => item.borrow_count)
  const revenues = timeStats.value.map(item => Number(item.total_revenue) || 0)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['借用次数', '营收(元)']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: periods
    },
    yAxis: [
      {
        type: 'value',
        name: '次数'
      },
      {
        type: 'value',
        name: '元'
      }
    ],
    series: [
      {
        name: '借用次数',
        type: 'bar',
        data: counts
      },
      {
        name: '营收(元)',
        type: 'line',
        yAxisIndex: 1,
        data: revenues
      }
    ]
  }

  chartInstance.setOption(option, true)
}

function getTimeSummary(param) {
  const { columns, data } = param
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }
    const values = data.map(item => Number(item[column.property]) || 0)
    if (column.property === 'borrow_count') {
      sums[index] = values.reduce((a, b) => a + b, 0)
    } else if (column.property === 'total_hours') {
      sums[index] = values.reduce((a, b) => a + b, 0).toFixed(2)
    } else if (column.property === 'total_revenue') {
      sums[index] = '¥' + values.reduce((a, b) => a + b, 0).toFixed(2)
    } else {
      sums[index] = ''
    }
  })
  return sums
}

async function loadData() {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      group_by: searchForm.groupBy
    }

    const [timeRes, deviceRes] = await Promise.all([
      getTimeStats(params),
      getDeviceStats({
        start_date: dateRange.value[0],
        end_date: dateRange.value[1]
      })
    ])

    timeStats.value = timeRes || []
    deviceStats.value = deviceRes || []

    await nextTick()
    renderChart()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  loadData()
}

async function handleExport() {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      group_by: searchForm.groupBy
    }

    const res = await exportStatistics(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `statistics_${params.start_date}_${params.end_date}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)

  // 默认查询最近7天
  const end = new Date()
  const start = new Date()
  start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
  dateRange.value = [formatDate(start), formatDate(end)]
  loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})
</script>

<style scoped>
.statistics-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 0;
}

.chart-card .chart-container {
  width: 100%;
  height: 400px;
}
</style>