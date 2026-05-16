<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-bg">
        <canvas ref="particleCanvas" class="particle-canvas"></canvas>
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
        <div class="hero-headline">
          <h1 class="main-title">智能规划，绿电未来</h1>
          <p class="sub-title">面向数据中心建设的多智能体能源规划平台，协同生成绿电、制冷与供配电方案。</p>
        </div>

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

        <div class="hero-signal-strip" aria-label="system capabilities">
          <span><i></i>GREEN POWER</span>
          <span><i></i>COOLING LOOP</span>
          <span><i></i>POWER RELIABILITY</span>
        </div>
      </div>

      <div class="hero-model-stage" aria-label="3D data center model">
        <canvas ref="heroModelCanvas" class="hero-model-canvas"></canvas>
        <div class="hero-model-caption">
          <span class="caption-dot"></span>
          <span>360° digital twin</span>
        </div>
      </div>
    </div>

    <section class="dc-overview-section">
      <div class="section-orbit-line"></div>
      <div class="section-header dc-overview-header">
        <div class="section-title">
          <h2>数据中心 3D 构成总览</h2>
          <span class="section-desc">点击立体模型中的关键系统，快速理解数据中心建设中的能源、制冷、供配电与成本策略。</span>
        </div>
      </div>

      <div class="dc-overview-layout">
        <div class="dc-model-panel">
          <div class="dc-model-stage">
            <div class="stage-grid"></div>
            <div class="stage-glow stage-glow-primary"></div>
            <div class="stage-glow stage-glow-accent"></div>

            <div class="dc-model-shell">
              <button
                v-for="part in dataCenterParts"
                :key="part.id"
                type="button"
                class="dc-part"
                :class="[`part-${part.id}`, { 'is-active': activeDataCenterPart.id === part.id }]"
                @click="activeDataCenterPartId = part.id"
                :aria-pressed="activeDataCenterPart.id === part.id"
                :aria-label="`查看${part.name}的成本与策略信息`"
              >
                <span class="dc-part-top"></span>
                <span class="dc-part-side"></span>
                <span class="dc-part-front">
                  <span class="dc-part-icon" :style="{ color: part.color }">
                    <el-icon><component :is="getIconComponent(part.icon)" /></el-icon>
                  </span>
                  <span class="dc-part-label">{{ part.name }}</span>
                </span>
                <span class="dc-part-pulse" :style="{ '--pulse-color': part.color }"></span>
              </button>

              <div class="dc-model-hub">
                <div class="hub-ring"></div>
                <div class="hub-core">DC</div>
              </div>

              <svg class="dc-link-layer" viewBox="0 0 640 420" preserveAspectRatio="none">
                <path
                  v-for="link in dcModelLinks"
                  :key="link.id"
                  class="dc-link-path"
                  :class="{ 'is-active': activeDataCenterPart.id === link.id }"
                  :d="link.path"
                />
                <path
                  v-for="link in dcModelLinks"
                  :key="`${link.id}-energy`"
                  class="dc-link-energy"
                  :class="{ 'is-active': activeDataCenterPart.id === link.id }"
                  :d="link.path"
                />
              </svg>
            </div>
          </div>
        </div>

        <aside class="dc-detail-panel">
          <div class="dc-detail-head">
            <span class="dc-detail-kicker">当前聚焦系统</span>
            <div class="dc-detail-title-row">
              <span class="dc-detail-icon" :style="{ color: activeDataCenterPart.color }">
                <el-icon><component :is="getIconComponent(activeDataCenterPart.icon)" /></el-icon>
              </span>
              <div>
                <h3>{{ activeDataCenterPart.name }}</h3>
                <p>{{ activeDataCenterPart.summary }}</p>
              </div>
            </div>
          </div>

          <div class="dc-detail-metrics">
            <div class="dc-detail-metric">
              <span class="dc-detail-label">成本关注</span>
              <span class="dc-detail-value">{{ activeDataCenterPart.costFocus }}</span>
            </div>
            <div class="dc-detail-metric">
              <span class="dc-detail-label">策略重心</span>
              <span class="dc-detail-value">{{ activeDataCenterPart.strategyFocus }}</span>
            </div>
          </div>

          <div class="dc-detail-section">
            <span class="dc-detail-section-title">关键考虑项</span>
            <div class="dc-chip-list">
              <span
                v-for="item in activeDataCenterPart.considerations"
                :key="item"
                class="dc-chip"
              >
                {{ item }}
              </span>
            </div>
          </div>

          <div class="dc-detail-section">
            <span class="dc-detail-section-title">策略提示</span>
            <ul class="dc-detail-list">
              <li
                v-for="point in activeDataCenterPart.strategyPoints"
                :key="point"
              >
                {{ point }}
              </li>
            </ul>
          </div>

          <div class="dc-detail-footer">
            <div
              v-for="part in dataCenterParts"
              :key="part.id"
              class="dc-mini-item"
              :class="{ 'is-active': activeDataCenterPart.id === part.id }"
              @click="activeDataCenterPartId = part.id"
              role="button"
              tabindex="0"
              @keydown.enter.prevent="activeDataCenterPartId = part.id"
              @keydown.space.prevent="activeDataCenterPartId = part.id"
            >
              <span class="dc-mini-dot" :style="{ background: part.color }"></span>
              <span>{{ part.name }}</span>
            </div>
          </div>
        </aside>
      </div>
    </section>

    <div class="stats-section">
      <div class="section-header stats-header">
        <div class="section-title">
          <h2>平台概览</h2>
          <span class="stats-subtitle">实时方案数据统计</span>
        </div>
      </div>
      <el-row :gutter="0" class="telemetry-grid">
        <el-col :span="6" class="telemetry-col" v-for="(stat, index) in statsData" :key="index">
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

    <div class="recent-projects animate-fade-in">
      <div class="section-header">
        <div class="section-title">
          <h2>项目态势舱</h2>
          <span class="section-count">{{ recentProjects.length }} 个项目在线</span>
        </div>
        <el-button type="primary" link @click="goToHistory">
          查看全部
          <el-icon><Right /></el-icon>
        </el-button>
      </div>
      <div class="project-command-deck">
        <button
          v-for="project in recentProjects.slice(0, 3)"
          :key="project.id"
          type="button"
          class="project-vault-card"
          @click="viewDetail(project)"
        >
          <span class="project-vault-beam"></span>
          <span class="project-vault-head">
            <span class="project-icon" :style="{ background: getProjectColor(project.status) }">
              <el-icon><Document /></el-icon>
            </span>
            <span class="project-vault-copy">
              <span class="project-name">{{ project.name }}</span>
              <span class="location-text">{{ project.location }} / {{ project.createTime }}</span>
            </span>
            <span class="project-status-pill">{{ project.status }}</span>
          </span>
          <span class="project-vault-metrics">
            <span class="metric-item">
              <span class="metric-label">PUE</span>
              <span class="metric-value">{{ project.coreMetrics.pue }}</span>
            </span>
            <span class="metric-item">
              <span class="metric-label">Green</span>
              <span class="metric-value primary">{{ project.coreMetrics.greenRate }}%</span>
            </span>
            <span class="metric-item">
              <span class="metric-label">LCOE</span>
              <span class="metric-value">{{ project.coreMetrics.lcoe }} yuan/kWh</span>
            </span>
          </span>
          <span class="project-vault-actions">
            <span @click.stop="continueEdit(project)">Edit</span>
            <span @click.stop="viewDetail(project)">View</span>
          </span>
        </button>

        <div v-if="!recentProjects.length" class="project-empty-console">
          <span class="project-empty-dot"></span>
          <div>
            <strong>暂无最近项目</strong>
            <p>载入示例项目后，可在这里查看项目状态、关键能效指标和方案入口。</p>
          </div>
          <el-button type="primary" @click="loadSample">载入示例</el-button>
        </div>
      </div>
    </div>

    <div class="quick-guide animate-fade-in">
      <div class="section-header">
        <div class="section-title">
          <h2>能源规划跑道</h2>
          <span class="section-desc">从项目建模到多智能体推演，再到完整方案报告输出。</span>
        </div>
      </div>
      <div class="planning-runway">
        <div
          v-for="(guide, index) in guideSteps"
          :key="index"
          class="runway-stage"
          :style="{ animationDelay: `${index * 150}ms` }"
        >
          <div class="runway-stage-index">0{{ index + 1 }}</div>
          <div class="runway-stage-node" :style="{ '--stage-color': guide.color }">
            <el-icon class="guide-icon">
              <component :is="getIconComponent(guide.icon)" />
            </el-icon>
          </div>
          <div class="runway-stage-copy">
            <h3 class="guide-title">{{ guide.title }}</h3>
            <p class="guide-desc">{{ guide.desc }}</p>
          </div>
          <div class="runway-connector" v-if="index < guideSteps.length - 1">
            <span></span>
          </div>
        </div>
      </div>
      <div class="guide-action">
        <el-button size="large" @click="loadSample">
          <template #icon>
            <el-icon><Document /></el-icon>
          </template>
          载入示例项目
        </el-button>
        <span class="guide-hint">推荐示例：乌兰察布 12MW 绿色算力数据中心</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  Download,
  Connection,
  Monitor,
  SwitchButton,
  DataAnalysis,
  Van
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { solutionApi } from '@/api'

