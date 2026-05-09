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
                  <div class="agent-detail">光伏容量: {{ nodeResults.draftPlan.pvCapacity }} MW</div>
                  <div class="agent-detail">风电容量: {{ nodeResults.draftPlan.windCapacity }} MW</div>
                  <div class="agent-detail">储能容量: {{ nodeResults.draftPlan.storageCapacity }} MWh</div>
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
                  <div class="agent-detail">预测PUE: {{ nodeResults.draftPlan.pue }}</div>
                  <div class="agent-detail">制冷功耗: {{ nodeResults.draftPlan.coolingPower }} kW</div>
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
                  <div class="agent-detail">Tier等级: {{ nodeResults.draftPlan.tierLevel }}</div>
                  <div class="agent-detail">可用性: {{ nodeResults.draftPlan.availability }}%</div>
                  <div class="agent-detail">UPS配置: {{ nodeResults.draftPlan.upsConfig }}</div>
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
          <el-card class="debate-card">
            <div class="debate-timeline">
              <div 
                v-for="(round, index) in debateResults.rounds" 
                :key="index" 
                class="debate-round-item"
                :class="{ active: index === debateResults.currentRound - 1 }"
              >
                <div class="round-header">第{{ round.number }}轮</div>
                <div class="round-statements">
                  <div v-for="(statement, i) in round.statements" :key="i" class="statement-item">
                    <span class="speaker">{{ statement.speaker }}:</span>
                    <span class="content">{{ statement.content }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
          <div v-if="debateResults.summary" class="debate-summary-card">
            <h4>辩论纪要</h4>
            <div v-if="debateResults.summary.consensusIssues.length > 0">
              <h5>共识问题</h5>
              <ul>
                <li v-for="(issue, i) in debateResults.summary.consensusIssues" :key="i">{{ issue }}</li>
              </ul>
            </div>
            <div v-if="debateResults.summary.partialConsensusIssues.length > 0">
              <h5>待协调问题</h5>
              <ul>
                <li v-for="(issue, i) in debateResults.summary.partialConsensusIssues" :key="i">{{ issue }}</li>
              </ul>
            </div>
            <div v-if="debateResults.summary.suggestions.length > 0">
              <h5>改进建议</h5>
              <ul>
                <li v-for="(suggestion, i) in debateResults.summary.suggestions" :key="i">{{ suggestion }}</li>
              </ul>
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
const workflowId = ref(null)
const eventSource = ref(null)
const completedNodes = ref(new Set())

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

const getMainScore = (scores) => {
  if (!scores || typeof scores !== 'object') return 0
  const vals = Object.values(scores).filter(v => typeof v === 'number')
  if (vals.length === 0) return 0
  return vals.reduce((a, b) => a + b, 0) / vals.length
}

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

const nodeIndexMap = {
  'requirement_parser': 0, 'draft_plan_agent': 1, 'cost_calculation': 2,
  'economic_analysis': 3, 'power_reliability_analysis': 4, 'environmental_analysis': 5,
  'debate_start': 6, 'debate_round': 6, 'debate_end': 6,
  'arbitrator': 7, 'final_report': 8, 'output': 9, 'completed': 9
}

let sseReconnectCount = 0
const MAX_SSE_RECONNECTS = 5
let lastDataTime = Date.now()
let safetyTimeoutId = null
let fallbackPollTimer = null
let lastSSEDataTime = Date.now()
let reconnectTimerId = null
let terminalWatchdogTimer = null
let finalReportFinalizeTimer = null
let solutionProbeFailCount = 0

const resetSafetyTimeout = () => {
  if (safetyTimeoutId) clearTimeout(safetyTimeoutId)
  lastDataTime = Date.now()
  safetyTimeoutId = setTimeout(() => {
    if (!isCompleted.value && !isFailed.value) {
      addLog('警告：长时间未收到数据（120秒），可能工作流已卡住', 'warning')
    }
  }, 120000)
}

const clearRuntimeTimers = () => {
  if (safetyTimeoutId) {
    clearTimeout(safetyTimeoutId)
    safetyTimeoutId = null
  }
  if (fallbackPollTimer) {
    clearInterval(fallbackPollTimer)
    fallbackPollTimer = null
  }
  if (reconnectTimerId) {
    clearTimeout(reconnectTimerId)
    reconnectTimerId = null
  }
  if (terminalWatchdogTimer) {
    clearInterval(terminalWatchdogTimer)
    terminalWatchdogTimer = null
  }
  if (finalReportFinalizeTimer) {
    clearTimeout(finalReportFinalizeTimer)
    finalReportFinalizeTimer = null
  }
}

const closeEventStream = () => {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
}

const applySolutionToPreview = (solution) => {
  const metrics = solution?.key_metrics || {}
  finalSolution.name = solution?.name || ''
  finalSolution.overallScore = toNumber(solution?.overall_scores?.overall)
  finalSolution.pue = toNumber(metrics.pue)
  finalSolution.greenPowerRatio = toNumber(metrics.green_power_ratio)
  finalSolution.totalCost = toNumber(metrics.total_cost)
  finalSolution.tierLevel = toNumber(metrics.tier_level)
  finalSolution.expectedAvailability = toNumber(metrics.expected_availability)
  finalSolution.annualCarbonEmission = toNumber(metrics.annual_carbon_emission)
  finalSolution.roi = toNumber(metrics.roi)
  finalSolution.paybackPeriod = toNumber(metrics.payback_period)
}

const checkAndFinalizeByBackendState = async (reason = 'backend-check') => {
  if (isCompleted.value || isFailed.value) return
  const wid = workflowId.value
  if (!wid) return

  try {
    const { data: status } = await workflowApi.getStatus(wid)
    console.log('[BACKEND CHECK]', reason, 'status=', status?.status)
    if (status?.status === 'completed') {
      await finalizeWorkflow({ source: `${reason}-status`, resultPayload: status || {} })
      return
    }
    if (status?.status === 'failed') {
      isFailed.value = true
      addLog(`❌ 后端状态为失败: ${status.error || '未知错误'}`, 'error')
      clearRuntimeTimers()
      closeEventStream()
      return
    }
  } catch (e) {
    addLog(`状态校验失败(${reason})，将继续尝试方案校验`, 'warning')
    // 状态接口失败时继续尝试方案接口，不中断流程
  }

  // 兜底：若 status 未及时切换，但方案已可读取，则视为后端已完成。
  // 仅在流程末段探测方案接口，避免早期 404 噪音。
  if (currentNodeIndex.value < 8) return

  try {
    const { data: solutionData } = await solutionApi.getById(wid)
    if (solutionData && (solutionData.success !== false)) {
      await finalizeWorkflow({
        source: `${reason}-solution-probe`,
        resultPayload: { solution: solutionData.solution || solutionData }
      })
      return
    }
  } catch (e) {
    const statusCode = e?.response?.status
    solutionProbeFailCount += 1
    // 404 代表后端尚未写入 solutions_store，属于预期重试场景，降低日志噪音。
    if (statusCode !== 404 && solutionProbeFailCount % 3 === 0) {
      addLog(`方案校验失败(${reason})，等待下一次重试`, 'warning')
    }
  }
}

const startTerminalWatchdog = () => {
  if (terminalWatchdogTimer || isCompleted.value || isFailed.value) return

  let retries = 0
  const maxRetries = 30 // 约 60 秒
  solutionProbeFailCount = 0
  addLog('进入终态校验阶段，启动完成态看门狗', 'info')

  terminalWatchdogTimer = setInterval(async () => {
    if (isCompleted.value || isFailed.value) {
      clearInterval(terminalWatchdogTimer)
      terminalWatchdogTimer = null
      return
    }

    retries += 1
    await checkAndFinalizeByBackendState(`terminal-watchdog-${retries}`)

    if (isCompleted.value || isFailed.value || retries >= maxRetries) {
      clearInterval(terminalWatchdogTimer)
      terminalWatchdogTimer = null
      if (!isCompleted.value && !isFailed.value) {
        // 最终兜底：final_report 已到达且后端没有失败信号时，按终态收口，避免永久卡 90%。
        addLog('终态看门狗超时，触发最终收口兜底', 'warning')
        finalizeWorkflow({ source: 'terminal-watchdog-timeout-fallback', resultPayload: {} })
      }
    }
  }, 2000)
}

const finalizeWorkflow = async ({ source, resultPayload } = {}) => {
  if (isCompleted.value) return

  const wid = workflowId.value
  isCompleted.value = true
  isFailed.value = false
  progressPercent.value = 100
  currentNodeIndex.value = 9
  completedNodes.value.add(9)

  if (wid) {
    localStorage.setItem('currentSolutionId', wid)
  }

  // 优先使用当前事件携带的数据；不足时再从后端详情接口补齐。
  const directSolution = resultPayload?.solution || resultPayload?.final_solution || null
  if (directSolution && typeof directSolution === 'object') {
    applySolutionToPreview(directSolution)
  }

  try {
    if (wid) {
      const { data } = await solutionApi.getById(wid)
      const solution = data?.solution || data || {}
      applySolutionToPreview(solution)
    }
  } catch (e) {
    addLog('已进入完成态，但详情数据补齐失败，可直接进入详情页查看', 'warning')
  }

  addLog(`✅ 工作流执行完成（来源: ${source || 'unknown'}）`, 'success')
  clearRuntimeTimers()
  closeEventStream()
}

const handleSSENode = (nodeName, data) => {
  console.log('[SSE] handleSSENode called with node:', nodeName)
  const idx = nodeIndexMap[nodeName]
  if (idx !== undefined) {
    currentNodeIndex.value = idx
    completedNodes.value.add(idx)
    if (idx > 0) completedNodes.value.add(idx - 1)
    resetSafetyTimeout()
  }
  const totalSteps = 10
  progressPercent.value = Math.min(Math.round((completedNodes.value.size / totalSteps) * 100), 100)

  try {
    if (nodeName === 'requirement_parser') {
      const d = data || {}
      const req = d.requirement || d
      console.log('[SSE] requirement_parser raw data keys:', Object.keys(d), 'req keys:', Object.keys(req), 'location:', req.location, 'load:', req.planned_load_kw)
      nodeResults.requirementParser = {
        summary: `${req.location || '未知地点'}需求参数已结构化解析`,
        location: req.location || '',
        load: req.planned_load_kw ?? null,
        greenRatio: toNumber(req.green_power_ratio) !== null ? toNumber(req.green_power_ratio) * 100 : null
      }
      addLog(`需求解析完成: ${req.location}, 负荷${req.planned_load_kw}kW`, 'success')
    }

    if (nodeName === 'draft_plan_agent') {
      const fullOutput = data || {}
      console.log('[SSE] draft_plan_agent raw keys:', Object.keys(fullOutput), 'has parsed:', !!fullOutput.parsed)
      const parsed = fullOutput.parsed || fullOutput
      const gpResult = parsed.green_power_result || fullOutput.green_power_result || {}
      const cooling = parsed.cooling_result || fullOutput.cooling_result || {}
      const power = parsed.power_supply_plan || fullOutput.power_supply_plan || {}
      const gp = gpResult.optimization || gpResult
      const powerRaw = power.raw_json || power
      nodeResults.draftPlan = {
        pvCapacity: toNumber(gp.pv_capacity_mw),
        windCapacity: toNumber(gp.wind_capacity_mw),
        storageCapacity: toNumber(gp.storage_capacity_mwh),
        coolingTech: cooling.cooling_technology || '--',
        pue: toNumber(cooling.estimated_pue || cooling.cooling_kpis?.predicted_PUE),
        coolingPower: toNumber(cooling.cooling_power_consumption || cooling.cooling_kpis?.cooling_power_kw),
        tierLevel: powerRaw.machine_room_grade || power.scheme_name || '--',
        availability: toNumber(powerRaw.expected_availability),
        upsConfig: power.redundancy_logic || power.diesel_status || '--'
      }
      addLog(`初稿方案: 光伏${gp.pv_capacity_mw || '--'}MW, 风电${gp.wind_capacity_mw || '--'}MW`, 'success')
    }

    if (nodeName === 'cost_calculation') {
      const d = data || {}
      const analysis = d.economic_analysis_result || d
      const breakdown = analysis.capex_breakdown || {}
      console.log('[SSE] cost_calculation raw keys:', Object.keys(d), 'analysis keys:', Object.keys(analysis), 'totalCost:', analysis.total_capex_lakh)
      nodeResults.costCalculation = {
        powerSupplyCost: toNumber(breakdown.power_supply_system_lakh),
        greenPowerCost: toNumber(breakdown.green_power_system_lakh),
        totalCost: toNumber(analysis.total_capex_lakh),
        budget: toNumber(analysis.budget_constraint_lakh),
        isOverBudget: Boolean(analysis.is_over_budget),
        budgetDelta: toNumber(analysis.budget_delta_lakh)
      }
      addLog(`成本计算: 总投资${analysis.total_capex_lakh || '--'}万元`, analysis.is_over_budget ? 'warning' : 'success')
    }

    if (nodeName === 'economic_analysis') {
      const d = data || {}
      const opinion = d.economic_opinion || d
      const confVal = toNumber(opinion.confidence)
      console.log('[SSE] economic_analysis confidence:', confVal, 'keys:', Object.keys(opinion))
      expertResults[0] = { ...expertResults[0], status: '已完成', score: confVal, summary: opinion.summary || '', recommendations: opinion.recommendations || [], concerns: opinion.concerns || [], metrics: opinion.metrics || {} }
      addLog(`经济性专家评审完成: 置信度${confVal}`, 'success')
    }

    if (nodeName === 'power_reliability_analysis') {
      const d = data || {}
      const opinion = d.power_reliability_opinion || d
      const confVal = toNumber(opinion.confidence)
      console.log('[SSE] reliability_analysis confidence:', confVal)
      expertResults[1] = { ...expertResults[1], status: '已完成', score: confVal, summary: opinion.summary || '', recommendations: opinion.recommendations || [], concerns: opinion.concerns || [], metrics: opinion.metrics || {} }
      addLog(`可靠性专家评审完成: 置信度${confVal}`, 'success')
    }

    if (nodeName === 'environmental_analysis') {
      const d = data || {}
      const opinion = d.environmental_opinion || d
      const confVal = toNumber(opinion.confidence)
      console.log('[SSE] environmental_analysis confidence:', confVal)
      expertResults[2] = { ...expertResults[2], status: '已完成', score: confVal, summary: opinion.summary || '', recommendations: opinion.recommendations || [], concerns: opinion.concerns || [], metrics: opinion.metrics || {} }
      addLog(`环保性专家评审完成: 置信度${confVal}`, 'success')
    }

    if (nodeName === 'debate_round' || nodeName === 'debate_start' || nodeName === 'debate_end') {
      const d = data || {}
      const round = toNumber(d.round, 1)
      if (d.speaker && d.content) {
        const signature = `${round}-${d.speaker}-${d.content.substring(0, 50)}`
        if (!debateSignatures.has(signature)) {
          debateSignatures.add(signature)
          if (!debateResults.value) {
            debateResults.value = { currentRound: round, consensusScore: 0, rounds: [], summary: { consensusIssues: [], partialConsensusIssues: [], suggestions: [] } }
          }
          let roundEntry = debateResults.value.rounds.find(r => r.number === round)
          if (!roundEntry) {
            roundEntry = { number: round, statements: [] }
            debateResults.value.rounds.push(roundEntry)
            debateResults.value.rounds.sort((a, b) => a.number - b.number)
          }
          roundEntry.statements.push({ speaker: d.speaker, content: d.content })
          debateResults.value.currentRound = round
        }
      }
      if (d.consensus_score !== undefined && debateResults.value) {
        debateResults.value.consensusScore = toNumber(d.consensus_score, 0)
      }
      addLog(`辩论第${round}轮: ${d.speaker || '专家'}`, 'info')
    }

    if (nodeName === 'arbitrator') {
      const d = data || {}
      const sol = d.solution || d
      const scores = sol.overall_scores || {}
      console.log('[SSE] arbitrator overall score:', scores.overall, 'solution keys:', Object.keys(sol))
      arbitratorResult.summary = sol.summary || ''
      arbitratorResult.confidence = toNumber(sol.confidence, 0)
      arbitratorResult.scores = { economic: toNumber(scores.economic, 0), reliability: toNumber(scores.reliability, 0), environmental: toNumber(scores.environmental, 0) }
      arbitratorResult.consensusScore = toNumber(scores.overall, 0)
      arbitratorResult.tradeOffs = sol.trade_offs || []
      if (debateResults.value) {
        debateResults.value.consensusScore = arbitratorResult.consensusScore
        debateResults.value.summary.suggestions = sol.recommendations || []
      }
      addLog(`仲裁决策完成: 综合评分${scores.overall ? (scores.overall * 100).toFixed(0) + '%' : '--'}`, 'success')
    }

    if (nodeName === 'final_report') {
      const d = data || {}
      const sol = d.solution || d
      console.log('[SSE] final_report path:', sol.final_report_path || sol.path || d.path)
      finalReport.value = {
        summary: arbitratorResult.summary || '报告已生成',
        path: sol.final_report_path || sol.path || d.path || '',
        wordCount: (sol.final_report || '').length || (d.final_report || '').length
      }
      addLog('最终报告生成完成', 'success')
      // 后端若已完成但末尾 SSE 丢失，主动校验后端状态并收敛。
      checkAndFinalizeByBackendState('after-final-report')
      startTerminalWatchdog()
      if (finalReportFinalizeTimer) clearTimeout(finalReportFinalizeTimer)
      finalReportFinalizeTimer = setTimeout(() => {
        if (!isCompleted.value && !isFailed.value) {
          addLog('final_report 后未收到终态信号，执行延时收口', 'warning')
          finalizeWorkflow({ source: 'final-report-delay-fallback', resultPayload: {} })
        }
      }, 8000)
    }

    if (nodeName === 'output') {
      console.log('[SSE] output node received, data keys:', Object.keys(data || {}))
      const d = data || {}
      const sol = d.final_solution || d.solution || {}
      if (sol.name) finalSolution.name = sol.name
      completedNodes.value.add(9)
      currentNodeIndex.value = 9
      progressPercent.value = 100
      addLog('输出节点完成', 'success')
    }
  } catch (e) {
    console.error(`[SSE] Error processing ${nodeName}:`, e, 'data:', JSON.stringify(data).substring(0, 200))
    addLog(`${nodeName}数据处理异常: ${e.message}`, 'error')
  }
}

const debateSignatures = new Set()

const connectSSE = () => {
  const wid = workflowId.value
  if (!wid) { addLog('未找到工作流ID', 'error'); isFailed.value = true; return }
  addLog(`连接实时流: ${wid} (重连次数: ${sseReconnectCount})`, 'info')
  resetSafetyTimeout()
  const es = workflowApi.connectStream(wid)

  es.onmessage = (event) => {
    try {
      console.log('[SSE RAW] event.data received:', event.data.substring(0, 200))
      const item = JSON.parse(event.data)
      const nodeName = item.node
      const nodeData = item.data

      console.log('[SSE PARSED] nodeName:', nodeName)

      if (nodeName === 'heartbeat') {
        console.log('[SSE] heartbeat received')
        return
      }

      if (nodeName === 'completed') {
        console.log('[SSE] ===== COMPLETED EVENT RECEIVED =====')
        finalizeWorkflow({ source: 'sse-completed', resultPayload: nodeData || {} })
        return
      }

      if (nodeName === 'error') {
        addLog(`工作流执行失败: ${nodeData?.error || '未知错误'}`, 'error')
        isFailed.value = true
        if (safetyTimeoutId) clearTimeout(safetyTimeoutId)
        es.close()
        eventSource.value = null
        return
      }

      handleSSENode(nodeName, nodeData)
      if (nodeName === 'output') {
        // output 代表后端流程已到最终收口，若 completed 事件丢失，前端仍需收敛。
        finalizeWorkflow({ source: 'sse-output', resultPayload: nodeData || {} })
        return
      }
      if (nodeName !== 'heartbeat') {
        lastSSEDataTime = Date.now()
      }
    } catch (error) {
      console.error('SSE parse error:', error, 'event.data:', event.data)
      addLog('检测到 SSE 消息解析异常，启动后端状态校验兜底', 'warning')
      checkAndFinalizeByBackendState('sse-parse-error')
    }
  }

  es.onerror = () => {
    if (!isCompleted.value && !isFailed.value) {
      sseReconnectCount++
      checkAndFinalizeByBackendState('sse-onerror')
      closeEventStream()
      if (sseReconnectCount > MAX_SSE_RECONNECTS) {
        addLog(`SSE重连次数超过${MAX_SSE_RECONNECTS}次，停止重连`, 'error')
        isFailed.value = true
        clearRuntimeTimers()
        return
      }
      addLog(`SSE连接断开，3秒后重连... (${sseReconnectCount}/${MAX_SSE_RECONNECTS})`, 'warning')
      reconnectTimerId = setTimeout(() => {
        if (!isCompleted.value && !isFailed.value && workflowId.value) connectSSE()
      }, 3000)
    }
  }
  eventSource.value = es

  startFallbackPolling()
}

const startFallbackPolling = () => {
  if (fallbackPollTimer) return
  lastSSEDataTime = Date.now()
  console.log('[FALLBACK] Starting fallback polling...')
  
  fallbackPollTimer = setInterval(async () => {
    if (isCompleted.value || isFailed.value || !workflowId.value) {
      clearInterval(fallbackPollTimer)
      fallbackPollTimer = null
      return
    }
    
    checkAndFinalizeByBackendState('fallback-poll')
  }, 5000) // 每5秒检查一次
}

const startWorkflow = async () => {
  const wid = localStorage.getItem('currentWorkflowId')
  if (wid) {
    sseReconnectCount = 0
    workflowId.value = wid
    addLog(`使用工作流ID: ${wid}`, 'info')
    connectSSE()
  } else {
    addLog('未找到工作流ID，请先在配置页提交参数', 'error')
    isFailed.value = true
  }
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
  clearRuntimeTimers()
  closeEventStream()
  router.push('/config')
}

const regenerate = () => {
  progressPercent.value = 0; currentNodeIndex.value = -1; isCompleted.value = false; isFailed.value = false
  logs.value = []; completedNodes.value = new Set(); debateSignatures.clear()
  nodeResults.requirementParser = null; nodeResults.draftPlan = null; nodeResults.costCalculation = null
  expertResults.forEach(e => { e.status = '等待中'; e.score = 0; e.summary = ''; e.recommendations = []; e.concerns = []; e.metrics = {} })
  debateResults.value = null
  arbitratorResult.summary = ''; arbitratorResult.confidence = 0; arbitratorResult.scores = { economic: 0, reliability: 0, environmental: 0 }; arbitratorResult.tradeOffs = []; arbitratorResult.consensusScore = 0
  finalReport.value = null
  Object.assign(finalSolution, { name: '', overallScore: 0, pue: 0, greenPowerRatio: 0, totalCost: 0, tierLevel: 0, expectedAvailability: 0, annualCarbonEmission: 0, roi: 0, paybackPeriod: 0 })
  localStorage.removeItem('currentWorkflowId')
  router.push('/config')
}

const viewError = () => { ElMessage.error('请查看下方实时日志中的错误信息') }

const goToDetail = () => {
  const solutionId = localStorage.getItem('currentSolutionId') || workflowId.value
  if (!solutionId) {
    ElMessage.error('未找到可用方案ID，请稍后重试')
    return
  }
  router.push(`/detail/${solutionId}`)
}

onMounted(() => {
  addLog('系统启动，开始连接后端工作流...', 'info')
  startWorkflow()
})

onUnmounted(() => {
  clearRuntimeTimers()
  closeEventStream()
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
  color: #165DFF;
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
  background: #165DFF;
  color: white;
}

.workflow-node.completed .node-icon {
  background: #00B42A;
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
  border-color: #165DFF;
  box-shadow: 0 4px 20px rgba(22, 93, 255, 0.1);
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
  color: #165DFF;
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

.metric-item {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 12px;
  color: #8F959E;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #165DFF;
}

.agent-result-card {
  height: 180px;
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.agent-icon {
  font-size: 20px;
  color: #165DFF;
}

.agent-name {
  font-size: 14px;
  font-weight: 600;
}

.agent-content {
  padding-left: 30px;
}

.agent-detail {
  font-size: 13px;
  color: #4E5969;
  margin-bottom: 6px;
}

.cost-card {
  background: #F5F7FA;
}

.cost-summary {
  padding: 20px;
  border-bottom: 1px solid #E4E7ED;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
}

.cost-row.total .cost-value {
  font-size: 24px;
  font-weight: 700;
  color: #165DFF;
}

.cost-label {
  font-size: 14px;
  color: #8F959E;
}

.cost-value {
  font-size: 16px;
  font-weight: 600;
  color: #1F2329;
}

.cost-value.over-budget {
  color: #F53F3F;
}

.cost-value.under-budget {
  color: #00B42A;
}

.budget-warning, .budget-success {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-top: 16px;
  border-radius: 8px;
}

.budget-warning {
  background: #FFF7E6;
  color: #D46B08;
}

.budget-success {
  background: #E8F8E8;
  color: #00B42A;
}

.expert-card {
  height: 220px;
  border-color: #E4E7ED;
}

.expert-card.waiting { border-color: #E4E7ED; }
.expert-card.running { border-color: #FF7D00; }
.expert-card.completed { border-color: #00B42A; }

.expert-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.expert-icon {
  font-size: 20px;
  color: #165DFF;
}

.expert-name {
  font-size: 14px;
  font-weight: 600;
}

.expert-status {
  margin-bottom: 10px;
}

.expert-score {
  margin-bottom: 10px;
}

.score-label {
  font-size: 12px;
  color: #8F959E;
  display: block;
}

.score-value {
  font-size: 20px;
  font-weight: 600;
  color: #165DFF;
}

.expert-summary {
  font-size: 13px;
  color: #646A76;
  line-height: 1.5;
  margin-bottom: 10px;
}

.expert-recommendations {
  padding-top: 10px;
  border-top: 1px solid #E4E7ED;
}

.recommendation-label {
  font-size: 12px;
  color: #8F959E;
  margin-bottom: 6px;
  display: block;
}

.expert-recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.expert-recommendations li {
  font-size: 12px;
  color: #4E5969;
  margin-bottom: 4px;
}

.debate-panel {
  margin-top: 10px;
}

.debate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.debate-round {
  font-size: 14px;
  font-weight: 600;
  color: #165DFF;
}

.consensus-score {
  font-size: 14px;
  color: #00B42A;
  font-weight: 500;
}

.debate-card {
  margin-bottom: 16px;
}

.debate-timeline {
  max-height: 200px;
  overflow-y: auto;
}

.debate-round-item {
  padding: 12px;
  margin-bottom: 12px;
  background: #F5F7FA;
  border-radius: 8px;
}

.debate-round-item.active {
  background: #E8F0FE;
}

.round-header {
  font-size: 13px;
  font-weight: 600;
  color: #165DFF;
  margin-bottom: 10px;
}

.statement-item {
  margin-bottom: 8px;
}

.speaker {
  font-weight: 600;
  color: #1F2329;
}

.content {
  color: #4E5969;
  font-size: 13px;
}

.debate-summary-card {
  background: #F5F7FA;
  padding: 16px;
  border-radius: 8px;
}

.debate-summary-card h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.debate-summary-card h5 {
  font-size: 13px;
  font-weight: 500;
  color: #165DFF;
  margin-bottom: 8px;
}

.debate-summary-card ul {
  margin: 0;
  padding-left: 20px;
}

.debate-summary-card li {
  font-size: 13px;
  color: #4E5969;
  margin-bottom: 6px;
}

.arbitrator-panel {
  margin-top: 10px;
}

.arbitrator-card {
  background: #F5F7FA;
}

.arbitrator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.arbitrator-title {
  font-size: 16px;
  font-weight: 600;
}

.confidence-badge {
  background: #00B42A;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.consensus-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  margin-bottom: 16px;
}

.consensus-indicator .label {
  font-size: 14px;
  color: #8F959E;
}

.consensus-indicator .value {
  font-size: 24px;
  font-weight: 700;
}

.consensus-indicator .value.high {
  color: #00B42A;
}

.consensus-indicator .value.medium {
  color: #FF7D00;
}

.decision-summary p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.7;
}

.overall-scores {
  margin-top: 20px;
}

.overall-scores h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.score-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.score-card.highlight {
  background: #E8F8E8;
}

.score-card .score-label {
  font-size: 12px;
  color: #8F959E;
  display: block;
  margin-bottom: 6px;
}

.score-card .score-value {
  font-size: 20px;
  font-weight: 600;
  color: #165DFF;
}

.trade-offs {
  margin-top: 20px;
}

.trade-offs h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.trade-offs ul {
  margin: 0;
  padding-left: 20px;
}

.trade-offs li {
  font-size: 13px;
  color: #4E5969;
  margin-bottom: 8px;
}

.report-panel {
  margin-top: 10px;
}

.report-preview {
  margin-top: 16px;
}

.report-preview h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.report-content {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.7;
}

.report-metrics {
  display: flex;
  gap: 30px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #E4E7ED;
}

.report-metric {
  display: flex;
  flex-direction: column;
}

.report-metric .metric-label {
  font-size: 12px;
  color: #8F959E;
}

.report-metric .metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1F2329;
}

.report-metric .metric-value.success {
  color: #00B42A;
}

.solution-preview {
  margin-top: 20px;
}

.solution-preview h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.preview-item {
  background: #F5F7FA;
  padding: 16px;
  border-radius: 8px;
}

.preview-label {
  display: block;
  font-size: 12px;
  color: #8F959E;
  margin-bottom: 8px;
}

.preview-value {
  font-size: 18px;
  font-weight: 600;
  color: #1F2329;
}

.preview-value.highlight {
  color: #165DFF;
}

.logs-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.logs-container {
  flex: 1;
  overflow-y: auto;
  background: #F5F7FA;
  border-radius: 8px;
  padding: 12px;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 6px 0;
  font-size: 13px;
}

.log-item.info .log-type { color: #165DFF; }
.log-item.warning .log-type { color: #FF7D00; }
.log-item.success .log-type { color: #00B42A; }
.log-item.error .log-type { color: #F53F3F; }

.log-time {
  color: #8F959E;
  width: 70px;
}

.log-type {
  font-weight: 600;
  width: 60px;
}

.log-content {
  flex: 1;
  color: #1F2329;
}

.generate-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #E4E7ED;
}

.primary-btn {
  background: #FF7D00;
  border: none;
  color: white;
}

.primary-btn:hover {
  background: #E67E22;
  color: white;
}
</style>
