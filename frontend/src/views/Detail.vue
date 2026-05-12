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
            <div class="metric-card" v-for="(metric, index) in overviewMetrics" :key="index" :style="{ animationDelay: `${index * 100}ms` }">
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-value" :class="{ highlight: metric.highlight }">{{ metric.value }}</div>
              <div v-if="metric.unit" class="metric-unit">{{ metric.unit }}</div>
            </div>
          </div>

          <div class="summary-section">
            <h3>方案摘要</h3>
            <p class="summary-text">{{ arbitrator.summary || '暂无后端仲裁摘要' }}</p>
            <div class="budget-status" :class="costResult.is_over_budget ? 'fail' : 'success'">
              <el-icon><CircleCheckFilled /></el-icon>
              <span v-if="costResult.is_over_budget">当前方案超预算 {{ formatNumber(Math.abs(costResult.budget_delta_lakh), 2) }} 万元</span>
              <span v-else-if="toNumber(costResult.budget_delta_lakh, 0) === 0">预算校验通过，当前方案与预算上限持平</span>
              <span v-else>预算校验通过，预算结余 {{ formatNumber(costResult.budget_delta_lakh, 2) }} 万元</span>
            </div>
            <div class="risk-warning" v-if="arbitrator.risks && arbitrator.risks.length">
              <el-icon><CircleCloseFilled /></el-icon>
              <span>{{ formatRisk(arbitrator.risks[0]) }}</span>
            </div>
            <div class="expert-recommendations" v-if="arbitrator.recommendations && arbitrator.recommendations.length">
              <h5>最终建议</h5>
              <ul>
                <li v-for="(rec, i) in arbitrator.recommendations" :key="`final-rec-${i}`">{{ rec }}</li>
              </ul>
            </div>
            <div class="expert-recommendations" v-if="arbitrator.trade_offs && arbitrator.trade_offs.length">
              <h5>关键权衡</h5>
              <ul>
                <li v-for="(item, i) in arbitrator.trade_offs" :key="`trade-${i}`">{{ item.conflict }}：{{ item.resolution }}</li>
              </ul>
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
                <div class="param-item">年运维成本：{{ formatNumber(coolingEconomics.annual_op_cost, 2) }} 万元</div>
                <div class="param-item">年电费：{{ formatNumber(coolingEconomics.annual_electricity_cost, 2) }} 万元</div>
                <div class="param-item">LCOE：{{ formatNumber(coolingEconomics.lcoe, 4) }} 元/kWh</div>
              </div>
            <div class="param-grid" v-if="environmentalSection.recommendations && environmentalSection.recommendations.length">
              <div class="param-item">环保建议：</div>
              <div class="param-item" v-for="(rec, idx) in environmentalSection.recommendations" :key="`env-rec-${idx}`">- {{ rec }}</div>
            </div>
            </el-card>
          </div>

          <section class="system-trace-shell">
            <div class="system-trace-header">
              <div>
                <h4>方案生成过程与依据</h4>
                <p>对应后端 `cooling-scheme-generator`，展示输入条件、寻优步骤、权重设置与候选策略排序。</p>
              </div>
              <div class="system-trace-badge">Tool 02</div>
            </div>

            <div class="system-trace-topology">
              <div class="trace-block">
                <div class="trace-block-title">输入条件</div>
                <div class="trace-chip-list">
                  <span v-for="input in coolingTrace.inputs" :key="input" class="trace-chip">{{ input }}</span>
                </div>
              </div>
              <div class="trace-block">
                <div class="trace-block-title">关键参数</div>
                <div class="trace-fact-grid">
                  <div v-for="fact in coolingTrace.facts" :key="fact.label" class="trace-fact-item">
                    <span class="trace-fact-label">{{ fact.label }}</span>
                    <span class="trace-fact-value">{{ fact.value }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">生成步骤</div>
              <div class="trace-step-list">
                <div v-for="(step, index) in coolingTrace.steps" :key="step.title" class="trace-step-item">
                  <span class="trace-step-index">{{ index + 1 }}</span>
                  <div class="trace-step-copy">
                    <div class="trace-step-title">{{ step.title }}</div>
                    <div class="trace-step-desc">{{ step.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">多目标寻优</div>
              <div class="trace-weight-grid">
                <div v-for="weight in coolingTrace.weights" :key="weight.label" class="trace-weight-item">
                  <span class="trace-weight-label">{{ weight.label }}</span>
                  <span class="trace-weight-value">{{ weight.value }}</span>
                </div>
              </div>
              <div class="trace-ranking-list">
                <div
                  v-for="candidate in coolingTrace.ranking"
                  :key="candidate.name"
                  class="trace-ranking-item"
                  :class="{ 'is-winner': candidate.isWinner }"
                >
                  <div class="trace-ranking-head">
                    <span class="trace-ranking-order">#{{ candidate.rank }}</span>
                    <span class="trace-ranking-name">{{ candidate.name }}</span>
                    <span class="trace-ranking-score">综合得分 {{ candidate.score }}</span>
                  </div>
                  <div class="trace-ranking-tags">
                    <span v-for="tag in candidate.tags" :key="tag" class="trace-ranking-tag">{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">判断依据</div>
              <ul class="trace-evidence-list">
                <li v-for="evidence in coolingTrace.evidences" :key="evidence">{{ evidence }}</li>
              </ul>
            </div>
          </section>

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
          <section class="system-trace-shell">
            <div class="system-trace-header">
              <div>
                <h4>方案生成过程与依据</h4>
                <p>对应后端 `green_power_allocation`，展示资源曲线生成、负荷输入、DE 参数和容量优化链路。</p>
              </div>
              <div class="system-trace-badge">Tool 01</div>
            </div>

            <div class="system-trace-topology">
              <div class="trace-block">
                <div class="trace-block-title">输入条件</div>
                <div class="trace-chip-list">
                  <span v-for="input in greenTrace.inputs" :key="input" class="trace-chip">{{ input }}</span>
                </div>
              </div>
              <div class="trace-block">
                <div class="trace-block-title">优化设定</div>
                <div class="trace-fact-grid">
                  <div v-for="fact in greenTrace.facts" :key="fact.label" class="trace-fact-item">
                    <span class="trace-fact-label">{{ fact.label }}</span>
                    <span class="trace-fact-value">{{ fact.value }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">生成步骤</div>
              <div class="trace-step-list">
                <div v-for="(step, index) in greenTrace.steps" :key="step.title" class="trace-step-item">
                  <span class="trace-step-index">{{ index + 1 }}</span>
                  <div class="trace-step-copy">
                    <div class="trace-step-title">{{ step.title }}</div>
                    <div class="trace-step-desc">{{ step.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">判断依据</div>
              <ul class="trace-evidence-list">
                <li v-for="evidence in greenTrace.evidences" :key="evidence">{{ evidence }}</li>
              </ul>
            </div>
          </section>

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
          <section class="system-trace-shell">
            <div class="system-trace-header">
              <div>
                <h4>方案生成过程与依据</h4>
                <p>对应后端 `power_supply_config`，展示标准模板命中、负荷折算、电压阈值判断与配置理由。</p>
              </div>
              <div class="system-trace-badge">Tool 03</div>
            </div>

            <div class="system-trace-topology">
              <div class="trace-block">
                <div class="trace-block-title">输入条件</div>
                <div class="trace-chip-list">
                  <span v-for="input in powerTrace.inputs" :key="input" class="trace-chip">{{ input }}</span>
                </div>
              </div>
              <div class="trace-block">
                <div class="trace-block-title">规则命中</div>
                <div class="trace-fact-grid">
                  <div v-for="fact in powerTrace.facts" :key="fact.label" class="trace-fact-item">
                    <span class="trace-fact-label">{{ fact.label }}</span>
                    <span class="trace-fact-value">{{ fact.value }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">生成步骤</div>
              <div class="trace-step-list">
                <div v-for="(step, index) in powerTrace.steps" :key="step.title" class="trace-step-item">
                  <span class="trace-step-index">{{ index + 1 }}</span>
                  <div class="trace-step-copy">
                    <div class="trace-step-title">{{ step.title }}</div>
                    <div class="trace-step-desc">{{ step.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="trace-block">
              <div class="trace-block-title">判断依据</div>
              <ul class="trace-evidence-list">
                <li v-for="evidence in powerTrace.evidences" :key="evidence">{{ evidence }}</li>
              </ul>
            </div>
          </section>

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
          <div class="economic-cost-panel">
            <section class="economic-cost-main">
              <div class="economic-cost-header">
                <div>
                  <h4>投资构成视图</h4>
                  <p>点击环形图扇区或下方成本项，可查看该部分的投资组成、设备配置与测算口径。</p>
                </div>
                <el-tag effect="plain" round>总投资口径已统一包含制冷系统</el-tag>
              </div>

              <div class="economic-chart-shell">
                <div ref="costChartRef" class="economic-cost-chart"></div>
              </div>

              <div class="economic-chart-note">
                当前详情页与方案生成页使用同一成本口径，总投资由供电系统、绿电系统和制冷系统三部分构成。
              </div>

              <div class="economic-cost-list">
                <button
                  v-for="segment in costStructureSegments"
                  :key="segment.key"
                  type="button"
                  class="economic-cost-item"
                  @click="openCostDetail(segment.key)"
                >
                  <span class="economic-cost-dot" :style="{ background: segment.color }"></span>
                  <span class="economic-cost-copy">
                    <span class="economic-cost-title">{{ segment.name }}</span>
                    <span class="economic-cost-desc">{{ segment.shortDescription }}</span>
                  </span>
                  <span class="economic-cost-meta">
                    <span class="economic-cost-value">{{ formatNumber(segment.amount, 0) }} 万元</span>
                    <span class="economic-cost-ratio">{{ segment.ratio }}%</span>
                  </span>
                </button>
              </div>
            </section>

            <aside class="economic-cost-summary">
              <div class="economic-kpi-grid">
                <div class="economic-kpi-card strong">
                  <span class="economic-kpi-label">项目总投资</span>
                  <span class="economic-kpi-value">{{ formatNumber(costResult.total_capex_lakh, 0) }} 万元</span>
                  <span class="economic-kpi-note">供电 + 绿电 + 制冷</span>
                </div>
                <div class="economic-kpi-card">
                  <span class="economic-kpi-label">预算约束</span>
                  <span class="economic-kpi-value" :class="costResult.is_over_budget ? 'danger' : 'success'">
                    {{ formatNumber(costResult.budget_constraint_lakh, 0) }} 万元
                  </span>
                  <span class="economic-kpi-note">配置参数基准</span>
                </div>
                <div class="economic-kpi-card">
                  <span class="economic-kpi-label">预算差额</span>
                  <span class="economic-kpi-value" :class="costResult.is_over_budget ? 'danger' : 'success'">
                    {{ formatNumber(Math.abs(costResult.budget_delta_lakh), 0) }} 万元
                  </span>
                  <span class="economic-kpi-note">
                    {{
                      costResult.is_over_budget
                        ? '超预算'
                        : toNumber(costResult.budget_delta_lakh, 0) === 0
                          ? '预算持平'
                          : '预算结余'
                    }}
                  </span>
                </div>
              </div>

              <div class="economic-summary-heading">
                <span class="economic-summary-title">成本清单</span>
                <span class="economic-summary-note">点击左侧图形或下方条目查看细节</span>
              </div>

              <div class="economic-summary-strip">
                <div
                  v-for="segment in costStructureSegments"
                  :key="segment.key"
                  class="economic-summary-row"
                >
                  <span class="economic-summary-dot" :style="{ background: segment.color }"></span>
                  <span class="economic-summary-label">{{ segment.name }}</span>
                  <span class="economic-summary-value">{{ formatNumber(segment.amount, 0) }} 万元</span>
                </div>
              </div>
            </aside>
          </div>

          <el-card class="economic-metrics-card">
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
              <h1 class="report-title">{{ finalReportData.name || '数据中心绿电消纳方案报告' }}</h1>
              <div class="report-meta">
                <span>方案编号：{{ solutionId }}</span>
                <span>生成时间：{{ solutionData.created_at || '-' }}</span>
                <span>置信度：{{ formatPercent(finalReportData.confidence) }}</span>
              </div>
            </div>
            <div class="report-executive-summary">
              <h2>执行摘要</h2>
              <p class="summary-text">{{ finalReportData.summary || '暂无摘要' }}</p>
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
              <h2>综合评分</h2>
              <div class="report-section-item">
                <div class="executive-grid">
                  <div class="executive-item">
                    <div class="executive-label">经济性</div>
                    <div class="executive-value">{{ formatPercent(overallScores.economic) }}</div>
                  </div>
                  <div class="executive-item">
                    <div class="executive-label">可靠性</div>
                    <div class="executive-value">{{ formatPercent(overallScores.reliability) }}</div>
                  </div>
                  <div class="executive-item">
                    <div class="executive-label">环保性</div>
                    <div class="executive-value">{{ formatPercent(overallScores.environmental) }}</div>
                  </div>
                  <div class="executive-item">
                    <div class="executive-label">总体</div>
                    <div class="executive-value">{{ formatPercent(overallScores.overall) }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="report-chapter">
              <h2>关键指标</h2>
              <div class="report-section-item">
                <el-table :data="keyMetricsRows" border>
                  <el-table-column prop="label" label="指标" width="240" />
                  <el-table-column prop="value" label="数值" />
                </el-table>
              </div>
            </div>
            <div class="report-chapter">
              <h2>经济性方案</h2>
              <div class="report-section-item">
                <p>{{ economicSection.description || '暂无经济性描述' }}</p>
                <el-table v-if="economicRows.length" :data="economicRows" border>
                  <el-table-column prop="label" label="指标" width="240" />
                  <el-table-column prop="value" label="数值" />
                </el-table>
                <ul v-if="economicSection.recommendations && economicSection.recommendations.length">
                  <li v-for="(item, idx) in economicSection.recommendations" :key="`eco-${idx}`">{{ item }}</li>
                </ul>
              </div>
            </div>
            <div class="report-chapter">
              <h2>供电可靠性方案</h2>
              <div class="report-section-item">
                <p>{{ powerSection.description || '暂无供电可靠性描述' }}</p>
                <el-table v-if="powerRows.length" :data="powerRows" border>
                  <el-table-column prop="label" label="指标" width="240" />
                  <el-table-column prop="value" label="数值" />
                </el-table>
                <ul v-if="powerSection.recommendations && powerSection.recommendations.length">
                  <li v-for="(item, idx) in powerSection.recommendations" :key="`power-${idx}`">{{ item }}</li>
                </ul>
              </div>
            </div>
            <div class="report-chapter">
              <h2>环保方案</h2>
              <div class="report-section-item">
                <p>{{ environmentalSection.description || '暂无环保描述' }}</p>
                <el-table v-if="environmentalRows.length" :data="environmentalRows" border>
                  <el-table-column prop="label" label="指标" width="240" />
                  <el-table-column prop="value" label="数值" />
                </el-table>
                <ul v-if="environmentalSection.recommendations && environmentalSection.recommendations.length">
                  <li v-for="(item, idx) in environmentalSection.recommendations" :key="`env-${idx}`">{{ item }}</li>
                </ul>
              </div>
            </div>
            <div class="report-chapter">
              <h2>关键权衡</h2>
              <div class="report-section-item">
                <ul v-if="finalReportData.trade_offs && finalReportData.trade_offs.length">
                  <li v-for="(item, idx) in finalReportData.trade_offs" :key="`trade-off-${idx}`">
                    {{ item.conflict || '-' }}：{{ item.resolution || '-' }}
                  </li>
                </ul>
                <p v-else>暂无关键权衡项</p>
              </div>
            </div>
            <div class="report-chapter">
              <h2>风险清单</h2>
              <div class="report-section-item">
                <ul v-if="finalReportData.risks && finalReportData.risks.length">
                  <li v-for="(item, idx) in finalReportData.risks" :key="`risk-${idx}`">
                    [{{ item.type || '未知类型' }}] {{ item.description || '-' }}
                  </li>
                </ul>
                <p v-else>暂无风险项</p>
              </div>
            </div>
            <div class="report-chapter">
              <h2>最终建议</h2>
              <div class="report-section-item">
                <ul v-if="finalReportData.recommendations && finalReportData.recommendations.length">
                  <li v-for="(item, idx) in finalReportData.recommendations" :key="`final-rec-${idx}`">{{ item }}</li>
                </ul>
                <p v-else>暂无最终建议</p>
              </div>
            </div>
            <div class="report-chapter" v-if="reportMarkdown">
              <h2>Markdown 报告预览</h2>
              <div class="report-section-item">
                <div class="markdown-rendered" v-html="reportHtml"></div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="costDetailDialogVisible"
      width="560px"
      destroy-on-close
      class="economic-cost-dialog"
    >
      <template #header>
        <div class="economic-detail-header">
          <span class="economic-detail-dot" :style="{ background: activeCostSegment.color }"></span>
          <div class="economic-detail-copy">
            <div class="economic-detail-title">{{ activeCostSegment.name }}</div>
            <div class="economic-detail-subtitle">{{ activeCostSegment.summary }}</div>
          </div>
        </div>
      </template>

      <div class="economic-detail-body">
        <div class="economic-detail-kpis">
          <div class="economic-detail-kpi">
            <span class="economic-detail-kpi-label">当前金额</span>
            <span class="economic-detail-kpi-value">{{ formatNumber(activeCostSegment.amount, 0) }} 万元</span>
          </div>
          <div class="economic-detail-kpi">
            <span class="economic-detail-kpi-label">投资占比</span>
            <span class="economic-detail-kpi-value">{{ activeCostSegment.ratio }}%</span>
          </div>
        </div>

        <div class="economic-detail-list">
          <div
            v-for="detail in activeCostSegment.details"
            :key="detail.label"
            class="economic-detail-row"
          >
            <span class="economic-detail-row-label">{{ detail.label }}</span>
            <span class="economic-detail-row-value">{{ detail.value }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { mockSolutionData } from '@/mock/data.js'
import { solutionApi } from '@/api'

const route = useRoute()
const activeTab = ref('overview')
const searchKeyword = ref('')
const solutionId = ref(route.params.id || 'mock-solution-001')
const solutionData = ref(mockSolutionData)
const reportMarkdown = ref(mockSolutionData.final_report)

const optimizationChartRef = ref(null)
const powerBalanceChartRef = ref(null)
const costChartRef = ref(null)
const costDetailDialogVisible = ref(false)
const activeCostDetailKey = ref('green_power')
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

const formatObjectRows = (obj = {}) => {
  if (!obj || typeof obj !== 'object') return []
  return Object.entries(obj).map(([key, value]) => ({
    label: key,
    value: typeof value === 'number' ? value : String(value)
  }))
}

const intermediate = computed(() => solutionData.value.intermediate_results || {})
const draftOutput = computed(() => intermediate.value.draft_plan_agent?.full_output || {})
const arbitrator = computed(() => intermediate.value.arbitrator?.full_output || solutionData.value || {})
const overallScores = computed(() => solutionData.value.overall_scores || arbitrator.value.overall_scores || {})
const keyMetrics = computed(() => solutionData.value.key_metrics || arbitrator.value.key_metrics || {})
const finalReportPath = computed(() => intermediate.value.final_report?.full_output?.path || solutionData.value.final_report_path || '')

const economicSection = computed(() => solutionData.value.economic_section || arbitrator.value.economic_section || {})
const powerSection = computed(() => solutionData.value.power_reliability_section || arbitrator.value.power_reliability_section || {})
const environmentalSection = computed(() => solutionData.value.environmental_section || arbitrator.value.environmental_section || {})
const economicContent = computed(() => economicSection.value.content || {})
const powerContent = computed(() => powerSection.value.content || {})
const environmentalContent = computed(() => environmentalSection.value.content || {})
const requirement = computed(() => intermediate.value.requirement_parser?.requirement || {})

const coolingResult = computed(() => {
  const draftCooling = draftOutput.value.cooling_result || {}
  return {
    ...draftCooling,
    cooling_technology: draftCooling.cooling_technology || environmentalSection.value.description || '-',
    estimated_pue: draftCooling.estimated_pue ?? environmentalContent.value.pue ?? keyMetrics.value.pue ?? null,
    predicted_wue: draftCooling.predicted_wue ?? environmentalContent.value.wue ?? null,
    cooling_power_consumption: draftCooling.cooling_power_consumption ?? draftCooling.cooling_kpis?.cooling_power_kw ?? null,
    waste_heat_recovery_kw: draftCooling.waste_heat_recovery_kw ?? draftCooling.cooling_kpis?.waste_heat_recovery_kw ?? null,
    strategy_optimization_trace: draftCooling.strategy_optimization_trace || []
  }
})
const coolingKpis = computed(() => coolingResult.value.cooling_kpis || {})
const coolingEconomics = computed(() => {
  const draftEco = coolingResult.value.economic_indicators || {}
  return {
    initial_investment: draftEco.initial_investment ?? economicContent.value.total_cost ?? keyMetrics.value.total_cost ?? null,
    annual_op_cost: draftEco.annual_op_cost ?? null,
    annual_electricity_cost: draftEco.annual_electricity_cost ?? null,
    lcoe: draftEco.lcoe ?? null
  }
})

const greenPowerResult = computed(() => draftOutput.value.green_power_result || {})
const greenOptimization = computed(() => greenPowerResult.value.optimization || {})
const greenFiles = computed(() => greenPowerResult.value.generated_files || {})

const powerPlan = computed(() => {
  const draftPower = draftOutput.value.power_supply_plan || {}
  return {
    ...draftPower,
    external_source_type: draftPower.external_source_type || powerSection.value.description || '-',
    redundancy_logic: draftPower.redundancy_logic || powerContent.value.ups_configuration || '-',
    bus_type: draftPower.bus_type || '-',
    secondary_voltage: draftPower.secondary_voltage || '-',
    external_voltage: draftPower.external_voltage || '-'
  }
})
const powerRaw = computed(() => {
  const raw = powerPlan.value.raw_json || {}
  return {
    ...raw,
    machine_room_grade: raw.machine_room_grade || keyMetrics.value.tier_level || powerContent.value.tier_level || '-',
    cost_per_mw: raw.cost_per_mw ?? null
  }
})

const costResult = computed(() => {
  const rawCost = intermediate.value.cost_calculation?.full_output || {}
  const economic = rawCost.economic_analysis_result || rawCost || {}
  const breakdown = economic.capex_breakdown || {}
  const coolingCapex = toNumber(coolingResult.value.economic_indicators?.initial_investment, 0)
  const powerSupplyCapex = toNumber(breakdown.power_supply_system_lakh, 0)
  const greenPowerCapex = toNumber(breakdown.green_power_system_lakh, 0)
  const recalculatedTotal = powerSupplyCapex + greenPowerCapex + coolingCapex
  const budgetConstraint = toNumber(economic.budget_constraint_lakh, 0)
  const normalizedTotal = recalculatedTotal > 0
    ? recalculatedTotal
    : toNumber(economic.total_capex_lakh, toNumber(keyMetrics.value.total_cost, 0))
  const normalizedBudgetDelta = budgetConstraint > 0
    ? budgetConstraint - normalizedTotal
    : toNumber(economic.budget_delta_lakh, 0)

  return {
    ...economic,
    total_capex_lakh: normalizedTotal,
    budget_constraint_lakh: budgetConstraint || toNumber(economic.budget_constraint_lakh, 0),
    budget_delta_lakh: normalizedBudgetDelta,
    is_over_budget: budgetConstraint > 0 ? normalizedBudgetDelta < 0 : Boolean(economic.is_over_budget),
    capex_breakdown: {
      ...breakdown,
      power_supply_system_lakh: powerSupplyCapex,
      green_power_system_lakh: greenPowerCapex,
      cooling_system_lakh: coolingCapex
    }
  }
})
const finalReportData = computed(() => ({
  ...arbitrator.value,
  ...solutionData.value
}))
const keyMetricsRows = computed(() => {
  const metrics = keyMetrics.value || {}
  return [
    { label: '总成本(万元)', value: formatNumber(costResult.value.total_capex_lakh || metrics.total_cost, 2) },
    { label: 'PUE', value: formatNumber(metrics.pue, 3) },
    { label: '绿电比例', value: formatPercent(metrics.green_power_ratio) },
    { label: 'Tier 等级', value: metrics.tier_level ?? '-' },
    { label: '预期可用性', value: metrics.expected_availability ?? '-' },
    { label: '年碳排放(吨)', value: metrics.annual_carbon_emission ?? '-' }
  ]
})
const economicRows = computed(() => formatObjectRows(economicContent.value))
const powerRows = computed(() => formatObjectRows(powerContent.value))
const environmentalRows = computed(() => formatObjectRows(environmentalContent.value))

const coolingOptimization = computed(() => coolingResult.value.optimization_summary || {})
const coolingWeights = computed(() => coolingOptimization.value.objective_weights || {})
const coolingRanking = computed(() => Array.isArray(coolingResult.value.all_strategy_scores) ? coolingResult.value.all_strategy_scores : [])
const greenInputs = computed(() => greenPowerResult.value.inputs || {})
const greenProfiles = computed(() => ({
  pv: greenPowerResult.value.pv_profile || {},
  wind: greenPowerResult.value.wind_profile || {}
}))
const powerFactor = computed(() => toNumber(powerRaw.value.power_factor, 0.9))
const totalLoadMw = computed(() => toNumber(powerRaw.value.total_load_mw, toNumber(requirement.value.planned_load_kw, 0) / 1000))
const totalLoadMva = computed(() => toNumber(powerRaw.value.total_load_mva, totalLoadMw.value / powerFactor.value))

const coolingTrace = computed(() => ({
  inputs: [
    `项目位置：${requirement.value.location || '-'}`,
    `IT 负荷：${formatNumber(toNumber(requirement.value.planned_load_kw, 0), 0)} kW`,
    `功率密度：${formatNumber(requirement.value.computing_power_density, 2)} kW/机柜`,
    `PUE 目标：${formatNumber(requirement.value.pue_target, 2)}`,
    `优先级：${coolingOptimization.value.priority_mode || requirement.value.priority || 'economic'}`,
    '优化目标：PUE / WUE / TCO / CUE / WHR'
  ],
  facts: [
    { label: '可行候选数', value: `${coolingOptimization.value.feasible_strategy_count || coolingRanking.value.length || '-'} 个` },
    { label: '最终胜出方案', value: coolingOptimization.value.selected_strategy || coolingResult.value.cooling_technology || '-' },
    { label: '寻优模式', value: coolingOptimization.value.optimization_mode || 'weighted_multi_objective' },
    { label: '输出内容', value: '技术路线 + KPI + 经济指标' }
  ],
  steps: [
    { title: '归并需求与显式参数', description: '后端先统一项目位置、负荷、功率密度、PUE/WUE 目标与优先级，形成可计算输入。' },
    { title: '筛掉不适合当前工况的方案', description: '结合环境条件与机柜密度约束，对候选制冷技术先做可行性筛选，只保留可比较路线。' },
    { title: '执行多目标加权寻优', description: '对每个可行候选同时评估 PUE、WUE、TCO、CUE 与余热回收能力，并按优先级动态加权。' },
    { title: '输出推荐方案与指标', description: '综合得分最优的路线会被选为推荐技术，并同步返回 KPI、经济指标与寻优轨迹。' }
  ],
  weights: [
    { label: 'PUE 权重', value: formatPercent(coolingWeights.value.PUE, 0) },
    { label: 'WUE 权重', value: formatPercent(coolingWeights.value.WUE, 0) },
    { label: 'TCO 权重', value: formatPercent(coolingWeights.value.TCO, 0) },
    { label: 'CUE 权重', value: formatPercent(coolingWeights.value.CUE, 0) },
    { label: 'WHR 权重', value: formatPercent(coolingWeights.value.WHR, 0) }
  ],
  ranking: coolingRanking.value.slice(0, 4).map(item => ({
    rank: item.ranking ?? '-',
    name: item.strategy || '--',
    score: formatNumber(item.total_score, 2),
    isWinner: (item.strategy || '') === (coolingOptimization.value.selected_strategy || coolingResult.value.cooling_technology),
    tags: [
      `PUE ${formatNumber(item.pue, 2)}`,
      `WUE ${formatNumber(item.wue, 2)}`,
      `TCO ${formatNumber(item.tco, 2)}`,
      `WHR ${formatNumber(item.whr, 2)}`
    ]
  })),
  evidences: [
    '制冷方案不是简单规则匹配，后端会对可行候选做多目标加权评分后再排序。',
    '功率密度、目标 PUE/WUE 和环境条件会共同影响候选方案的可行性边界。',
    '最终结果同时输出技术路线、PUE、WUE、制冷功耗和经济指标，因此结论具备可追溯性。'
  ]
}))

const greenTrace = computed(() => ({
  inputs: [
    `项目位置：${requirement.value.location || '-'}`,
    `负荷规模：${formatNumber(totalLoadMw.value, 2)} MW`,
    `绿电目标：${formatPercent(greenInputs.value.green_power_ratio ?? requirement.value.green_power_ratio, 0)}`,
    `仿真时长：${greenInputs.value.sim_hours || requirement.value.sim_hours || 168} h`,
    `气象年份：${greenInputs.value.year || requirement.value.year || 2025}`,
    '容量边界：风/光 1-500MW，储能 20-500MWh'
  ],
  facts: [
    { label: '仿真模式', value: greenProfiles.value.pv.mode || greenProfiles.value.wind.mode || '--' },
    { label: '资源曲线', value: '先生成 PV / Wind 单位出力曲线' },
    { label: 'DE 参数', value: `maxiter ${greenInputs.value.maxiter || 60} · popsize ${greenInputs.value.popsize || 10} · seed ${greenInputs.value.seed || 42}` },
    { label: '后端产物', value: greenFiles.value.balance_plot ? '平衡图 + 曲线 CSV' : '容量优化结果' }
  ],
  steps: [
    { title: '根据地点生成风光资源曲线', description: '后端会先分别调用光伏与风电子工具，按地点、年份和设备参数生成单位出力曲线。' },
    { title: '载入负荷曲线与容量边界', description: '将总负荷、仿真时长、负荷 CSV、风光储容量范围和目标绿电比例一起整理为优化输入。' },
    { title: '执行差分进化容量优化', description: '在风电、光伏、储能三维搜索空间内迭代寻优，目标是在满足约束下最小化总投资。' },
    { title: '输出装机结果与平衡图', description: '得到最优组合后，返回装机容量、目标绿电占比、成本拆分以及功率平衡图文件。' }
  ],
  evidences: [
    '绿电方案不是直接估算容量，而是先生成当地风光出力曲线，再进入容量优化。',
    `当前负荷为 ${formatNumber(totalLoadMw.value, 2)} MW，绿电目标为 ${formatPercent(greenInputs.value.green_power_ratio ?? requirement.value.green_power_ratio, 0)}。`,
    '差分进化参数、搜索边界和仿真时长都会影响容量优化的收敛路径和最终结果。'
  ]
}))

const powerTrace = computed(() => {
  const voltageCriteria = totalLoadMva.value >= 100
    ? '命中 220kV 阈值（>=100MVA）'
    : totalLoadMva.value >= 40
      ? '命中 110kV 阈值（>=40MVA）'
      : totalLoadMva.value >= 30
        ? '命中 66kV 阈值（>=30MVA）'
        : '命中 35kV 阈值（<30MVA）'

  return {
    inputs: [
      `机房等级：${powerRaw.value.machine_room_grade || '-'}`,
      `总负荷：${formatNumber(totalLoadMw.value, 2)} MW`,
      `PUE 目标：${formatNumber(requirement.value.pue_target, 2)}`,
      `功率因数：${formatNumber(powerFactor.value, 2)}`,
      '依据标准：GB 50174—2017 / YD/T 5235—2019'
    ],
    facts: [
      { label: '等级模板', value: `${powerRaw.value.machine_room_grade || '-'} 级标准化模板` },
      { label: '负荷折算', value: `${formatNumber(totalLoadMw.value, 2)} MW ÷ ${formatNumber(powerFactor.value, 2)} = ${formatNumber(totalLoadMva.value, 2)} MVA` },
      { label: '电压阈值', value: voltageCriteria },
      { label: '详细理由', value: powerPlan.value.reasons ? '已生成结构化 reasons' : '使用默认解释' }
    ],
    steps: [
      { title: '按机房等级选供电模板', description: '后端先从 A+/A/B/C 标准方案库中选出对应等级模板，锁定外部电源、冗余和母线基线。' },
      { title: '将总负荷从 MW 折算为 MVA', description: '工具按功率因数将总负荷换算为视在功率，这一步直接影响外部电压档位选择。' },
      { title: '按阈值匹配外部电压等级', description: '系统依次检查 220kV、110kV、66kV、35kV 的容量阈值，命中的首个档位即成为外部接入方案。' },
      { title: '拼接次级配电与详细理由', description: '在确定模板和电压档位后，生成次级配电、配变组织方式、柴油机策略和完整 reasons 文本。' }
    ],
    evidences: [
      '供电方案不是自由生成文案，而是标准模板、阈值规则和负荷换算共同决定的结果。',
      `当前负荷折算后约为 ${formatNumber(totalLoadMva.value, 2)} MVA，因此当前命中规则为“${voltageCriteria}”。`,
      '最终输出包含 reasons 与 raw_json，说明每个配置项都能追溯到明确的标准依据。'
    ]
  }
})

const economicOpinion = computed(() => intermediate.value.economic_analysis?.full_output || {})
const reliabilityOpinion = computed(() => intermediate.value.power_reliability_analysis?.full_output || {})
const environmentalOpinion = computed(() => intermediate.value.environmental_analysis?.full_output || {})

const expertOpinions = computed(() => {
  const source = [economicOpinion.value, reliabilityOpinion.value, environmentalOpinion.value].filter(item => item && Object.keys(item).length)
  if (source.length) {
    return source.map((item) => ({
      name: item.expert_name || '专家',
      type: item.expert_type || '分析',
      summary: item.summary || '',
      metrics: item.metrics || {},
      recommendations: item.recommendations || []
    }))
  }

  const fallback = [
    { expert_name: '经济性结论', expert_type: 'economic', summary: economicSection.value.description || '', metrics: economicContent.value, recommendations: economicSection.value.recommendations || [] },
    { expert_name: '可靠性结论', expert_type: 'power_reliability', summary: powerSection.value.description || '', metrics: powerContent.value, recommendations: powerSection.value.recommendations || [] },
    { expert_name: '环保性结论', expert_type: 'environmental', summary: environmentalSection.value.description || '', metrics: environmentalContent.value, recommendations: environmentalSection.value.recommendations || [] }
  ].filter(item => item.summary || Object.keys(item.metrics || {}).length)

  return fallback.map((item) => ({
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
  if (total <= 0) {
    const ratio = toNumber(keyMetrics.value.green_power_ratio, null)
    return [
      { type: '绿电占比(最终方案)', capacity: '-', ratio: ratio !== null ? (ratio * 100).toFixed(1) : '-' },
      { type: '传统电占比(推导)', capacity: '-', ratio: ratio !== null ? (100 - ratio * 100).toFixed(1) : '-' }
    ]
  }
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

const costStructureSegments = computed(() => {
  const breakdown = costResult.value.capex_breakdown || {}
  const total = toNumber(costResult.value.total_capex_lakh, 0)
  const safeRatio = (amount) => (total > 0 ? ((toNumber(amount, 0) / total) * 100).toFixed(1) : '0.0')

  return [
    {
      key: 'power_supply',
      name: '供电系统CAPEX',
      amount: toNumber(breakdown.power_supply_system_lakh, 0),
      ratio: safeRatio(breakdown.power_supply_system_lakh),
      color: '#16b8c4',
      shortDescription: '35kV 双路接入与高可靠配电架构',
      summary: '供电系统投资主要覆盖外部接入、电压等级、冗余配置和母线方案等建设成本。',
      details: [
        { label: '系统方案', value: powerPlan.value.scheme_name || '-' },
        { label: '外部电压', value: powerPlan.value.external_voltage || '-' },
        { label: '外部电源', value: powerPlan.value.external_source_type || '-' },
        { label: '冗余配置', value: powerPlan.value.redundancy_logic || '-' },
        { label: '母线类型', value: powerPlan.value.bus_type || '-' },
        { label: '单位成本', value: `${formatNumber(powerRaw.value.cost_per_mw, 2)} 万元/MW` }
      ]
    },
    {
      key: 'green_power',
      name: '绿电系统CAPEX',
      amount: toNumber(breakdown.green_power_system_lakh, 0),
      ratio: safeRatio(breakdown.green_power_system_lakh),
      color: '#18b26b',
      shortDescription: '风光储协同的绿电建设投入',
      summary: '绿电系统投资由风电、光伏与储能构成，对应当前方案的装机容量与消纳目标。',
      details: [
        { label: '风电CAPEX', value: `${formatNumber(breakdown.details?.wind_capex_lakh, 0)} 万元` },
        { label: '光伏CAPEX', value: `${formatNumber(breakdown.details?.pv_capex_lakh, 0)} 万元` },
        { label: '储能CAPEX', value: `${formatNumber(breakdown.details?.storage_capex_lakh, 0)} 万元` },
        { label: '风电装机容量', value: `${formatNumber(greenOptimization.value.wind_capacity_mw, 2)} MW` },
        { label: '光伏装机容量', value: `${formatNumber(greenOptimization.value.pv_capacity_mw, 2)} MW` },
        { label: '储能容量', value: `${formatNumber(greenOptimization.value.storage_capacity_mwh, 2)} MWh` }
      ]
    },
    {
      key: 'cooling',
      name: '制冷系统CAPEX',
      amount: toNumber(breakdown.cooling_system_lakh, 0),
      ratio: safeRatio(breakdown.cooling_system_lakh),
      color: '#d99a27',
      shortDescription: '制冷工艺与效率优化投入',
      summary: '制冷系统投资来自当前推荐制冷技术方案的建设成本，并纳入项目总投资统一核算。',
      details: [
        { label: '推荐技术', value: coolingResult.value.cooling_technology || '-' },
        { label: '初始投资', value: `${formatNumber(coolingEconomics.value.initial_investment, 0)} 万元` },
        { label: '年运维成本', value: `${formatNumber(coolingEconomics.value.annual_op_cost, 0)} 万元` },
        { label: '年电费', value: `${formatNumber(coolingEconomics.value.annual_electricity_cost, 0)} 万元` },
        { label: 'LCOE', value: `${formatNumber(coolingEconomics.value.lcoe, 4)} 元/kWh` },
        { label: '预测PUE', value: formatNumber(coolingResult.value.estimated_pue, 3) }
      ]
    }
  ]
})

const activeCostSegment = computed(() => {
  return costStructureSegments.value.find(segment => segment.key === activeCostDetailKey.value) || costStructureSegments.value[0] || {
    key: '',
    name: '--',
    amount: 0,
    ratio: '0.0',
    color: '#18b26b',
    summary: '',
    details: []
  }
})

const overviewMetrics = computed(() => [
  { label: '推荐制冷技术', value: coolingResult.value.cooling_technology || '-', highlight: false },
  { label: '预测PUE', value: formatNumber(coolingResult.value.estimated_pue, 3), highlight: true },
  { label: '预测WUE', value: `${formatNumber(coolingResult.value.predicted_wue, 3)}`, unit: 'L/kWh', highlight: false },
  { label: '绿电消纳率', value: formatPercent(keyMetrics.value.green_power_ratio), highlight: true },
  { label: '总初始投资', value: formatNumber(costResult.value.total_capex_lakh || keyMetrics.value.total_cost, 2), unit: '万元', highlight: false },
  { label: '综合评分', value: formatPercent(overallScores.value.overall), highlight: false }
])

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

const renderInlineMarkdown = (text) => {
  const escaped = escapeHtml(text)
  return escaped
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^\*])\*([^*]+)\*(?!\*)/g, '$1<em>$2</em>')
}

const isMarkdownTableSeparator = (line) => {
  const normalized = line.replace(/\|/g, '').replace(/\s+/g, '')
  return normalized.length > 0 && /^(:?-{3,}:?)+$/.test(normalized)
}

const splitMarkdownTableRow = (line) => {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map(cell => renderInlineMarkdown(cell.trim()))
}

const markdownToHtml = (md) => {
  if (!md) return '<p>暂无报告内容</p>'
  const lines = String(md).split('\n')
  const html = []
  let i = 0

  const closeListIfNeeded = (state) => {
    if (state === 'ul') html.push('</ul>')
    if (state === 'ol') html.push('</ol>')
  }

  let listState = null

  while (i < lines.length) {
    const rawLine = lines[i]
    const line = rawLine.trim()
    const nextLine = lines[i + 1]?.trim() || ''

    if (!line) {
      closeListIfNeeded(listState)
      listState = null
      i += 1
      continue
    }

    if (line.includes('|') && nextLine.includes('|') && isMarkdownTableSeparator(nextLine)) {
      closeListIfNeeded(listState)
      listState = null

      const headers = splitMarkdownTableRow(line)
      const rows = []
      i += 2
      while (i < lines.length && lines[i].trim().includes('|')) {
        rows.push(splitMarkdownTableRow(lines[i]))
        i += 1
      }

      html.push('<div class="markdown-table-wrap"><table><thead><tr>')
      headers.forEach(header => html.push(`<th>${header}</th>`))
      html.push('</tr></thead><tbody>')
      rows.forEach((row) => {
        html.push('<tr>')
        row.forEach(cell => html.push(`<td>${cell}</td>`))
        html.push('</tr>')
      })
      html.push('</tbody></table></div>')
      continue
    }

    if (line.startsWith('### ')) {
      closeListIfNeeded(listState)
      listState = null
      html.push(`<h3>${renderInlineMarkdown(line.slice(4))}</h3>`)
      i += 1
      continue
    }

    if (line.startsWith('## ')) {
      closeListIfNeeded(listState)
      listState = null
      html.push(`<h2>${renderInlineMarkdown(line.slice(3))}</h2>`)
      i += 1
      continue
    }

    if (line.startsWith('# ')) {
      closeListIfNeeded(listState)
      listState = null
      html.push(`<h1>${renderInlineMarkdown(line.slice(2))}</h1>`)
      i += 1
      continue
    }

    if (/^[-*]\s+/.test(line)) {
      if (listState !== 'ul') {
        closeListIfNeeded(listState)
        html.push('<ul>')
        listState = 'ul'
      }
      html.push(`<li>${renderInlineMarkdown(line.replace(/^[-*]\s+/, ''))}</li>`)
      i += 1
      continue
    }

    if (/^\d+\.\s+/.test(line)) {
      if (listState !== 'ol') {
        closeListIfNeeded(listState)
        html.push('<ol>')
        listState = 'ol'
      }
      html.push(`<li>${renderInlineMarkdown(line.replace(/^\d+\.\s+/, ''))}</li>`)
      i += 1
      continue
    }

    closeListIfNeeded(listState)
    listState = null
    html.push(`<p>${renderInlineMarkdown(line)}</p>`)
    i += 1
  }

  closeListIfNeeded(listState)
  return html.join('\n')
}

const reportHtml = computed(() => markdownToHtml(filteredMarkdown.value))

const getExpertColor = (type) => {
  if (type?.includes('economic')) return 'linear-gradient(135deg, #10B981 0%, #059669 100%)'
  if (type?.includes('reliability')) return 'linear-gradient(135deg, #059669 0%, #10B981 100%)'
  return 'linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)'
}

const openCostDetail = (segmentKey) => {
  activeCostDetailKey.value = segmentKey
  costDetailDialogVisible.value = true
}

const loadSolutionData = async () => {
  try {
    const { data } = await solutionApi.getById(solutionId.value)
    solutionData.value = data || {}
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
    series: [{ type: 'line', data: points.map(p => p.y), smooth: true, areaStyle: {}, color: '#10B981' }]
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
      data: source.map(item => ({ name: item.type, value: toNumber(item.ratio, 0) })),
      color: ['#10B981', '#34D399', '#06B6D4']
    }]
  })
  charts.powerBalance = chart
}

const initCostChart = () => {
  if (!costChartRef.value) return
  if (charts.cost) charts.cost.dispose()
  const chart = echarts.init(costChartRef.value)
  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 24, 18, 0.94)',
      borderColor: 'rgba(24, 178, 107, 0.24)',
      textStyle: { color: '#eefaf3' },
      formatter: (params) => {
        const segment = costStructureSegments.value.find(item => item.name === params.name)
        if (!segment) return params.name
        return [
          `<div style="font-weight:600;margin-bottom:6px;">${segment.name}</div>`,
          `<div style="color:rgba(238,250,243,0.72);margin-bottom:4px;">${segment.shortDescription}</div>`,
          `<div>金额：${formatNumber(segment.amount, 0)} 万元</div>`,
          `<div>占比：${segment.ratio}%</div>`
        ].join('')
      }
    },
    series: [{
      type: 'pie',
      radius: ['54%', '74%'],
      center: ['50%', '48%'],
      padAngle: 1.2,
      minAngle: 12,
      avoidLabelOverlap: true,
      selectedOffset: 6,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#f4fbf7',
        borderWidth: 4
      },
      label: {
        color: '#17201c',
        formatter: ({ name, value }) => `${name}\n${value} 万元`,
        fontSize: 12,
        lineHeight: 18
      },
      labelLine: {
        length: 14,
        length2: 10,
        lineStyle: {
          color: 'rgba(80, 97, 90, 0.36)'
        }
      },
      emphasis: {
        scale: true,
        scaleSize: 5
      },
      data: costStructureSegments.value.map(segment => ({
        name: segment.name,
        value: segment.amount,
        itemStyle: { color: segment.color }
      }))
    }],
    graphic: [
      {
        type: 'group',
        left: 'center',
        top: '40%',
        children: [
          {
            type: 'text',
            style: {
              text: '项目总投资',
              fill: '#50615a',
              fontSize: 12,
              fontWeight: 500,
              textAlign: 'center'
            },
            left: 'center'
          },
          {
            type: 'text',
            top: 20,
            style: {
              text: `${formatNumber(costResult.value.total_capex_lakh, 0)} 万元`,
              fill: '#17201c',
              fontSize: 22,
              fontWeight: 700,
              textAlign: 'center'
            },
            left: 'center'
          },
          {
            type: 'text',
            top: 50,
            style: {
              text: '点击查看成本细节',
              fill: '#7a8d85',
              fontSize: 12,
              textAlign: 'center'
            },
            left: 'center'
          }
        ]
      }
    ]
  })
  chart.off('click')
  chart.on('click', (params) => {
    const segment = costStructureSegments.value.find(item => item.name === params.name)
    if (segment) openCostDetail(segment.key)
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
  gap: 20px;
  min-height: calc(100% - 20px);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 22px 24px;
  margin-bottom: 0;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 22px;
  box-shadow: var(--shadow-sm);
}

.detail-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-tabs {
  flex: 1;
  overflow: hidden;
  background: transparent;
}

.detail-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 18px;
  padding: 8px 14px 0;
  box-shadow: var(--shadow-sm);
}

.detail-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.detail-tabs :deep(.el-tabs__item) {
  font-weight: 600;
  height: 42px;
  color: var(--text-secondary);
}

.detail-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary-dark);
}

.detail-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--primary-color);
}

.detail-tabs :deep(.el-tab-pane) {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.overview-section,
.cooling-section,
.green-section,
.power-section,
.economic-section,
.reliability-section,
.environment-section,
.experts-section,
.report-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 0;
}

.metric-card {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border-radius: 18px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all var(--transition-normal);
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
}

.metric-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.metric-value.highlight {
  color: var(--primary-dark);
}

.metric-unit {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-placeholder);
  margin-top: 4px;
}

.summary-section {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 0;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.summary-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.summary-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 16px;
}

.budget-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 14px;
  margin-bottom: 12px;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.budget-status.success {
  background: var(--success-bg);
  color: var(--success-color);
  border-color: color-mix(in oklab, var(--success-color) 22%, transparent);
}

.budget-status.fail {
  background: var(--danger-bg);
  color: var(--danger-color);
  border-color: color-mix(in oklab, var(--danger-color) 22%, transparent);
}

.risk-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--warning-bg);
  color: var(--warning-color);
  border-radius: 14px;
  border: 1px solid color-mix(in oklab, var(--warning-color) 24%, transparent);
}