const router = useRouter()
const particleCanvas = ref(null)
const heroModelCanvas = ref(null)
const activeNode = ref(null)
let animationFrame = null
let heroModelFrame = null
let heroModelCleanup = null
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
  Download,
  Connection,
  Monitor,
  SwitchButton,
  DataAnalysis,
  Van
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
  resizeHeroModel()
}

const createModelRenderer = () => {
  const canvas = heroModelCanvas.value
  if (!canvas) return null
  const ctx = canvas.getContext('2d')
  if (!ctx) return null

  const state = {
    width: 0,
    height: 0,
    dpr: 1,
    angle: 0,
    targetX: 0.56,
    targetY: 0.48,
    dragX: 0.56,
    dragY: 0.48,
    dragging: false,
    lastX: 0,
    lastY: 0
  }

  const palette = {
    platform: 'rgba(17, 35, 31, 0.96)',
    platformSide: 'rgba(8, 20, 18, 0.98)',
    edge: 'rgba(116, 232, 190, 0.44)',
    rack: 'rgba(37, 55, 61, 0.98)',
    rackTop: 'rgba(94, 114, 118, 0.96)',
    rackFace: 'rgba(20, 32, 37, 0.98)',
    cyan: 'rgba(87, 221, 232, 0.9)',
    green: 'rgba(121, 239, 171, 0.92)',
    red: 'rgba(255, 88, 92, 0.82)',
    amber: 'rgba(246, 197, 106, 0.86)',
    violet: 'rgba(156, 134, 255, 0.72)',
    glass: 'rgba(132, 242, 220, 0.12)',
    text: 'rgba(223, 249, 239, 0.86)'
  }

  const resize = () => {
    const rect = canvas.getBoundingClientRect()
    state.dpr = Math.min(window.devicePixelRatio || 1, 2)
    state.width = Math.max(320, rect.width)
    state.height = Math.max(260, rect.height)
    canvas.width = Math.floor(state.width * state.dpr)
    canvas.height = Math.floor(state.height * state.dpr)
    ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0)
  }

  const rotate = (point) => {
    const [x, y, z] = point
    const cy = Math.cos(state.dragY)
    const sy = Math.sin(state.dragY)
    const cx = Math.cos(state.dragX)
    const sx = Math.sin(state.dragX)
    const x1 = x * cy - z * sy
    const z1 = x * sy + z * cy
    const y1 = y * cx - z1 * sx
    const z2 = y * sx + z1 * cx
    return [x1, y1, z2]
  }

  const project = (point) => {
    const [x, y, z] = rotate(point)
    const camera = 760
    const scale = camera / (camera + z)
    const fit = Math.min(state.width / 880, state.height / 560)
    return {
      x: state.width * 0.55 + x * scale * fit,
      y: state.height * 0.41 + y * scale * fit,
      z,
      scale
    }
  }

  const faceDepth = (points) => points.reduce((sum, point) => sum + rotate(point)[2], 0) / points.length

  const drawFace = (points, fill, stroke = 'rgba(168, 255, 220, 0.16)', lineWidth = 1) => {
    const projected = points.map(project)
    ctx.beginPath()
    projected.forEach((point, index) => {
      if (index === 0) ctx.moveTo(point.x, point.y)
      else ctx.lineTo(point.x, point.y)
    })
    ctx.closePath()
    ctx.fillStyle = fill
    ctx.fill()
    ctx.strokeStyle = stroke
    ctx.lineWidth = lineWidth
    ctx.stroke()
  }

  const cubeFaces = (cx, cy, cz, sx, sy, sz, colors) => {
    const x0 = cx - sx / 2
    const x1 = cx + sx / 2
    const y0 = cy - sy / 2
    const y1 = cy + sy / 2
    const z0 = cz - sz / 2
    const z1 = cz + sz / 2
    const p = {
      lbf: [x0, y1, z0], rbf: [x1, y1, z0], rtf: [x1, y0, z0], ltf: [x0, y0, z0],
      lbb: [x0, y1, z1], rbb: [x1, y1, z1], rtb: [x1, y0, z1], ltb: [x0, y0, z1]
    }
    return [
      { points: [p.ltf, p.rtf, p.rtb, p.ltb], fill: colors.top },
      { points: [p.rbf, p.rbb, p.rtb, p.rtf], fill: colors.right },
      { points: [p.lbf, p.rbf, p.rtf, p.ltf], fill: colors.front },
      { points: [p.lbb, p.lbf, p.ltf, p.ltb], fill: colors.left || colors.right },
      { points: [p.lbb, p.rbb, p.rbf, p.lbf], fill: colors.bottom || colors.front }
    ].map(face => ({ ...face, depth: faceDepth(face.points), type: 'face' }))
  }

  const drawLine3d = (points, color, width = 2, dash = null, glow = 5) => {
    const projected = points.map(project)
    ctx.save()
    ctx.beginPath()
    projected.forEach((point, index) => {
      if (index === 0) ctx.moveTo(point.x, point.y)
      else ctx.lineTo(point.x, point.y)
    })
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    if (dash) ctx.setLineDash(dash)
    ctx.shadowColor = color
    ctx.shadowBlur = width * glow
    ctx.stroke()
    ctx.restore()
  }

  const drawGlowPoint = (point, color, radius = 4) => {
    const p = project(point)
    ctx.save()
    const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, radius * 5)
    gradient.addColorStop(0, color)
    gradient.addColorStop(0.28, color.replace(/[\d.]+\)$/u, '0.38)'))
    gradient.addColorStop(1, 'rgba(8, 21, 18, 0)')
    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.arc(p.x, p.y, radius * 5, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.arc(p.x, p.y, radius, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }

  const drawEnergyPulse = (points, color, offset = 0) => {
    const index = (state.angle * 0.42 + offset) % 1
    const segment = Math.max(0, Math.min(points.length - 2, Math.floor(index * (points.length - 1))))
    const local = index * (points.length - 1) - segment
    const start = points[segment]
    const end = points[segment + 1]
    const point = [
      start[0] + (end[0] - start[0]) * local,
      start[1] + (end[1] - start[1]) * local,
      start[2] + (end[2] - start[2]) * local
    ]
    drawGlowPoint(point, color, 3.5)
  }

  const drawRoundedRect = (x, y, width, height, radius) => {
    if (typeof ctx.roundRect === 'function') {
      ctx.roundRect(x, y, width, height, radius)
      return
    }
    const r = Math.min(radius, width / 2, height / 2)
    ctx.moveTo(x + r, y)
    ctx.lineTo(x + width - r, y)
    ctx.quadraticCurveTo(x + width, y, x + width, y + r)
    ctx.lineTo(x + width, y + height - r)
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height)
    ctx.lineTo(x + r, y + height)
    ctx.quadraticCurveTo(x, y + height, x, y + height - r)
    ctx.lineTo(x, y + r)
    ctx.quadraticCurveTo(x, y, x + r, y)
  }

  const drawLabel = (text, point, align = 'center') => {
    const p = project(point)
    ctx.save()
    ctx.font = '600 12px Microsoft YaHei, sans-serif'
    ctx.textAlign = align
    const metrics = ctx.measureText(text)
    const paddingX = 8
    const boxWidth = metrics.width + paddingX * 2
    const boxHeight = 23
    const boxX = align === 'left' ? p.x - 2 : align === 'right' ? p.x - boxWidth + 2 : p.x - boxWidth / 2
    const boxY = p.y - 18
    ctx.fillStyle = 'rgba(7, 24, 21, 0.72)'
    ctx.strokeStyle = 'rgba(132, 242, 220, 0.24)'
    ctx.shadowColor = 'rgba(87, 221, 232, 0.36)'
    ctx.shadowBlur = 14
    ctx.beginPath()
    drawRoundedRect(boxX, boxY, boxWidth, boxHeight, 8)
    ctx.fill()
    ctx.stroke()
    ctx.fillStyle = palette.text
    ctx.shadowBlur = 8
    ctx.fillText(text, p.x, p.y)
    ctx.restore()
  }

  const drawRackDetails = (cx, cy, cz, sx, sy, sz) => {
    drawFace([
      [cx - sx * 0.42, cy - sy * 0.45, cz - sz * 0.56],
      [cx + sx * 0.42, cy - sy * 0.45, cz - sz * 0.56],
      [cx + sx * 0.42, cy + sy * 0.38, cz - sz * 0.56],
      [cx - sx * 0.42, cy + sy * 0.38, cz - sz * 0.56]
    ], 'rgba(92, 242, 205, 0.055)', 'rgba(132, 242, 220, 0.26)', 0.8)
    for (let i = 0; i < 7; i += 1) {
      const y = cy - sy * 0.33 + i * (sy * 0.1)
      drawLine3d([[cx - sx * 0.34, y, cz - sz * 0.53], [cx + sx * 0.34, y, cz - sz * 0.53]], 'rgba(112, 190, 198, 0.26)', 1)
    }
    for (let i = 0; i < 3; i += 1) {
      drawLine3d([[cx - sx * 0.25 + i * sx * 0.22, cy + sy * 0.1, cz - sz * 0.54], [cx - sx * 0.18 + i * sx * 0.22, cy + sy * 0.1, cz - sz * 0.54]], palette.green, 1.4)
    }
    drawGlowPoint([cx + sx * 0.26, cy - sy * 0.18, cz - sz * 0.57], palette.green, 2.2)
    drawGlowPoint([cx - sx * 0.22, cy + sy * 0.22, cz - sz * 0.57], palette.cyan, 2)
  }

  const drawSolarPanel = (cx, cy, cz) => {
    const panel = [
      [cx - 70, cy, cz - 42],
      [cx + 70, cy - 24, cz - 42],
      [cx + 70, cy - 24, cz + 42],
      [cx - 70, cy, cz + 42]
    ]
    drawFace(panel, 'rgba(22, 57, 66, 0.96)', 'rgba(119, 238, 199, 0.6)', 1.3)
    for (let i = 1; i < 4; i += 1) {
      const x = cx - 70 + i * 35
      drawLine3d([[x, cy - i * 6, cz - 40], [x, cy - i * 6, cz + 40]], 'rgba(87, 221, 232, 0.32)', 1)
    }
    for (let i = 1; i < 3; i += 1) {
      const z = cz - 42 + i * 28
      drawLine3d([[cx - 68, cy, z], [cx + 68, cy - 24, z]], 'rgba(87, 221, 232, 0.32)', 1)
    }
  }

  const drawWindTurbine = (cx, cy, cz) => {
    drawLine3d([[cx, cy + 80, cz], [cx, cy - 72, cz]], 'rgba(190, 255, 220, 0.7)', 2)
    const hub = project([cx, cy - 72, cz])
    ctx.save()
    ctx.translate(hub.x, hub.y)
    ctx.rotate(-state.angle * 1.6)
    ctx.strokeStyle = 'rgba(174, 255, 218, 0.86)'
    ctx.lineWidth = 2
    ctx.shadowColor = palette.green
    ctx.shadowBlur = 12
    for (let i = 0; i < 3; i += 1) {
      ctx.rotate((Math.PI * 2) / 3)
      ctx.beginPath()
      ctx.moveTo(0, 0)
      ctx.lineTo(0, -34)
      ctx.stroke()
    }
    ctx.restore()
  }

  const drawPlatformCircuitry = () => {
    const border = [
      [-280, 80, -190],
      [280, 80, -190],
      [280, 80, 190],
      [-280, 80, 190],
      [-280, 80, -190]
    ]
    drawLine3d(border, 'rgba(132, 242, 220, 0.34)', 1.4, null, 9)
    drawLine3d([[-250, 76, -152], [-158, 76, -152], [-118, 76, -110], [-40, 76, -110]], 'rgba(87, 221, 232, 0.22)', 1, [6, 8], 4)
    drawLine3d([[245, 76, 154], [122, 76, 154], [82, 76, 104], [-36, 76, 104]], 'rgba(121, 239, 171, 0.24)', 1, [5, 7], 4)
    drawLine3d([[-210, 77, 42], [-122, 77, 42], [-84, 77, 0], [22, 77, 0], [80, 77, -34]], 'rgba(156, 134, 255, 0.22)', 1, [4, 7], 4)
    ;[
      [-250, 75, -152],
      [-40, 75, -110],
      [245, 75, 154],
      [-36, 75, 104],
      [80, 75, -34]
    ].forEach((point, index) => drawGlowPoint(point, index % 2 ? palette.cyan : palette.green, 2.1))
  }

  const drawCoolingManifold = () => {
    const upper = [[-150, 24, -28], [-58, 18, -20], [44, 18, -18], [150, 24, -24]]
    const lower = [[-150, 34, 32], [-54, 28, 22], [50, 28, 20], [148, 34, 28]]
    drawLine3d(upper, 'rgba(255, 88, 92, 0.72)', 5, null, 8)
    drawLine3d(lower, 'rgba(91, 211, 255, 0.72)', 4, null, 8)
    for (let i = 0; i < 5; i += 1) {
      const x = -112 + i * 56
      drawLine3d([[x, 24, -28], [x, 32, 28]], 'rgba(138, 231, 255, 0.28)', 1.2, null, 4)
    }
  }

  const render = () => {
    state.angle += 0.0045
    if (!state.dragging) state.targetY += 0.0028
    state.dragX += (state.targetX - state.dragX) * 0.05
    state.dragY += (state.targetY - state.dragY) * 0.05

    ctx.clearRect(0, 0, state.width, state.height)
    const glow = ctx.createRadialGradient(state.width * 0.54, state.height * 0.36, 20, state.width * 0.54, state.height * 0.36, state.width * 0.52)
    glow.addColorStop(0, 'rgba(39, 224, 169, 0.18)')
    glow.addColorStop(0.48, 'rgba(24, 184, 196, 0.08)')
    glow.addColorStop(1, 'rgba(8, 21, 18, 0)')
    ctx.fillStyle = glow
    ctx.fillRect(0, 0, state.width, state.height)
    ctx.save()
    ctx.globalAlpha = 0.34
    for (let i = 0; i < 7; i += 1) {
      const y = state.height * (0.2 + i * 0.1)
      const gradient = ctx.createLinearGradient(0, y, state.width, y)
      gradient.addColorStop(0, 'rgba(121, 239, 171, 0)')
      gradient.addColorStop(0.5, 'rgba(121, 239, 171, 0.16)')
      gradient.addColorStop(1, 'rgba(121, 239, 171, 0)')
      ctx.strokeStyle = gradient
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(state.width * 0.08, y)
      ctx.lineTo(state.width * 0.92, y - 28)
      ctx.stroke()
    }
    ctx.restore()

    const objects = []
    objects.push(...cubeFaces(0, 92, 0, 560, 22, 380, {
      top: 'rgba(15, 40, 34, 0.98)',
      right: palette.platformSide,
      front: 'rgba(11, 29, 26, 0.98)',
      left: 'rgba(8, 23, 20, 0.98)'
    }))
    objects.push(...cubeFaces(-245, 8, -70, 54, 118, 74, { top: 'rgba(111, 134, 134, 0.98)', right: palette.rack, front: palette.rackFace }))
    objects.push(...cubeFaces(230, 32, 118, 92, 78, 92, { top: 'rgba(88, 112, 114, 0.98)', right: 'rgba(39, 53, 58, 0.96)', front: 'rgba(18, 29, 34, 0.98)' }))
    objects.push(...cubeFaces(-230, 48, 125, 112, 46, 84, { top: 'rgba(30, 64, 66, 0.96)', right: 'rgba(18, 45, 48, 0.98)', front: 'rgba(12, 33, 36, 0.98)' }))
    objects.push(...cubeFaces(0, 16, -112, 70, 118, 58, { top: palette.rackTop, right: palette.rack, front: palette.rackFace }))
    objects.push(...cubeFaces(0, 16, 112, 70, 118, 58, { top: palette.rackTop, right: palette.rack, front: palette.rackFace }))
    for (let i = 0; i < 4; i += 1) {
      const x = -126 + i * 84
      objects.push(...cubeFaces(x, 10, -112, 58, 130, 62, { top: palette.rackTop, right: palette.rack, front: palette.rackFace }))
      objects.push(...cubeFaces(x, 10, 112, 58, 130, 62, { top: palette.rackTop, right: palette.rack, front: palette.rackFace }))
    }
    for (let i = 0; i < 3; i += 1) {
      objects.push(...cubeFaces(172 + i * 48, 46, -82, 34, 52, 58, { top: 'rgba(54, 72, 76, 0.96)', right: 'rgba(31, 45, 50, 0.98)', front: 'rgba(12, 25, 30, 0.98)' }))
    }
    for (let i = 0; i < 4; i += 1) {
      objects.push(...cubeFaces(-240 + i * 40, 42, 162, 26, 62, 26, { top: 'rgba(55, 73, 68, 0.95)', right: 'rgba(34, 50, 47, 0.98)', front: 'rgba(16, 30, 28, 0.98)' }))
    }
    objects.sort((a, b) => b.depth - a.depth).forEach(face => drawFace(face.points, face.fill))
    drawPlatformCircuitry()

    for (let i = 0; i < 4; i += 1) {
      const x = -126 + i * 84
      drawRackDetails(x, 10, -112, 58, 130, 62)
      drawRackDetails(x, 10, 112, 58, 130, 62)
    }
    drawSolarPanel(-350, -34, 10)
    drawWindTurbine(-420, 20, -100)
    drawWindTurbine(-382, 34, -170)
    drawCoolingManifold()

    const phase = (state.angle * 120) % 16
    const greenPath = [[-330, 54, 10], [-220, 46, 52], [-90, 36, 28], [40, 28, 0], [210, 40, -72]]
    const gridPath = [[-260, 40, 160], [-90, 34, 126], [40, 26, 78], [170, 34, 118]]
    drawLine3d(greenPath, palette.green, 3.2, [10, 6], 9)
    drawLine3d(gridPath, palette.cyan, 3.1, [10, 7], 9)
    drawEnergyPulse(greenPath, palette.green, 0)
    drawEnergyPulse(greenPath, palette.green, 0.46)
    drawEnergyPulse(gridPath, palette.cyan, 0.2)
    drawEnergyPulse(gridPath, palette.cyan, 0.68)
    ctx.setLineDash([8, 8])
    ctx.lineDashOffset = -phase
    drawLine3d([[-440, 70, 200], [-280, 62, 160], [-160, 54, 120]], 'rgba(135, 231, 255, 0.5)', 2)
    ctx.setLineDash([])
    ;[
      [0, -58, -92],
      [-86, -54, 94],
      [124, -42, 112],
      [-244, -46, -70],
      [226, 8, 118]
    ].forEach((point, index) => drawGlowPoint(point, index % 2 ? palette.cyan : palette.green, 2.8))

    drawLabel('IT racks', [24, -92, -156])
    drawLabel('Cooling loop', [256, -26, -120], 'left')
    drawLabel('UPS', [-300, -88, -86], 'right')
    drawLabel('Green power', [-402, -86, 18])
    drawLabel('Battery bank', [-190, -46, 198])
    drawLabel('Grid access', [270, -8, 196], 'left')

    heroModelFrame = requestAnimationFrame(render)
  }

  const pointerDown = (event) => {
    state.dragging = true
    state.lastX = event.clientX
    state.lastY = event.clientY
    canvas.setPointerCapture?.(event.pointerId)
  }
  const pointerMove = (event) => {
    if (!state.dragging) return
    const dx = event.clientX - state.lastX
    const dy = event.clientY - state.lastY
    state.lastX = event.clientX
    state.lastY = event.clientY
    state.targetY += dx * 0.008
    state.targetX = Math.max(0.22, Math.min(0.92, state.targetX + dy * 0.006))
  }
  const pointerUp = (event) => {
    state.dragging = false
    canvas.releasePointerCapture?.(event.pointerId)
  }

  canvas.addEventListener('pointerdown', pointerDown)
  canvas.addEventListener('pointermove', pointerMove)
  canvas.addEventListener('pointerup', pointerUp)
  canvas.addEventListener('pointerleave', pointerUp)

  resize()
  render()

  return {
    resize,
    cleanup() {
      canvas.removeEventListener('pointerdown', pointerDown)
      canvas.removeEventListener('pointermove', pointerMove)
      canvas.removeEventListener('pointerup', pointerUp)
      canvas.removeEventListener('pointerleave', pointerUp)
      if (heroModelFrame) cancelAnimationFrame(heroModelFrame)
      heroModelFrame = null
    }
  }
}

