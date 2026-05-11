<template>
  <div class="workflow-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">方案工作流</h1>
          <p class="page-subtitle">了解数据中心绿电一体化方案的完整工作流程</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="startWorkflow">
            <el-icon><RefreshRight /></el-icon>
            开始方案生成
          </el-button>
        </div>
      </div>
    </div>

    <!-- 工作流概览卡片 -->
    <div class="overview-card card">
      <div class="overview-header">
        <h3 class="overview-title">工作流概览</h3>
        <p class="overview-desc">点击各模块查看详细信息</p>
      </div>
      
      <!-- 工作流可视化区域 -->
      <div class="workflow-graph">
        <!-- 中心节点 - 数据中心 -->
        <div class="center-node" :class="{ active: selectedModule === 'datacenter' }" @click="selectModule('datacenter')">
          <div class="node-icon">
            <el-icon class="icon-lg"><Files /></el-icon>
          </div>
          <div class="node-label">数据中心</div>
          <div class="node-subtitle">核心计算设施</div>
        </div>

        <!-- 连接线条 -->
        <svg class="workflow-lines" viewBox="0 0 800 500">
          <!-- 绿电系统连线 -->
          <path d="M400,60 L400,120" class="line line-green" />
          <!-- 制冷系统连线 -->
          <path d="M400,440 L400,380" class="line line-blue" />
          <!-- 供电系统连线 -->
          <path d="M80,250 L160,250" class="line line-orange" />
          <!-- IT设备连线 -->
          <path d="M720,250 L640,250" class="line line-purple" />
        </svg>

        <!-- 绿电系统 -->
        <div class="workflow-node green" :class="{ active: selectedModule === 'green-power' }" @click="selectModule('green-power')">
          <div class="node-icon-wrapper green-bg">
            <el-icon class="icon-md"><Lightning /></el-icon>
          </div>
          <div class="node-content">
            <h4 class="node-title">绿电系统</h4>
            <p class="node-desc">光伏 + 风电 + 储能</p>
            <div class="node-stats">
              <span class="stat-item">70% 绿电目标</span>
            </div>
          </div>
        </div>

        <!-- 制冷系统 -->
        <div class="workflow-node blue" :class="{ active: selectedModule === 'cooling' }" @click="selectModule('cooling')">
          <div class="node-icon-wrapper blue-bg">
            <el-icon class="icon-md"><Location /></el-icon>
          </div>
          <div class="node-content">
            <h4 class="node-title">制冷系统</h4>
            <p class="node-desc">液冷 + 热通道封闭</p>
            <div class="node-stats">
              <span class="stat-item">PUE: 1.23</span>
            </div>
          </div>
        </div>

        <!-- 供电系统 -->
        <div class="workflow-node orange" :class="{ active: selectedModule === 'power-supply' }" @click="selectModule('power-supply')">
          <div class="node-icon-wrapper orange-bg">
            <el-icon class="icon-md"><Aim /></el-icon>
          </div>
          <div class="node-content">
            <h4 class="node-title">供电系统</h4>
            <p class="node-desc">UPS + 备用发电机</p>
            <div class="node-stats">
              <span class="stat-item">2N 冗余</span>
            </div>
          </div>
        </div>

        <!-- IT设备 -->
        <div class="workflow-node purple" :class="{ active: selectedModule === 'it-equipment' }" @click="selectModule('it-equipment')">
          <div class="node-icon-wrapper purple-bg">
            <el-icon class="icon-md"><Operation /></el-icon>
          </div>
          <div class="node-content">
            <h4 class="node-title">IT设备</h4>
            <p class="node-desc">服务器 + 存储 + 网络</p>
            <div class="node-stats">
              <span class="stat-item">500 kW 负荷</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情面板 -->
    <div class="detail-panel" v-if="selectedModule" @click.self="closeDetail">
      <div class="detail-content" :class="selectedModule">
        <div class="detail-header">
          <div class="detail-icon" :class="getModuleIconClass(selectedModule)">
            <el-icon>{{ getModuleIcon(selectedModule) }}</el-icon>
          </div>
          <div class="detail-title-area">
            <h3 class="detail-title">{{ getModuleTitle(selectedModule) }}</h3>
            <p class="detail-subtitle">{{ getModuleSubtitle(selectedModule) }}</p>
          </div>
          <button class="close-btn" @click="closeDetail">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        
        <div class="detail-body">
          <!-- 绿电系统详情 -->
          <div v-if="selectedModule === 'green-power'" class="module-detail">
            <div class="detail-section">
              <h4 class="section-title">系统组成</h4>
              <div class="component-grid">
                <div class="component-card">
                  <div class="component-icon sun">
                    <el-icon><Lightning /></el-icon>
                  </div>
                  <div class="component-info">
                    <div class="component-name">光伏系统</div>
                    <div class="component-value">1.0 MW</div>
                  </div>
                </div>
                <div class="component-card">
                  <div class="component-icon wind">
                    <el-icon><Setting /></el-icon>
                  </div>
                  <div class="component-info">
                    <div class="component-name">风力发电</div>
                    <div class="component-value">1.0 MW</div>
                  </div>
                </div>
                <div class="component-card">
                  <div class="component-icon battery">
                    <el-icon><CircleCheckFilled /></el-icon>
                  </div>
                  <div class="component-info">
                    <div class="component-name">储能系统</div>
                    <div class="component-value">39.56 MWh</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <h4 class="section-title">关键指标</h4>
              <div class="metrics-list">
                <div class="metric-item">
                  <span class="metric-label">绿电消纳率</span>
                  <span class="metric-value">70%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">年发电量</span>
                  <span class="metric-value">30,000 MWh</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">投资成本</span>
                  <span class="metric-value">1,094 万元</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 制冷系统详情 -->
          <div v-if="selectedModule === 'cooling'" class="module-detail">
            <div class="detail-section">
              <h4 class="section-title">推荐方案</h4>
              <div class="cooling-info">
                <div class="cooling-tech">
                  <el-icon class="tech-icon"><Location /></el-icon>
                  <span>传统房间级CRAC(上送风)+热通道封闭</span>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <h4 class="section-title">性能指标</h4>
              <div class="metrics-list">
                <div class="metric-item">
                  <span class="metric-label">预测PUE</span>
                  <span class="metric-value">1.23</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">预测WUE</span>
                  <span class="metric-value">1.65</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">制冷功耗</span>
                  <span class="metric-value">79.61 kW</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 供电系统详情 -->
          <div v-if="selectedModule === 'power-supply'" class="module-detail">
            <div class="detail-section">
              <h4 class="section-title">方案等级</h4>
              <div class="power-grade">A级-35 kV 供电一体化方案</div>
            </div>
            <div class="detail-section">
              <h4 class="section-title">系统配置</h4>
              <div class="config-list">
                <div class="config-item">
                  <span class="config-label">外部电压</span>
                  <span class="config-value">35 kV</span>
                </div>
                <div class="config-item">
                  <span class="config-label">冗余配置</span>
                  <span class="config-value">主变N+1，配变2N（互为备用）</span>
                </div>
                <div class="config-item">
                  <span class="config-label">母线类型</span>
                  <span class="config-value">380/220V 单母线分段接线</span>
                </div>
              </div>
            </div>
          </div>

          <!-- IT设备详情 -->
          <div v-if="selectedModule === 'it-equipment'" class="module-detail">
            <div class="detail-section">
              <h4 class="section-title">设备组成</h4>
              <div class="component-grid">
                <div class="component-card">
                  <div class="component-icon server">
                    <el-icon><Operation /></el-icon>
                  </div>
                  <div class="component-info">
                    <div class="component-name">服务器</div>
                    <div class="component-value">高密度机架</div>
                  </div>
                </div>
                <div class="component-card">
                  <div class="component-icon database">
                    <el-icon><Database /></el-icon>
                  </div>
                  <div class="component-info">
                    <div class="component-name">存储系统</div>
                    <div class="component-value">分布式存储</div>
                  </div>
                </div>
                <div class="component-card">
                  <div class="component-icon network">
                    <el-icon><Link /></el-icon>
                  </div>
                  <div class="component-info">
                    <div class="component-name">网络设备</div>
                    <div class="component-value">高性能交换机</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <h4 class="section-title">负荷参数</h4>
              <div class="metrics-list">
                <div class="metric-item">
                  <span class="metric-label">总负荷</span>
                  <span class="metric-value">500 kW</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">功率密度</span>
                  <span class="metric-value">8.0 kW/柜</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 数据中心详情 -->
          <div v-if="selectedModule === 'datacenter'" class="module-detail">
            <div class="detail-section">
              <h4 class="section-title">项目概况</h4>
              <div class="datacenter-info">
                <div class="info-item">
                  <span class="info-label">项目地点</span>
                  <span class="info-value">乌兰察布</span>
                </div>
                <div class="info-item">
                  <span class="info-label">建设规模</span>
                  <span class="info-value">中型数据中心</span>
                </div>
                <div class="info-item">
                  <span class="info-label">设计标准</span>
                  <span class="info-value">Tier 3</span>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <h4 class="section-title">系统架构</h4>
              <div class="architecture-diagram">
                <div class="arch-layer">
                  <div class="layer-title">绿电层</div>
                  <div class="layer-items">光伏 · 风电 · 储能</div>
                </div>
                <div class="arch-arrow">↓</div>
                <div class="arch-layer">
                  <div class="layer-title">供电层</div>
                  <div class="layer-items">UPS · 配电 · 发电机</div>
                </div>
                <div class="arch-arrow">↓</div>
                <div class="arch-layer">
                  <div class="layer-title">IT层</div>
                  <div class="layer-items">服务器 · 存储 · 网络</div>
                </div>
                <div class="arch-arrow">↓</div>
                <div class="arch-layer">
                  <div class="layer-title">制冷层</div>
                  <div class="layer-items">CRAC · 冷通道 · 液冷</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 工作流流程图 -->
    <div class="flow-chart-card card">
      <h3 class="card-title">方案生成流程</h3>
      <div class="flow-chart">
        <div class="flow-step" v-for="(step, index) in workflowSteps" :key="index">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.description }}</div>
          </div>
          <div class="step-arrow" v-if="index < workflowSteps.length - 1">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  RefreshRight,
  Files,
  Lightning,
  Location,
  Aim,
  Operation,
  Setting,
  CircleCheckFilled,
  CircleCloseFilled,
  Link,
  Document,
  Message,
  Phone,
  Close,
  ArrowRight
} from '@element-plus/icons-vue'