.expert-recommendations {
  margin-top: 16px;
}

.expert-recommendations h5 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.expert-recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.expert-recommendations li {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.7;
}

.info-section {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.info-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.info-item {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.param-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 0;
}

.param-card {
  flex: 1;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  border: 1px solid var(--border-light);
}

.param-card h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.param-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-item {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.system-trace-shell {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 100%);
}

.system-trace-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid color-mix(in oklab, var(--border-light) 88%, var(--primary-color) 12%);
}

.system-trace-header h4 {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.system-trace-header p {
  max-width: 58ch;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.system-trace-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  color: var(--primary-dark);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.system-trace-topology {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trace-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid color-mix(in oklab, var(--border-light) 90%, var(--primary-color) 10%);
  background: color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%);
}

.trace-block-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.trace-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-content: flex-start;
}

.trace-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 9px;
  border-radius: 999px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  font-size: 11px;
  line-height: 1.45;
  color: var(--text-secondary);
}

.trace-fact-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.trace-fact-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-height: 64px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.trace-fact-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.trace-fact-value {
  font-size: 12px;
  line-height: 1.55;
  font-weight: 600;
  color: var(--text-primary);
}

.trace-step-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trace-step-item {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  align-items: flex-start;
}

.trace-step-index {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: color-mix(in oklab, var(--primary-color) 12%, var(--bg-card));
  color: var(--primary-dark);
  font-size: 12px;
  font-weight: 700;
}