const initHeroModel = () => {
  if (heroModelCleanup) heroModelCleanup()
  const renderer = createModelRenderer()
  if (renderer) {
    heroModelCleanup = renderer.cleanup
    initHeroModel.resize = renderer.resize
  }
}

const resizeHeroModel = () => {
  if (typeof initHeroModel.resize === 'function') {
    initHeroModel.resize()
  }
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
    label: '平均 PUE 目标',
    trend: 0,
    progress: 0,
    color: '#F59E0B',
    bgColor: 'rgba(245, 158, 11, 0.08)'
  },
  {
    icon: 'Wallet',
    value: '--',
    unit: '',
    label: '平均绿电占比',
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
    title: '配置项目边界',
    desc: '输入城市、负载、机房等级、绿电目标与预算约束，建立项目基线。',
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.1)'
  },
  {
    icon: 'Refresh',
    title: '多智能体协同推演',
    desc: '绿电、制冷、供配电与经济性工具同步计算，形成可复核的初稿方案。',
    color: '#F59E0B',
    bgColor: 'rgba(245, 158, 11, 0.1)'
  },
  {
    icon: 'Document',
    title: '输出可沟通报告',
    desc: '汇总核心指标、方案详情和权衡建议，支持 Markdown 与 PDF 导出。',
    color: '#06B6D4',
    bgColor: 'rgba(6, 182, 212, 0.1)'
  }
])