const router = useRouter()
const selectedModule = ref(null)

const workflowSteps = [
  { title: '需求解析', description: '收集项目参数，解析用户需求' },
  { title: '初稿生成', description: '调用工具生成绿电、制冷、供电方案' },
  { title: '成本计算', description: '计算项目总投资，检查预算约束' },
  { title: '专家评审', description: '经济性、可靠性、环保性分析' },
  { title: '多轮辩论', description: '专家意见辩论，优化方案' },
  { title: '仲裁决策', description: '综合各方意见，生成最终方案' },
  { title: '报告输出', description: '生成可行性研究报告' }
]

const selectModule = (module) => {
  selectedModule.value = module
}

const closeDetail = () => {
  selectedModule.value = null
}

const getModuleTitle = (module) => {
  const titles = {
    'green-power': '绿电系统',
    'cooling': '制冷系统',
    'power-supply': '供电系统',
    'it-equipment': 'IT设备',
    'datacenter': '数据中心'
  }
  return titles[module] || ''
}

const getModuleSubtitle = (module) => {
  const subtitles = {
    'green-power': '光伏 + 风电 + 储能一体化解决方案',
    'cooling': '高效制冷与热管理系统',
    'power-supply': '可靠供电与冗余保障',
    'it-equipment': '高性能计算与存储设施',
    'datacenter': '数据中心整体架构'
  }
  return subtitles[module] || ''
}

