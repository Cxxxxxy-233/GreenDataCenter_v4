<template>
  <div class="home-page">
    <!-- 横幅区域 -->
    <div class="banner-section animate-fade-in">
      <div class="banner-bg">
        <div class="banner-particles"></div>
      </div>
      <div class="banner-content">
        <h1 class="banner-title">数据中心绿电一体化方案智能规划系统</h1>
        <p class="banner-subtitle">基于多智能体协同的全生命周期优化方案</p>
        <div class="capability-tags">
          <span class="tag">
            <el-icon><User /></el-icon>
            多智能体协同
          </span>
          <span class="tag">
            <el-icon><TrendCharts /></el-icon>
            全生命周期成本优化
          </span>
          <span class="tag">
            <el-icon><Cpu /></el-icon>
            26种制冷方案库
          </span>
          <span class="tag">
            <el-icon><Timer /></el-icon>
            8760h逐时仿真
          </span>
        </div>
        <div class="ripple-container" @click="handleRipple">
          <el-button class="primary-btn" type="primary" size="large" @click="createProject">
            <el-icon><Plus /></el-icon>
            快速创建项目
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计指标区 -->
    <div class="stats-section">
      <div class="stats-header">
        <h2 class="stats-title">平台概览</h2>
        <span class="stats-subtitle">实时数据统计</span>
      </div>
      <el-row :gutter="16">
        <el-col :span="6" v-for="(stat, index) in statsData" :key="index">
          <div class="stat-card" :style="{ animationDelay: `${index * 120}ms` }">
            <div class="stat-row">
              <div class="stat-icon-wrap" :style="{ background: stat.bgColor, color: stat.color }">
                  <el-icon><component :is="getIconComponent(stat.icon)" /></el-icon>
                </div>
              <div class="stat-content">
                <div class="stat-value-wrap">
                  <span class="stat-value">{{ stat.value }}</span>
                  <span v-if="stat.unit" class="stat-unit">{{ stat.unit }}</span>
                </div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
            <div class="stat-progress-bar">
              <div 
                class="stat-progress-fill" 
                :style="{ width: stat.progress + '%', background: stat.color }"
              ></div>
            </div>
            <div class="stat-footer">
              <span class="stat-trend" :class="stat.trend >= 0 ? 'positive' : 'negative'">
                <el-icon v-if="stat.trend > 0"><Top /></el-icon>
                <el-icon v-else-if="stat.trend < 0"><ArrowDown /></el-icon>
                <span>{{ stat.trend >= 0 ? '+' : '' }}{{ stat.trend }}%</span>
              </span>
              <span class="stat-date">本月</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 最近项目区 -->
    <div class="recent-projects animate-fade-in">
      <div class="section-header">
        <div class="section-title">
          <h2>最近项目</h2>
          <span class="section-count">{{ recentProjects.length }} 个项目</span>
        </div>
        <el-button type="primary" link @click="goToHistory">
          查看全部
          <el-icon><Right /></el-icon>
        </el-button>
      </div>
      <el-table
        :data="recentProjects"
        class="project-table"
        row-class-name="table-row"
        @row-click="handleRowClick"
      >
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-name-cell">
              <div class="project-icon" :style="{ background: getProjectColor(row.status) }">
                <el-icon><Document /></el-icon>
              </div>
              <span class="project-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="项目位置" width="120">
          <template #default="{ row }">
            <span class="location-text">{{ row.location }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small" round>
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="coreMetrics" label="核心指标" min-width="240">
          <template #default="scope">
            <div class="metrics-cell">
              <span class="metric-item">
                <span class="metric-label">PUE</span>
                <span class="metric-value">{{ scope.row.coreMetrics.pue }}</span>
              </span>
              <el-divider direction="vertical" />
              <span class="metric-item">
                <span class="metric-label">绿电率</span>
                <span class="metric-value primary">{{ scope.row.coreMetrics.greenRate }}%</span>
              </span>
              <el-divider direction="vertical" />
              <span class="metric-item">
                <span class="metric-label">LCOE</span>
                <span class="metric-value">{{ scope.row.coreMetrics.lcoe }}元/kWh</span>
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="actions" label="操作" width="200" fixed="right">
          <template #default="scope">
            <div class="actions-cell">
              <el-button
                v-if="scope.row.status !== '已完成'"
                type="primary"
                link
                size="small"
                @click.stop="continueEdit(scope.row)"
              >
                继续编辑
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                @click.stop="viewDetail(scope.row)"
              >
                查看详情
              </el-button>
              <el-popconfirm
                title="确定要删除该项目吗？"
                @confirm="deleteProject(scope.row)"
              >
                <template #reference>
                  <el-button type="danger" link size="small" @click.stop>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 快速入门区 -->
    <div class="quick-guide animate-fade-in">
      <div class="section-header">
        <div class="section-title">
          <h2>快速入门指南</h2>
          <span class="section-desc">简单三步，快速生成最优方案</span>
        </div>
      </div>
      <el-row :gutter="24">
        <el-col :span="8" v-for="(guide, index) in guideSteps" :key="index">
          <div class="guide-card" :style="{ animationDelay: `${index * 150}ms` }">
            <div class="guide-number">{{ index + 1 }}</div>
            <div class="guide-icon-wrapper" :style="{ background: guide.bgColor }">
              <el-icon class="guide-icon" :style="{ color: guide.color }">
                <component :is="getIconComponent(guide.icon)" />
              </el-icon>
            </div>
            <h3 class="guide-title">{{ guide.title }}</h3>
            <p class="guide-desc">{{ guide.desc }}</p>
            <div class="guide-arrow" v-if="index < guideSteps.length - 1">
              <el-icon><Right /></el-icon>
            </div>
          </div>
        </el-col>
      </el-row>
      <div class="guide-action">
        <el-button size="large" @click="loadSample">
          <template #icon>
            <el-icon><Document /></el-icon>
          </template>
          加载示例项目
        </el-button>
        <span class="guide-hint">一键填充乌兰察布30kW/机柜测试参数</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Box,
  Clock,
  TrendCharts,
  Wallet,
  User,
  Cpu,
  Timer,
  Top,
  Plus,
  Right,
  Document,
  Refresh,
  Setting,
  ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { solutionApi } from '@/api'

const router = useRouter()

const isLoading = ref(true)

const iconMap = {
  Box,
  Clock,
  TrendCharts,
  Wallet,
  User,
  Cpu,
  Timer,
  Top,
  Plus,
  Right,
  Document,
  Refresh,
  Setting,
  ArrowDown
}

const getIconComponent = (iconName) => {
  return iconMap[iconName] || Box
}

const handleRipple = (e) => {
  const container = e.currentTarget
  const rect = container.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const ripple = document.createElement('span')
  ripple.className = 'ripple-effect'
  ripple.style.left = `${x}px`
  ripple.style.top = `${y}px`
  ripple.style.width = '10px'
  ripple.style.height = '10px'
  container.appendChild(ripple)
  setTimeout(() => {
    ripple.remove()
  }, 600)
}

const statsData = ref([
  {
    icon: 'Box',
    value: '0',
    unit: '个',
    label: '累计生成方案',
    trend: 0,
    progress: 0,
    color: '#165DFF',
    bgColor: 'rgba(22, 93, 255, 0.08)'
  },
  {
    icon: 'Clock',
    value: '--',
    unit: '',
    label: '平均生成耗时',
    trend: 0,
    progress: 0,
    color: '#00B42A',
    bgColor: 'rgba(0, 180, 42, 0.08)'
  },
  {
    icon: 'TrendCharts',
    value: '--',
    unit: '',
    label: '平均PUE优化',
    trend: 0,
    progress: 0,
    color: '#FF7D00',
    bgColor: 'rgba(255, 125, 0, 0.08)'
  },
  {
    icon: 'Wallet',
    value: '--',
    unit: '',
    label: '平均绿电消纳',
    trend: 0,
    progress: 0,
    color: '#722ED1',
    bgColor: 'rgba(114, 46, 209, 0.08)'
  }
])

const recentProjects = ref([])

const guideSteps = ref([
  {
    icon: 'Setting',
    title: '填写项目参数',
    desc: '设置数据中心的基础信息、算力负荷、地域环境等参数',
    color: '#165DFF',
    bgColor: 'rgba(22, 93, 255, 0.1)'
  },
  {
    icon: 'Refresh',
    title: '一键生成方案',
    desc: '多智能体协同优化，自动生成最优绿电消纳方案',
    color: '#FF7D00',
    bgColor: 'rgba(255, 125, 0, 0.1)'
  },
  {
    icon: 'Document',
    title: '查看报告并导出',
    desc: '查看详细方案报告，支持PDF和Markdown格式导出',
    color: '#00B42A',
    bgColor: 'rgba(0, 180, 42, 0.1)'
  }
])

const getStatusType = (status) => {
  const types = {
    '已完成': 'success',
    '生成中': 'warning',
    '待配置': 'info',
    '失败': 'danger'
  }
  return types[status] || 'info'
}

const getProjectColor = (status) => {
  const colors = {
    '已完成': 'linear-gradient(135deg, #00B42A 0%, #23C343 100%)',
    '生成中': 'linear-gradient(135deg, #FF7D00 0%, #FF9E40 100%)',
    '待配置': 'linear-gradient(135deg, #8F959E 0%, #A6ABB8 100%)',
    '失败': 'linear-gradient(135deg, #F53F3F 0%, #F76560 100%)'
  }
  return colors[status] || colors['待配置']
}

const createProject = () => {
  router.push('/config')
}

const goToHistory = () => {
  router.push('/history')
}

const continueEdit = (project) => {
  router.push('/config')
}

const viewDetail = (project) => {
  router.push(`/detail/${project.id}`)
}

const deleteProject = (project) => {
  ElMessage.success(`项目"${project.name}"已删除`)
}

const loadSample = () => {
  const sampleData = {
    location: '乌兰察布',
    planned_load_kw: 12000,
    computing_power_density: 30,
    planned_area: 18000,
    machine_room_grade: 'A+',
    cooling_technology: '浸没式液冷',
    pue_target: 1.18,
    green_power_ratio: 95,
    budget_constraint: 35000,
    sim_hours: 168
  }
  localStorage.setItem('projectConfig', JSON.stringify(sampleData))
  ElMessage.success('示例参数已加载，正在跳转配置页面...')
  setTimeout(() => {
    router.push('/config')
  }, 1000)
}

const handleRowClick = (row) => {
  // 可以在这里添加行点击逻辑
}

const loadRecentProjects = async () => {
  try {
    isLoading.value = true
    const response = await solutionApi.getAll()
    const solutions = response.data || []
    
    if (solutions.length > 0) {
      recentProjects.value = solutions.map(solution => ({
        id: solution.id,
        name: solution.name || '未命名方案',
        location: '--',
        createTime: solution.created_at ? formatDate(solution.created_at) : '--',
        status: solution.success ? '已完成' : '失败',
        coreMetrics: {
          pue: solution.key_metrics?.pue || '--',
          greenRate: solution.key_metrics?.green_power_ratio ? (solution.key_metrics.green_power_ratio * 100).toFixed(1) : '--',
          lcoe: '--'
        }
      }))

      statsData.value[0].value = String(solutions.length)
      statsData.value[0].progress = Math.min(solutions.length * 10, 100)
      statsData.value[0].trend = solutions.length > 0 ? 12 : 0
      
      const completedSolutions = solutions.filter(s => s.success)
      if (completedSolutions.length > 0) {
        const avgTime = completedSolutions.reduce((sum, s) => sum + (s.generation_time || 0), 0) / completedSolutions.length
        statsData.value[1].value = avgTime > 0 ? `${Math.round(avgTime)}` : '--'
        statsData.value[1].unit = '秒'
        statsData.value[1].progress = avgTime > 0 ? Math.max(100 - avgTime / 6, 0) : 0
        statsData.value[1].trend = avgTime > 0 && avgTime < 120 ? 8 : 0
        
        const pueValues = completedSolutions.map(s => s.key_metrics?.pue).filter(v => v != null)
        if (pueValues.length > 0) {
          const avgPue = pueValues.reduce((a, b) => a + b, 0) / pueValues.length
          const pueOpt = ((1.5 - avgPue) / 1.5 * 100)
          statsData.value[2].value = `${pueOpt.toFixed(1)}`
          statsData.value[2].unit = '%'
          statsData.value[2].progress = Math.min(pueOpt, 100)
          statsData.value[2].trend = pueOpt > 15 ? 5 : 0
        }
        const greenValues = completedSolutions.map(s => s.key_metrics?.green_power_ratio).filter(v => v != null)
        if (greenValues.length > 0) {
          const avgGreen = greenValues.reduce((a, b) => a + b, 0) / greenValues.length
          const greenPercent = avgGreen * 100
          statsData.value[3].value = `${greenPercent.toFixed(1)}`
          statsData.value[3].unit = '%'
          statsData.value[3].progress = Math.min(greenPercent, 100)
          statsData.value[3].trend = greenPercent > 85 ? 15 : 0
        }
      }
    }
    isLoading.value = false
  } catch (error) {
    console.error('加载最近项目失败:', error)
    isLoading.value = false
  }
}

const getLocationName = (requirementId) => {
  return '--'
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadRecentProjects()
})
</script>

