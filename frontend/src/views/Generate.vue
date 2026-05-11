<template>
  <div class="generate-page">
    <div class="progress-section">
      <div class="progress-header">
        <h2>方案生成进度</h2>
        <span class="progress-percent">{{ progressPercent }}%</span>
      </div>
      <el-progress :percentage="progressPercent" :status="progressStatus" />
      
      <div class="full-workflow">
        <div
          v-for="(node, index) in workflowNodes"
          :key="index"
          class="workflow-node"
          :class="{ 
            active: currentNodeIndex === index,
            completed: completedNodes.has(index),
            skipped: node.status === 'skipped'
          }"
        >
          <div class="node-icon">
            <el-icon v-if="completedNodes.has(index)"><Check /></el-icon>
            <span v-else-if="currentNodeIndex === index" class="node-spinner">
              <el-icon class="spinning"><Refresh /></el-icon>
            </span>
            <span v-else>{{ node.icon }}</span>
          </div>
          <span class="node-name">{{ node.name }}</span>
          <div v-if="completedNodes.has(index) && node.description" class="node-tooltip">
            {{ node.description }}
          </div>
        </div>
      </div>
    </div>

    <div class="node-detail-section">
      <div v-if="currentNodeIndex >= 0 || anyNodeCompleted(0)" class="stage-panel" :class="{ active: currentNodeIndex === 0 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Document /></el-icon> {{ workflowNodes[0].name }}</h3>
          <el-tag :type="getNodeTagType(0)">{{ getNodeStatus(0) }}</el-tag>
        </div>
        <div v-if="nodeResults.requirementParser" class="node-result">
          <el-card class="result-card">
            <div class="result-content">
              <p>{{ nodeResults.requirementParser.summary }}</p>
              <div class="result-metrics">
                <div class="metric-item">
                  <span class="metric-label">项目地点</span>
                  <span class="metric-value">{{ nodeResults.requirementParser.location }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">总负荷</span>
                  <span class="metric-value">{{ nodeResults.requirementParser.load }} kW</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">绿电目标</span>
                  <span class="metric-value">{{ nodeResults.requirementParser.greenRatio }}%</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 1 || anyNodeCompleted(1)" class="stage-panel" :class="{ active: currentNodeIndex === 1 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Document /></el-icon> {{ workflowNodes[1].name }}</h3>
          <el-tag :type="getNodeTagType(1)">{{ getNodeStatus(1) }}</el-tag>
        </div>
        <div v-if="nodeResults.draftPlan">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="agent-result-card">
                <div class="agent-header">
                  <el-icon class="agent-icon"><Edit /></el-icon>
                  <span class="agent-name">绿电分配方案</span>
                </div>
                <div class="agent-content">
                  <div class="agent-detail">光伏容量: {{ formatNumber(nodeResults.draftPlan.pvCapacity) }} MW</div>
                  <div class="agent-detail">风电容量: {{ formatNumber(nodeResults.draftPlan.windCapacity) }} MW</div>
                  <div class="agent-detail">储能容量: {{ formatNumber(nodeResults.draftPlan.storageCapacity) }} MWh</div>
                  <div class="agent-detail">绿电占比: {{ formatPercent(nodeResults.draftPlan.achievedGreenRatio) }}</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="agent-result-card">
                <div class="agent-header">
                  <el-icon class="agent-icon"><Tools /></el-icon>
                  <span class="agent-name">制冷方案</span>
                </div>
                <div class="agent-content">
                  <div class="agent-detail">推荐技术: {{ nodeResults.draftPlan.coolingTech }}</div>
                  <div class="agent-detail">预测PUE: {{ formatNumber(nodeResults.draftPlan.pue, 2) }}</div>
                  <div class="agent-detail">预测WUE: {{ formatNumber(nodeResults.draftPlan.wue, 2) }}</div>
                  <div class="agent-detail">制冷功耗: {{ formatNumber(nodeResults.draftPlan.coolingPower) }} kW</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="agent-result-card">
                <div class="agent-header">
                  <el-icon class="agent-icon"><Tools /></el-icon>
                  <span class="agent-name">供电方案</span>
                </div>
                <div class="agent-content">
                  <div class="agent-detail">方案等级: {{ nodeResults.draftPlan.tierLevel }}</div>
                  <div class="agent-detail">外部电压: {{ nodeResults.draftPlan.externalVoltage }}</div>
                  <div class="agent-detail">冗余配置: {{ nodeResults.draftPlan.redundancyLogic }}</div>
                  <div class="agent-detail">母线类型: {{ nodeResults.draftPlan.upsConfig }}</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 2 || anyNodeCompleted(2)" class="stage-panel" :class="{ active: currentNodeIndex === 2 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Tools /></el-icon> {{ workflowNodes[2].name }}</h3>
          <el-tag :type="getNodeTagType(2)">{{ getNodeStatus(2) }}</el-tag>
        </div>
        <div v-if="nodeResults.costCalculation" class="cost-panel">
          <el-card class="cost-card">
            <div class="cost-summary">
              <div class="cost-row">
                <span class="cost-label">供电系统成本</span>
                <span class="cost-value">{{ nodeResults.costCalculation.powerSupplyCost }} 万元</span>
              </div>
              <div class="cost-row">
                <span class="cost-label">绿电系统成本</span>
                <span class="cost-value">{{ nodeResults.costCalculation.greenPowerCost }} 万元</span>
              </div>
              <div class="cost-row total">
                <span class="cost-label">项目总投资</span>
                <span class="cost-value">{{ nodeResults.costCalculation.totalCost }} 万元</span>
              </div>
              <div class="cost-row budget">
                <span class="cost-label">预算约束</span>
                <span class="cost-value" :class="nodeResults.costCalculation.isOverBudget ? 'over-budget' : 'under-budget'">
                  {{ nodeResults.costCalculation.budget }} 万元
                </span>
              </div>
            </div>
            <div v-if="nodeResults.costCalculation.isOverBudget" class="budget-warning">
              <el-icon class="warning-icon"><Warning /></el-icon>
              <span>超出预算 {{ nodeResults.costCalculation.budgetDelta }} 万元，正在重新优化方案...</span>
            </div>
            <div v-else class="budget-success">
              <el-icon class="success-icon"><Check /></el-icon>
              <span>预算校验通过，结余 {{ Math.abs(nodeResults.costCalculation.budgetDelta) }} 万元</span>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 3 || anyNodeCompleted(3)" class="stage-panel" :class="{ active: currentNodeIndex >= 3 && currentNodeIndex <= 5 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><User /></el-icon> 多专家交叉评审</h3>
          <el-tag :type="getExpertStageTagType()">{{ getExpertStageStatus() }}</el-tag>
        </div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="(expert, index) in expertResults" :key="index">
            <el-card class="expert-card" :class="getExpertStatusClass(expert)">
              <div class="expert-header">
                <el-icon class="expert-icon"><User /></el-icon>
                <span class="expert-name">{{ expert.name }}</span>
              </div>
              <div class="expert-status">
                <el-tag :type="getExpertTagType(expert.status)">{{ expert.status }}</el-tag>
              </div>
              <div v-if="expert.status === '已完成'" class="expert-score">
                <div class="score-label">置信度</div>
                <div class="score-value">{{ expert.score.toFixed(2) }}</div>
              </div>
              <div v-if="expert.status === '已完成'" class="expert-summary">
                {{ expert.summary }}
              </div>
              <div v-if="expert.status === '已完成' && expert.recommendations.length > 0" class="expert-recommendations">
                <div class="recommendation-label">建议</div>
                <ul>
                  <li v-for="(rec, i) in expert.recommendations" :key="i">{{ rec }}</li>
                </ul>
              </div>
              <div v-if="expert.status === '已完成' && expert.concerns && expert.concerns.length > 0" class="expert-concerns">
                <div class="concern-label">关注事项</div>
                <ul>
                  <li v-for="(concern, i) in expert.concerns" :key="i">{{ concern }}</li>
                </ul>
              </div>
              <div v-if="expert.status === '已完成' && expert.metrics && Object.keys(expert.metrics).length > 0" class="expert-metrics">
                <div class="metrics-label">关键指标</div>
                <div class="metrics-grid">
                  <div v-for="(value, key) in expert.metrics" :key="key" class="metric-item">
                    <span class="metric-key">{{ formatMetricKey(key) }}</span>
                    <span class="metric-val">{{ formatMetricValue(key, value) }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div v-if="currentNodeIndex >= 6 || anyNodeCompleted(6)" class="stage-panel" :class="{ active: currentNodeIndex === 6 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Document /></el-icon> {{ workflowNodes[6].name }}</h3>
          <el-tag :type="getNodeTagType(6)">{{ getNodeStatus(6) }}</el-tag>
        </div>
        <div v-if="debateResults" class="debate-panel">
          <div class="debate-header">
            <span class="debate-round">第 {{ debateResults.currentRound }} 轮辩论</span>
            <span class="consensus-score">共识度: {{ formatPercent(debateResults.consensusScore, 0) }}</span>
          </div>
          <el-card class="debate-chat-container">
            <div ref="debateChatRef" class="debate-chat-messages">
              <template v-for="(round, roundIndex) in debateResults.rounds" :key="roundIndex">
                <div class="round-divider">
                  <span class="round-label">第 {{ round.number }} 轮辩论</span>
                </div>
                <div 
                  v-for="(statement, stmtIndex) in round.statements" 
                  :key="stmtIndex" 
                  class="chat-message"
                  :class="getExpertClass(statement.speaker)"
                >
                  <div class="avatar-wrapper">
                    <div class="avatar" :style="{ background: getExpertColor(statement.speaker) }">
                      <span class="avatar-text">{{ getExpertInitial(statement.speaker) }}</span>
                    </div>
                    <span class="speaker-name">{{ statement.speaker }}</span>
                  </div>
                  <div class="message-bubble">
                    <span class="message-content">{{ statement.content }}</span>
                  </div>
                </div>
              </template>
              <div v-if="debateResults.rounds.length === 0" class="empty-chat">
                <p>辩论尚未开始...</p>
              </div>
            </div>
          </el-card>
          <div v-if="debateResults.summary && debateResults.summary.suggestions.length > 0" class="debate-summary-card">
            <h4><el-icon><Lightbulb /></el-icon> 辩论纪要与建议</h4>
            <div class="suggestions-list">
              <div v-for="(suggestion, i) in debateResults.summary.suggestions" :key="i" class="suggestion-item">
                <el-icon class="suggestion-icon"><CheckCircle /></el-icon>
                <span>{{ suggestion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 7 || anyNodeCompleted(7)" class="stage-panel" :class="{ active: currentNodeIndex === 7 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Document /></el-icon> {{ workflowNodes[7].name }}</h3>
          <el-tag :type="getNodeTagType(7)">{{ getNodeStatus(7) }}</el-tag>
        </div>
        <div v-if="arbitratorResult" class="arbitrator-panel">
          <el-card class="arbitrator-card">
            <div class="arbitrator-header">
              <span class="arbitrator-title">仲裁决策结果</span>
              <span class="confidence-badge">置信度: {{ formatPercent(arbitratorResult.confidence, 0) }}</span>
            </div>
            <div class="arbitrator-content">
              <div class="consensus-indicator">
                <span class="label">最终共识度</span>
                <span class="value" :class="Number.isFinite(Number(arbitratorResult.consensusScore)) && Number(arbitratorResult.consensusScore) >= 0.8 ? 'high' : 'medium'">
                  {{ formatPercent(arbitratorResult.consensusScore, 0) }}
                </span>
              </div>
              <div class="decision-summary">
                <p>{{ arbitratorResult.summary }}</p>
              </div>
              <div class="overall-scores">
                <h4>综合评分</h4>
                <el-row :gutter="20">
                  <el-col :span="8">
                    <div class="score-card">
                      <span class="score-label">经济性</span>
                      <span class="score-value">{{ formatPercent(arbitratorResult.scores.economic, 0) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="score-card">
                      <span class="score-label">可靠性</span>
                      <span class="score-value">{{ formatPercent(arbitratorResult.scores.reliability, 0) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="score-card highlight">
                      <span class="score-label">环保性</span>
                      <span class="score-value">{{ formatPercent(arbitratorResult.scores.environmental, 0) }}</span>
                    </div>
                  </el-col>
                </el-row>
              </div>
              <div v-if="arbitratorResult.tradeOffs && arbitratorResult.tradeOffs.length > 0" class="trade-offs">
                <h4>权衡方案</h4>
                <ul>
                  <li v-for="(trade, i) in arbitratorResult.tradeOffs" :key="i">
                    <strong>{{ trade.conflict }}:</strong> {{ trade.resolution }}
                  </li>
                </ul>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 8 || anyNodeCompleted(8)" class="stage-panel" :class="{ active: currentNodeIndex === 8 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Files /></el-icon> {{ workflowNodes[8].name }}</h3>
          <el-tag :type="getNodeTagType(8)">{{ getNodeStatus(8) }}</el-tag>
        </div>
        <div v-if="finalReport" class="report-panel">
          <el-alert
            title="报告生成完成"
            type="success"
            description="方案报告已生成，包含完整的可行性分析和实施建议"
            :closable="false"
            show-icon
          />
          <el-card class="report-preview">
            <h4>报告摘要</h4>
            <div class="report-content" v-html="finalReport.summary"></div>
            <div class="report-metrics">
              <div class="report-metric">
                <span class="metric-label">报告状态</span>
                <span class="metric-value success">已完成</span>
              </div>
              <div class="report-metric">
                <span class="metric-label">报告格式</span>
                <span class="metric-value">Markdown</span>
              </div>
              <div class="report-metric">
                <span class="metric-label">字数统计</span>
                <span class="metric-value">{{ finalReport.wordCount }} 字</span>
              </div>
              <div class="report-metric">
                <span class="metric-label">报告路径</span>
                <span class="metric-value">{{ finalReport.path || '-' }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 9 || isCompleted" class="stage-panel" :class="{ active: currentNodeIndex === 9 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Download /></el-icon> {{ workflowNodes[9].name }}</h3>
          <el-tag type="success">已完成</el-tag>
        </div>
        <el-alert
          title="方案生成成功！"
          type="success"
          description="点击下方按钮查看完整方案详情"
          :closable="false"
          show-icon
        />
        
        <div class="solution-preview">
          <h4>方案概览</h4>
          <div class="preview-grid">
            <div class="preview-item">
              <span class="preview-label">方案名称</span>
              <span class="preview-value">{{ finalSolution.name || '--' }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">总体评分</span>
              <span class="preview-value highlight">{{ formatPercent(finalSolution.overallScore, 0) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">PUE</span>
              <span class="preview-value">{{ formatNumber(finalSolution.pue, 2) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">绿电比例</span>
              <span class="preview-value">{{ formatPercent(finalSolution.greenPowerRatio, 0) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">总投资</span>
              <span class="preview-value">{{ formatWithUnit(finalSolution.totalCost, '万元', 0) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">Tier等级</span>
              <span class="preview-value">{{ finalSolution.tierLevel ? `Tier ${finalSolution.tierLevel}` : '--' }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">可用性</span>
              <span class="preview-value">{{ Number.isFinite(Number(finalSolution.expectedAvailability)) ? `${Number(finalSolution.expectedAvailability).toFixed(4)}%` : '--' }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">年碳排放</span>
              <span class="preview-value">{{ formatWithUnit(finalSolution.annualCarbonEmission, '吨', 0) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">投资回报率</span>
              <span class="preview-value">{{ formatPercent(finalSolution.roi, 1) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">投资回收期</span>
              <span class="preview-value">{{ formatWithUnit(finalSolution.paybackPeriod, '年', 1) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="logs-section">
      <div class="logs-header">
        <h3><el-icon><Document /></el-icon> 实时日志输出</h3>
        <div class="logs-actions">
          <el-button type="text" @click="clearLogs">清空日志</el-button>
          <el-button type="text" @click="downloadLogs">下载日志</el-button>
        </div>
      </div>
      <div class="logs-container" ref="logsContainer">
        <div
          v-for="(log, index) in logs"
          :key="index"
          class="log-item"
          :class="log.type"
        >
          <span class="log-time">{{ log.time }}</span>
          <span class="log-type">{{ log.type.toUpperCase() }}</span>
          <span class="log-content">{{ log.content }}</span>
        </div>
      </div>
    </div>

    <div class="generate-footer">
      <el-button v-if="!isCompleted && !isFailed" @click="cancelGenerate">取消生成</el-button>
      <el-button
        v-if="isCompleted"
        class="primary-btn"
        @click="goToDetail"
      >查看方案详情</el-button>
      <template v-if="isFailed">
        <el-button @click="regenerate">重新生成</el-button>
        <el-button type="text" @click="viewError">查看错误详情</el-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Check, Document, Edit, User, Files, Download, Refresh, Warning, Tools 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { workflowApi, solutionApi } from '@/api'
import { mockSolutionData } from '@/mock/data.js'

const router = useRouter()

const workflowNodes = [
  { name: '需求解析', icon: '1', description: '解析用户输入参数' },
  { name: '初稿生成', icon: '2', description: '调用工具生成初始方案' },
  { name: '成本计算', icon: '3', description: '计算项目投资成本' },
  { name: '经济性分析', icon: '4', description: '经济专家评估' },
  { name: '可靠性分析', icon: '5', description: '可靠性专家评估' },
  { name: '环保性分析', icon: '6', description: '环保专家评估' },
  { name: '辩论阶段', icon: '7', description: '专家交叉辩论' },
  { name: '仲裁决策', icon: '8', description: '综合仲裁' },
  { name: '最终报告', icon: '9', description: '生成报告' },
  { name: '输出', icon: '10', description: '输出方案' }
]

const currentNodeIndex = ref(-1)
const progressPercent = ref(0)
const isCompleted = ref(false)
const isFailed = ref(false)
const logsContainer = ref(null)
const workflowId = ref('mock-workflow-001')
const completedNodes = ref(new Set())
let mockTimer = null
let currentStepIndex = 0

const nodeResults = reactive({
  requirementParser: null,
  draftPlan: null,
  costCalculation: null
})

const expertResults = reactive([
  { name: '经济性专家', expertType: 'economic', status: '等待中', score: 0, summary: '', recommendations: [], concerns: [], metrics: {} },
  { name: '供电可靠性专家', expertType: 'reliability', status: '等待中', score: 0, summary: '', recommendations: [], concerns: [], metrics: {} },
  { name: '环保性专家', expertType: 'environmental', status: '等待中', score: 0, summary: '', recommendations: [], concerns: [], metrics: {} }
])

const debateResults = ref(null)

const arbitratorResult = reactive({
  consensusScore: 0,
  summary: '',
  confidence: 0,
  scores: { economic: 0, reliability: 0, environmental: 0 },
  tradeOffs: []
})

const finalReport = ref(null)

const finalSolution = reactive({
  name: '',
  overallScore: 0,
  pue: 0,
  greenPowerRatio: 0,
  totalCost: 0,
  tierLevel: 0,
  expectedAvailability: 0,
  annualCarbonEmission: 0,
  roi: 0,
  paybackPeriod: 0
})

const progressStatus = computed(() => {
  if (isCompleted.value) return 'success'
  if (isFailed.value) return 'exception'
  return 'active'
})

const getNodeStatus = (index) => {
  if (completedNodes.value.has(index)) return '已完成'
  if (currentNodeIndex.value === index) return '进行中'
  return '等待中'
}

const getNodeTagType = (index) => {
  const status = getNodeStatus(index)
  const types = { '已完成': 'success', '进行中': 'warning', '等待中': 'info' }
  return types[status] || 'info'
}

const anyNodeCompleted = (index) => {
  return completedNodes.value.has(index)
}

const getExpertStageTagType = () => {
  const completedCount = expertResults.filter(e => e.status === '已完成').length
  if (completedCount === 3) return 'success'
  if (completedCount > 0) return 'warning'
  return 'info'
}

const getExpertStageStatus = () => {
  const completedCount = expertResults.filter(e => e.status === '已完成').length
  if (completedCount === 3) return '已完成'
  if (completedCount > 0) return `${completedCount}/3 进行中`
  return '等待中'
}

const getExpertStatusClass = (expert) => {
  const classes = { '等待中': 'waiting', '运行中': 'running', '已完成': 'completed', '失败': 'failed' }
  return classes[expert.status] || 'waiting'
}

const getExpertTagType = (status) => {
  const types = { '等待中': 'info', '运行中': 'warning', '已完成': 'success', '失败': 'danger' }
  return types[status] || 'info'
}

const formatMetricKey = (key) => {
  const keyMap = {
    total_cost: '总成本', cost_per_rack: '单柜成本', roi: '投资回报率',
    payback_period: '回收期', availability: '可用性', annual_downtime: '年停机时间',
    annual_carbon_emission: '年碳排放', pue_target: 'PUE目标',
    green_power_ratio: '绿电比例', carbon_per_rack: '单柜碳排放',
    tier_level: 'Tier等级', expected_availability: '预期可用性',
    cost_efficiency: '成本效率', reliability: '可靠性',
    environmental_score: '环保评分', pue_score: 'PUE评分',
    green_power_score: '绿电评分', carbon_efficiency: '碳效率'
  }
  return keyMap[key] || key
}

const formatMetricValue = (key, value) => {
  if (typeof value !== 'number') return value
  if (key.includes('ratio') || key.includes('score') || key.includes('efficiency') || key === 'roi' || key.includes('availability') || key.includes('reliability')) return `${(value * 100).toFixed(1)}%`
  if (key.includes('cost') || key.includes('carbon_per_rack')) return `${value.toFixed(2)}万元`
  if (key.includes('period')) return `${value.toFixed(1)}年`
  if (key.includes('emission')) return `${value.toFixed(1)}吨`
  if (key.includes('downtime')) return `${value.toFixed(2)}小时`
  return value.toFixed(2)
}

const addLog = (content, type = 'info') => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ time, type, content })
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

const logs = ref([])

const toNumber = (v, fallback = null) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : fallback
}

const formatNumber = (v, digits = 2) => {
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(digits) : '--'
}

const formatPercent = (v, digits = 0) => {
  const n = Number(v)
  return Number.isFinite(n) ? `${(n * 100).toFixed(digits)}%` : '--'
}

const formatWithUnit = (v, unit, digits = 2) => {
  const n = Number(v)
  if (!Number.isFinite(n)) return '--'
  return `${n.toFixed(digits)} ${unit}`
}

// ============================================
// 模拟工作流进度
// ============================================
const mockSteps = [
  {
    name: 'requirement_parser',
    index: 0,
    duration: 1500,
    execute: () => {
      const req = mockSolutionData.intermediate_results.requirement_parser.requirement
      nodeResults.requirementParser = {
        summary: `${req.location}需求参数已结构化解析`,
        location: req.location,
        load: req.planned_load_kw,
        greenRatio: req.green_power_ratio * 100
      }
      addLog(`需求解析完成: ${req.location}, 负荷${req.planned_load_kw}kW`, 'success')
    }
  },
  {
    name: 'draft_plan_agent',
    index: 1,
    duration: 2500,
    execute: () => {
      const draft = mockSolutionData.intermediate_results.draft_plan_agent.full_output
      const gp = draft.green_power_result.optimization
      const cooling = draft.cooling_result
      const power = draft.power_supply_plan
      
      nodeResults.draftPlan = {
        pvCapacity: gp.pv_capacity_mw,
        windCapacity: gp.wind_capacity_mw,
        storageCapacity: gp.storage_capacity_mwh,
        achievedGreenRatio: gp.achieved_green_ratio,
        coolingTech: cooling.cooling_technology,
        pue: cooling.estimated_pue,
        wue: cooling.predicted_wue,
        coolingPower: cooling.cooling_power_consumption,
        wasteHeatRecovery: cooling.waste_heat_recovery_kw,
        tierLevel: power.raw_json.machine_room_grade,
        externalVoltage: power.external_voltage,
        redundancyLogic: power.redundancy_logic,
        upsConfig: power.bus_type,
        schemeName: power.scheme_name,
        costPerMw: power.raw_json.cost_per_mw
      }
      addLog(`初稿方案: 光伏${gp.pv_capacity_mw}MW, 风电${gp.wind_capacity_mw}MW, 储能${gp.storage_capacity_mwh}MWh`, 'success')
    }
  },
  {
    name: 'cost_calculation',
    index: 2,
    duration: 1500,
    execute: () => {
      const cost = mockSolutionData.intermediate_results.cost_calculation.full_output.economic_analysis_result
      nodeResults.costCalculation = {
        powerSupplyCost: cost.capex_breakdown.power_supply_system_lakh,
        greenPowerCost: cost.capex_breakdown.green_power_system_lakh,
        totalCost: cost.total_capex_lakh,
        budget: cost.budget_constraint_lakh,
        isOverBudget: cost.is_over_budget,
        budgetDelta: cost.budget_delta_lakh
      }
      addLog(`成本计算: 总投资${cost.total_capex_lakh}万元`, cost.is_over_budget ? 'warning' : 'success')
    }
  },
  {
    name: 'economic_analysis',
    index: 3,
    duration: 1800,
    execute: () => {
      const expert = mockSolutionData.intermediate_results.economic_analysis.full_output
      expertResults[0] = { ...expertResults[0], status: '已完成', score: expert.confidence, summary: expert.summary, recommendations: expert.recommendations, concerns: expert.concerns, metrics: expert.metrics }
      addLog(`经济性专家评审完成: 置信度${expert.confidence}`, 'success')
    }
  },
  {
    name: 'power_reliability_analysis',
    index: 4,
    duration: 1800,
    execute: () => {
      const expert = mockSolutionData.intermediate_results.power_reliability_analysis.full_output
      expertResults[1] = { ...expertResults[1], status: '已完成', score: expert.confidence, summary: expert.summary, recommendations: expert.recommendations, concerns: expert.concerns, metrics: expert.metrics }
      addLog(`可靠性专家评审完成: 置信度${expert.confidence}`, 'success')
    }
  },
  {
    name: 'environmental_analysis',
    index: 5,
    duration: 1800,
    execute: () => {
      const expert = mockSolutionData.intermediate_results.environmental_analysis.full_output
      expertResults[2] = { ...expertResults[2], status: '已完成', score: expert.confidence, summary: expert.summary, recommendations: expert.recommendations, concerns: expert.concerns, metrics: expert.metrics }
      addLog(`环保性专家评审完成: 置信度${expert.confidence}`, 'success')
    }
  },
  {
    name: 'debate_round',
    index: 6,
    duration: 3500,
    execute: () => {
      debateResults.value = {
        currentRound: 2,
        consensusScore: 0.85,
        rounds: [],
        summary: { suggestions: mockSolutionData.intermediate_results.arbitrator.full_output.recommendations }
      }
      
      const debates = mockSolutionData.debate_history
      debates.forEach(d => {
        let roundEntry = debateResults.value.rounds.find(r => r.number === d.round)
        if (!roundEntry) {
          roundEntry = { number: d.round, statements: [] }
          debateResults.value.rounds.push(roundEntry)
        }
        roundEntry.statements.push({ speaker: d.speaker, content: d.content })
      })
      
      addLog('辩论阶段完成，专家已达成共识', 'success')
    }
  },
  {
    name: 'arbitrator',
    index: 7,
    duration: 2000,
    execute: () => {
      const arb = mockSolutionData.intermediate_results.arbitrator.full_output
      arbitratorResult.summary = arb.summary
      arbitratorResult.confidence = mockSolutionData.confidence
      arbitratorResult.scores = { 
        economic: arb.scores.economic, 
        reliability: arb.scores.reliability, 
        environmental: arb.scores.environmental 
      }
      arbitratorResult.consensusScore = arb.scores.overall
      arbitratorResult.tradeOffs = arb.trade_offs
      addLog(`仲裁决策完成: 综合评分${(arb.scores.overall * 100).toFixed(0)}%`, 'success')
    }
  },
  {
    name: 'final_report',
    index: 8,
    duration: 1500,
    execute: () => {
      finalReport.value = {
        summary: mockSolutionData.intermediate_results.arbitrator.full_output.summary,
        path: '/data/reports/mock-solution-001.md',
        wordCount: 3520
      }
      addLog('最终报告生成完成', 'success')
    }
  },
  {
    name: 'output',
    index: 9,
    duration: 1200,
    execute: () => {
      finalSolution.name = mockSolutionData.name
      finalSolution.overallScore = mockSolutionData.overall_scores.overall
      finalSolution.pue = mockSolutionData.key_metrics.pue
      finalSolution.greenPowerRatio = mockSolutionData.key_metrics.green_power_ratio
      finalSolution.totalCost = mockSolutionData.key_metrics.total_cost
      finalSolution.tierLevel = mockSolutionData.key_metrics.tier_level
      finalSolution.expectedAvailability = mockSolutionData.key_metrics.expected_availability
      finalSolution.annualCarbonEmission = mockSolutionData.key_metrics.annual_carbon_emission
      finalSolution.roi = mockSolutionData.key_metrics.roi
      finalSolution.paybackPeriod = mockSolutionData.key_metrics.payback_period
      addLog('输出节点完成，方案生成成功！', 'success')
    }
  }
]

const executeNextStep = () => {
  if (currentStepIndex >= mockSteps.length || isFailed.value || isCompleted.value) {
    if (currentStepIndex >= mockSteps.length) {
      isCompleted.value = true
      progressPercent.value = 100
      localStorage.setItem('currentSolutionId', workflowId.value)
      addLog('✅ 工作流执行完成（来源: mock data）', 'success')
    }
    return
  }

  const step = mockSteps[currentStepIndex]
  currentNodeIndex.value = step.index
  addLog(`开始执行 ${workflowNodes[step.index].name}...`, 'info')
  
  // 更新进度
  progressPercent.value = Math.round((currentStepIndex / mockSteps.length) * 100)
  
  setTimeout(() => {
    step.execute()
    completedNodes.value.add(step.index)
    progressPercent.value = Math.round(((currentStepIndex + 1) / mockSteps.length) * 100)
    currentStepIndex++
    
    mockTimer = setTimeout(executeNextStep, 500)
  }, step.duration)
}

const startMockWorkflow = () => {
  addLog('系统启动，开始生成方案（模拟模式）...', 'info')
  addLog('使用工作流ID: mock-workflow-001', 'info')
  addLog('开始模拟工作流进度...', 'info')
  
  setTimeout(executeNextStep, 800)
}

const clearLogs = () => { logs.value = [] }

const downloadLogs = () => {
  const content = logs.value.map(log => `${log.time} [${log.type.toUpperCase()}] ${log.content}`).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'generate_logs.txt'; a.click()
  URL.revokeObjectURL(url)
}

const cancelGenerate = () => {
  if (mockTimer) clearTimeout(mockTimer)
  router.push('/config')
}

const regenerate = () => {
  if (mockTimer) clearTimeout(mockTimer)
  progressPercent.value = 0; currentNodeIndex.value = -1; isCompleted.value = false; isFailed.value = false
  logs.value = []; completedNodes.value = new Set(); currentStepIndex = 0
  nodeResults.requirementParser = null; nodeResults.draftPlan = null; nodeResults.costCalculation = null
  expertResults.forEach(e => { e.status = '等待中'; e.score = 0; e.summary = ''; e.recommendations = []; e.concerns = []; e.metrics = {} })
  debateResults.value = null
  arbitratorResult.summary = ''; arbitratorResult.confidence = 0; arbitratorResult.scores = { economic: 0, reliability: 0, environmental: 0 }; arbitratorResult.tradeOffs = []; arbitratorResult.consensusScore = 0
  finalReport.value = null
  Object.assign(finalSolution, { name: '', overallScore: 0, pue: 0, greenPowerRatio: 0, totalCost: 0, tierLevel: 0, expectedAvailability: 0, annualCarbonEmission: 0, roi: 0, paybackPeriod: 0 })
  router.push('/config')
}

const viewError = () => { ElMessage.error('请查看下方实时日志中的错误信息') }

const expertColors = {
  'Economic Analysis Expert-Zhang': { color: '#00b894', bg: '#ecfdf5', class: 'expert-economic' },
  'Power Reliability Expert-Li': { color: '#00cec9', bg: '#cffafe', class: 'expert-reliability' },
  'Environmental Analysis Expert-Wang': { color: '#f39c12', bg: '#fff7ed', class: 'expert-environmental' },
  '经济性专家': { color: '#00b894', bg: '#ecfdf5', class: 'expert-economic' },
  '供电可靠性专家': { color: '#00cec9', bg: '#cffafe', class: 'expert-reliability' },
  '环保性专家': { color: '#f39c12', bg: '#fff7ed', class: 'expert-environmental' },
}

const getExpertColor = (speaker) => {
  for (const [name, config] of Object.entries(expertColors)) {
    if (speaker.includes(name.split('-')[0].split(' ')[0]) || speaker.includes(name.split('-')[1]) || name.includes(speaker)) {
      return config.color
    }
  }
  return '#636e72'
}

const getExpertClass = (speaker) => {
  for (const [name, config] of Object.entries(expertColors)) {
    if (speaker.includes(name.split('-')[0].split(' ')[0]) || speaker.includes(name.split('-')[1]) || name.includes(speaker)) {
      return config.class
    }
  }
  return 'expert-default'
}

const getExpertInitial = (speaker) => {
  if (speaker.includes('Economic') || speaker.includes('Zhang') || speaker.includes('经济性')) return '经'
  if (speaker.includes('Reliability') || speaker.includes('Li') || speaker.includes('可靠性')) return '电'
  if (speaker.includes('Environmental') || speaker.includes('Wang') || speaker.includes('环保性')) return '环'
  return speaker.charAt(0)
}

const goToDetail = () => {
  const solutionId = localStorage.getItem('currentSolutionId') || workflowId.value
  if (!solutionId) {
    ElMessage.error('未找到可用方案ID，请稍后重试')
    return
  }
  router.push(`/detail/${solutionId}`)
}

onMounted(() => {
  startMockWorkflow()
})

onUnmounted(() => {
  if (mockTimer) clearTimeout(mockTimer)
})
</script>

<style scoped>
.generate-page {
  display: flex;
  flex-direction: column;
  height: calc(100% - 20px);
  overflow-y: auto;
}

.progress-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.progress-percent {
  font-size: 24px;
  font-weight: 600;
  color: #00b894;
}

.full-workflow {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  position: relative;
  padding-bottom: 50px;
}

.full-workflow::before {
  content: '';
  position: absolute;
  top: 18px;
  left: 3%;
  right: 3%;
  height: 2px;
  background: #E4E7ED;
  z-index: 0;
}

.workflow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 1;
  flex: 1;
  position: relative;
  cursor: pointer;
}

.workflow-node:hover .node-tooltip {
  opacity: 1;
  visibility: visible;
}

.node-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #E4E7ED;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #8F959E;
  font-weight: 600;
  transition: all 0.3s;
}

.workflow-node.active .node-icon {
  background: #00b894;
  color: white;
}

.workflow-node.completed .node-icon {
  background: #00cec9;
  color: white;
}

.node-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.node-name {
  font-size: 12px;
  color: #8F959E;
  text-align: center;
  max-width: 80px;
}

.workflow-node.active .node-name,
.workflow-node.completed .node-name {
  color: #1F2329;
  font-weight: 500;
}

.node-tooltip {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: #1F2329;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
  z-index: 10;
}

.node-tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #1F2329;
}

.node-detail-section {
  margin-bottom: 20px;
}

.stage-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.stage-panel.active {
  border-color: #00b894;
  box-shadow: 0 4px 20px rgba(0, 184, 148, 0.1);
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stage-header h3 {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.stage-icon {
  color: #00b894;
}

.result-card {
  background: #F5F7FA;
}

.result-content p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.7;
  margin-bottom: 16px;
}

.result-metrics {
  display: flex;
  gap: 30px;
}

.agent-result-card {
  margin-bottom: 16px;
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.agent-icon {
  color: #00b894;
}

.agent-name {
  font-weight: 600;
  font-size: 14px;
}

.agent-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.agent-detail {
  font-size: 13px;
  color: #4E5969;
}

.cost-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #F5F7FA;
  border-radius: 8px;
}

.cost-row.total {
  background: linear-gradient(135deg, #00b89415 0%, #00cec915 100%);
  font-weight: 600;
}

.cost-label {
  color: #8F959E;
  font-size: 14px;
}

.cost-value {
  font-size: 16px;
  font-weight: 600;
  color: #1F2329;
}

.over-budget {
  color: #F53F3F !important;
}

.under-budget {
  color: #00b894 !important;
}

.budget-warning,
.budget-success {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
}

.budget-warning {
  background: #FFF2F0;
  color: #F53F3F;
}

.budget-success {
  background: #ECFDF5;
  color: #00b894;
}

.expert-card {
  transition: all 0.3s;
}

.expert-card.waiting {
  opacity: 0.6;
}

.expert-card.running {
  border: 2px solid #f39c12;
}

.expert-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.expert-icon {
  color: #00b894;
}

.expert-name {
  font-weight: 600;
  font-size: 14px;
}

.expert-status {
  margin-bottom: 12px;
}

.expert-score {
  background: #F5F7FA;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 12px;
}

.score-label {
  font-size: 12px;
  color: #8F959E;
  margin-bottom: 4px;
}

.score-value {
  font-size: 20px;
  font-weight: 600;
  color: #00b894;
}

.expert-summary {
  font-size: 13px;
  color: #4E5969;
  line-height: 1.6;
  margin-bottom: 12px;
}

.expert-recommendations,
.expert-concerns {
  margin-bottom: 12px;
}

.recommendation-label,
.concern-label,
.metrics-label {
  font-size: 12px;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 8px;
}

.expert-recommendations ul,
.expert-concerns ul {
  margin: 0;
  padding-left: 20px;
}

.expert-recommendations li,
.expert-concerns li {
  font-size: 12px;
  color: #4E5969;
  margin-bottom: 4px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.metrics-grid .metric-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background: #F5F7FA;
  border-radius: 6px;
  font-size: 12px;
}

.metric-key {
  color: #8F959E;
}

.metric-val {
  color: #1F2329;
  font-weight: 500;
}

.debate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.debate-round,
.consensus-score {
  font-size: 14px;
  font-weight: 600;
  color: #00b894;
}

.debate-chat-container {
  margin-bottom: 20px;
}

.debate-chat-messages {
  max-height: 400px;
  overflow-y: auto;
}

.round-divider {
  text-align: center;
  margin: 16px 0;
  color: #8F959E;
  font-size: 12px;
}

.round-label {
  background: #F5F7FA;
  padding: 4px 16px;
  border-radius: 12px;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.speaker-name {
  font-size: 11px;
  color: #8F959E;
}

.message-bubble {
  flex: 1;
  background: #F5F7FA;
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
}

.message-content {
  font-size: 13px;
  color: #4E5969;
  line-height: 1.6;
}

.empty-chat {
  text-align: center;
  color: #8F959E;
  padding: 40px;
}

.debate-summary-card {
  padding: 20px;
  background: #F5F7FA;
  border-radius: 12px;
}

.debate-summary-card h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4E5969;
  background: white;
  padding: 10px 14px;
  border-radius: 8px;
}

.suggestion-icon {
  color: #00b894;
}

.arbitrator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E4E7ED;
}

.arbitrator-title {
  font-size: 16px;
  font-weight: 600;
  color: #1F2329;
}

.confidence-badge {
  background: #ECFDF5;
  color: #00b894;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.consensus-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 10px;
  margin-bottom: 20px;
}

.consensus-indicator .label {
  color: #8F959E;
  font-size: 14px;
}

.consensus-indicator .value {
  font-size: 22px;
  font-weight: 600;
  color: #f39c12;
}

.consensus-indicator .value.high {
  color: #00b894;
}

.decision-summary {
  margin-bottom: 24px;
}

.decision-summary p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.7;
}

.overall-scores h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 16px;
}

.score-card {
  background: #F5F7FA;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.score-card.highlight {
  background: linear-gradient(135deg, #00b89415 0%, #00cec915 100%);
}

.score-label {
  display: block;
  font-size: 13px;
  color: #8F959E;
  margin-bottom: 8px;
}

.score-value {
  font-size: 24px;
  font-weight: 600;
  color: #1F2329;
}

.score-card.highlight .score-value {
  color: #00b894;
}

.trade-offs {
  margin-top: 24px;
}

.trade-offs h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 12px;
}

.trade-offs ul {
  margin: 0;
  padding-left: 20px;
}

.trade-offs li {
  font-size: 13px;
  color: #4E5969;
  line-height: 1.7;
  margin-bottom: 8px;
}

.report-panel {
  margin-bottom: 20px;
}

.report-preview {
  margin-top: 20px;
}

.report-preview h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
}

.report-content {
  font-size: 13px;
  color: #4E5969;
  line-height: 1.7;
  margin-bottom: 20px;
}

.report-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.report-metric {
  background: #F5F7FA;
  padding: 16px;
  border-radius: 10px;
  text-align: center;
}

.report-metric .metric-label {
  display: block;
  font-size: 12px;
  color: #8F959E;
  margin-bottom: 6px;
}

.report-metric .metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1F2329;
}

.report-metric .metric-value.success {
  color: #00b894;
}

.solution-preview h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #1F2329;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.preview-item {
  background: #F5F7FA;
  padding: 16px;
  border-radius: 10px;
  text-align: center;
}

.preview-label {
  display: block;
  font-size: 12px;
  color: #8F959E;
  margin-bottom: 8px;
}

.preview-value {
  font-size: 15px;
  font-weight: 600;
  color: #1F2329;
}

.preview-value.highlight {
  color: #00b894;
}

.logs-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.logs-header h3 {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logs-actions {
  display: flex;
  gap: 8px;
}

.logs-container {
  background: #1F2329;
  border-radius: 10px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 6px 0;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.log-time {
  color: #8F959E;
  min-width: 80px;
}

.log-type {
  min-width: 60px;
  font-weight: 600;
}

.log-type.info {
  color: #00b894;
}

.log-type.success {
  color: #00cec9;
}

.log-type.warning {
  color: #f39c12;
}

.log-type.error {
  color: #F53F3F;
}

.log-content {
  flex: 1;
  color: #E4E7ED;
  line-height: 1.5;
}

.generate-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}

.primary-btn {
  background: #00b894 !important;
  border-color: #00b894 !important;
}

.primary-btn:hover {
  background: #00cec9 !important;
  border-color: #00cec9 !important;
}

@media (max-width: 1200px) {
  .preview-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .full-workflow {
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .workflow-node {
    flex: 0 0 30%;
  }
  
  .preview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .report-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