const dataCenterParts = [
  {
    id: 'it-load',
    name: 'IT 负载中心',
    icon: 'Monitor',
    color: '#20c997',
    summary: '承载服务器、网络与存储资源，是数据中心用电规划的核心需求源。',
    costFocus: '机架功率密度与设备扩容',
    strategyFocus: '负载分期、算力密度与能效目标',
    considerations: ['设计负载', '算力密度', '机房等级', '扩容节奏'],
    strategyPoints: [
      '将 IT 负载作为绿电、制冷和供配电的统一约束输入。',
      '通过分期建设减少一次性容量冗余，保持投资与需求匹配。'
    ]
  },
  {
    id: 'power',
    name: '供配电系统',
    icon: 'Connection',
    color: '#16b8c4',
    summary: '基于 GB 50174 等标准配置外部接入电压、母线形式、变压器冗余与备用电源。',
    costFocus: '外线接入、变压器与 UPS CAPEX',
    strategyFocus: '可靠性等级、N+1 冗余与备电时长',
    considerations: ['接入电压', '母线形式', '冗余架构', '备用电源'],
    strategyPoints: [
      '根据机房等级和负载规模推荐双路市电、段式母线和变压器冗余。',
      '将供电可靠性与绿电波动性联合评估，避免单点故障。'
    ]
  },
  {
    id: 'cooling',
    name: '制冷系统',
    icon: 'SwitchButton',
    color: '#3aa0ff',
    summary: '根据省份气候、水资源紧缺指数和算力密度，对多种制冷架构进行评分排序。',
    costFocus: '冷源设备、管网和运行电耗',
    strategyFocus: 'PUE 改善、WUE 约束与余热回收',
    considerations: ['年平均温度', 'WUE', 'PUE', '余热回收'],
    strategyPoints: [
      '高冷源区域优先自然冷却与间接蒸发冷却，平衡能效与用水。',
      '对高密机架预留液冷或混合冷却升级路径。'
    ]
  },
  {
    id: 'green',
    name: '绿电系统',
    icon: 'Sunny',
    color: '#72d672',
    summary: '结合当地风电、光伏资源和用电负荷，推荐直连绿电容量、储能配置与外部绿电采购策略。',
    costFocus: '风电、光伏、储能和绿证采购',
    strategyFocus: '绿电直连占比与总绿电达标路径',
    considerations: ['风光资源', '储能时长', '弃电率', '绿证采购'],
    strategyPoints: [
      '直连绿电承担可见的本地供给，剩余绿电通过绿电交易或绿证补足。',
      '储能不追求完全离网，重点用于平滑波动和削峰。'
    ]
  },
  {
    id: 'ops',
    name: '运维与经济性',
    icon: 'DataAnalysis',
    color: '#f5b041',
    summary: '跟踪 CAPEX、OPEX、碳排放和回收期，帮助用户理解方案权衡。',
    costFocus: '投资分布、电价敏感性与回收期',
    strategyFocus: '经济性与可持续指标联合判断',
    considerations: ['CAPEX', 'OPEX', '碳减排', 'ROI'],
    strategyPoints: [
      '将绿电投资、制冷节能和供电可靠性放在同一决策框架内比较。',
      '用年化成本、单位电量成本和碳排放同步表达方案价值。'
    ]
  },
  {
    id: 'site',
    name: '场址与资源',
    icon: 'Van',
    color: '#9b8cff',
    summary: '综合城市区位、气候、电网条件与可再生能源资源，形成方案输入基础。',
    costFocus: '土地、外线、水资源与并网条件',
    strategyFocus: '区域资源禀赋与建设约束匹配',
    considerations: ['城市区位', '气候条件', '风光资源', '电网接入'],
    strategyPoints: [
      '优先识别富集风光资源和外部接入条件较好的区域。',
      '将场址约束前置，避免后期因供电、用水或并网条件反复调整方案。'
    ]
  }
]