const getModuleIcon = (module) => {
  const icons = {
    'green-power': Lightning,
    'cooling': Location,
    'power-supply': Aim,
    'it-equipment': Operation,
    'datacenter': Files
  }
  return icons[module] || Files
}

const getModuleIconClass = (module) => {
  const classes = {
    'green-power': 'icon-green',
    'cooling': 'icon-blue',
    'power-supply': 'icon-orange',
    'it-equipment': 'icon-purple',
    'datacenter': 'icon-primary'
  }
  return classes[module] || 'icon-primary'
}

const startWorkflow = () => {
  router.push({ name: 'Generate' })
}
</script>

<style scoped>
.workflow-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

/* 页面标题 */
.page-header {
  margin-bottom: var(--spacing-2xl);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: var(--font-size-md);
  color: var(--text-secondary);
}

/* 概览卡片 */
.overview-card {
  padding: var(--spacing-2xl);
  margin-bottom: var(--spacing-2xl);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.overview-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
}

.overview-desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* 工作流图 */
.workflow-graph {
  position: relative;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.workflow-lines {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.line {
  fill: none;
  stroke-width: 3;
  stroke-dasharray: 8 4;
  animation: dash 20s linear infinite;
}

.line-green { stroke: var(--success-color); }
.line-blue { stroke: var(--info-color); }
.line-orange { stroke: var(--warning-color); }
.line-purple { stroke: #8B5CF6; }

@keyframes dash {
  to { stroke-dashoffset: -100; }
}

/* 中心节点 */
.center-node {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-2xl);
  background: linear-gradient(145deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border-radius: var(--radius-xl);
  box-shadow: 0 15px 40px rgba(16, 185, 129, 0.35);
  cursor: pointer;
  transition: all var(--transition-normal);
  z-index: 10;
}

.center-node:hover,
.center-node.active {
  transform: translate(-50%, -50%) scale(1.05);
  box-shadow: 0 20px 50px rgba(16, 185, 129, 0.45);
}

.icon-lg {
  font-size: 48px;
  color: white;
  margin-bottom: var(--spacing-md);
}

.center-node .node-label {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: white;
}

.center-node .node-subtitle {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.85);
}

/* 工作流节点 */
.workflow-node {
  position: absolute;
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  z-index: 5;
}

.workflow-node:hover,
.workflow-node.active {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}

.workflow-node.green { top: 30px; left: 50%; transform: translateX(-50%); }
.workflow-node.blue { bottom: 30px; left: 50%; transform: translateX(-50%); }
.workflow-node.orange { left: 30px; top: 50%; transform: translateY(-50%); }
.workflow-node.purple { right: 30px; top: 50%; transform: translateY(-50%); }

.node-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.green-bg { background: var(--success-bg); }
.blue-bg { background: var(--info-bg); }
.orange-bg { background: var(--warning-bg); }
.purple-bg { background: rgba(139, 92, 246, 0.1); }

.icon-md {
  font-size: 28px;
}

.green-bg .icon-md { color: var(--success-color); }
.blue-bg .icon-md { color: var(--info-color); }
.orange-bg .icon-md { color: var(--warning-color); }
.purple-bg .icon-md { color: #8B5CF6; }

.node-content {
  display: flex;
  flex-direction: column;
}

.node-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.node-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
}

.node-stats {
  display: flex;
  gap: var(--spacing-sm);
}

.stat-item {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  background: var(--bg-hover);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
}

/* 详情面板 */
.detail-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn var(--transition-normal);
}

.detail-content {
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  background: white;
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: scaleIn var(--transition-normal);
}

.detail-header {
  display: flex;
  align-items: center;
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
}

.detail-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-lg);
  font-size: 28px;
}

