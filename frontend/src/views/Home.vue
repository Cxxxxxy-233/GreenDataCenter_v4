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
        <el-button class="primary-btn" type="primary" size="large" @click="createProject">
          <el-icon><Plus /></el-icon>
          快速创建项目
        </el-button>
      </div>
    </div>

    <!-- 统计指标区 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6" v-for="(stat, index) in statsData" :key="index">
          <div class="stat-card animate-slide-in-up" :style="{ animationDelay: `${index * 100}ms` }">
            <div class="stat-header">
              <div class="stat-icon" :style="{ background: stat.color }">
                <el-icon><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><Top /></el-icon>
                <span>{{ Math.abs(stat.trend) }}%</span>
              </div>
            </div>
            <div class="stat-body">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="stat-footer">
              <span class="stat-period">较上月</span>
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
                <component :is="guide.icon" />
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
  Setting
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { solutionApi } from '@/api'

const router = useRouter()

const statsData = ref([
  {
    icon: 'Box',
    value: '0',
    label: '累计生成方案数',
    trend: 0,
    color: 'linear-gradient(135deg, #165DFF 0%, #4080FF 100%)'
  },
  {
    icon: 'Clock',
    value: '--',
    label: '平均方案生成时间',
    trend: 0,
    color: 'linear-gradient(135deg, #00B42A 0%, #23C343 100%)'
  },
  {
    icon: 'TrendCharts',
    value: '--',
    label: '平均PUE优化率',
    trend: 0,
    color: 'linear-gradient(135deg, #FF7D00 0%, #FF9E40 100%)'
  },
  {
    icon: 'Wallet',
    value: '--',
    label: '平均绿电消纳率',
    trend: 0,
    color: 'linear-gradient(135deg, #722ED1 0%, #9254DE 100%)'
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
      const completedSolutions = solutions.filter(s => s.success)
      if (completedSolutions.length > 0) {
        const avgTime = completedSolutions.reduce((sum, s) => sum + (s.generation_time || 0), 0) / completedSolutions.length
        statsData.value[1].value = avgTime > 0 ? `${Math.round(avgTime)}s` : '--'
        const pueValues = completedSolutions.map(s => s.key_metrics?.pue).filter(v => v != null)
        if (pueValues.length > 0) {
          const avgPue = pueValues.reduce((a, b) => a + b, 0) / pueValues.length
          statsData.value[2].value = `${((1.5 - avgPue) / 1.5 * 100).toFixed(1)}%`
        }
        const greenValues = completedSolutions.map(s => s.key_metrics?.green_power_ratio).filter(v => v != null)
        if (greenValues.length > 0) {
          const avgGreen = greenValues.reduce((a, b) => a + b, 0) / greenValues.length
          statsData.value[3].value = `${(avgGreen * 100).toFixed(1)}%`
        }
      }
    }
  } catch (error) {
    console.error('加载最近项目失败:', error)
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

/* 横幅区域 */
.banner-section {
  position: relative;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border-radius: var(--radius-lg);
  padding: var(--spacing-3xl);
  margin-bottom: var(--spacing-xl);
  overflow: hidden;
}

.banner-bg {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

.banner-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.banner-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: white;
  margin-bottom: var(--spacing-md);
  letter-spacing: 1px;
}

.banner-subtitle {
  font-size: var(--font-size-md);
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: var(--spacing-xl);
}

.capability-tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.capability-tags .tag {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: rgba(255, 255, 255, 0.15);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  backdrop-filter: blur(10px);
  transition: all var(--transition-fast);
}

.capability-tags .tag:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.primary-btn {
  background: var(--accent-color);
  border: none;
  color: white;
  font-weight: 600;
  padding: 12px 32px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.primary-btn:hover {
  background: var(--accent-light);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 125, 0, 0.3);
}

/* 统计区域 */
.stats-section {
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  background: var(--bg-container);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  color: white;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.stat-trend.up {
  color: var(--success-color);
  background: var(--success-bg);
}

.stat-trend.down {
  color: var(--danger-color);
  background: var(--danger-bg);
}

.stat-body {
  margin-bottom: var(--spacing-sm);
}

.stat-value {
  font-size: var(--font-size-4xl);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-top: var(--spacing-xs);
}

.stat-footer {
  font-size: var(--font-size-xs);
  color: var(--text-placeholder);
}

/* 最近项目区域 */
.recent-projects {
  background: var(--bg-container);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.section-title {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.section-title h2 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin: 0;
}

.section-count {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.section-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.project-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.project-table :deep(.table-row) {
  transition: all var(--transition-fast);
  cursor: pointer;
}

.project-table :deep(.table-row:hover) {
  background: var(--primary-bg);
}

.project-table :deep(.el-table__header th) {
  background: var(--bg-page) !important;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: var(--font-size-sm);
  border: none !important;
}

.project-table :deep(.el-table__body td) {
  border-color: var(--border-light);
  border-bottom: 1px solid var(--border-light);
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.project-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-md);
}

.project-name {
  font-weight: 500;
  color: var(--text-primary);
}

.location-text {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.metrics-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: var(--font-size-xs);
  color: var(--text-placeholder);
}

.metric-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.metric-value.primary {
  color: var(--primary-color);
}

:deep(.el-divider) {
  height: 32px;
  margin: 0;
  align-self: center;
}

.actions-cell {
  display: flex;
  gap: var(--spacing-xs);
}

/* 快速入门区域 */
.quick-guide {
  background: var(--bg-container);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.guide-card {
  position: relative;
  text-align: center;
  padding: var(--spacing-2xl);
  background: var(--bg-page);
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);
}

.guide-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.guide-number {
  position: absolute;
  top: var(--spacing-lg);
  left: var(--spacing-lg);
  width: 28px;
  height: 28px;
  background: var(--primary-color);
  color: white;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.guide-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--spacing-lg);
}

.guide-icon {
  font-size: var(--font-size-3xl);
}

.guide-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.guide-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0;
}

.guide-arrow {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-placeholder);
  font-size: var(--font-size-xl);
}

.guide-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-2xl);
}

.guide-hint {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 动画 */
.animate-fade-in {
  animation: fadeIn var(--transition-normal) ease-out;
}

.animate-slide-in-up {
  animation: slideInUp var(--transition-normal) ease-out forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