const activeDataCenterPartId = ref('power')

const activeDataCenterPart = computed(() => {
  return dataCenterParts.find(part => part.id === activeDataCenterPartId.value) || dataCenterParts[0]
})

const dcModelLinks = [
  { id: 'site', path: 'M320 210 C240 168, 190 130, 150 96' },
  { id: 'power', path: 'M320 210 C240 216, 188 214, 128 206' },
  { id: 'cooling', path: 'M320 210 C248 258, 204 282, 168 308' },
  { id: 'green', path: 'M320 210 C390 168, 454 142, 528 118' },
  { id: 'ops', path: 'M320 210 C404 220, 470 228, 536 246' },
  { id: 'it-load', path: 'M320 210 C388 258, 428 292, 486 320' }
]

const getStatusType = (status) => {
  const types = {
    '已完成': 'success',
    '生成中': 'warning',
    '草稿': 'info',
    '失败': 'danger'
  }
  return types[status] || 'info'
}

const getProjectColor = (status) => {
  const colors = {
    '已完成': 'linear-gradient(135deg, #00B42A 0%, #23C343 100%)',
    '生成中': 'linear-gradient(135deg, #FF7D00 0%, #FF9E40 100%)',
    '草稿': 'linear-gradient(135deg, #8F959E 0%, #A6ABB8 100%)',
    '失败': 'linear-gradient(135deg, #F53F3F 0%, #F76560 100%)'
  }
  return colors[status] || colors['草稿']
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
  ElMessage.success(`??"${project.name}"???`)
}

const loadSample = () => {
  const sampleData = {
    location: '内蒙古乌兰察布',
    planned_load_kw: 12000,
    computing_power_density: 30,
    planned_area: 18000,
    machine_room_grade: 'A+',
    cooling_technology: '间接蒸发冷却',
    pue_target: 1.18,
    green_power_ratio: 95,
    direct_green_power_ratio: 55,
    budget_constraint: 35000,
    sim_hours: 168
  }
  localStorage.setItem('projectConfig', JSON.stringify(sampleData))
  ElMessage.success('示例参数已载入，即将进入参数配置页')
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
    console.error('加载最近项目失败', error)
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
  setTimeout(initHeroModel, 120)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  if (heroModelCleanup) {
    heroModelCleanup()
    heroModelCleanup = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.home-page {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-bottom: 56px;
}

.home-page::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 486px;
  bottom: 0;
  border-radius: 30px;
  background:
    radial-gradient(circle at 16% 8%, rgba(121, 239, 171, 0.08), transparent 22%),
    radial-gradient(circle at 84% 12%, rgba(87, 221, 232, 0.06), transparent 24%),
    linear-gradient(180deg, rgba(8, 28, 23, 0.78) 0%, rgba(8, 28, 23, 0.84) 40%, rgba(7, 24, 21, 0.88) 100%);
  border: 1px solid rgba(121, 239, 171, 0.08);
  box-shadow: inset 0 1px 0 rgba(225, 255, 236, 0.04);
  pointer-events: none;
  z-index: 0;
}

.hero-section {
  position: relative;
  z-index: 2;
  isolation: isolate;
  min-height: 500px;
  background:
    radial-gradient(circle at 18% 22%, color-mix(in oklab, var(--primary-light) 18%, transparent), transparent 26%),
    radial-gradient(circle at 84% 28%, color-mix(in oklab, var(--accent-color) 18%, transparent), transparent 24%),
    radial-gradient(circle at 52% 98%, color-mix(in oklab, var(--primary-color) 16%, transparent), transparent 30%),
    linear-gradient(135deg, color-mix(in oklab, var(--bg-stage) 92%, oklch(0.06 0.018 160) 8%) 0%, color-mix(in oklab, var(--bg-stage-soft) 84%, var(--primary-dark) 16%) 48%, color-mix(in oklab, var(--bg-stage) 78%, var(--primary-color) 22%) 100%);
  border-radius: 28px 28px 14px 14px;
  overflow: hidden;
  box-shadow: 0 18px 44px rgba(2, 12, 8, 0.2);
  border: 1px solid color-mix(in oklab, var(--primary-color) 16%, transparent);
  border-bottom-color: rgba(121, 239, 171, 0.04);
}

.hero-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.035) 46%, transparent 100%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 16%, transparent 86%, rgba(255, 255, 255, 0.018));
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
  z-index: 2;
  display: flex;
  min-height: 500px;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 56px 48px 52px;
  text-align: left;
  width: min(46%, 620px);
}

.hero-headline {
  max-width: 640px;
  margin-bottom: 32px;
}

.main-title {
  font-size: 48px;
  font-weight: 700;
  color: rgba(244, 252, 246, 0.98);
  margin-bottom: 16px;
  letter-spacing: -0.035em;
  line-height: 1.04;
  max-width: 20ch;
  white-space: nowrap;
}

.sub-title {
  font-size: 16px;
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
  margin-top: 4px;
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

.hero-model-stage {
  position: absolute;
  z-index: 1;
  top: -8px;
  right: -6px;
  bottom: 44px;
  width: min(60%, 860px);
  min-width: 480px;
  border-radius: 24px;
  overflow: hidden;
  pointer-events: auto;
  background:
    radial-gradient(circle at 44% 34%, rgba(89, 245, 183, 0.18), transparent 38%),
    radial-gradient(circle at 78% 24%, rgba(87, 221, 232, 0.14), transparent 34%),
    linear-gradient(145deg, rgba(11, 31, 27, 0.16), rgba(4, 14, 13, 0.02));
  box-shadow: inset 0 -24px 56px rgba(3, 14, 12, 0.22);
  mask-image: none;
}

.hero-model-stage::before {
  content: '';
  position: absolute;
  inset: 9% 5% 7% 8%;
  border: 1px solid rgba(121, 239, 171, 0.08);
  border-radius: 28px;
  background:
    linear-gradient(rgba(116, 232, 190, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(116, 232, 190, 0.05) 1px, transparent 1px);
  background-size: 34px 34px;
  transform: perspective(700px) rotateX(62deg) rotateZ(-8deg) translateY(58px);
  transform-origin: center;
  opacity: 0.54;
}

.hero-model-stage::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(8, 21, 18, 0.18), transparent 14%, transparent 84%, rgba(8, 21, 18, 0.12)),
    radial-gradient(circle at 70% 30%, rgba(87, 221, 232, 0.14), transparent 34%),
    linear-gradient(180deg, rgba(240, 255, 246, 0.04), transparent 20%, rgba(4, 16, 14, 0.12));
  pointer-events: none;
}

.hero-model-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
  cursor: grab;
  touch-action: none;
}

.hero-model-canvas:active {
  cursor: grabbing;
}

.hero-model-caption {
  position: absolute;
  z-index: 2;
  right: 28px;
  bottom: 24px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid rgba(121, 239, 171, 0.32);
  border-radius: 999px;
  color: rgba(229, 251, 239, 0.8);
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 11px;
  letter-spacing: 0;
  background: rgba(5, 20, 17, 0.66);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22), inset 0 1px 0 rgba(226, 255, 238, 0.1);
}