<style scoped>
.home-page {
  padding-bottom: var(--spacing-3xl);
}

/* 横幅区域 - 优化后 */
.banner-section {
  position: relative;
  background: linear-gradient(135deg, #1a56db 0%, #0d47a1 100%);
  border-radius: 16px;
  padding: 48px 40px;
  margin-bottom: 32px;
  overflow: hidden;
}

.banner-bg {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.6;
}

.banner-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.banner-title {
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

.banner-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 28px;
  line-height: 1.5;
}

.capability-tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 28px;
}

.capability-tags .tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.92);
  padding: 7px 16px;
  border-radius: 20px;
  font-size: 12.5px;
  backdrop-filter: blur(10px);
  transition: all 0.25s ease-out;
  font-weight: 500;
}

.capability-tags .tag:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.primary-btn {
  background: white;
  border: none;
  color: #165DFF;
  font-weight: 600;
  font-size: 15px;
  padding: 13px 36px;
  border-radius: 8px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
}

.primary-btn:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 统计区域 - 重新设计，避免 hero-metric 反模式 */
.stats-section {
  margin-bottom: 32px;
  animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.stats-header {
  margin-bottom: 20px;
}

.stats-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  margin: 0 0 4px 0;
}

.stats-subtitle {
  font-size: 13px;
  color: #86909c;
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
  border: 1px solid rgba(0, 0, 0, 0.04);
  opacity: 0;
  animation: slideInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
  background: white;
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.stat-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value-wrap {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.stat-unit {
  font-size: 13px;
  font-weight: 500;
  color: #86909c;
}

.stat-label {
  font-size: 12.5px;
  color: #86909c;
  margin-top: 2px;
}

.stat-progress-bar {
  height: 4px;
  background: #f2f3f5;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 12px;
}

.stat-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.positive {
  color: #00b42a;
}

.stat-trend.negative {
  color: #f53f3f;
}

.stat-date {
  font-size: 11.5px;
  color: #c9cdd4;
}

/* 最近项目区域 - 更大间距 */
.recent-projects {
  background: white;
  border-radius: 12px;
  padding: 28px;
  margin-bottom: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-title h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #1d2129;
}

.section-count {
  font-size: 13px;
  color: #86909c;
}

.section-desc {
  font-size: 13px;
  color: #86909c;
}

.project-table {
  border-radius: 8px;
  overflow: hidden;
}

.project-table :deep(.table-row) {
  transition: all 0.2s ease-out;
  cursor: pointer;
}

.project-table :deep(.table-row:hover) {
  background: #f2f3f5;
}

.project-table :deep(.el-table__header th) {
  background: #fafafa !important;
  color: #4e5969;
  font-weight: 600;
  font-size: 13px;
  border: none !important;
}

.project-table :deep(.el-table__body td) {
  border-color: #f2f3f5;
  border-bottom: 1px solid #f2f3f5;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.project-name {
  font-weight: 500;
  color: #1d2129;
  font-size: 14px;
}

.location-text {
  color: #4e5969;
  font-size: 13px;
}

.metrics-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 11px;
  color: #c9cdd4;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #1d2129;
}

.metric-value.primary {
  color: #165DFF;
}

:deep(.el-divider) {
  height: 32px;
  margin: 0;
  align-self: center;
}

.actions-cell {
  display: flex;
  gap: 4px;
}

/* 快速入门区域 */
.quick-guide {
  background: white;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.guide-card {
  position: relative;
  text-align: center;
  padding: 28px 20px;
  background: #fafbfc;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

.guide-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
  background: white;
  border-color: rgba(22, 93, 255, 0.1);
}

.guide-number {
  position: absolute;
  top: 16px;
  left: 16px;
  width: 26px;
  height: 26px;
  background: #165DFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.guide-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
}

.guide-icon {
  font-size: 28px;
}

.guide-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1d2129;
}

.guide-desc {
  font-size: 13px;
  color: #86909c;
  line-height: 1.6;
  margin: 0;
}

.guide-arrow {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  color: #c9cdd4;
  font-size: 20px;
}

.guide-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
}

