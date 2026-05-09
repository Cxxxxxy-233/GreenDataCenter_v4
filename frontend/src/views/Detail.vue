<template>
  <div class="detail-page">
    <div class="detail-header">
      <h1>方案详情</h1>
      <div class="header-actions">
        <el-button @click="exportMarkdown">导出Markdown报告</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="detail-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="方案概览" name="overview">
        <div class="overview-section">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">推荐制冷技术</div>
              <div class="metric-value">{{ coolingResult.cooling_technology || '-' }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">预测PUE</div>
              <div class="metric-value highlight">{{ formatNumber(coolingResult.estimated_pue, 3) }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">预测WUE</div>
              <div class="metric-value">{{ formatNumber(coolingResult.predicted_wue, 3) }} <span class="unit">L/kWh</span></div>
            </div>
            <div class="metric-card">
              <div class="metric-label">绿电消纳率</div>
              <div class="metric-value highlight">{{ formatPercent(keyMetrics.green_power_ratio) }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">总初始投资</div>
              <div class="metric-value">{{ formatNumber(costResult.total_capex_lakh || keyMetrics.total_cost, 2) }} <span class="unit">万元</span></div>
            </div>
            <div class="metric-card">
              <div class="metric-label">综合评分</div>
              <div class="metric-value">{{ formatPercent(overallScores.overall) }}</div>
            </div>
          </div>

          <div class="summary-section">
            <h3>方案摘要</h3>
            <p class="summary-text">{{ arbitrator.summary || '暂无后端仲裁摘要' }}</p>
            <div class="budget-status" :class="costResult.is_over_budget ? 'fail' : 'success'">
              <el-icon><CircleCheckFilled /></el-icon>
              <span v-if="costResult.is_over_budget">当前方案超预算 {{ formatNumber(costResult.budget_delta_lakh, 2) }} 万元</span>
              <span v-else>预算校验通过，预算差额 {{ formatNumber(costResult.budget_delta_lakh, 2) }} 万元</span>
            </div>
            <div class="risk-warning" v-if="arbitrator.risks && arbitrator.risks.length">
              <el-icon><CircleCloseFilled /></el-icon>
              <span>{{ formatRisk(arbitrator.risks[0]) }}</span>
            </div>
          </div>

          <div class="info-section">
            <h3>生成信息</h3>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="info-item">方案ID</div>
                <div class="info-value">{{ solutionData.id || '-' }}</div>
              </el-col>
              <el-col :span="6">
                <div class="info-item">生成时间</div>
                <div class="info-value">{{ solutionData.created_at || '-' }}</div>
              </el-col>
              <el-col :span="6">
                <div class="info-item">置信度</div>
                <div class="info-value">{{ formatPercent(solutionData.confidence) }}</div>
              </el-col>
              <el-col :span="6">
                <div class="info-item">报告路径</div>
                <div class="info-value">{{ finalReportPath || '-' }}</div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="制冷系统详情" name="cooling">
        <div class="cooling-section">
          <div class="param-cards">
            <el-card class="param-card">
              <h4>制冷方案核心参数</h4>
              <div class="param-grid">
                <div class="param-item">推荐技术：{{ coolingResult.cooling_technology || '-' }}</div>
                <div class="param-item">制冷负荷：{{ formatNumber(coolingKpis.cooling_load_kw, 2) }} kW</div>
                <div class="param-item">制冷功耗：{{ formatNumber(coolingKpis.cooling_power_kw || coolingResult.cooling_power_consumption, 2) }} kW</div>
                <div class="param-item">修正后COP：{{ formatNumber(coolingKpis.corrected_cop, 2) }}</div>
                <div class="param-item">余热回收量：{{ formatNumber(coolingKpis.waste_heat_recovery_kw, 2) }} kW</div>
              </div>
            </el-card>
            <el-card class="param-card">
              <h4>经济指标</h4>
              <div class="param-grid">
                <div class="param-item">初始投资：{{ formatNumber(coolingEconomics.initial_investment, 2) }} 万元</div>
                <div class="param-item">年运维成本：{{ formatNumber(coolingEconomics.annual_opex, 2) }} 万元</div>
                <div class="param-item">年电费：{{ formatNumber(coolingEconomics.annual_electricity_cost, 2) }} 万元</div>
                <div class="param-item">LCOE：{{ formatNumber(coolingEconomics.lcoe, 4) }} 元/kWh</div>
              </div>
            </el-card>
          </div>

          <el-card class="table-card">
            <h4>寻优结果</h4>
            <el-table :data="coolingTableData" border>
              <el-table-column prop="name" label="指标" />
              <el-table-column prop="value" label="数值" />
            </el-table>
          </el-card>

          <el-card class="chart-card">
            <h4>寻优轨迹图</h4>
            <div ref="optimizationChartRef" class="chart-container"></div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="绿电系统详情" name="green">
        <div class="green-section">
          <el-card>
            <h4>风光储容量配置表</h4>
            <el-table :data="greenConfig" border>
              <el-table-column prop="type" label="类型" />
              <el-table-column prop="capacity" label="容量" />
              <el-table-column prop="ratio" label="占比(%)" />
            </el-table>
          </el-card>
          <el-card>
            <h4>容量占比图</h4>
            <div ref="powerBalanceChartRef" class="chart-container"></div>
          </el-card>
          <el-card>
            <h4>后端产物文件</h4>
            <div class="param-grid">
              <div class="param-item">光伏曲线文件：{{ greenFiles.pv_csv || '-' }}</div>
              <div class="param-item">风电曲线文件：{{ greenFiles.wind_csv || '-' }}</div>
              <div class="param-item">平衡图文件：{{ greenFiles.balance_plot || '-' }}</div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="供电系统详情" name="power">
        <div class="power-section">
          <el-card>
            <h4>主备供电架构</h4>
            <div class="architecture-diagram">
              <div class="arch-item">{{ powerPlan.external_source_type || '外部电源' }}</div>
              <div class="arch-arrow">→</div>
              <div class="arch-item">{{ powerPlan.redundancy_logic || '冗余策略' }}</div>
              <div class="arch-arrow">→</div>
              <div class="arch-item">{{ powerPlan.bus_type || '母线' }}</div>
              <div class="arch-arrow">→</div>
              <div class="arch-item">{{ powerPlan.secondary_voltage || '负载侧' }}</div>
            </div>
          </el-card>
          <el-card>
            <h4>系统参数</h4>
            <div class="availability-stats">
              <div class="stat-item">外部电压：{{ powerPlan.external_voltage || '-' }}</div>
              <div class="stat-item">机房等级：{{ powerRaw.machine_room_grade || '-' }}</div>
              <div class="stat-item">单位成本：{{ formatNumber(powerRaw.cost_per_mw, 2) }} 万元/MW</div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="经济分析" name="economic">
        <div class="economic-section">
          <el-card>
            <h4>全局成本结构图</h4>
            <div ref="costChartRef" class="chart-container"></div>
          </el-card>
          <el-card>
            <h4>全生命周期成本分解</h4>
            <el-table :data="costBreakdown" border>
              <el-table-column prop="item" label="项目" />
              <el-table-column prop="amount" label="金额(万元)" />
              <el-table-column prop="ratio" label="占比(%)" />
            </el-table>
          </el-card>
          <el-card>
            <h4>经济专家指标</h4>
            <div class="param-grid">
              <div v-for="(value, key) in economicOpinion.metrics || {}" :key="key" class="param-item">
                {{ key }}：{{ value }}
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="可靠性分析" name="reliability">
        <div class="reliability-section">
          <el-card>
            <h4>系统可用性指标</h4>
            <div class="reliability-stats">
              <div class="stat-card">可用性：{{ reliabilityOpinion.metrics?.expected_availability || keyMetrics.expected_availability || '-' }}</div>
              <div class="stat-card">Tier等级：{{ keyMetrics.tier_level || powerRaw.machine_room_grade || '-' }}</div>
              <div class="stat-card">可靠性评分：{{ formatPercent(overallScores.reliability) }}</div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="环保分析" name="environment">
        <div class="environment-section">
          <el-card>
            <h4>碳排放计算</h4>
            <div class="carbon-stats">
              <div class="stat-card">年度碳排放：{{ keyMetrics.annual_carbon_emission || environmentalOpinion.metrics?.annual_carbon_emission || '-' }}</div>
              <div class="stat-card">绿电比例：{{ formatPercent(keyMetrics.green_power_ratio || environmentalOpinion.metrics?.green_power_ratio) }}</div>
              <div class="stat-card">环保评分：{{ formatPercent(overallScores.environmental) }}</div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="专家评审记录" name="experts">
        <div class="experts-section">
          <el-card>
            <h4>专家意见汇总</h4>
            <div class="expert-opinions">
              <div v-for="(expert, index) in expertOpinions" :key="index" class="expert-opinion-card">
                <div class="expert-header">
                  <div class="expert-avatar" :style="{ background: getExpertColor(expert.type) }">
                    {{ expert.name.charAt(0) }}
                  </div>
                  <div class="expert-info">
                    <div class="expert-name">{{ expert.name }}</div>
                    <div class="expert-type">{{ expert.type }}</div>
                  </div>
                  <el-tag type="success">后端输出</el-tag>
                </div>
                <div class="expert-summary">{{ expert.summary || '-' }}</div>
                <div class="expert-metrics">
                  <span v-for="(value, key) in expert.metrics" :key="key">
                    {{ key }}: {{ value }}
                  </span>
                </div>
                <div class="expert-recommendations" v-if="expert.recommendations && expert.recommendations.length">
                  <h5>建议</h5>
                  <ul>
                    <li v-for="(rec, i) in expert.recommendations" :key="i">{{ rec }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </el-card>
          <el-card>
            <h4>辩论记录</h4>
            <div class="debate-history">
              <div v-for="(round, index) in debateHistory" :key="index" class="debate-round">
                <div class="round-title">第{{ round.round }}轮辩论</div>
                <div v-for="(message, i) in round.messages" :key="i" class="debate-message">
                  <span class="speaker">{{ message.speaker }}:</span>
                  <span class="content">{{ message.content }}</span>
                </div>
              </div>
              <div v-if="!debateHistory.length" class="report-loading">暂无辩论明细（后端当前仅返回最新辩论节点）</div>
            </div>
          </el-card>
          <el-card>
            <h4>仲裁决策</h4>
            <div class="arbitration-result">
              <div class="consensus-score">综合评分：{{ formatPercent(overallScores.overall) }}</div>
              <div class="arbitration-summary">{{ arbitrator.summary || '-' }}</div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="完整方案报告" name="report">
        <div class="report-section">
          <div class="report-header">
            <h3>完整方案报告</h3>
            <el-input v-model="searchKeyword" placeholder="搜索报告内容" />
          </div>
          <div class="report-content">
            <div class="report-title-section">
              <h1 class="report-title">{{ solutionData.name || '数据中心绿电消纳方案报告' }}</h1>
              <div class="report-meta">
                <span>方案编号：{{ solutionId }}</span>
                <span>生成时间：{{ solutionData.created_at || '-' }}</span>
                <span>置信度：{{ formatPercent(solutionData.confidence) }}</span>
              </div>
            </div>
            <div class="report-executive-summary">
              <h2>执行摘要</h2>
              <div class="executive-grid">
                <div class="executive-item">
                  <div class="executive-label">推荐制冷方案</div>
                  <div class="executive-value">{{ coolingResult.cooling_technology || '-' }}</div>
                </div>
                <div class="executive-item">
                  <div class="executive-label">预测PUE</div>
                  <div class="executive-value highlight">{{ formatNumber(keyMetrics.pue || coolingResult.estimated_pue, 3) }}</div>
                </div>
                <div class="executive-item">
                  <div class="executive-label">绿电消纳率</div>
                  <div class="executive-value highlight">{{ formatPercent(keyMetrics.green_power_ratio) }}</div>
                </div>
                <div class="executive-item">
                  <div class="executive-label">总投资</div>
                  <div class="executive-value">{{ formatNumber(costResult.total_capex_lakh || keyMetrics.total_cost, 2) }} 万元</div>
                </div>
              </div>
            </div>
            <div class="report-chapter">
              <h2>仲裁摘要</h2>
              <div class="report-section-item">
                <p>{{ arbitrator.summary || solutionData.report_summary || '暂无报告摘要内容' }}</p>
              </div>
            </div>
            <div class="report-chapter" v-if="reportMarkdown">
              <h2>Markdown 报告文本</h2>
              <div class="report-section-item">
                <div class="markdown-rendered" v-html="reportHtml"></div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { solutionApi } from '@/api'

const route = useRoute()
const activeTab = ref('overview')
const searchKeyword = ref('')
const solutionId = ref(route.params.id || '')
const solutionData = ref({})
const reportMarkdown = ref('')

const optimizationChartRef = ref(null)
const powerBalanceChartRef = ref(null)
const costChartRef = ref(null)
let charts = { optimization: null, powerBalance: null, cost: null }

const toNumber = (v, fallback = 0) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : fallback
}

const formatNumber = (v, digits = 2) => {
  if (v === null || v === undefined || v === '') return '-'
  const n = Number(v)
  if (!Number.isFinite(n)) return '-'
  return n.toFixed(digits)
}

const formatPercent = (v) => {
  if (v === null || v === undefined || v === '') return '-'
  const n = Number(v)
  if (!Number.isFinite(n)) return '-'
  return `${(n * 100).toFixed(1)}%`
}

const formatRisk = (risk) => {
  if (!risk) return '-'
  if (typeof risk === 'string') return risk
  if (risk.description) return risk.description
  return JSON.stringify(risk)
}

const intermediate = computed(() => solutionData.value.intermediate_results || {})
const draftOutput = computed(() => intermediate.value.draft_plan_agent?.full_output || {})
const coolingResult = computed(() => draftOutput.value.cooling_result || {})
const coolingKpis = computed(() => coolingResult.value.cooling_kpis || {})
const coolingEconomics = computed(() => coolingResult.value.economic_indicators || {})
const greenPowerResult = computed(() => draftOutput.value.green_power_result || {})
const greenOptimization = computed(() => greenPowerResult.value.optimization || {})
const greenFiles = computed(() => greenPowerResult.value.generated_files || {})
const powerPlan = computed(() => draftOutput.value.power_supply_plan || {})
const powerRaw = computed(() => powerPlan.value.raw_json || {})
const costResult = computed(() => intermediate.value.cost_calculation?.full_output || {})
const arbitrator = computed(() => intermediate.value.arbitrator?.full_output || solutionData.value || {})
const overallScores = computed(() => solutionData.value.overall_scores || arbitrator.value.overall_scores || {})
const keyMetrics = computed(() => solutionData.value.key_metrics || arbitrator.value.key_metrics || {})
const finalReportPath = computed(() => intermediate.value.final_report?.full_output?.path || solutionData.value.final_report_path || '')

const economicOpinion = computed(() => intermediate.value.economic_analysis?.full_output || {})
const reliabilityOpinion = computed(() => intermediate.value.power_reliability_analysis?.full_output || {})
const environmentalOpinion = computed(() => intermediate.value.environmental_analysis?.full_output || {})

const expertOpinions = computed(() => {
  const source = [economicOpinion.value, reliabilityOpinion.value, environmentalOpinion.value].filter(Boolean)
  return source.map((item) => ({
    name: item.expert_name || '专家',
    type: item.expert_type || '分析',
    summary: item.summary || '',
    metrics: item.metrics || {},
    recommendations: item.recommendations || []
  }))
})

const debateHistory = computed(() => {
  const raw = solutionData.value.debate_history || []
  if (Array.isArray(raw) && raw.length) {
    const grouped = {}
    raw.forEach(item => {
      const round = item.round || 1
      if (!grouped[round]) grouped[round] = { round, messages: [] }
      grouped[round].messages.push({ speaker: item.speaker || item.expert || '专家', content: item.content || '' })
    })
    return Object.values(grouped).sort((a, b) => a.round - b.round)
  }
  return []
})

const greenConfig = computed(() => {
  const wind = toNumber(greenOptimization.value.wind_capacity_mw, 0)
  const pv = toNumber(greenOptimization.value.pv_capacity_mw, 0)
  const storage = toNumber(greenOptimization.value.storage_capacity_mwh, 0)
  const total = wind + pv + storage
  return [
    { type: '光伏', capacity: `${formatNumber(pv)} MW`, ratio: total ? ((pv / total) * 100).toFixed(1) : '0.0' },
    { type: '风电', capacity: `${formatNumber(wind)} MW`, ratio: total ? ((wind / total) * 100).toFixed(1) : '0.0' },
    { type: '储能', capacity: `${formatNumber(storage)} MWh`, ratio: total ? ((storage / total) * 100).toFixed(1) : '0.0' }
  ]
})

const coolingTableData = computed(() => {
  const rows = []
  const push = (name, value) => rows.push({ name, value: value ?? '-' })
  push('策略名称', coolingResult.value.cooling_technology || '-')
  push('预测PUE', formatNumber(coolingResult.value.estimated_pue, 3))
  push('预测WUE', formatNumber(coolingResult.value.predicted_wue, 3))
  push('制冷功耗', `${formatNumber(coolingResult.value.cooling_power_consumption, 2)} kW`)
  push('余热回收', `${formatNumber(coolingResult.value.waste_heat_recovery_kw, 2)} kW`)
  return rows
})

const costBreakdown = computed(() => {
  const b = costResult.value.capex_breakdown || {}
  const total = toNumber(costResult.value.total_capex_lakh, 0)
  const items = [
    { item: '供电系统CAPEX', amount: toNumber(b.power_supply_system_lakh, 0) },
    { item: '绿电系统CAPEX', amount: toNumber(b.green_power_system_lakh, 0) },
    { item: '风电CAPEX', amount: toNumber(b.details?.wind_capex_lakh, 0) },
    { item: '光伏CAPEX', amount: toNumber(b.details?.pv_capex_lakh, 0) },
    { item: '储能CAPEX', amount: toNumber(b.details?.storage_capex_lakh, 0) }
  ]
  return items.filter(i => i.amount > 0).map(i => ({
    ...i,
    ratio: total > 0 ? ((i.amount / total) * 100).toFixed(1) : '0.0'
  }))
})

const filteredMarkdown = computed(() => {
  if (!searchKeyword.value) return reportMarkdown.value
  const kw = searchKeyword.value.toLowerCase()
  return reportMarkdown.value
    .split('\n')
    .filter(line => line.toLowerCase().includes(kw))
    .join('\n')
})

const escapeHtml = (text) =>
  String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const markdownToHtml = (md) => {
  if (!md) return '<p>暂无报告内容</p>'
  const lines = String(md).split('\n')
  const html = []
  let inList = false
  for (const rawLine of lines) {
    const line = rawLine.trimEnd()
    const escaped = escapeHtml(line)
    if (!line.trim()) {
      if (inList) {
        html.push('</ul>')
        inList = false
      }
      continue
    }
    if (line.startsWith('### ')) {
      if (inList) {
        html.push('</ul>')
        inList = false
      }
      html.push(`<h3>${escapeHtml(line.slice(4))}</h3>`)
    } else if (line.startsWith('## ')) {
      if (inList) {
        html.push('</ul>')
        inList = false
      }
      html.push(`<h2>${escapeHtml(line.slice(3))}</h2>`)
    } else if (line.startsWith('# ')) {
      if (inList) {
        html.push('</ul>')
        inList = false
      }
      html.push(`<h1>${escapeHtml(line.slice(2))}</h1>`)
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${escapeHtml(line.slice(2))}</li>`)
    } else {
      if (inList) {
        html.push('</ul>')
        inList = false
      }
      html.push(`<p>${escaped}</p>`)
    }
  }
  if (inList) html.push('</ul>')
  return html.join('\n')
}

const reportHtml = computed(() => markdownToHtml(filteredMarkdown.value))

const getExpertColor = (type) => {
  if (type?.includes('economic')) return 'linear-gradient(135deg, #165DFF 0%, #4080FF 100%)'
  if (type?.includes('reliability')) return 'linear-gradient(135deg, #00B42A 0%, #23C343 100%)'
  return 'linear-gradient(135deg, #FF7D00 0%, #FF9E40 100%)'
}

const loadSolutionData = async () => {
  try {
    const { data } = await solutionApi.getById(solutionId.value)
    solutionData.value = data || {}
    // 直接使用后端落库的最终完整报告，避免展示摘要替代正文
    if (solutionData.value?.final_report) {
      reportMarkdown.value = solutionData.value.final_report
    }
  } catch (error) {
    ElMessage.error(`加载方案失败: ${error.message}`)
  }
}

const loadMarkdownReport = async () => {
  if (solutionData.value?.final_report) {
    reportMarkdown.value = solutionData.value.final_report
    return
  }
  try {
    const { data } = await solutionApi.exportMarkdown(solutionId.value)
    reportMarkdown.value = data?.content || ''
  } catch (error) {
    reportMarkdown.value = ''
  }
}

const exportMarkdown = async () => {
  await loadMarkdownReport()
  const content = reportMarkdown.value || '暂无可导出的报告内容'
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `方案报告_${solutionId.value}.md`
  a.click()
  URL.revokeObjectURL(url)
}

const initOptimizationChart = () => {
  if (!optimizationChartRef.value) return
  if (charts.optimization) charts.optimization.dispose()
  const chart = echarts.init(optimizationChartRef.value)
  const trace = coolingResult.value.strategy_optimization_trace || []
  const points = Array.isArray(trace) && trace.length
    ? trace.map((item, idx) => ({ x: idx + 1, y: toNumber(item.score ?? item.value ?? item.objective, 0) }))
    : [{ x: 1, y: toNumber(coolingResult.value.estimated_pue, 0) }]
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: points.map(p => p.x) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: points.map(p => p.y), smooth: true, areaStyle: {} }]
  })
  charts.optimization = chart
}

const initPowerBalanceChart = () => {
  if (!powerBalanceChartRef.value) return
  if (charts.powerBalance) charts.powerBalance.dispose()
  const chart = echarts.init(powerBalanceChartRef.value)
  const source = greenConfig.value
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: source.map(item => ({ name: item.type, value: toNumber(item.ratio, 0) }))
    }]
  })
  charts.powerBalance = chart
}

const initCostChart = () => {
  if (!costChartRef.value) return
  if (charts.cost) charts.cost.dispose()
  const chart = echarts.init(costChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: costBreakdown.value.map(i => ({ name: i.item, value: i.amount }))
    }]
  })
  charts.cost = chart
}

const handleTabChange = async (tabName) => {
  await nextTick()
  if (tabName === 'cooling') initOptimizationChart()
  if (tabName === 'green') initPowerBalanceChart()
  if (tabName === 'economic') initCostChart()
  if (tabName === 'report' && !reportMarkdown.value) await loadMarkdownReport()
}

const handleResize = () => {
  Object.values(charts).forEach(chart => chart && chart.resize())
}

onMounted(async () => {
  await loadSolutionData()
  await nextTick()
  if (activeTab.value === 'overview') initCostChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  Object.values(charts).forEach(chart => chart && chart.dispose())
})
</script>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  height: calc(100% - 20px);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h1 {
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-tabs {
  flex: 1;
  overflow: hidden;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.metric-label {
  font-size: 14px;
  color: #8F959E;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #1F2329;
}

.metric-value.highlight {
  color: #165DFF;
}

.unit {
  font-size: 14px;
  font-weight: normal;
  color: #8F959E;
}

.metric-note {
  font-size: 12px;
  color: #00B42A;
  margin-top: 4px;
}

.summary-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.summary-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.summary-text {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.8;
  margin-bottom: 16px;
}

.budget-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.budget-status.success {
  background: #E8F8E8;
  color: #00B42A;
}

.budget-status.fail {
  background: #FFECE8;
  color: #F53F3F;
}

.risk-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #FFF7E6;
  color: #D46B08;
  border-radius: 8px;
}

.info-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.info-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.info-item {
  font-size: 13px;
  color: #8F959E;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #1F2329;
}

.param-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.param-card {
  flex: 1;
}

.param-card h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.param-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item {
  font-size: 14px;
  color: #4E5969;
}

.table-card, .chart-card, .guide-card, .recovery-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
  min-height: 300px;
}

.guide-content {
  display: flex;
  gap: 20px;
}

.guide-section {
  flex: 1;
}

.guide-section h5 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.guide-section p {
  font-size: 13px;
  color: #4E5969;
}

.recovery-content {
  display: flex;
  gap: 40px;
}

.recovery-item {
  font-size: 14px;
  color: #4E5969;
}

.architecture-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 8px;
}

.arch-item {
  padding: 12px 24px;
  background: #165DFF;
  color: white;
  border-radius: 8px;
}

.availability-stats, .reliability-stats, .carbon-stats {
  display: flex;
  gap: 20px;
}

.stat-card {
  flex: 1;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
  text-align: center;
}

.report-section {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.report-content {
  flex: 1;
  overflow-y: auto;
}

.report-chapter {
  margin-bottom: 24px;
}

.report-chapter h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.report-chapter p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.8;
}

.expert-opinions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.expert-opinion-card {
  background: #F5F7FA;
  border-radius: 8px;
  padding: 16px;
}

.expert-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.expert-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.expert-info {
  flex: 1;
}

.expert-name {
  font-weight: 600;
}

.expert-type {
  font-size: 12px;
  color: #8F959E;
}

.expert-summary {
  font-size: 14px;
  color: #4E5969;
  margin-bottom: 12px;
}

.expert-metrics {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #646A76;
}

.expert-recommendations h5 {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.expert-recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.expert-recommendations li {
  font-size: 13px;
  color: #4E5969;
}

.debate-history {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.debate-round {
  background: #F5F7FA;
  border-radius: 8px;
  padding: 12px;
}

.round-title {
  font-size: 13px;
  font-weight: 600;
  color: #165DFF;
  margin-bottom: 10px;
}

.debate-message {
  margin-bottom: 8px;
}

.debate-message .speaker {
  font-weight: 600;
}

.debate-message .content {
  color: #4E5969;
}

.arbitration-result {
  padding: 16px;
  background: #E8F8E8;
  border-radius: 8px;
}

.consensus-score {
  font-size: 18px;
  font-weight: 600;
  color: #00B42A;
  margin-bottom: 8px;
}

.arbitration-summary {
  font-size: 14px;
  color: #4E5969;
}

.report-title-section {
  text-align: center;
  padding: 20px;
  border-bottom: 2px solid #165DFF;
  margin-bottom: 24px;
}

.report-title {
  font-size: 24px;
  font-weight: 700;
  color: #1F2329;
  margin-bottom: 12px;
}

.report-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  font-size: 13px;
  color: #8F959E;
}

.report-executive-summary {
  background: #F5F7FA;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.report-executive-summary h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #1F2329;
}

.executive-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.executive-item {
  background: white;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.executive-label {
  font-size: 13px;
  color: #8F959E;
  margin-bottom: 8px;
}

.executive-value {
  font-size: 18px;
  font-weight: 600;
  color: #1F2329;
}

.executive-value.highlight {
  color: #165DFF;
}

.report-chapter {
  margin-bottom: 24px;
}

.report-chapter h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E5E6EB;
}

.report-section-item {
  margin-bottom: 16px;
}

.report-section-item h3 {
  font-size: 15px;
  font-weight: 600;
  color: #4E5969;
  margin-bottom: 8px;
}

.report-section-item p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.8;
}

.markdown-preview {
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.7;
  color: #4E5969;
  background: #F5F7FA;
  padding: 12px;
  border-radius: 8px;
}

.markdown-rendered {
  font-size: 14px;
  line-height: 1.8;
  color: #4E5969;
  background: #F5F7FA;
  padding: 16px;
  border-radius: 8px;
}

.markdown-rendered :deep(h1),
.markdown-rendered :deep(h2),
.markdown-rendered :deep(h3) {
  color: #1F2329;
  margin: 12px 0 8px;
}

.markdown-rendered :deep(h1) {
  font-size: 22px;
}

.markdown-rendered :deep(h2) {
  font-size: 18px;
}

.markdown-rendered :deep(h3) {
  font-size: 16px;
}

.markdown-rendered :deep(p) {
  margin: 8px 0;
}

.markdown-rendered :deep(ul) {
  margin: 8px 0 8px 20px;
}

.report-section-item ul {
  margin: 0;
  padding-left: 20px;
}

.report-section-item li {
  font-size: 14px;
  color: #4E5969;
  margin-bottom: 8px;
}

.report-table {
  margin-top: 12px;
  overflow-x: auto;
}

.report-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.report-table th,
.report-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #E5E6EB;
}

.report-table th {
  background: #F5F7FA;
  font-weight: 600;
  color: #4E5969;
}

.report-table td {
  color: #4E5969;
}

.report-conclusion {
  background: #E8F8E8;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.report-conclusion h2 {
  font-size: 16px;
  font-weight: 600;
  color: #00B42A;
  margin-bottom: 12px;
}

.report-conclusion p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.8;
}

.report-next-steps {
  background: #FFFBE6;
  border-radius: 8px;
  padding: 20px;
}

.report-next-steps h2 {
  font-size: 16px;
  font-weight: 600;
  color: #D46B08;
  margin-bottom: 12px;
}

.report-next-steps ul {
  margin: 0;
  padding-left: 20px;
}

.report-next-steps li {
  font-size: 14px;
  color: #4E5969;
  margin-bottom: 8px;
}

.report-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}
</style>