.caption-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #79efab;
  box-shadow: 0 0 14px rgba(121, 239, 171, 0.9);
}

.stats-section {
  position: relative;
  z-index: 1;
  padding: 10px 0 0;
  margin-top: -10px;
}

.dc-overview-section {
  position: relative;
  z-index: 1;
  background: linear-gradient(180deg, rgba(8, 28, 23, 0.52) 0%, rgba(9, 31, 26, 0.58) 100%);
  border-radius: 12px 12px 10px 10px;
  padding: 24px 24px 18px;
  margin: -10px 0 0;
  box-shadow: none;
  border: 1px solid rgba(121, 239, 171, 0.08);
  border-top: none;
  border-bottom-color: rgba(121, 239, 171, 0.04);
}

.dc-overview-header {
  margin-bottom: 20px;
}

.dc-overview-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.18fr) minmax(340px, 0.82fr);
  gap: 22px;
  align-items: stretch;
}

.dc-model-panel,
.dc-detail-panel {
  border-radius: 22px;
  border: 1px solid rgba(121, 239, 171, 0.1);
  overflow: hidden;
}

.dc-model-panel {
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 12%, transparent), transparent 32%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage) 96%, var(--accent-color) 4%) 0%, color-mix(in oklab, var(--bg-stage-soft) 86%, var(--primary-dark) 14%) 100%);
  min-height: 560px;
}

.dc-model-stage {
  position: relative;
  height: 100%;
  min-height: 560px;
  overflow: hidden;
}

.stage-grid {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.12), rgba(0, 0, 0, 0.75));
}

.stage-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.42;
}

.stage-glow-primary {
  width: 220px;
  height: 220px;
  background: color-mix(in oklab, var(--primary-color) 70%, transparent);
  top: 28px;
  left: 40px;
  animation: stageGlowFloat 12s ease-in-out infinite;
}

.stage-glow-accent {
  width: 260px;
  height: 260px;
  background: color-mix(in oklab, var(--accent-color) 58%, transparent);
  bottom: 18px;
  right: 52px;
  animation: stageGlowFloat 15s ease-in-out infinite reverse;
}

.dc-model-shell {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 560px;
  perspective: 1200px;
  animation: shellFloat 9s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
}

.dc-link-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.dc-link-path {
  fill: none;
  stroke: color-mix(in oklab, var(--primary-color) 48%, transparent);
  stroke-width: 1.6;
  stroke-dasharray: 6 8;
  opacity: 0.38;
}

.dc-link-path.is-active {
  stroke: color-mix(in oklab, var(--accent-color) 72%, white);
  opacity: 0.9;
}

.dc-link-energy {
  fill: none;
  stroke: rgba(173, 255, 226, 0.92);
  stroke-width: 2.1;
  stroke-linecap: round;
  stroke-dasharray: 6 90;
  stroke-dashoffset: 0;
  opacity: 0.45;
  filter: drop-shadow(0 0 7px rgba(111, 255, 218, 0.55));
  animation: energyFlow 4.8s linear infinite;
}

.dc-link-energy.is-active {
  stroke: rgba(112, 224, 255, 0.98);
  opacity: 0.95;
  stroke-dasharray: 10 78;
  animation-duration: 2.6s;
}

.dc-model-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 124px;
  height: 124px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hub-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(132, 240, 199, 0.28);
  background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, rgba(6, 182, 212, 0.08) 48%, transparent 74%);
  box-shadow:
    0 0 0 12px rgba(16, 185, 129, 0.04),
    0 0 48px rgba(16, 185, 129, 0.18);
  animation: hubPulse 4.8s ease-in-out infinite;
}

.hub-core {
  position: relative;
  z-index: 1;
  width: 74px;
  height: 74px;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.94) 0%, rgba(8, 145, 178, 0.9) 100%);
  color: rgba(246, 252, 248, 0.98);
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.08em;
  box-shadow: 0 22px 48px rgba(8, 145, 178, 0.26);
  animation: coreBreath 5.6s ease-in-out infinite;
}

.dc-part {
  position: absolute;
  width: 118px;
  height: 118px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  transform-style: preserve-3d;
  transition: transform 240ms cubic-bezier(0.22, 1, 0.36, 1), filter 240ms ease;
  animation: partFloat 7.2s ease-in-out infinite;
}

.dc-part:hover,
.dc-part.is-active {
  transform: translateY(-4px) scale(1.02);
  filter: brightness(1.08);
}

.dc-part:focus-visible {
  outline: 2px solid color-mix(in oklab, var(--accent-color) 76%, white);
  outline-offset: 6px;
}

.dc-part-top,
.dc-part-side,
.dc-part-front {
  position: absolute;
  inset: 0;
  border-radius: 20px;
}

.dc-part-front {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 8px;
  padding: 14px;
  background: linear-gradient(180deg, rgba(8, 22, 20, 0.84) 0%, rgba(17, 42, 37, 0.96) 100%);
  border: 1px solid rgba(140, 244, 209, 0.12);
  transform: translateZ(0);
  box-shadow: 0 16px 28px rgba(4, 11, 13, 0.22);
  overflow: hidden;
}

.dc-part-front::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 18%, rgba(162, 255, 223, 0.12) 50%, transparent 82%);
  transform: translateX(-130%);
  animation: surfaceSweep 6.8s ease-in-out infinite;
}

.dc-part-top {
  inset: -12px 6px auto 6px;
  height: 34px;
  background: linear-gradient(180deg, rgba(96, 255, 205, 0.2) 0%, rgba(59, 162, 255, 0.08) 100%);
  border: 1px solid rgba(144, 244, 217, 0.16);
  transform: rotateX(68deg) translateZ(18px);
  transform-origin: bottom;
}

.dc-part-side {
  inset: 10px -12px 10px auto;
  width: 32px;
  background: linear-gradient(180deg, rgba(13, 54, 49, 0.94) 0%, rgba(8, 25, 22, 0.94) 100%);
  border: 1px solid rgba(140, 244, 209, 0.08);
  transform: rotateY(68deg) translateZ(16px);
  transform-origin: left;
}

.dc-part-icon {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  font-size: 20px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.dc-part-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.45;
  color: rgba(245, 252, 247, 0.92);
  text-align: left;
}

.dc-part-pulse {
  position: absolute;
  inset: -8px;
  border-radius: 26px;
  border: 1px solid color-mix(in oklab, var(--pulse-color, var(--primary-color)) 48%, transparent);
  opacity: 0;
  transition: opacity 220ms ease;
  animation: partPulse 4.8s ease-in-out infinite;
}

.dc-part.is-active .dc-part-pulse,
.dc-part:hover .dc-part-pulse {
  opacity: 0.85;
}

.part-site {
  left: 72px;
  top: 54px;
  animation-delay: -1.2s;
}

.part-power {
  left: 44px;
  top: 182px;
  animation-delay: -3.4s;
}

.part-cooling {
  left: 92px;
  bottom: 82px;
  animation-delay: -4.6s;
}

.part-green {
  right: 86px;
  top: 76px;
  animation-delay: -2.2s;
}

.part-ops {
  right: 54px;
  top: 222px;
  animation-delay: -5.1s;
}

.part-it-load {
  right: 120px;
  bottom: 76px;
  animation-delay: -0.4s;
}

@keyframes shellFloat {
  0%, 100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, -8px, 0);
  }
}

@keyframes partFloat {
  0%, 100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, -7px, 0);
  }
}

@keyframes partPulse {
  0%, 100% {
    opacity: 0.16;
    transform: scale(0.98);
  }
  50% {
    opacity: 0.48;
    transform: scale(1.04);
  }
}

@keyframes surfaceSweep {
  0%, 18% {
    transform: translateX(-130%);
    opacity: 0;
  }
  30%, 58% {
    opacity: 1;
  }
  74%, 100% {
    transform: translateX(130%);
    opacity: 0;
  }
}

@keyframes energyFlow {
  from {
    stroke-dashoffset: 0;
  }
  to {
    stroke-dashoffset: -96;
  }
}

@keyframes hubPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.84;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}

@keyframes coreBreath {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 22px 48px rgba(8, 145, 178, 0.26);
  }
  50% {
    transform: scale(1.04);
    box-shadow: 0 26px 56px rgba(8, 145, 178, 0.34);
  }
}