.trace-step-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 1px;
}

.trace-step-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.trace-step-desc {
  font-size: 11px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.trace-weight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  gap: 8px;
}

.trace-weight-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-height: 62px;
  padding: 9px 11px;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.trace-weight-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.trace-weight-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.trace-ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trace-ranking-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.trace-ranking-item.is-winner {
  border-color: color-mix(in oklab, var(--primary-color) 24%, var(--border-default));
  background: color-mix(in oklab, var(--primary-color) 8%, var(--bg-card));
}

.trace-ranking-head {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 8px;
  align-items: baseline;
}

.trace-ranking-order {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.trace-ranking-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
}

.trace-ranking-score {
  font-size: 11px;
  color: var(--text-secondary);
}

.trace-ranking-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.trace-ranking-tag {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 7px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
  font-size: 11px;
  color: var(--text-secondary);
}

.trace-evidence-list {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.trace-evidence-list li {
  font-size: 11px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.green-section :deep(.el-card),
.power-section :deep(.el-card),
.economic-section :deep(.el-card),
.reliability-section :deep(.el-card),
.environment-section :deep(.el-card),
.experts-section :deep(.el-card) {
  border-radius: 18px;
}

.table-card, .chart-card, .economic-metrics-card {
  margin-bottom: 0;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  border: 1px solid var(--border-light);
}

.chart-container {
  height: 300px;
  width: 100%;
  min-height: 300px;
}

.economic-cost-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.86fr);
  gap: 18px;
}

