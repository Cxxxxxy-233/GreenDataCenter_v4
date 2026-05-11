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
  padding-bottom: var(--spacing-3xl);
}

/* Hero区域 - 科技智能风设计 */
.hero-section {
  position: relative;
  min-height: 300px;
  background: linear-gradient(135deg, #05161a 0%, #0a1f18 30%, #0d2818 60%, #0f3d2e 100%);
  border-radius: var(--radius-xl);
  margin-bottom: var(--spacing-2xl);
  overflow: hidden;
  box-shadow: 0 25px 80px rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.1);
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -25%;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.12) 0%, rgba(16, 185, 129, 0.02) 50%, transparent 70%);
  animation: pulseGlow 8s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
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
}

.flow-path {
  fill: none;
  stroke: url(#lineGradient);
  stroke-width: 1.5;
  stroke-dasharray: 8 4;
  animation: flowDash 20s linear infinite;
  opacity: 0.3;
}

.flow-path-1 {
  animation-duration: 25s;
}

/* SVG阶段背景样式 */
.phase-bg-primary {
  fill: rgba(16, 185, 129, 0.08);
}

.phase-bg-warning {
  fill: rgba(245, 158, 11, 0.06);
}

.phase-bg-accent {
  fill: rgba(6, 182, 212, 0.06);
}

.phase-bg-accent-light {
  fill: rgba(6, 182, 212, 0.04);
}

/* SVG关系标签样式 */
.relation-tag-primary rect {
  fill: rgba(16, 185, 129, 0.2);
}

.relation-tag-primary text {
  fill: var(--primary-color);
}

.relation-tag-warning rect {
  fill: rgba(245, 158, 11, 0.2);
}

.relation-tag-warning text {
  fill: var(--warning-color);
}

.relation-tag-accent rect {
  fill: rgba(6, 182, 212, 0.2);
}

.relation-tag-accent text {
  fill: var(--accent-color);
}

.flow-path-2 {
  animation-duration: 20s;
  animation-delay: -5s;
}

.flow-path-3 {
  animation-duration: 30s;
  animation-delay: -10s;
}

@keyframes flowDash {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -1000;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  padding: 48px 40px;
  text-align: center;
}

/* 标语区 */
.hero-headline {
  margin-bottom: 36px;
}

.main-title {
  font-size: 42px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 16px;
  letter-spacing: 2px;
  position: relative;
}

.main-title::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 4px;
  background: linear-gradient(90deg, transparent, #22C55E, transparent);
  border-radius: 2px;
}

.sub-title {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 工作流可视化区 */
.workflow-visualization {
  position: relative;
  max-width: 1000px;
  margin: 0 auto 36px;
}

.workflow-container {
  position: relative;
}

.workflow-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.connector {
  stroke-width: 2;
  fill: none;
  stroke-dasharray: 8 4;
  animation: flowAnimation 1.5s linear infinite;
}

.connector-green {
  stroke: #22C55E;
  opacity: 0.8;
}

.connector-orange {
  stroke: #F97316;
  opacity: 0.8;
  animation-delay: 0.3s;
}

.connector-cyan {
  stroke: #00cec9;
  opacity: 0.8;
  animation-delay: 0.6s;
}

@keyframes flowAnimation {
  0% {
    stroke-dashoffset: 12;
  }
  100% {
    stroke-dashoffset: 0;
  }
}

.flow-label {
  font-size: 10px;
  fill: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.phase-label {
  font-size: 11px;
  fill: rgba(255, 255, 255, 0.4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.flow-direction {
  font-size: 16px;
  fill: rgba(255, 255, 255, 0.3);
  font-weight: 300;
}

.relation-tag {
  opacity: 0.9;
}

.workflow-nodes {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.node-row {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70px;
}

.core-row {
  margin-top: 22px;
  gap: 165px;
}

.expert-row {
  gap: 265px;
}

.debate-row {
  gap: 130px;
}

.flow-indicator {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 6px 0;
  margin: 2px 0;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.indicator-line {
  width: 24px;
  height: 3px;
  border-radius: 2px;
}

.indicator-line.green {
  background: var(--primary-color);
}

.indicator-line.orange {
  background: var(--warning-color);
}

.indicator-line.cyan {
  background: var(--accent-color);
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.indicator-dot.green {
  background: var(--primary-color);
  box-shadow: 0 0 8px var(--primary-glow);
}

.indicator-dot.orange {
  background: var(--warning-color);
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
}

.indicator-dot.cyan {
  background: var(--accent-color);
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.5);
}

.indicator-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.workflow-node {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.02) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  animation: nodeAppear 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  opacity: 0;
}

@keyframes nodeAppear {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.workflow-node::before {
  content: '';
  position: absolute;
  inset: -1px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, transparent 50%, rgba(6, 182, 212, 0.2) 100%);
  border-radius: var(--radius-lg);
  opacity: 0;
  transition: opacity var(--transition-normal);
  z-index: -1;
}

.workflow-node:hover,
.workflow-node.active {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
  border-color: rgba(16, 185, 129, 0.5);
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 40px rgba(16, 185, 129, 0.25), 0 0 0 1px rgba(16, 185, 129, 0.1);
}

.workflow-node:hover::before,
.workflow-node.active::before {
  opacity: 1;
}

.workflow-node.core {
  min-width: 140px;
}

.workflow-node.expert {
  min-width: 130px;
}

.workflow-node.debate {
  min-width: 140px;
}

.node-icon {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: linear-gradient(145deg, var(--primary-color) 0%, #047857 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
  transition: all var(--transition-fast);
}

.node-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
  border-radius: var(--radius-md);
}

.workflow-node:hover .node-icon,
.workflow-node.active .node-icon {
  transform: scale(1.1);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5), 0 0 20px rgba(16, 185, 129, 0.3);
}

.node-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.node-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.node-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.node-tooltip {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(34, 197, 94, 0.5);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  z-index: 10;
  backdrop-filter: blur(8px);
}

.node-tooltip::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid rgba(34, 197, 94, 0.5);
}

/* 行动引导区 */
.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-btn {
  min-width: 160px;
  height: 48px;
  font-size: 16px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.primary-action {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  border: none;
  color: white;
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.3);
}

.primary-action:hover {
  background: linear-gradient(135deg, #16A34A, #15803D);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(34, 197, 94, 0.4);
}

.secondary-action {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.secondary-action:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

/* 统计区域 */
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
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  cursor: default;
  border: 1px solid rgba(16, 185, 129, 0.08);
  opacity: 0;
  animation: slideInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.2);
}

.stat-card:hover::before {
  opacity: 1;
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

/* 最近项目区域 */
.recent-projects {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-2xl);
  box-shadow: var(--shadow-sm);
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
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.guide-card {
  position: relative;
  text-align: center;
  padding: var(--spacing-2xl) var(--spacing-lg);
  background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
  border-radius: var(--radius-xl);
  transition: all var(--transition-normal);
  border: 1px solid rgba(16, 185, 129, 0.08);
  overflow: hidden;
}

.guide-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
  transition: width var(--transition-normal);
}

.guide-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 40px rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.25);
}

.guide-card:hover::before {
  width: 100%;
}

.guide-number {
  position: absolute;
  top: var(--spacing-md);
  left: var(--spacing-md);
  width: 28px;
  height: 28px;
  background: linear-gradient(145deg, var(--primary-color) 0%, #047857 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.guide-icon-wrapper {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
  transition: all var(--transition-fast);
}

.guide-card:hover .guide-icon-wrapper {
  transform: scale(1.1);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.25);
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

.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* 响应式适配 */
@media (max-width: 992px) {
  .hero-section {
    min-height: auto;
    padding: var(--spacing-xl) var(--spacing-lg);
  }

  .main-title {
    font-size: 2rem;
  }

  .sub-title {
    font-size: 0.875rem;
  }

  .workflow-nodes {
    gap: 10px;
  }

  .node-row {
    flex-wrap: wrap;
    gap: 16px;
    height: auto;
    min-height: 70px;
  }

  .core-row {
    gap: 60px;
  }

  .expert-row {
    gap: 60px;
  }

  .debate-row {
    gap: 50px;
  }

  .workflow-node {
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .node-icon {
    width: 30px;
    height: 30px;
    font-size: 14px;
  }

  .node-name {
    font-size: 0.8125rem;
  }

  .node-desc {
    font-size: 0.625rem;
  }

  .flow-indicator {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .hero-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .action-btn {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .main-title {
    font-size: 1.75rem;
    letter-spacing: 1px;
  }

  .hero-headline {
    margin-bottom: var(--spacing-xl);
  }

  .workflow-visualization {
    display: none;
  }

  .mobile-workflow {
    display: block;
    margin-top: var(--spacing-xl);
  }

  .mobile-workflow-title {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: var(--spacing-md);
    text-align: center;
  }

  .mobile-workflow-steps {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--spacing-sm);
  }

  .mobile-step {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.9);
  }

  .mobile-step .step-num {
    width: 18px;
    height: 18px;
    background: var(--primary-color);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 600;
  }

  .guide-card {
    padding: var(--spacing-xl) var(--spacing-md);
  }

  .guide-icon-wrapper {
    width: 50px;
    height: 50px;
    margin-bottom: var(--spacing-md);
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
    text-align: center;
  }

  .guide-hint {
    font-size: 0.75rem;
  }

  .project-table :deep(.el-table__header) {
    display: none;
  }

  .stats-section {
    margin-bottom: var(--spacing-xl);
  }
}
</style>