@keyframes stageGlowFloat {
  0%, 100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(0, -10px, 0) scale(1.06);
  }
}

@media (prefers-reduced-motion: reduce) {
  .stage-glow-primary,
  .stage-glow-accent,
  .dc-model-shell,
  .hub-ring,
  .hub-core,
  .dc-part,
  .dc-part-front::after,
  .dc-part-pulse,
  .dc-link-energy {
    animation: none !important;
  }
}

.dc-detail-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.dc-detail-head {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dc-detail-kicker {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.dc-detail-title-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.dc-detail-icon {
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
  font-size: 22px;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 20%, transparent);
}

.dc-detail-title-row h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.dc-detail-title-row p {
  margin: 0;
  font-size: 13px;
  line-height: 1.75;
  color: var(--text-secondary);
}

.dc-detail-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.dc-detail-metric {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.dc-detail-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.dc-detail-value {
  display: block;
  font-size: 14px;
  line-height: 1.65;
  font-weight: 600;
  color: var(--text-primary);
}

.dc-detail-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dc-detail-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.dc-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.dc-chip {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  font-size: 12px;
  color: var(--text-secondary);
}

.dc-detail-list {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dc-detail-list li {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.dc-detail-footer {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: auto;
}

.dc-mini-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 0 12px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dc-mini-item:hover,
.dc-mini-item.is-active {
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
  color: var(--text-primary);
  background: color-mix(in oklab, var(--primary-color) 7%, var(--bg-card));
}

.dc-mini-item:focus-visible {
  outline: 2px solid color-mix(in oklab, var(--primary-color) 72%, white);
  outline-offset: 3px;
}

.dc-mini-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: 0 0 8px;
}

.stats-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 0 24px;
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

.project-command-deck {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.project-vault-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 178px;
  padding: 18px;
  text-align: left;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(121, 239, 171, 0.16);
  background:
    radial-gradient(circle at top left, rgba(121, 239, 171, 0.11), transparent 34%),
    linear-gradient(180deg, rgba(8, 31, 26, 0.86), rgba(5, 19, 17, 0.94));
  box-shadow: inset 0 1px 0 rgba(224, 255, 235, 0.06);
  transition: transform var(--transition-normal), border-color var(--transition-normal), box-shadow var(--transition-normal);
}

.project-vault-card:hover {
  transform: translateY(-3px);
  border-color: rgba(121, 239, 171, 0.34);
  box-shadow: 0 22px 54px rgba(2, 24, 16, 0.26), inset 0 1px 0 rgba(224, 255, 235, 0.08);
}

.project-vault-card:focus-visible {
  outline: 2px solid rgba(37, 214, 210, 0.86);
  outline-offset: 4px;
}

.project-vault-beam {
  position: absolute;
  left: 16px;
  right: 16px;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(121, 239, 171, 0.58), rgba(37, 214, 210, 0.42), transparent);
}

.project-vault-head {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.project-vault-copy {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.project-status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(121, 239, 171, 0.18);
  background: rgba(121, 239, 171, 0.08);
  color: rgba(121, 239, 171, 0.96);
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.project-vault-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.project-vault-metrics .metric-item {
  min-height: 64px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(3, 16, 13, 0.5);
  border: 1px solid rgba(121, 239, 171, 0.1);
}

.project-vault-actions {
  display: flex;
  justify-content: flex-end;
  gap: 14px;
  color: rgba(37, 214, 210, 0.92);
  font-size: 12px;
  font-weight: 700;
}

.project-vault-actions span {
  cursor: pointer;
}

.project-empty-console {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  min-height: 108px;
  padding: 18px;
  border-radius: 18px;
  border: 1px dashed rgba(121, 239, 171, 0.24);
  background: rgba(3, 16, 13, 0.46);
}

.project-empty-console strong {
  display: block;
  margin-bottom: 4px;
  color: rgba(239, 252, 245, 0.96);
}

.project-empty-console p {
  margin: 0;
  color: rgba(211, 235, 224, 0.68);
  font-size: 13px;
}

.project-empty-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(121, 239, 171, 0.96);
  box-shadow: 0 0 18px rgba(121, 239, 171, 0.72);
}

.planning-runway {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  padding: 8px 2px 4px;
}

.planning-runway::before {
  content: '';
  position: absolute;
  left: 7%;
  right: 7%;
  top: 54px;
  height: 1px;
  background: linear-gradient(90deg, rgba(121, 239, 171, 0.16), rgba(37, 214, 210, 0.42), rgba(121, 239, 171, 0.16));
  box-shadow: 0 0 18px rgba(37, 214, 210, 0.24);
}

.runway-stage {
  position: relative;
  display: grid;
  grid-template-columns: 62px minmax(0, 1fr);
  gap: 14px;
  min-height: 184px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(121, 239, 171, 0.15);
  background:
    radial-gradient(circle at 32px 34px, color-mix(in oklab, var(--stage-color, var(--primary-color)) 18%, transparent), transparent 34%),
    linear-gradient(180deg, rgba(8, 31, 26, 0.82), rgba(5, 19, 17, 0.92));
  box-shadow: inset 0 1px 0 rgba(224, 255, 235, 0.055);
}

.runway-stage-index {
  grid-column: 1 / -1;
  color: rgba(121, 239, 171, 0.7);
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.runway-stage-node {
  position: relative;
  z-index: 1;
  width: 58px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  color: var(--stage-color, rgba(121, 239, 171, 0.96));
  background: rgba(3, 16, 13, 0.58);
  border: 1px solid color-mix(in oklab, var(--stage-color, var(--primary-color)) 36%, transparent);
  box-shadow: 0 0 28px color-mix(in oklab, var(--stage-color, var(--primary-color)) 22%, transparent);
}

.runway-stage-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.runway-connector {
  position: absolute;
  top: 50px;
  right: -28px;
  z-index: 2;
  width: 54px;
  height: 8px;
  pointer-events: none;
}

.runway-connector span {
  display: block;
  width: 100%;
  height: 2px;
  margin-top: 3px;
  background: linear-gradient(90deg, rgba(121, 239, 171, 0.1), rgba(37, 214, 210, 0.86), rgba(121, 239, 171, 0.1));
  box-shadow: 0 0 14px rgba(37, 214, 210, 0.5);
}

.hero-signal-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
  color: rgba(222, 250, 238, 0.78);
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 11px;
  letter-spacing: 0;
}

.hero-signal-strip span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  padding: 0 12px;
  border: 1px solid rgba(121, 239, 171, 0.18);
  border-radius: 999px;
  background: rgba(4, 18, 15, 0.42);
  box-shadow: inset 0 1px 0 rgba(221, 255, 235, 0.08);
}

.hero-signal-strip i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #79efab;
  box-shadow: 0 0 12px rgba(121, 239, 171, 0.86);
}

.dc-overview-section {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 22%, rgba(121, 239, 171, 0.08), transparent 32%),
    radial-gradient(circle at 84% 24%, rgba(87, 221, 232, 0.06), transparent 34%),
    linear-gradient(135deg, rgba(8, 28, 23, 0.72) 0%, rgba(10, 34, 28, 0.68) 46%, rgba(7, 24, 21, 0.74) 100%);
  border: 1px solid rgba(121, 239, 171, 0.08);
  box-shadow: none;
}

.section-orbit-line {
  position: absolute;
  left: -8%;
  right: -8%;
  top: 116px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(121, 239, 171, 0.28), rgba(87, 221, 232, 0.24), transparent);
  transform: rotate(-2deg);
}

.dc-overview-section .section-title h2,
.dc-overview-section .dc-detail-title-row h3,
.dc-overview-section .dc-detail-section-title,
.dc-overview-section .dc-detail-value {
  color: rgba(239, 252, 245, 0.96);
}

.dc-overview-section .section-desc,
.dc-overview-section .dc-detail-title-row p,
.dc-overview-section .dc-detail-label,
.dc-overview-section .dc-detail-list li,
.dc-overview-section .dc-chip,
.dc-overview-section .dc-mini-item {
  color: rgba(211, 235, 224, 0.72);
}

.dc-model-panel,
.dc-detail-panel {
  border-color: rgba(121, 239, 171, 0.18);
  background:
    linear-gradient(180deg, rgba(9, 31, 27, 0.72), rgba(5, 19, 17, 0.9));
  box-shadow: inset 0 1px 0 rgba(224, 255, 235, 0.06);
}