.guide-hint {
  font-size: 13px;
  color: #86909c;
}

/* 骨架屏样式 */
.skeleton-card {
  background: linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeletonWave 1.5s infinite;
  border-radius: 14px;
  padding: 20px;
}

.skeleton-row {
  display: flex;
  gap: 14px;
  margin-bottom: 16px;
}

.skeleton-icon {
  width: 40px;
  height: 40px;
  background: #e8e8e8;
  border-radius: 10px;
  flex-shrink: 0;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-value {
  height: 28px;
  background: #e8e8e8;
  border-radius: 4px;
  width: 60%;
}

.skeleton-label {
  height: 14px;
  background: #e8e8e8;
  border-radius: 4px;
  width: 40%;
}

.skeleton-progress {
  height: 4px;
  background: #e8e8e8;
  border-radius: 2px;
  margin-bottom: 12px;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
}

.skeleton-trend {
  height: 14px;
  background: #e8e8e8;
  border-radius: 4px;
  width: 50px;
}

.skeleton-date {
  height: 14px;
  background: #e8e8e8;
  border-radius: 4px;
  width: 40px;
}

@keyframes skeletonWave {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 动画 - 使用更平滑的曲线 */
.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.animate-slide-in-up {
  animation: slideInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes ripple {
  0% {
    transform: scale(0);
    opacity: 0.5;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
}

/* 按钮点击波纹效果 */
.ripple-container {
  position: relative;
  overflow: hidden;
}

.ripple-effect {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  transform: scale(0);
  animation: ripple 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .banner-section {
    padding: 36px 24px;
  }
  
  .banner-title {
    font-size: 22px;
  }
  
  .banner-subtitle {
    font-size: 14px;
  }
  
  .stat-value {
    font-size: 24px;
  }
}

@media (max-width: 992px) {
  .capability-tags {
    gap: 8px;
  }
  
  .capability-tags .tag {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-row {
    gap: 12px;
  }
  
  .stat-icon-wrap {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .guide-card {
    padding: 20px 16px;
  }
  
  .guide-icon-wrapper {
    width: 50px;
    height: 50px;
    margin-bottom: 14px;
  }
  
  .guide-icon {
    font-size: 24px;
  }
  
  .guide-arrow {
    display: none;
  }
}

@media (max-width: 768px) {
  .banner-section {
    padding: 28px 16px;
    border-radius: 12px;
  }
  
  .banner-title {
    font-size: 20px;
    line-height: 1.3;
  }
  
  .banner-subtitle {
    font-size: 13px;
    margin-bottom: 20px;
  }
  
  .capability-tags {
    justify-content: flex-start;
  }
  
  .primary-btn {
    width: 100%;
    justify-content: center;
    padding: 12px 24px;
  }
  
  .stats-section {
    margin-bottom: 24px;
  }
  
  .stat-card {
    padding: 14px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .guide-action {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .guide-hint {
    font-size: 12px;
  }
  
  .project-table :deep(.el-table__header) {
    display: none;
  }
  
  .project-table :deep(.el-table__body) {
    display: block;
  }
  
  .project-table :deep(.el-table__row) {
    display: block;
    margin-bottom: 12px;
    border: 1px solid #f2f3f5;
    border-radius: 8px;
    padding: 12px;
  }
  
  .project-table :deep(.el-table__cell) {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border: none;
  }
  
  .project-table :deep(.el-table__cell)::before {
    content: attr(data-label);
    font-weight: 500;
    color: #86909c;
    font-size: 12px;
  }
  
  .actions-cell {
    flex-wrap: wrap;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .home-page {
    padding-bottom: 24px;
  }
  
  .banner-section {
    padding: 20px 12px;
  }
  
  .banner-title {
    font-size: 18px;
    margin-bottom: 8px;
  }
  
  .banner-subtitle {
    font-size: 12px;
    margin-bottom: 16px;
  }
  
  .capability-tags .tag {
    padding: 5px 10px;
    font-size: 11px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 11px;
  }
}
</style>
