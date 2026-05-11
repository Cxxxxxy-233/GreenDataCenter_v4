<template>
  <div class="home-page">
    <!-- 全新Hero区域 - 工作流可视化 -->
    <div class="hero-section">
      <div class="hero-bg">
        <!-- 粒子背景 -->
        <canvas ref="particleCanvas" class="particle-canvas"></canvas>
        <!-- 流动线条背景 -->
        <svg class="flow-lines" viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid slice">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" :stop-color="primaryColor" stop-opacity="0"/>
              <stop offset="50%" :stop-color="primaryColor" stop-opacity="1"/>
              <stop offset="100%" :stop-color="primaryColor" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <path class="flow-path flow-path-1" d="M0,300 Q300,200 600,300 T1200,300" fill="none"/>
          <path class="flow-path flow-path-2" d="M0,350 Q400,250 800,350 T1200,300" fill="none"/>
          <path class="flow-path flow-path-3" d="M0,280 Q350,380 700,280 T1200,320" fill="none"/>
        </svg>
      </div>

      <div class="hero-content">
        <!-- 标语区 -->
        <div class="hero-headline">
          <h1 class="main-title">智能规划，绿电未来</h1>
          <p class="sub-title">基于多智能体协同的数据中心绿电一体化方案智能规划系统</p>
        </div>





        <!-- 行动引导区 -->
        <div class="hero-actions">
          <el-button class="action-btn primary-action" type="primary" size="large" @click="createProject">
            <el-icon><Plus /></el-icon>
            开始规划
          </el-button>
          <el-button class="action-btn secondary-action" size="large" @click="viewSample">
            <el-icon><Document /></el-icon>
            查看示例方案
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
import { ref, onMounted, onUnmounted } from 'vue'
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
  ArrowDown,
  Edit,
  Coin,
  Sunny,
  Odometer,
  ChatDotRound,
  SetUp,
  Files,
  Download
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { solutionApi } from '@/api'

const router = useRouter()
const particleCanvas = ref(null)
const activeNode = ref(null)
let animationFrame = null
let particles = []

const isLoading = ref(true)

const primaryColor = '#10B981'
const warningColor = '#F59E0B'
const accentColor = '#06B6D4'

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
  ArrowDown,
  Edit,
  Coin,
  Sunny,
  Odometer,
  ChatDotRound,
  SetUp,
  Files,
  Download
}

const getIconComponent = (iconName) => {
  return iconMap[iconName] || Box
}



class Particle {
  constructor(canvas) {
    this.canvas = canvas
    this.reset()
  }

  reset() {
    this.x = Math.random() * this.canvas.width
    this.y = Math.random() * this.canvas.height
    this.size = Math.random() * 2 + 0.5
    this.speedX = Math.random() * 0.5 - 0.25
    this.speedY = Math.random() * 0.5 - 0.25
    this.opacity = Math.random() * 0.5 + 0.1
  }