.economic-cost-main,
.economic-cost-summary {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 20px;
}

.economic-cost-main {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.economic-cost-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.economic-cost-header h4 {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.economic-cost-header p {
  margin-top: 6px;
  max-width: 60ch;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.economic-chart-shell {
  min-height: 340px;
}

.economic-cost-chart {
  width: 100%;
  height: 340px;
}

.economic-chart-note {
  padding: 12px 14px;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border: 1px solid var(--border-light);
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.economic-cost-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.economic-cost-item {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  text-align: left;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  transition: background var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
}

.economic-cost-item:hover {
  background: color-mix(in oklab, var(--primary-color) 6%, var(--bg-card));
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
  transform: translateY(-1px);
}

.economic-cost-item:focus-visible {
  outline: 2px solid color-mix(in oklab, var(--primary-color) 72%, white);
  outline-offset: 2px;
}

.economic-cost-dot,
.economic-summary-dot,
.economic-detail-dot {
  border-radius: 50%;
}

.economic-cost-dot {
  width: 12px;
  height: 12px;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.6);
}

.economic-cost-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.economic-cost-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.economic-cost-desc {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.economic-cost-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.economic-cost-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.economic-cost-ratio {
  font-size: 12px;
  color: var(--text-placeholder);
}

.economic-cost-summary {
  display: flex;
  flex-direction: column;
}

.economic-kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.economic-kpi-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 108px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.economic-kpi-card.strong {
  grid-column: 1 / -1;
  justify-content: center;
  min-height: 124px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 10%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.economic-kpi-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.economic-kpi-value {
  font-size: 24px;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text-primary);
}

.economic-kpi-value.success {
  color: var(--success-color);
}

.economic-kpi-value.danger {
  color: var(--danger-color);
}

.economic-kpi-note {
  font-size: 12px;
  color: var(--text-placeholder);
}

.economic-summary-heading {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 10px;
  padding: 0 4px;
}

.economic-summary-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.economic-summary-note {
  font-size: 12px;
  color: var(--text-placeholder);
}

.economic-summary-strip {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.economic-summary-row {
  display: grid;
  grid-template-columns: 10px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.economic-summary-dot {
  width: 10px;
  height: 10px;
}

.economic-summary-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.economic-summary-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.economic-cost-dialog :deep(.el-dialog) {
  border-radius: 22px;
}

.economic-detail-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.economic-detail-dot {
  width: 14px;
  height: 14px;
  margin-top: 4px;
}

.economic-detail-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.economic-detail-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.economic-detail-subtitle {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.economic-detail-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.economic-detail-kpis {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.economic-detail-kpi {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.economic-detail-kpi-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.economic-detail-kpi-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.economic-detail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.economic-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.economic-detail-row-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.economic-detail-row-value {
  font-size: 13px;
  line-height: 1.65;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

.architecture-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  border: 1px solid var(--border-light);
}

.arch-item {
  padding: 12px 24px;
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: rgba(249, 253, 250, 0.98);
  border-radius: 14px;
  font-weight: 500;
  box-shadow: 0 12px 24px color-mix(in oklab, var(--primary-color) 22%, transparent);
}

.arch-arrow {
  color: var(--text-placeholder);
  font-size: 18px;
}

.availability-stats, .reliability-stats, .carbon-stats {
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 1;
  padding: 16px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 100%);
  border-radius: 16px;
  border: 1px solid var(--border-light);
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.report-section {
  min-height: calc(100vh - 240px);
  display: flex;
  flex-direction: column;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 18px 20px;
  margin-bottom: 0;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 18px;
  box-shadow: var(--shadow-sm);
}

.report-content {
  flex: 1;
  overflow-y: auto;
  padding: 22px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%) 0%, color-mix(in oklab, var(--bg-panel) 97%, var(--primary-color) 3%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
}

.report-title-section {
  text-align: center;
  padding: 24px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 24%, var(--border-default));
  margin-bottom: 24px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, transparent 100%);
  border-radius: 18px;
}

.report-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.report-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  font-size: 13px;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.report-executive-summary {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--border-light);
}

.report-executive-summary h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.executive-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.executive-item {
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  padding: 16px;
  border-radius: 14px;
  text-align: center;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.executive-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.executive-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.executive-value.highlight {
  color: var(--primary-dark);
}

.report-chapter {
  margin-bottom: 24px;
}

.report-chapter h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 20%, var(--border-default));
}

.report-section-item {
  margin-bottom: 16px;
}

.report-section-item p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.expert-opinions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.expert-opinion-card {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  padding: 20px;
  border: 1px solid var(--border-light);
}

.expert-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.expert-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.expert-info {
  flex: 1;
}

.expert-name {
  font-weight: 600;
  color: var(--text-primary);
}

.expert-type {
  font-size: 12px;
  color: var(--text-secondary);
}

.expert-summary {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.6;
}

.expert-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.debate-history {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.debate-round {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  padding: 16px;
  border: 1px solid var(--border-light);
}

.round-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-dark);
  margin-bottom: 12px;
}

.debate-message {
  margin-bottom: 10px;
}

.debate-message .speaker {
  font-weight: 600;
  color: var(--text-primary);
  margin-right: 8px;
}

.debate-message .content {
  color: var(--text-secondary);
}

.arbitration-result {
  padding: 20px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 10%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  border: 1px solid var(--border-light);
}

.consensus-score {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-dark);
  margin-bottom: 12px;
}

.arbitration-summary {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.markdown-rendered {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
}

.markdown-rendered :deep(h1),
.markdown-rendered :deep(h2),
.markdown-rendered :deep(h3) {
  color: var(--text-primary);
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

.markdown-rendered :deep(ul),
.markdown-rendered :deep(ol) {
  margin: 8px 0 8px 20px;
}

.markdown-rendered :deep(strong) {
  color: var(--text-primary);
  font-weight: 700;
}

.markdown-rendered :deep(code) {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 8px;
  background: color-mix(in oklab, var(--bg-card) 88%, var(--primary-color) 12%);
  color: var(--primary-ink);
  font-size: 0.92em;
}

.markdown-rendered :deep(a) {
  color: var(--primary-dark);
  text-decoration: none;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 28%, transparent);
}

.markdown-rendered :deep(a:hover) {
  color: var(--primary-color);
}

.markdown-rendered :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  overflow: hidden;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border: 1px solid var(--border-light);
}

.markdown-rendered :deep(th),
.markdown-rendered :deep(td) {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}

.markdown-rendered :deep(th) {
  color: var(--text-primary);
  font-weight: 700;
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
}

.markdown-rendered :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-rendered :deep(.markdown-table-wrap) {
  overflow-x: auto;
}

.report-section-item ul {
  margin: 0;
  padding-left: 20px;
}

.report-section-item li {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.report-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-secondary);
}

@media (max-width: 992px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .executive-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .param-cards {
    flex-direction: column;
  }

  .system-trace-topology {
    grid-template-columns: 1fr;
  }

  .economic-cost-panel {
    grid-template-columns: 1fr;
  }
  
  .availability-stats, .reliability-stats, .carbon-stats {
    flex-direction: column;
  }
  
  .architecture-diagram {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .detail-header,
  .report-header,
  .report-content,
  .summary-section,
  .info-section {
    padding: 16px;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .executive-grid {
    grid-template-columns: 1fr;
  }

  .system-trace-shell {
    padding: 16px;
  }

  .system-trace-header,
  .economic-cost-header,
  .economic-summary-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .trace-fact-grid,
  .trace-weight-grid,
  .economic-kpi-grid,
  .economic-detail-kpis {
    grid-template-columns: 1fr;
  }

  .economic-cost-header,
  .economic-summary-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .economic-kpi-grid,
  .economic-detail-kpis {
    grid-template-columns: 1fr;
  }

  .economic-kpi-card.strong {
    grid-column: auto;
    min-height: 108px;
  }

  .economic-cost-chart {
    height: 280px;
  }

  .economic-cost-item,
  .economic-summary-row {
    grid-template-columns: 12px 1fr;
  }

  .economic-cost-meta,
  .economic-detail-row-value {
    align-items: flex-start;
    text-align: left;
  }

  .report-header {
    flex-direction: column;
    align-items: stretch;
  }

  .detail-tabs :deep(.el-tabs__header) {
    padding-left: 12px;
    padding-right: 12px;
  }
}
</style>