.icon-green { background: rgba(16, 185, 129, 0.3); color: #34D399; }
.icon-blue { background: rgba(6, 182, 212, 0.3); color: #22D3EE; }
.icon-orange { background: rgba(245, 158, 11, 0.3); color: #FBBF24; }
.icon-purple { background: rgba(139, 92, 246, 0.3); color: #A78BFA; }
.icon-primary { background: rgba(16, 185, 129, 0.3); color: var(--primary-light); }

.detail-title-area {
  flex: 1;
}

.detail-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: 2px;
}

.detail-subtitle {
  font-size: var(--font-size-sm);
  opacity: 0.85;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.detail-body {
  padding: var(--spacing-xl);
  overflow-y: auto;
  max-height: calc(80vh - 120px);
}

.module-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.detail-section {
  background: var(--bg-page);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
}

.section-title {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
}

/* 组件网格 */
.component-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.component-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.component-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: var(--spacing-sm);
}

.component-icon.sun { background: rgba(251, 191, 36, 0.1); color: #FBBF24; }
.component-icon.wind { background: rgba(6, 182, 212, 0.1); color: #06B6D4; }
.component-icon.battery { background: var(--success-bg); color: var(--success-color); }
.component-icon.server { background: rgba(139, 92, 246, 0.1); color: #8B5CF6; }
.component-icon.database { background: rgba(236, 72, 153, 0.1); color: #EC4899; }
.component-icon.network { background: rgba(6, 182, 212, 0.1); color: #06B6D4; }

.component-info {
  text-align: center;
}

.component-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.component-value {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* 指标列表 */
.metrics-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background: white;
  border-radius: var(--radius-md);
}

.metric-label {
  color: var(--text-secondary);
}

.metric-value {
  font-weight: 600;
  color: var(--primary-color);
}

/* 配置列表 */
.config-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.config-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  background: white;
  border-radius: var(--radius-md);
}

.config-label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.config-value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

/* 制冷信息 */
.cooling-info {
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--radius-md);
}

.cooling-tech {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.tech-icon {
  color: var(--info-color);
}

/* 供电等级 */
.power-grade {
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
}

/* 数据中心信息 */
.datacenter-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  background: white;
  border-radius: var(--radius-md);
}

.info-label {
  color: var(--text-secondary);
}

.info-value {
  font-weight: 500;
  color: var(--text-primary);
}

/* 架构图 */
.architecture-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.arch-layer {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-xl);
  background: white;
  border-radius: var(--radius-md);
  min-width: 200px;
}

.layer-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.layer-items {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.arch-arrow {
  color: var(--border-dark);
  font-size: var(--font-size-lg);
}

/* 流程图卡片 */
.flow-chart-card {
  padding: var(--spacing-xl);
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xl);
}

.flow-chart {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-md);
}

.flow-step {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  display: flex;
  flex-direction: column;
}

.step-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
}

.step-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.step-arrow {
  color: var(--border-dark);
  font-size: var(--font-size-lg);
  margin: 0 var(--spacing-sm);
}

/* 响应式 */
@media (max-width: 1024px) {
  .workflow-node {
    flex-direction: column;
    padding: var(--spacing-lg);
    gap: var(--spacing-sm);
  }
  
  .node-content {
    align-items: center;
    text-align: center;
  }
  
  .workflow-node.green { left: 20px; right: 20px; top: 20px; transform: none; }
  .workflow-node.blue { left: 20px; right: 20px; bottom: 20px; transform: none; }
  .workflow-node.orange { left: 20px; top: auto; bottom: 150px; transform: none; }
  .workflow-node.purple { right: 20px; top: auto; bottom: 150px; transform: none; }
}
</style>