  update() {
    this.x += this.speedX
    this.y += this.speedY

    if (this.x < 0 || this.x > this.canvas.width || this.y < 0 || this.y > this.canvas.height) {
      this.reset()
    }
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(16, 185, 129, ${this.opacity})`
    ctx.fill()
  }
}

const initParticles = () => {
  if (!particleCanvas.value) return

  const canvas = particleCanvas.value
  const ctx = canvas.getContext('2d')

  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight

  particles = []
  for (let i = 0; i < 80; i++) {
    particles.push(new Particle(canvas))
  }

  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach(particle => {
      particle.update()
      particle.draw(ctx)
    })

    animationFrame = requestAnimationFrame(animate)
  }

  animate()
}

const handleResize = () => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  initParticles()
}

const createProject = () => {
  router.push('/config')
}

const viewSample = () => {
  router.push('/detail/mock-solution-001')
}

const statsData = ref([
  {
    icon: 'Box',
    value: '0',
    unit: '个',
    label: '累计生成方案',
    trend: 0,
    progress: 0,
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.08)'
  },
  {
    icon: 'Clock',
    value: '--',
    unit: '',
    label: '平均生成耗时',
    trend: 0,
    progress: 0,
    color: '#06B6D4',
    bgColor: 'rgba(6, 182, 212, 0.08)'
  },
  {
    icon: 'TrendCharts',
    value: '--',
    unit: '',
    label: '平均PUE优化',
    trend: 0,
    progress: 0,
    color: '#F59E0B',
    bgColor: 'rgba(245, 158, 11, 0.08)'
  },
  {
    icon: 'Wallet',
    value: '--',
    unit: '',
    label: '平均绿电消纳',
    trend: 0,
    progress: 0,
    color: '#059669',
    bgColor: 'rgba(5, 150, 105, 0.08)'
  }
])

const recentProjects = ref([])

const guideSteps = ref([
  {
    icon: 'Setting',
    title: '填写项目参数',
    desc: '设置数据中心的基础信息、算力负荷、地域环境等参数',
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.1)'
  },
  {
    icon: 'Refresh',
    title: '一键生成方案',
    desc: '多智能体协同优化，自动生成最优绿电消纳方案',
    color: '#F59E0B',
    bgColor: 'rgba(245, 158, 11, 0.1)'
  },
  {
    icon: 'Document',
    title: '查看报告并导出',
    desc: '查看详细方案报告，支持PDF和Markdown格式导出',
    color: '#06B6D4',
    bgColor: 'rgba(6, 182, 212, 0.1)'
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

const handleRowClick = (row) => {}

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
    }
    isLoading.value = false
  } catch (error) {
    console.error('加载最近项目失败:', error)
    isLoading.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadRecentProjects()
  setTimeout(initParticles, 100)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: var(--spacing-4xl);
}

.hero-section {
  position: relative;
  min-height: 360px;
  background:
    radial-gradient(circle at 20% 20%, color-mix(in oklab, var(--primary-light) 16%, transparent), transparent 26%),
    radial-gradient(circle at 80% 30%, color-mix(in oklab, var(--accent-color) 16%, transparent), transparent 24%),
    linear-gradient(135deg, var(--bg-stage) 0%, color-mix(in oklab, var(--bg-stage-soft) 88%, var(--primary-dark) 12%) 50%, color-mix(in oklab, var(--bg-stage) 82%, var(--primary-color) 18%) 100%);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid color-mix(in oklab, var(--primary-color) 18%, transparent);
}

.hero-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.03) 45%, transparent 100%);
  pointer-events: none;
}

.hero-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.flow-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.9;
}

.flow-path {
  fill: none;
  stroke: url(#lineGradient);
  stroke-width: 1.25;
  stroke-dasharray: 10 8;
  animation: flowDash 24s linear infinite;
  opacity: 0.28;
}

.flow-path-1 {
  animation-duration: 28s;
}

.flow-path-2 {
  animation-duration: 22s;
  animation-delay: -4s;
}

.flow-path-3 {
  animation-duration: 30s;
  animation-delay: -8s;
}

@keyframes flowDash {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -1000; }
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  min-height: 360px;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 42px 42px 40px;
  text-align: left;
}

.hero-headline {
  max-width: 640px;
  margin-bottom: 28px;
}

.main-title {
  font-size: 40px;
  font-weight: 700;
  color: rgba(244, 252, 246, 0.98);
  margin-bottom: 14px;
  letter-spacing: -0.03em;
  line-height: 1.08;
  max-width: 20ch;
  white-space: nowrap;
}

.sub-title {
  font-size: 15px;
  color: rgba(232, 244, 237, 0.76);
  max-width: 62ch;
  line-height: 1.7;
  margin: 0;
}

.hero-actions {
  display: flex;
  justify-content: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.action-btn {
  min-width: 152px;
  height: 46px;
  font-size: 15px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-fast);
}

.primary-action {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: rgba(249, 253, 250, 0.98);
  border: 1px solid color-mix(in oklab, var(--primary-light) 30%, transparent);
  box-shadow: 0 14px 30px color-mix(in oklab, var(--primary-color) 26%, transparent);
}

.primary-action:hover {
  box-shadow: 0 18px 36px color-mix(in oklab, var(--primary-color) 30%, transparent);
}

.secondary-action {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(232, 244, 237, 0.18);
  color: rgba(240, 250, 243, 0.9);
  backdrop-filter: blur(8px);
}

.secondary-action:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(240, 250, 243, 0.28);
}

.stats-section {
  padding: 4px 2px 0;
}

.stats-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 18px;
}

.stats-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.stats-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-card {
  position: relative;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%) 100%);
  border-radius: 20px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  cursor: default;
  border: 1px solid var(--border-light);
  overflow: hidden;
  min-height: 156px;
}

.stat-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 36%);
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.24);
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
  color: var(--text-primary);
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.stat-unit {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.stat-label {
  font-size: 12.5px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.stat-progress-bar {
  height: 4px;
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--border-light) 12%);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.stat-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1);
}

.stat-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.positive {
  color: var(--success-color);
}

.stat-trend.negative {
  color: var(--danger-color);
}

.stat-date {
  font-size: 11.5px;
  color: var(--text-placeholder);
}

.recent-projects {
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border-radius: 22px;
  padding: 22px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.section-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-title h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.section-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.section-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.project-table {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.project-table :deep(.table-row) {
  transition: background var(--transition-fast);
  cursor: pointer;
}

.project-table :deep(.table-row:hover) {
  background: color-mix(in oklab, var(--primary-color) 6%, var(--bg-card));
}

.project-table :deep(.el-table__header th) {
  background: color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%) !important;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
  border: none !important;
}

.project-table :deep(.el-table__body td) {
  border-color: var(--border-light);
  border-bottom: 1px solid var(--border-light);
  background: transparent;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(248, 253, 249, 0.98);
  font-size: 16px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.16);
}

.project-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.location-text {
  color: var(--text-secondary);
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
  padding: 2px 0;
}

.metric-label {
  font-size: 11px;
  color: var(--text-placeholder);
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.metric-value.primary {
  color: var(--primary-dark);
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

.quick-guide {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--accent-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--accent-color) 6%) 100%);
  border-radius: 22px;
  padding: 22px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.guide-card {
  position: relative;
  text-align: center;
  padding: 26px 18px 24px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border-radius: 20px;
  transition: all var(--transition-normal);
  border: 1px solid var(--border-light);
  overflow: hidden;
  min-height: 220px;
}

.guide-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top center, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 32%);
  pointer-events: none;
}

.guide-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
}

.guide-number {
  position: absolute;
  top: 14px;
  left: 14px;
  width: 30px;
  height: 30px;
  background: color-mix(in oklab, var(--primary-color) 16%, var(--bg-card));
  color: var(--primary-dark);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 24%, transparent);
}

.guide-icon-wrapper {
  position: relative;
  width: 62px;
  height: 62px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.22);
  transition: all var(--transition-fast);
}

.guide-card:hover .guide-icon-wrapper {
  transform: translateY(-1px);
}

.guide-icon {
  font-size: 28px;
}

.guide-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.guide-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.guide-arrow {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-placeholder);
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
  color: var(--text-secondary);
}

@media (max-width: 992px) {
  .hero-section {
    min-height: auto;
  }

  .hero-content {
    min-height: auto;
    padding: 34px 28px;
  }

  .main-title {
    font-size: 34px;
  }

  .stats-section :deep(.el-col) {
    margin-bottom: 16px;
  }

  .recent-projects,
  .quick-guide {
    padding: 18px;
  }

  .hero-actions {
    width: 100%;
  }

  .action-btn {
    min-width: 0;
  }
}

@media (max-width: 768px) {
  .main-title {
    font-size: 28px;
  }

  .hero-headline {
    margin-bottom: 20px;
  }

  .guide-card {
    min-height: auto;
    padding: 22px 14px 20px;
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

  .guide-action {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: stretch;
  }

  .guide-hint {
    font-size: 12px;
    text-align: center;
  }

  .project-table :deep(.el-table__header) {
    display: none;
  }

  .section-header,
  .stats-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