.dc-detail-panel {
  background:
    radial-gradient(circle at top left, rgba(121, 239, 171, 0.1), transparent 36%),
    linear-gradient(180deg, rgba(8, 30, 26, 0.8), rgba(5, 18, 16, 0.92));
}

.dc-detail-kicker {
  color: rgba(121, 239, 171, 0.9);
}

.dc-detail-icon,
.dc-detail-metric,
.dc-chip,
.dc-mini-item {
  border-color: rgba(121, 239, 171, 0.14);
  background: rgba(7, 26, 23, 0.66);
}

.dc-mini-item:hover,
.dc-mini-item.is-active {
  border-color: rgba(121, 239, 171, 0.36);
  background: rgba(25, 72, 58, 0.54);
  color: rgba(242, 255, 248, 0.96);
}

.stats-section {
  position: relative;
  padding: 12px 0 0;
  margin-top: -10px;
}

.stats-header {
  padding: 0 24px 8px;
}

.telemetry-grid {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(121, 239, 171, 0.08);
  border-top: none;
  border-radius: 10px;
  background:
    linear-gradient(90deg, rgba(8, 29, 24, 0.6), rgba(12, 45, 36, 0.56), rgba(8, 29, 24, 0.6));
  box-shadow: none;
}

.telemetry-grid::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent 0, rgba(121, 239, 171, 0.08) 1px, transparent 1px),
    radial-gradient(circle at 20% 20%, rgba(121, 239, 171, 0.12), transparent 22%),
    radial-gradient(circle at 78% 64%, rgba(87, 221, 232, 0.12), transparent 28%);
  background-size: 64px 100%, auto, auto;
  pointer-events: none;
}

.telemetry-col {
  position: relative;
}

.telemetry-col + .telemetry-col::before {
  content: '';
  position: absolute;
  left: 0;
  top: 18px;
  bottom: 18px;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(121, 239, 171, 0.22), transparent);
  z-index: 2;
}

.stat-card {
  min-height: 132px;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  background: transparent;
}

.stat-card::before {
  display: none;
}

.stat-card:hover {
  transform: none;
  box-shadow: none;
  background: rgba(121, 239, 171, 0.045);
}

.stat-icon-wrap {
  background: rgba(121, 239, 171, 0.1) !important;
  color: rgba(121, 239, 171, 0.95) !important;
  box-shadow: inset 0 0 0 1px rgba(121, 239, 171, 0.16), 0 0 20px rgba(121, 239, 171, 0.1);
}

.stat-value,
.stats-title,
.project-name,
.metric-value,
.guide-title {
  color: rgba(239, 252, 245, 0.96);
}

.stat-label,
.stats-subtitle,
.stat-unit,
.stat-date,
.location-text,
.metric-label,
.guide-desc,
.guide-hint,
.section-count {
  color: rgba(211, 235, 224, 0.68);
}

.stat-progress-bar {
  background: rgba(211, 235, 224, 0.1);
}

.recent-projects,
.quick-guide {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 12% 0%, rgba(121, 239, 171, 0.05), transparent 32%),
    linear-gradient(135deg, rgba(7, 24, 21, 0.58), rgba(11, 38, 32, 0.54));
  border: 1px solid rgba(121, 239, 171, 0.08);
  box-shadow: none;
}

.recent-projects {
  z-index: 1;
  margin: -10px 0 0;
  border-top: none;
  border-radius: 10px;
}

.quick-guide {
  z-index: 1;
  margin: -10px 0 0;
  border-top: none;
  border-radius: 10px 10px 22px 22px;
}

.dc-overview-section::before,
.stats-section::before,
.recent-projects::before,
.quick-guide::before {
  content: '';
  position: absolute;
  left: 18px;
  right: 18px;
  top: -18px;
  height: 30px;
  background: linear-gradient(180deg, rgba(10, 34, 28, 0), rgba(10, 34, 28, 0.38) 55%, rgba(10, 34, 28, 0.72) 100%);
  filter: blur(10px);
  opacity: 0.9;
  pointer-events: none;
}

.recent-projects .section-title h2,
.quick-guide .section-title h2 {
  color: rgba(239, 252, 245, 0.96);
}

.project-table {
  border: 1px solid rgba(121, 239, 171, 0.14);
  background: rgba(4, 18, 16, 0.44);
}

.project-table :deep(.el-table),
.project-table :deep(.el-table__inner-wrapper),
.project-table :deep(.el-table__body-wrapper),
.project-table :deep(.el-table__header-wrapper) {
  background: transparent;
}

.project-table :deep(.el-table__header th) {
  background: rgba(17, 58, 47, 0.78) !important;
  color: rgba(211, 235, 224, 0.78);
}

.project-table :deep(.el-table__body td) {
  border-color: rgba(121, 239, 171, 0.1);
  color: rgba(230, 248, 238, 0.88);
}

.project-table :deep(.table-row:hover) {
  background: rgba(121, 239, 171, 0.07);
}

.guide-card {
  min-height: 204px;
  border: 1px solid rgba(121, 239, 171, 0.14);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(9, 32, 28, 0.7), rgba(5, 19, 17, 0.84));
  box-shadow: none;
}

.guide-card:hover {
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.18);
  border-color: rgba(121, 239, 171, 0.28);
}

.guide-number {
  background: rgba(121, 239, 171, 0.12);
  color: rgba(121, 239, 171, 0.94);
  box-shadow: inset 0 0 0 1px rgba(121, 239, 171, 0.18);
}

.guide-icon-wrapper {
  background: rgba(121, 239, 171, 0.1) !important;
  box-shadow: inset 0 0 0 1px rgba(121, 239, 171, 0.18), 0 0 26px rgba(121, 239, 171, 0.08);
}

@media (max-width: 992px) {
  .hero-section {
    min-height: auto;
  }

  .hero-content {
    min-height: auto;
    padding: 34px 28px;
    width: 100%;
  }

  .main-title {
    font-size: 34px;
    white-space: normal;
  }

  .hero-model-stage {
    position: relative;
    top: auto;
    right: auto;
    bottom: auto;
    width: calc(100% - 32px);
    min-width: 0;
    height: 400px;
    margin: -10px 16px 18px;
    mask-image: none;
  }

  .stats-section :deep(.el-col) {
    margin-bottom: 16px;
  }

  .telemetry-grid {
    flex-wrap: wrap;
  }

  .telemetry-grid .telemetry-col {
    flex: 0 0 50%;
    max-width: 50%;
  }

  .telemetry-col:nth-child(odd)::before {
    display: none;
  }

  .project-command-deck,
  .planning-runway {
    grid-template-columns: 1fr;
  }

  .planning-runway::before,
  .runway-connector {
    display: none;
  }

  .recent-projects,
  .quick-guide,
  .dc-overview-section {
    padding: 18px;
  }

  .hero-actions {
    width: 100%;
  }

  .action-btn {
    min-width: 0;
  }

  .dc-overview-layout {
    grid-template-columns: 1fr;
  }

  .dc-model-panel,
  .dc-model-stage,
  .dc-model-shell {
    min-height: 500px;
  }
}

@media (max-width: 768px) {
  .main-title {
    font-size: 28px;
  }

  .hero-model-stage {
    height: 320px;
    width: calc(100% - 20px);
    margin: -2px 10px 12px;
    border-radius: 18px;
  }

  .hero-model-caption {
    right: 16px;
    bottom: 14px;
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

  .project-vault-head,
  .project-empty-console {
    grid-template-columns: 1fr;
  }

  .project-vault-metrics {
    grid-template-columns: 1fr;
  }

  .project-vault-actions {
    justify-content: flex-start;
  }

  .runway-stage {
    grid-template-columns: 52px minmax(0, 1fr);
    min-height: auto;
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

  .telemetry-grid .telemetry-col {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .telemetry-col::before {
    display: none;
  }

  .dc-model-panel,
  .dc-model-stage,
  .dc-model-shell {
    min-height: 520px;
  }

  .dc-detail-metrics,
  .dc-detail-footer {
    grid-template-columns: 1fr;
  }

  .part-site {
    left: 24px;
    top: 54px;
  }

  .part-power {
    left: 12px;
    top: 196px;
  }

  .part-cooling {
    left: 42px;
    bottom: 62px;
  }

  .part-green {
    right: 20px;
    top: 72px;
  }

  .part-ops {
    right: 8px;
    top: 216px;
  }

  .part-it-load {
    right: 38px;
    bottom: 64px;
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
