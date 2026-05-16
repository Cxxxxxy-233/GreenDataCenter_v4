<template>
  <div class="detail-page">
    <div class="detail-header">
      <h1>方案详情</h1>
      <div class="header-actions">
        <div class="header-actions-meta">
          <span class="header-actions-kicker">Deliverables</span>
          <span class="header-actions-note">Markdown / PDF</span>
        </div>
        <div class="header-action-buttons">
          <el-button class="header-action-btn" @click="exportMarkdown">&#23548;&#20986;Markdown&#25253;&#21578;</el-button>
          <el-button class="header-action-btn header-action-btn--primary" type="primary" plain @click="exportPdf">&#23548;&#20986;PDF&#25253;&#21578;</el-button>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="detail-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="方案概览" name="overview">
        <div class="overview-section">
          <div class="overview-hero">
            <div class="overview-hero-head">
              <div class="overview-hero-copy">
                <span class="overview-kicker">Final Recommended Scheme</span>
                <h2>{{ finalReportData.name || solutionData.name || '数据中心绿电消纳推荐方案' }}</h2>
                <p class="overview-hero-summary">{{ arbitrator.summary || '暂无后端仲裁摘要' }}</p>
              </div>
              <div class="overview-hero-badge">
                <span class="overview-hero-badge-label">修订条目</span>
                <strong>{{ revisionComparison.changeCount }}</strong>
                <span class="overview-hero-badge-note">仲裁后参数调整</span>
              </div>
            </div>

            <div class="metrics-grid">
              <div class="metric-card" v-for="(metric, index) in overviewMetrics" :key="index" :style="{ animationDelay: `${index * 100}ms` }">
                <div class="metric-label">{{ metric.label }}</div>
                <div class="metric-value" :class="{ highlight: metric.highlight }">{{ metric.value }}</div>
                <div v-if="metric.unit" class="metric-unit">{{ metric.unit }}</div>
              </div>
            </div>
          </div>

          <div class="summary-section">
            <div class="summary-section-head">
              <h3>执行判断</h3>
              <span class="summary-section-tag">方案已完成仲裁</span>
            </div>
            <div class="budget-status" :class="costResult.is_over_budget ? 'fail' : 'success'">
              <el-icon><CircleCheckFilled /></el-icon>
              <span v-if="costResult.is_over_budget">当前方案超预算 {{ formatNumber(Math.abs(costResult.budget_delta_lakh), 2) }} 万元</span>
              <span v-else-if="toNumber(costResult.budget_delta_lakh, 0) === 0">预算校验通过，当前方案与预算上限持平</span>
              <span v-else>预算校验通过，预算结余 {{ formatNumber(costResult.budget_delta_lakh, 2) }} 万元</span>
            </div>
            <div v-if="revisionComparison.changes.length" class="revision-overview">
              <h5>初稿与仲裁修订</h5>
              <div class="revision-overview-grid">
                <div class="revision-overview-column revision-overview-column--draft">
                  <div class="revision-overview-title">初稿方案</div>
                  <div class="revision-overview-list">
                    <div v-for="(change, index) in revisionComparison.changes" :key="`overview-draft-${index}`" class="revision-overview-item">
                      <span>{{ change.label }}</span>
                      <strong>{{ change.before }}</strong>
                    </div>
                  </div>
                </div>
                <div class="revision-overview-column revision-overview-column--revised">
                  <div class="revision-overview-title">修订后方案</div>
                  <div class="revision-overview-list">
                    <div v-for="(change, index) in revisionComparison.changes" :key="`overview-revised-${index}`" class="revision-overview-item">
                      <span>{{ change.label }}</span>
                      <strong>{{ change.after }}</strong>
                    </div>
                  </div>
                </div>
              </div>
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
            <div class="info-section-head">
              <h3>方案信息</h3>
              <span class="info-section-note">用于项目归档与报告导出</span>
            </div>
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
                <div class="info-item">报告路径</div>
                <div class="info-value">{{ finalReportPath || '-' }}</div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="制冷系统详情" name="cooling">
        <div class="cooling-section detail-workbench">
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

        </div>
      </el-tab-pane>

      <el-tab-pane label="绿电系统详情" name="green">
        <div class="green-section detail-workbench">
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

          <div class="green-insight-grid">
          <el-card class="green-summary-card">
            <h4>风光储容量配置表</h4>
            <el-table :data="greenConfig" border>
              <el-table-column prop="type" label="类型" />
              <el-table-column prop="capacity" label="容量" />
              <el-table-column prop="ratio" label="占比(%)" />
            </el-table>
          </el-card>
          <el-card class="green-chart-card">
            <h4>绿电占比分布图</h4>
            <div ref="powerBalanceChartRef" class="chart-container"></div>
          </el-card>
          </div>
          <el-card class="artifact-card-panel">
            <div class="artifact-panel-header">
              <div>
                <h4>后端产物文件</h4>
                <p>直接展示后端绿电工具生成的平衡图和资源曲线文件，不再只显示本地路径。</p>
              </div>
            </div>

            <div v-if="greenArtifactFiles.length" class="artifact-list">
              <section v-for="artifact in greenArtifactFiles" :key="artifact.key" class="artifact-item">
                <div class="artifact-item-header">
                  <div class="artifact-item-copy">
                    <div class="artifact-item-title">{{ artifact.label }}</div>
                    <div class="artifact-item-desc">{{ artifact.description }}</div>
                  </div>
                  <div class="artifact-item-actions">
                    <a :href="artifact.url" target="_blank" rel="noopener noreferrer">打开原文件</a>
                    <a :href="artifact.downloadUrl" target="_blank" rel="noopener noreferrer">下载</a>
                  </div>
                </div>

                <div class="artifact-item-meta">{{ artifact.fileName }}</div>
                <div class="artifact-item-path">{{ artifact.path }}</div>

                <div v-if="artifact.kind === 'image'" class="artifact-image-shell">
                  <img :src="artifact.url" :alt="artifact.label" class="artifact-image" />
                </div>

                <div v-else class="artifact-placeholder">该文件仅保留“打开原文件”和“下载”入口，不再展示具体数据内容。</div>
              </section>
            </div>

            <div v-else class="artifact-placeholder">后端当前未返回绿电系统产物文件。</div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="供电系统详情" name="power">
        <div class="power-section detail-workbench">
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

          <el-card class="power-architecture-card">
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
          <el-card class="power-kpi-card">
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
        <div class="economic-section detail-workbench detail-workbench--economic">
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
              <div class="economic-summary-shell">
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
              <div class="stat-card">可用性：{{ formatPercentAuto(reliabilityOpinion.metrics?.expected_availability ?? keyMetrics.expected_availability) }}</div>
              <div class="stat-card">Tier等级：{{ keyMetrics.tier_level || powerRaw.machine_room_grade || '-' }}</div>
              <div class="stat-card">仲裁修订项：{{ revisionComparison.changeCount }}</div>
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
              <div class="stat-card">修订说明数：{{ revisionComparison.revisionNotes.length }}</div>
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
              <div class="consensus-score">修订条目：{{ revisionComparison.changeCount }}</div>
              <div class="arbitration-summary">{{ arbitrator.summary || '-' }}</div>
              <div v-if="revisionComparison.changes.length" class="arbitration-revision-list">
                <div v-for="(change, index) in revisionComparison.changes" :key="index" class="arbitration-revision-item">
                  <div class="arbitration-revision-head">
                    <strong>{{ change.label }}</strong>
                    <span>{{ change.before }} → {{ change.after }}</span>
                  </div>
                  <div class="arbitration-revision-reason">{{ change.reason }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="完整方案报告" name="report">
        <div class="report-section detail-workbench detail-workbench--report">
          <div class="report-header">
            <div class="report-header-copy">
              <span class="report-header-kicker">Solution Report</span>
              <h3>完整方案报告</h3>
            </div>
            <div class="report-header-tools">
              <el-input v-model="searchKeyword" placeholder="搜索报告内容" />
            </div>
          </div>
          <div class="report-preview-shell">
          <div ref="reportExportRef" class="report-content">
            <div class="report-title-section">
              <span class="report-cover-kicker">Project Deliverable</span>
              <div class="report-cover-grid">
                <div class="report-cover-main">
                  <h1 class="report-title">{{ finalReportData.name || '数据中心绿电消纳方案报告' }}</h1>
                  <div class="report-meta">
                    <span>方案编号：{{ solutionId }}</span>
                    <span>生成时间：{{ solutionData.created_at || '-' }}</span>
                  </div>
                  <div class="report-decision-banner" :class="reportDecision.toneClass">
                    <div class="report-decision-copy">
                      <span class="report-decision-label">建议结论</span>
                      <strong>{{ reportDecision.label }}</strong>
                      <p>{{ reportDecision.description }}</p>
                    </div>
                    <div class="report-decision-meta">
                          <span>修订条目 {{ revisionComparison.changeCount }}</span>
                    </div>
                  </div>
                </div>
                    <div class="report-cover-score">
                      <span class="report-cover-score-label">Revision Notes</span>
                      <strong>{{ revisionComparison.revisionNotes.length }}</strong>
                      <small>Multi-agent arbitration</small>
                </div>
              </div>
            </div>
            <div v-if="reportPrimaryFacts.length || reportSecondaryFacts.length" class="report-input-summary">
              <div class="report-chapter-head">
                <h2>项目关键输入</h2>
              </div>
              <div v-if="reportPrimaryFacts.length" class="report-input-primary">
                <div
                  v-for="fact in reportPrimaryFacts"
                  :key="fact.label"
                  class="report-input-item report-input-item--primary"
                >
                  <div class="report-input-label">{{ fact.label }}</div>
                  <div class="report-input-value">{{ fact.value }}</div>
                </div>
              </div>
              <div v-if="reportSecondaryFacts.length" class="report-input-grid">
                <div
                  v-for="fact in reportSecondaryFacts"
                  :key="fact.label"
                  class="report-input-item"
                >
                  <div class="report-input-label">{{ fact.label }}</div>
                  <div class="report-input-value">{{ fact.value }}</div>
                </div>
              </div>
            </div>
            <div class="report-executive-summary">
              <div class="report-executive-layout">
                <div class="report-executive-main">
                  <h2>执行摘要</h2>
                  <p class="summary-text">{{ reportSummaryLead }}</p>
                  <ul v-if="reportSummaryPoints.length" class="report-summary-points">
                    <li v-for="point in reportSummaryPoints" :key="point">{{ point }}</li>
                  </ul>
                </div>
                <div class="report-executive-side">
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
              </div>
            </div>
            <div class="report-chapter report-chapter--document">
              <div class="report-chapter-head">
                <h2>顾问报告正文</h2>
              </div>
              <div class="report-section-item report-section-item--document">
                <div class="markdown-rendered markdown-rendered--document" v-html="reportDocumentHtml"></div>
              </div>
            </div>
            <div class="report-chapter">
              <h2>仲裁修订</h2>
              <div class="report-section-item">
                <div class="executive-grid">
                  <div class="executive-item">
                    <div class="executive-label">修订条目</div>
                    <div class="executive-value">{{ revisionComparison.changeCount }}</div>
                  </div>
                  <div class="executive-item">
                    <div class="executive-label">修订说明</div>
                    <div class="executive-value">{{ revisionComparison.revisionNotes.length }}</div>
                  </div>
                  <div class="executive-item">
                    <div class="executive-label">方案状态</div>
                    <div class="executive-value">已完成仲裁</div>
                  </div>
                  <div class="executive-item">
                    <div class="executive-label">仲裁摘要</div>
                    <div class="executive-value">{{ arbitrator.summary ? '已生成' : '暂无' }}</div>
                  </div>
                </div>
                <div v-if="revisionComparison.changes.length" class="revision-report-list">
                  <div v-for="(change, index) in revisionComparison.changes" :key="index" class="revision-report-item">
                    <div class="revision-report-head">
                      <strong>{{ change.label }}</strong>
                      <span>{{ change.before }} → {{ change.after }}</span>
                    </div>
                    <div class="revision-report-reason">{{ change.reason }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="report-chapter">
              <h2>关键指标</h2>
              <div class="report-section-item report-section-item--table">
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
                <el-table v-if="economicRows.length" :data="economicRows" border class="report-data-table">
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
                <el-table v-if="powerRows.length" :data="powerRows" border class="report-data-table">
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
                <el-table v-if="environmentalRows.length" :data="environmentalRows" border class="report-data-table">
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
            <details v-if="reportMarkdown" class="report-appendix">
              <summary>附录：查看 Markdown 渲染内容</summary>
              <div class="report-section-item report-section-item--appendix">
                <div class="markdown-rendered" v-html="reportHtml"></div>
              </div>
            </details>
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
import { computed, ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { solutionApi, artifactApi } from '@/api'

const route = useRoute()
const activeTab = ref('overview')
const searchKeyword = ref('')
const solutionId = ref(route.params.id || '')
const solutionData = ref({})
const reportMarkdown = ref('')
const reportExportRef = ref(null)
const powerBalanceChartRef = ref(null)
const costChartRef = ref(null)
const costDetailDialogVisible = ref(false)
const activeCostDetailKey = ref('green_power')
let charts = { powerBalance: null, cost: null }

const loadSavedProjectConfig = () => {
  try {
    const saved = localStorage.getItem('projectConfig')
    return saved ? JSON.parse(saved) : {}
  } catch (error) {
    console.error('读取本地项目配置失败:', error)
    return {}
  }
}

const normalizeRequirementFields = (raw = {}) => {
  const normalized = { ...raw }
  const ratio = Number(normalized.green_power_ratio)
  if (Number.isFinite(ratio) && ratio > 1) {
    normalized.green_power_ratio = ratio / 100
  }
  const directRatio = Number(normalized.direct_connection_ratio)
  if (Number.isFinite(directRatio) && directRatio > 1) {
    normalized.direct_connection_ratio = directRatio / 100
  }
  return normalized
}

const savedProjectConfig = ref(normalizeRequirementFields(loadSavedProjectConfig()))

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

const formatPercentAuto = (v, digits = 1) => {
  if (v === null || v === undefined || v === '') return '-'
  const n = Number(v)
  if (!Number.isFinite(n)) return '-'
  return `${(n > 1 ? n : n * 100).toFixed(digits)}%`
}

const sanitizeProcurementMethodLabel = (value) => {
  const label = String(value || '').trim()
  if (!label) return '-'
  if (label.includes('缁跨數浜ゆ槗') && label.includes('缁胯瘉琛ヨ冻')) return '绿电交易+绿证补足'
  if (label.includes('缁跨數浜ゆ槗')) return '绿电交易'
  if (label.includes('缁胯瘉琛ヨ冻')) return '绿证补足'
  return label
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

const detectArtifactKind = (path = '') => {
  const ext = String(path).split('.').pop()?.toLowerCase() || ''
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext)) return 'image'
  if (ext === 'csv') return 'csv'
  if (['txt', 'md', 'log', 'json'].includes(ext)) return 'text'
  return 'binary'
}

const getArtifactFileName = (path = '') => {
  const normalized = String(path || '').split(/[\\/]/)
  return normalized[normalized.length - 1] || '-'
}

const isNonEmptyObject = (value) => {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length > 0
}

const pickFirstFiniteNumber = (...values) => {
  for (const value of values) {
    const n = Number(value)
    if (Number.isFinite(n)) return n
  }
  return null
}

const normalizeGreenPowerResult = (rawValue, metrics = {}) => {
  const source = isNonEmptyObject(rawValue?.green_power_result) ? rawValue.green_power_result : (rawValue || {})
  const isErrorResult = source.status === 'error'
  const baseOptimization = isNonEmptyObject(source.optimization) ? { ...source.optimization } : {}
  const derivedOptimization = !isErrorResult && isNonEmptyObject(source.derived_metrics) ? source.derived_metrics : {}
  const optimization = { ...derivedOptimization, ...baseOptimization }

  const fallbackFields = {
    wind_capacity_mw: isErrorResult ? null : pickFirstFiniteNumber(optimization.wind_capacity_mw, source.wind_capacity_mw, metrics.wind_capacity_mw),
    pv_capacity_mw: isErrorResult ? null : pickFirstFiniteNumber(optimization.pv_capacity_mw, source.pv_capacity_mw, metrics.pv_capacity_mw),
    storage_capacity_mwh: isErrorResult ? null : pickFirstFiniteNumber(optimization.storage_capacity_mwh, source.storage_capacity_mwh, metrics.storage_capacity_mwh),
    green_supply_ratio: pickFirstFiniteNumber(
      optimization.green_supply_ratio,
      optimization.achieved_green_ratio,
      source.green_supply_ratio,
      source.achieved_green_ratio,
      metrics.green_supply_ratio,
      metrics.achieved_green_ratio,
      metrics.green_power_ratio
    ),
    target_green_ratio: pickFirstFiniteNumber(
      optimization.target_green_ratio,
      source.target_green_ratio,
      metrics.target_green_ratio,
      metrics.green_power_ratio
    )
  }
  Object.entries(fallbackFields).forEach(([key, value]) => {
    if (value !== null) optimization[key] = value
  })

  const procurementPlan = isNonEmptyObject(source.procurement_plan) ? { ...source.procurement_plan } : {}
  const procurementFallback = {
    total_green_power_ratio: pickFirstFiniteNumber(procurementPlan.total_green_power_ratio, metrics.green_power_ratio),
    actual_direct_connection_ratio: pickFirstFiniteNumber(procurementPlan.actual_direct_connection_ratio, metrics.direct_connection_ratio),
    procured_green_ratio: pickFirstFiniteNumber(procurementPlan.procured_green_ratio, metrics.procured_green_ratio),
    annual_procurement_cost_lakh: pickFirstFiniteNumber(procurementPlan.annual_procurement_cost_lakh, metrics.annual_green_procurement_cost_lakh)
  }
  Object.entries(procurementFallback).forEach(([key, value]) => {
    if (value !== null) procurementPlan[key] = value
  })

  return {
    ...source,
    optimization,
    procurement_plan: procurementPlan
  }
}

const intermediate = computed(() => solutionData.value.intermediate_results || {})
const draftOutput = computed(() => intermediate.value.draft_plan_agent?.full_output || {})
const arbitrator = computed(() => intermediate.value.arbitrator?.full_output || solutionData.value || {})
const keyMetrics = computed(() => solutionData.value.key_metrics || arbitrator.value.key_metrics || {})
const finalReportPath = computed(() => intermediate.value.final_report?.full_output?.path || solutionData.value.final_report_path || '')

const revisionParameterLabels = {
  storage_capacity_mwh: '储能容量',
  storage_capacity: '储能容量',
  pv_capacity_mw: '光伏容量',
  wind_capacity_mw: '风电容量',
  green_power_ratio: '绿电比例',
  green_supply_ratio: '绿电供给比例',
  pue: 'PUE',
  estimated_pue: '预测PUE',
  predicted_wue: '预测WUE',
  cooling_technology: '制冷技术',
  cooling_initial_investment_lakh: '制冷初始投资',
  scheme_name: '供电方案',
  redundancy_logic: '冗余逻辑',
  distribution_transformers: '配电变压器配置',
  tier_level: 'Tier 等级',
  expected_availability: '预期可用性',
  annual_carbon_emission: '年碳排放',
  total_cost: '总投资',
  total_capex_lakh: '总投资',
  roi: '投资回报率',
  payback_period: '投资回收期'
}

const revisionValueFormatters = {
  storage_capacity_mwh: value => formatWithUnit(value, 'MWh', 2),
  storage_capacity: value => formatWithUnit(value, 'MWh', 2),
  pv_capacity_mw: value => formatWithUnit(value, 'MW', 2),
  wind_capacity_mw: value => formatWithUnit(value, 'MW', 2),
  green_power_ratio: value => formatPercentAuto(value, 0),
  green_supply_ratio: value => formatPercentAuto(value, 0),
  pue: value => formatNumber(value, 2),
  estimated_pue: value => formatNumber(value, 2),
  predicted_wue: value => formatNumber(value, 2),
  tier_level: value => (Number.isFinite(Number(value)) ? `Tier ${value}` : String(value ?? '--')),
  expected_availability: value => formatPercentAuto(value, 3),
  annual_carbon_emission: value => formatWithUnit(value, '吨', 0),
  total_cost: value => formatWithUnit(value, '万元', 2),
  total_capex_lakh: value => formatWithUnit(value, '万元', 2),
  cooling_initial_investment_lakh: value => formatWithUnit(value, '万元', 2),
  roi: value => formatPercentAuto(value, 1),
  payback_period: value => formatWithUnit(value, '年', 1)
}

const formatRevisionValue = (parameter, value) => {
  if (value === null || value === undefined || value === '') return '--'
  const formatter = revisionValueFormatters[parameter]
  if (formatter) return formatter(value)
  if (typeof value === 'number') return formatNumber(value, 2)
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const normalizeRevisionChanges = (changes = []) => {
  if (!Array.isArray(changes)) return []
  return changes
    .map((item) => {
      const parameter = String(item?.parameter || '').trim()
      if (!parameter) return null
      return {
        parameter,
        label: revisionParameterLabels[parameter] || parameter,
        before: formatRevisionValue(parameter, item?.before),
        after: formatRevisionValue(parameter, item?.after),
        reason: String(item?.reason || '').trim() || '仲裁专家根据评审意见进行了修订。'
      }
    })
    .filter(Boolean)
}

const normalizeRevisionDisplayItems = (items = []) => {
  if (!Array.isArray(items)) return []
  return items
    .map((item) => {
      const label = String(item?.label || '').trim()
      const change = String(item?.change || '').trim()
      if (!label || !change) return null
      const parts = change.split('→').map(part => part.trim()).filter(Boolean)
      return {
        label,
        change,
        before: parts[0] || '--',
        after: parts[1] || parts[0] || '--',
        reason: String(item?.reason || '').trim() || '仲裁专家根据评审意见进行了修订。'
      }
    })
    .filter(Boolean)
}

const revisionComparison = computed(() => {
  const revisedDraftPlan = arbitrator.value.revised_draft_plan && typeof arbitrator.value.revised_draft_plan === 'object'
    ? arbitrator.value.revised_draft_plan
    : {}
  const displayItems = normalizeRevisionDisplayItems(arbitrator.value.revision_display_items || [])
  const changes = displayItems.length ? displayItems : normalizeRevisionChanges(arbitrator.value.parameter_changes || [])
  const revisionNotes = Array.isArray(revisedDraftPlan.revision_notes)
    ? revisedDraftPlan.revision_notes.map(item => String(item || '').trim()).filter(Boolean)
    : []

  return {
    revisedDraftPlan,
    displayItems,
    changes,
    revisionNotes,
    changeCount: Number.isFinite(Number(arbitrator.value.revision_display_count)) && Number(arbitrator.value.revision_display_count) > 0
      ? Number(arbitrator.value.revision_display_count)
      : changes.length
  }
})

const economicSection = computed(() => solutionData.value.economic_section || arbitrator.value.economic_section || {})
const powerSection = computed(() => solutionData.value.power_reliability_section || arbitrator.value.power_reliability_section || {})
const environmentalSection = computed(() => solutionData.value.environmental_section || arbitrator.value.environmental_section || {})
const economicContent = computed(() => economicSection.value.content || {})
const powerContent = computed(() => powerSection.value.content || {})
const environmentalContent = computed(() => environmentalSection.value.content || {})
const requirement = computed(() => {
  const rawRequirement = intermediate.value.requirement_parser?.full_output || {}
  const normalized = rawRequirement.requirement && typeof rawRequirement.requirement === 'object'
    ? rawRequirement.requirement
    : rawRequirement
  return {
    ...normalizeRequirementFields(savedProjectConfig.value),
    ...normalized
  }
})

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
  const costBreakdown = intermediate.value.cost_calculation?.full_output?.economic_analysis_result?.capex_breakdown
    || intermediate.value.cost_calculation?.full_output?.capex_breakdown
    || {}
  return {
    initial_investment: draftEco.initial_investment ?? costBreakdown.cooling_system_lakh ?? null,
    annual_op_cost: draftEco.annual_op_cost ?? null,
    annual_electricity_cost: draftEco.annual_electricity_cost ?? null,
    lcoe: draftEco.lcoe ?? null
  }
})

const greenPowerResult = computed(() => normalizeGreenPowerResult(draftOutput.value.green_power_result || {}, keyMetrics.value))
const greenOptimization = computed(() => greenPowerResult.value.optimization || {})
const greenProcurementPlan = computed(() => greenPowerResult.value.procurement_plan || {})
const greenFiles = computed(() => greenPowerResult.value.generated_files || {})
const greenArtifactFiles = computed(() => {
  const files = greenFiles.value || {}
  return [
    {
      key: 'balance_plot',
      label: '功率平衡图',
      description: '差分进化容量优化完成后生成的风光储与负荷平衡图。',
      path: files.balance_plot || ''
    },
    {
      key: 'pv_csv',
      label: '光伏资源曲线 CSV',
      description: '光伏单位出力系数曲线文件，可直接查看后端生成结果。',
      path: files.pv_csv || ''
    },
    {
      key: 'wind_csv',
      label: '风电资源曲线 CSV',
      description: '风电单位出力系数曲线文件，可直接查看后端生成结果。',
      path: files.wind_csv || ''
    },
    {
      key: 'load_csv',
      label: '负荷曲线 CSV',
      description: '容量优化使用的负荷曲线文件。',
      path: files.load_csv || ''
    }
  ]
    .filter(item => item.path)
    .map(item => ({
      ...item,
      fileName: getArtifactFileName(item.path),
      kind: detectArtifactKind(item.path),
      url: artifactApi.getFileUrl(item.path),
      downloadUrl: artifactApi.getFileUrl(item.path, true)
    }))
})

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
  const opexBreakdown = economic.opex_breakdown || {}
  const coolingCapex = toNumber(
    breakdown.cooling_system_lakh,
    toNumber(coolingResult.value.economic_indicators?.initial_investment, 0)
  )
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
    opex_breakdown: opexBreakdown,
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
const reportRequirementFacts = computed(() => {
  const req = requirement.value || {}
  const plannedLoadKw = toNumber(req.planned_load_kw, 0)
  const density = toNumber(req.computing_power_density, 0)
  const area = toNumber(req.planned_area, 0)
  const cabinetCount = plannedLoadKw > 0 && density > 0
    ? Math.round(plannedLoadKw / density)
    : null

  const facts = [
    { label: '项目地点', value: req.location || '-' },
    { label: '建设规模', value: plannedLoadKw > 0 ? `${formatNumber(plannedLoadKw / 1000, 2)} MW` : '-' },
    { label: '规划建筑面积', value: area > 0 ? `${formatNumber(area, 0)} m²` : '-' },
    { label: '算力功率密度', value: density > 0 ? `${formatNumber(density, 0)} kW/柜` : '-' },
    { label: '估算机柜数量', value: cabinetCount ? `${formatNumber(cabinetCount, 0)} 柜` : '-' },
    { label: '机房等级', value: req.machine_room_grade || '-' },
    { label: '目标 PUE', value: req.pue_target ? formatNumber(req.pue_target, 2) : '-' },
    { label: '绿电目标', value: req.green_power_ratio != null ? formatPercent(req.green_power_ratio) : '-' },
    {
      label: '绿电直连占比',
      value: req.direct_connection_ratio != null && req.direct_connection_ratio !== ''
        ? formatPercent(req.direct_connection_ratio)
        : '未指定'
    },
    { label: '预算约束', value: req.budget_constraint ? `${formatNumber(req.budget_constraint, 0)} 万元` : '-' },
    { label: '制冷偏好', value: req.cooling_technology || '-' },
    { label: '仿真时长', value: req.sim_hours ? `${formatNumber(req.sim_hours, 0)} 小时` : '-' }
  ]

  return facts.filter(item => item.value && item.value !== '-')
})
const reportPrimaryFacts = computed(() => reportRequirementFacts.value.filter(item => ['建设规模', '项目地点', '预算约束'].includes(item.label)))
const reportSecondaryFacts = computed(() => reportRequirementFacts.value.filter(item => !['建设规模', '项目地点', '预算约束'].includes(item.label)))
const reportSummaryLead = computed(() => {
  const summary = String(finalReportData.value.summary || '').trim()
  if (!summary) return '暂无摘要'
  const firstSentence = summary.split(/[。！？]/).map(item => item.trim()).filter(Boolean)[0]
  return firstSentence || summary
})
const reportSummaryPoints = computed(() => {
  const points = []
  if (Array.isArray(finalReportData.value.recommendations)) {
    points.push(...finalReportData.value.recommendations.slice(0, 2))
  }
  const firstTradeoff = Array.isArray(finalReportData.value.trade_offs) ? finalReportData.value.trade_offs[0] : null
  if (firstTradeoff?.conflict || firstTradeoff?.resolution) {
    points.push(`关键权衡：${firstTradeoff.conflict || '核心取舍'}，${firstTradeoff.resolution || '需进一步明确'}`)
  }
  const firstRisk = Array.isArray(finalReportData.value.risks) ? finalReportData.value.risks[0] : null
  if (firstRisk?.description) {
    points.push(`主要风险：${firstRisk.description}`)
  }
  return points.map(item => String(item || '').trim()).filter(Boolean).slice(0, 3)
})
const reportDecision = computed(() => {
  const revisionCount = revisionComparison.value.changeCount
  const noteCount = revisionComparison.value.revisionNotes.length
  const hasRisks = Array.isArray(finalReportData.value.risks) && finalReportData.value.risks.length > 0
  if (revisionCount === 0) {
    return {
      label: '方案已完成仲裁',
      toneClass: hasRisks ? 'is-caution' : 'is-positive',
      description: '仲裁输出已整理为最终方案，可直接用于归档、导出和后续评审。'
    }
  }
  if (revisionCount <= 3 || noteCount > 0) {
    return {
      label: '已完成修订，可推进',
      toneClass: 'is-caution',
      description: '仲裁者已根据评审意见调整关键参数，建议结合修订原因继续核对落地边界。'
    }
  }
  return {
    label: '建议复核修订项',
    toneClass: 'is-warning',
    description: '修订条目较多，建议在定稿前再次核对参数边界、取值来源与依赖条件。'
  }
})
const keyMetricsRows = computed(() => {
  const metrics = keyMetrics.value || {}
  return [
    { label: '总成本(万元)', value: formatNumber(costResult.value.total_capex_lakh || metrics.total_cost, 2) },
    { label: 'PUE', value: formatNumber(metrics.pue, 3) },
    { label: '绿电比例', value: formatPercent(metrics.green_power_ratio) },
    { label: 'Tier 等级', value: metrics.tier_level ?? '-' },
    { label: '预期可用性', value: formatPercentAuto(metrics.expected_availability) },
    { label: '年碳排放(吨)', value: metrics.annual_carbon_emission ?? '-' }
  ]
})
const economicRows = computed(() => formatObjectRows(economicContent.value))
const powerRows = computed(() => formatObjectRows(powerContent.value))
const environmentalRows = computed(() => formatObjectRows(environmentalContent.value))

const sanitizeMarkdownCell = (value) => String(value ?? '-')
  .replace(/\|/g, '\\|')
  .replace(/\r?\n/g, '<br/>')

const buildMarkdownTable = (rows = [], headers = ['\u6307\u6807', '\u6570\u503c']) => {
  if (!Array.isArray(rows) || !rows.length) return '\u6682\u65e0\u6570\u636e'
  const head = '| ' + headers.map(sanitizeMarkdownCell).join(' | ') + ' |'
  const separator = '| ' + headers.map(() => '---').join(' | ') + ' |'
  const body = rows.map((row) => '| ' + sanitizeMarkdownCell(row?.label) + ' | ' + sanitizeMarkdownCell(row?.value) + ' |')
  return [head, separator, ...body].join('\n')
}

const buildMarkdownList = (items = [], formatter = (item) => String(item ?? '').trim()) => {
  if (!Array.isArray(items) || !items.length) return '- \u6682\u65e0'
  const lines = items
    .map(item => formatter(item))
    .map(item => String(item || '').trim())
    .filter(Boolean)
  return lines.length ? lines.map(item => '- ' + item).join('\n') : '- \u6682\u65e0'
}

const generatedReportMarkdown = computed(() => {
  const report = finalReportData.value || {}
  const lines = [
    '# ' + (report.name || '\u6570\u636e\u4e2d\u5fc3\u521d\u7a3f\u65b9\u6848\u62a5\u544a'),
    '',
    '## \u57fa\u672c\u4fe1\u606f',
    '- \u65b9\u6848\u7f16\u53f7\uff1a' + (solutionId.value || '-'),
    '- \u751f\u6210\u65f6\u95f4\uff1a' + (solutionData.value.created_at || '-'),
    finalReportPath.value ? ('- \u62a5\u544a\u8def\u5f84\uff1a' + finalReportPath.value) : null,
    '',
    '## \u6267\u884c\u6458\u8981',
    report.summary || '\u6682\u65e0\u6458\u8981',
    '',
    '## \u4ee3\u7406\u4fee\u8ba2',
    buildMarkdownTable([
      { label: '\u4fee\u8ba2\u6761\u76ee', value: String(revisionComparison.value.changeCount) },
      { label: '\u4fee\u8ba2\u8bf4\u660e', value: String(revisionComparison.value.revisionNotes.length) },
      { label: '\u4e0b\u4e00\u6b65\u5efa\u8bae', value: reportDecision.value.label }
    ]),
    '',
    '## \u4fee\u8ba2\u6e05\u5355',
    buildMarkdownTable(
      revisionComparison.value.changes.map(change => ({
        label: change.label,
        value: `${change.before} -> ${change.after}\n${change.reason}`
      }))
    ),
    '',
    '## \u5173\u952e\u6307\u6807',
    buildMarkdownTable(keyMetricsRows.value),
    '',
    '## \u7ecf\u6d4e\u6027\u65b9\u6848',
    economicSection.value.description || '\u6682\u65e0\u7ecf\u6d4e\u6027\u63cf\u8ff0',
    '',
    buildMarkdownTable(economicRows.value),
    '',
    '\u7ecf\u6d4e\u6027\u5efa\u8bae\uff1a',
    buildMarkdownList(economicSection.value.recommendations),
    '',
    '## \u4f9b\u7535\u53ef\u9760\u6027\u65b9\u6848',
    powerSection.value.description || '\u6682\u65e0\u4f9b\u7535\u53ef\u9760\u6027\u63cf\u8ff0',
    '',
    buildMarkdownTable(powerRows.value),
    '',
    '\u4f9b\u7535\u53ef\u9760\u6027\u5efa\u8bae\uff1a',
    buildMarkdownList(powerSection.value.recommendations),
    '',
    '## \u73af\u4fdd\u65b9\u6848',
    environmentalSection.value.description || '\u6682\u65e0\u73af\u4fdd\u63cf\u8ff0',
    '',
    buildMarkdownTable(environmentalRows.value),
    '',
    '\u73af\u4fdd\u5efa\u8bae\uff1a',
    buildMarkdownList(environmentalSection.value.recommendations),
    '',
    '## \u5173\u952e\u6743\u8861',
    buildMarkdownList(report.trade_offs, item => (item?.conflict || '-') + '\uff1a' + (item?.resolution || '-')),
    '',
    '## \u98ce\u9669\u6e05\u5355',
    buildMarkdownList(report.risks, item => '[' + (item?.type || '\u672a\u5206\u7c7b') + '] ' + (item?.description || formatRisk(item))),
    '',
    '## \u6700\u7ec8\u5efa\u8bae',
    buildMarkdownList(report.recommendations)
  ].filter(item => item !== null)

  return lines.join('\n').replace(/\n{3,}/g, '\n\n').trim()
})

const professionalReportSectionsMarkdown = computed(() => {
  const req = requirement.value || {}
  const plannedLoadKw = toNumber(req.planned_load_kw, 0)
  const density = toNumber(req.computing_power_density, 0)
  const area = toNumber(req.planned_area, 0)
  const pue = toNumber(keyMetrics.value.pue || coolingResult.value.estimated_pue || req.pue_target, 0)
  const rackCount = plannedLoadKw > 0 && density > 0 ? Math.round(plannedLoadKw / density) : 0
  const facilityLoadKw = plannedLoadKw > 0 ? plannedLoadKw * Math.max(pue || 1, 1) : 0
  const annualEnergyMwh = facilityLoadKw > 0 ? facilityLoadKw * 8760 / 1000 : 0
  const carbonFactor = toNumber(req.carbon_emission_factor, 0)
  const greenRatio = toNumber(greenProcurementPlan.value.total_green_power_ratio, toNumber(keyMetrics.value.green_power_ratio || req.green_power_ratio, 0))
  const residualEnergyMwh = annualEnergyMwh * Math.max(0, 1 - greenRatio)
  const residualCarbon = residualEnergyMwh * carbonFactor
  const capexBreakdown = costResult.value.capex_breakdown || {}
  const opexBreakdown = costResult.value.opex_breakdown || {}

  const lines = [
    '## \u8bbe\u8ba1\u8fb9\u754c\u3001\u4f9d\u636e\u4e0e\u5173\u952e\u5047\u8bbe',
    '\u672c\u8282\u7528\u4e8e\u660e\u786e\u62a5\u544a\u7684\u9002\u7528\u8fb9\u754c\uff0c\u907f\u514d\u5c06\u65b9\u6848\u9636\u6bb5\u6d4b\u7b97\u76f4\u63a5\u7b49\u540c\u4e8e\u65bd\u5de5\u56fe\u6216\u62db\u6807\u63a7\u5236\u4ef7\u3002',
    '',
    buildMarkdownTable([
      { label: '\u9879\u76ee\u5b9a\u4f4d', value: '\u6570\u636e\u4e2d\u5fc3\u7eff\u8272\u4f9b\u80fd\u4e0e\u57fa\u7840\u8bbe\u65bd\u7efc\u5408\u65b9\u6848' },
      { label: '\u8f93\u5165\u6765\u6e90', value: '\u7528\u6237\u53c2\u6570\u3001\u5236\u51b7\u5bfb\u4f18\u3001\u7eff\u7535\u5bb9\u91cf\u4f18\u5316\u3001\u4f9b\u7535\u53ef\u9760\u6027\u5206\u6790\u3001\u591a\u4e13\u5bb6\u4ef2\u88c1' },
      { label: '\u673a\u623f\u7b49\u7ea7', value: req.machine_room_grade || '\u5f85\u8865\u5145' },
      { label: '\u8bbe\u8ba1\u53c2\u8003', value: 'GB 50174-2017 / YD/T 5235-2019 \u7b49\u6570\u636e\u4e2d\u5fc3\u8bbe\u8ba1\u53e3\u5f84\uff0c\u540e\u7eed\u9700\u5728\u65bd\u5de5\u56fe\u9636\u6bb5\u590d\u6838' },
      { label: '\u6295\u8d44\u8fb9\u754c', value: 'CAPEX/OPEX \u4e3a\u65b9\u6848\u9636\u6bb5\u4f30\u7b97\uff0c\u9700\u4e0e\u5382\u5bb6\u62a5\u4ef7\u548c\u62db\u6807\u6e05\u5355\u95ed\u73af' }
    ], ['\u8fb9\u754c\u9879', '\u8bf4\u660e']),
    '',
    '## \u5efa\u8bbe\u89c4\u6a21\u4e0e\u5bb9\u91cf\u6d4b\u7b97',
    '\u5bb9\u91cf\u6d4b\u7b97\u7528\u4e8e\u6821\u6838\u5236\u51b7\u3001\u4f9b\u914d\u7535\u3001\u7eff\u7535\u548c\u6295\u8d44\u4f30\u7b97\u662f\u5426\u5728\u540c\u4e00\u8d1f\u8377\u8fb9\u754c\u4e0b\u5c55\u5f00\u3002',
    '',
    buildMarkdownTable([
      { label: 'IT \u8d1f\u8377\u89c4\u6a21', value: plannedLoadKw > 0 ? `${formatNumber(plannedLoadKw / 1000, 2)} MW` : '\u5f85\u8865\u5145' },
      { label: '\u4f30\u7b97\u673a\u67dc\u6570\u91cf', value: rackCount ? `${formatNumber(rackCount, 0)} \u67dc` : '\u5f85\u8865\u5145' },
      { label: '\u5355\u67dc\u529f\u7387\u5bc6\u5ea6', value: density > 0 ? `${formatNumber(density, 2)} kW/\u67dc` : '\u5f85\u8865\u5145' },
      { label: '\u5efa\u7b51\u9762\u79ef\u8d1f\u8377\u5bc6\u5ea6', value: area > 0 && plannedLoadKw > 0 ? `${formatNumber(plannedLoadKw / area, 2)} kW/m\u00b2` : '\u5f85\u8865\u5145' },
      { label: '\u65b9\u6848 PUE / \u76ee\u6807 PUE', value: `${formatNumber(pue, 3)} / ${formatNumber(req.pue_target, 3)}` },
      { label: '\u4f30\u7b97\u8bbe\u65bd\u603b\u8d1f\u8377', value: facilityLoadKw > 0 ? `${formatNumber(facilityLoadKw / 1000, 2)} MW` : '\u5f85\u8865\u5145' },
      { label: '\u4f30\u7b97\u5e74\u7528\u7535\u91cf', value: annualEnergyMwh > 0 ? `${formatNumber(annualEnergyMwh, 0)} MWh/\u5e74` : '\u5f85\u8865\u5145' }
    ], ['\u6d4b\u7b97\u9879', '\u65b9\u6848\u503c']),
    '',
    '## \u7efc\u5408\u6280\u672f\u65b9\u6848\u6df1\u5316',
    '\u987e\u95ee\u62a5\u544a\u9700\u5c06\u5236\u51b7\u3001\u4f9b\u7535\u3001\u7eff\u7535\u548c\u8fd0\u7ef4\u76d1\u6d4b\u89c6\u4e3a\u4e00\u4e2a\u7cfb\u7edf\uff0c\u800c\u4e0d\u662f\u4e09\u4e2a\u5b64\u7acb\u5b50\u65b9\u6848\u3002',
    '',
    buildMarkdownTable([
      { label: '\u5236\u51b7\u7cfb\u7edf', value: coolingResult.value.cooling_technology || '\u5f85\u8865\u5145' },
      { label: '\u4f9b\u914d\u7535\u7cfb\u7edf', value: powerPlan.value.scheme_name || powerPlan.value.external_voltage || '\u5f85\u8865\u5145' },
      { label: '\u7eff\u7535\u76f4\u8fde', value: formatPercent(greenProcurementPlan.value.actual_direct_connection_ratio, 0) },
      { label: '\u7eff\u7535\u91c7\u8d2d\u8865\u8db3', value: sanitizeProcurementMethodLabel(greenProcurementPlan.value.method_label || '\u5f85\u8865\u5145') },
      { label: '\u98ce\u5149\u50a8\u5bb9\u91cf', value: `\u98ce\u7535 ${formatNumber(greenOptimization.value.wind_capacity_mw, 2)} MW\uff1b\u5149\u4f0f ${formatNumber(greenOptimization.value.pv_capacity_mw, 2)} MWp\uff1b\u50a8\u80fd ${formatNumber(greenOptimization.value.storage_capacity_mwh, 2)} MWh` },
      { label: '\u53ef\u8fd0\u7ef4\u6027', value: '\u5efa\u8bae\u5efa\u7acb EMS + DCIM \u8054\u52a8\uff0c\u6301\u7eed\u8ddf\u8e2a PUE\u3001\u7eff\u7535\u5360\u6bd4\u3001\u78b3\u6392\u548c\u8bbe\u5907\u5065\u5eb7\u72b6\u6001' }
    ], ['\u7cfb\u7edf', '\u63a8\u8350\u914d\u7f6e/\u8bf4\u660e']),
    '',
    '## \u7ecf\u6d4e\u6027\u4e0e\u5168\u751f\u547d\u5468\u671f\u6210\u672c',
    '\u7ecf\u6d4e\u6027\u5224\u65ad\u4e0d\u53ea\u770b\u4e00\u6b21\u6027\u6295\u8d44\uff0c\u8fd8\u5e94\u540c\u65f6\u5173\u6ce8\u7535\u8d39\u3001\u7eff\u7535\u6ea2\u4ef7\u3001\u7eff\u8bc1\u6210\u672c\u3001\u8fd0\u7ef4\u6210\u672c\u548c\u672a\u6765\u6269\u5bb9\u5f39\u6027\u3002',
    '',
    buildMarkdownTable([
      { label: '\u9884\u7b97\u7ea6\u675f', value: req.budget_constraint ? `${formatNumber(req.budget_constraint, 0)} \u4e07\u5143` : '\u5f85\u8865\u5145' },
      { label: '\u4f30\u7b97\u603b CAPEX', value: `${formatNumber(costResult.value.total_capex_lakh || keyMetrics.value.total_cost, 0)} \u4e07\u5143` },
      { label: '\u4f9b\u7535\u7cfb\u7edf CAPEX', value: `${formatNumber(capexBreakdown.power_supply_system_lakh, 0)} \u4e07\u5143` },
      { label: '\u7eff\u7535\u7cfb\u7edf CAPEX', value: `${formatNumber(capexBreakdown.green_power_system_lakh, 0)} \u4e07\u5143` },
      { label: '\u5236\u51b7\u7cfb\u7edf CAPEX', value: `${formatNumber(capexBreakdown.cooling_system_lakh, 0)} \u4e07\u5143` },
      { label: '\u5e74\u8fd0\u7ef4\u6210\u672c', value: opexBreakdown.annual_opex_lakh ? `${formatNumber(opexBreakdown.annual_opex_lakh, 2)} \u4e07\u5143/\u5e74` : '\u5f85\u8865\u5145' }
    ], ['\u6210\u672c\u9879', '\u4f30\u7b97\u503c']),
    '',
    '## \u80fd\u8017\u3001\u7eff\u7535\u6d88\u7eb3\u4e0e\u78b3\u6392\u5206\u6790',
    '\u672c\u8282\u5c06\u80fd\u8017\u3001\u7eff\u7535\u6d88\u7eb3\u548c\u78b3\u6392\u653e\u653e\u5728\u540c\u4e00\u5f20\u8d26\u4e2d\uff0c\u4fbf\u4e8e\u540e\u7eed ESG \u62ab\u9732\u548c\u8fd0\u8425\u8003\u6838\u3002',
    '',
    buildMarkdownTable([
      { label: '\u4f30\u7b97\u5e74\u603b\u7528\u7535\u91cf', value: annualEnergyMwh > 0 ? `${formatNumber(annualEnergyMwh, 0)} MWh/\u5e74` : '\u5f85\u8865\u5145' },
      { label: '\u76ee\u6807\u7eff\u7535\u5360\u6bd4', value: formatPercent(greenRatio, 0) },
      { label: '\u76f4\u8fde\u7eff\u7535\u7535\u91cf', value: `${formatNumber(greenProcurementPlan.value.annual_direct_green_energy_mwh, 0)} MWh/\u5e74` },
      { label: '\u5e02\u573a\u5316\u7eff\u7535/\u7eff\u8bc1\u8865\u8db3', value: `${formatNumber(greenProcurementPlan.value.annual_procured_green_energy_mwh, 0)} MWh/\u5e74` },
      { label: '\u5269\u4f59\u7f51\u7535\u7535\u91cf', value: annualEnergyMwh > 0 ? `${formatNumber(residualEnergyMwh, 0)} MWh/\u5e74` : '\u5f85\u8865\u5145' },
      { label: '\u5269\u4f59\u8303\u56f4\u4e8c\u6392\u653e', value: annualEnergyMwh > 0 && carbonFactor > 0 ? `${formatNumber(residualCarbon, 0)} tCO2/\u5e74` : '\u5f85\u8865\u5145' }
    ], ['\u6307\u6807', '\u6d4b\u7b97\u503c']),
    '',
    '## \u5b9e\u65bd\u8def\u7ebf\u3001\u9a8c\u6536\u53e3\u5f84\u4e0e\u540e\u7eed\u5de5\u4f5c',
    buildMarkdownTable([
      { label: '\u65b9\u6848\u6df1\u5316', value: '\u590d\u6838\u8d1f\u8377\u8fb9\u754c\u3001\u673a\u67dc\u5bc6\u5ea6\u3001\u4f9b\u7535\u63a5\u5165\u6761\u4ef6\u3001\u7eff\u7535\u4ea4\u6613\u8def\u5f84\u548c\u5168\u5e74\u6c14\u8c61/\u8d1f\u8377\u66f2\u7ebf' },
      { label: '\u521d\u6b65\u8bbe\u8ba1', value: '\u5f62\u6210\u603b\u56fe\u3001\u4f9b\u914d\u7535\u4e00\u6b21\u65b9\u6848\u3001\u5236\u51b7\u7cfb\u7edf\u56fe\u3001\u80fd\u6e90\u7ad9\u8fb9\u754c\u3001EMS/DCIM \u63a5\u53e3\u548c\u6295\u8d44\u4f30\u7b97' },
      { label: '\u62db\u91c7\u4e0e\u65bd\u5de5\u56fe', value: '\u9501\u5b9a\u8bbe\u5907\u53c2\u6570\u3001\u5197\u4f59\u7b56\u7565\u3001\u65bd\u5de5\u56fe\u9884\u7b97\u3001\u62db\u6807\u6280\u672f\u89c4\u683c\u4e66\u548c\u4ea4\u4ed8\u8d23\u4efb\u8fb9\u754c' },
      { label: '\u65bd\u5de5\u4e0e\u8c03\u8bd5', value: '\u5b8c\u6210\u5355\u673a\u8c03\u8bd5\u3001\u7cfb\u7edf\u8054\u8c03\u3001\u5e26\u8f7d\u6d4b\u8bd5\u3001PUE \u521d\u6d4b\u3001\u7eff\u7535\u8ba1\u91cf\u94fe\u8def\u9a8c\u8bc1' },
      { label: '\u8fd0\u8425\u4f18\u5316', value: '\u6309\u6708\u8ddf\u8e2a PUE\u3001\u7eff\u7535\u5360\u6bd4\u3001\u78b3\u6392\u5f3a\u5ea6\u3001\u50a8\u80fd\u5229\u7528\u7387\u548c\u9884\u7b97\u504f\u5dee' }
    ], ['\u9636\u6bb5', '\u5173\u952e\u5de5\u4f5c'])
  ]

  return lines.join('\n').replace(/\n{3,}/g, '\n\n').trim()
})

const enrichProfessionalReportMarkdown = (content = '') => {
  const base = String(content || '').trim()
  const tail = professionalReportSectionsMarkdown.value
  if (!tail) return base
  const missingTail = tail
    .split('\n## ')
    .map((section, index) => index === 0 ? section : '## ' + section)
    .filter(section => {
      const heading = section.split('\n')[0].trim()
      const title = heading.replace(/^##\s+/, '').replace(/^\d+\.\s*/, '')
      return heading && title && !base.includes(title)
    })
  if (!base) return tail
  return missingTail.length ? `${base}\n\n${missingTail.join('\n\n')}` : base
}

const exportableReportMarkdown = computed(() => {
  const backendReport = String(reportMarkdown.value || solutionData.value?.final_report || '').trim()
  return enrichProfessionalReportMarkdown(backendReport || generatedReportMarkdown.value)
})

const stripReportTitle = (content = '') => String(content || '').replace(/^#\s+.+\n+/, '').trim()

const reportDocumentMarkdown = computed(() => stripReportTitle(exportableReportMarkdown.value || generatedReportMarkdown.value))

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
    `直连目标：${requirement.value.direct_connection_ratio != null ? formatPercent(requirement.value.direct_connection_ratio, 0) : '自动推荐'}`,
    `仿真时长：${greenInputs.value.sim_hours || requirement.value.sim_hours || 168} h`,
    `气象年份：${greenInputs.value.year || requirement.value.year || 2025}`,
    '容量边界：风/光 1-500MW，储能 0-500MWh'
  ],
  facts: [
    { label: '仿真模式', value: greenProfiles.value.pv.mode || greenProfiles.value.wind.mode || '--' },
    { label: '资源曲线', value: '先生成 PV / Wind 单位出力曲线' },
    { label: '采购方式', value: sanitizeProcurementMethodLabel(greenProcurementPlan.value.method_label || '--') },
    { label: '采购补足占比', value: formatPercent(greenProcurementPlan.value.procured_green_ratio, 0) },
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
    `系统先形成直连方案，再以 ${sanitizeProcurementMethodLabel(greenProcurementPlan.value.method_label || '市场化采购')} 补足剩余绿色电量。`,
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
  const grouped = {}
  const appendMessage = (item = {}) => {
    if (!item || !item.content) return
    const round = item.round || 1
    if (!grouped[round]) grouped[round] = { round, messages: [] }
    grouped[round].messages.push({
      speaker: item.speaker || item.expert || '专家',
      content: item.content || ''
    })
  }

  const rawHistory = solutionData.value.debate_history || []
  if (Array.isArray(rawHistory)) {
    rawHistory.forEach(appendMessage)
  }

  if (!Object.keys(grouped).length && Array.isArray(solutionData.value.streaming_output)) {
    solutionData.value.streaming_output.forEach((item) => {
      if (item?.node === 'debate_round') {
        appendMessage(item.data || {})
      }
    })
  }

  return Object.values(grouped).sort((a, b) => a.round - b.round)
})

const greenConfig = computed(() => {
  const errorMessage = greenPowerResult.value.error_message || greenPowerResult.value.message || ''
  if (greenPowerResult.value.status === 'error') {
    return [
      { type: '绿电系统', capacity: '计算失败', ratio: errorMessage || '-' }
    ]
  }
  const procurement = greenProcurementPlan.value
  const wind = toNumber(greenOptimization.value.wind_capacity_mw, null)
  const pv = toNumber(greenOptimization.value.pv_capacity_mw, null)
  const storage = toNumber(greenOptimization.value.storage_capacity_mwh, null)
  const total = wind + pv + storage
  const totalGreenRatio = toNumber(procurement.total_green_power_ratio, keyMetrics.value.green_power_ratio)
  const directRatio = toNumber(procurement.actual_direct_connection_ratio, keyMetrics.value.direct_connection_ratio)
  const procuredRatio = toNumber(procurement.procured_green_ratio, keyMetrics.value.procured_green_ratio)
  return [
    { type: '总绿电占比', capacity: '-', ratio: Number.isFinite(totalGreenRatio) ? (totalGreenRatio * 100).toFixed(1) : '-' },
    { type: '直连占比', capacity: '-', ratio: Number.isFinite(directRatio) ? (directRatio * 100).toFixed(1) : '-' },
    { type: '采购补足占比', capacity: sanitizeProcurementMethodLabel(greenProcurementPlan.value.method_label || '-'), ratio: Number.isFinite(procuredRatio) ? (procuredRatio * 100).toFixed(1) : '-' },
    { type: '光伏装机', capacity: `${formatNumber(pv)} MWp`, ratio: Number.isFinite(total) && total > 0 ? ((pv / total) * 100).toFixed(1) : '0.0' },
    { type: '风电装机', capacity: `${formatNumber(wind)} MW`, ratio: Number.isFinite(total) && total > 0 ? ((wind / total) * 100).toFixed(1) : '0.0' },
    { type: '储能装机', capacity: `${formatNumber(storage)} MWh`, ratio: Number.isFinite(total) && total > 0 ? ((storage / total) * 100).toFixed(1) : '0.0' }
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
  const opexBreakdown = costResult.value.opex_breakdown || {}
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
        { label: '光伏装机容量', value: `${formatNumber(greenOptimization.value.pv_capacity_mw, 2)} MWp` },
        { label: '储能额定能量', value: `${formatNumber(greenOptimization.value.storage_capacity_mwh, 2)} MWh` },
        { label: '总绿电占比', value: formatPercent(greenProcurementPlan.value.total_green_power_ratio, 0) },
        { label: '直连占比', value: formatPercent(greenProcurementPlan.value.actual_direct_connection_ratio, 0) },
        { label: '采购补足占比', value: formatPercent(greenProcurementPlan.value.procured_green_ratio, 0) },
        { label: '采购方式', value: sanitizeProcurementMethodLabel(greenProcurementPlan.value.method_label || '-') },
        { label: '年采购成本(OPEX)', value: `${formatNumber(opexBreakdown.annual_green_procurement_cost_lakh, 2)} 万元/年` }
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
  { label: '修订条目', value: revisionComparison.value.changeCount, highlight: false }
])

const filteredMarkdown = computed(() => {
  const source = reportDocumentMarkdown.value || reportMarkdown.value
  if (!searchKeyword.value) return source
  const kw = searchKeyword.value.toLowerCase()
  return source
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
const reportDocumentHtml = computed(() => markdownToHtml(filteredMarkdown.value))

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
      reportMarkdown.value = enrichProfessionalReportMarkdown(solutionData.value.final_report)
    }
  } catch (error) {
    ElMessage.error(`加载方案失败: ${error.message}`)
  }
}

const loadMarkdownReport = async () => {
  if (solutionData.value?.final_report) {
    reportMarkdown.value = enrichProfessionalReportMarkdown(solutionData.value.final_report)
    return
  }
  try {
    const { data } = await solutionApi.exportMarkdown(solutionId.value)
    reportMarkdown.value = enrichProfessionalReportMarkdown((data?.content || '').trim() || generatedReportMarkdown.value)
  } catch (error) {
    reportMarkdown.value = enrichProfessionalReportMarkdown(generatedReportMarkdown.value)
  }
}

const exportMarkdown = async () => {
  await loadMarkdownReport()
  const content = exportableReportMarkdown.value || generatedReportMarkdown.value
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '\u65b9\u6848\u62a5\u544a_' + solutionId.value + '.md'
  a.click()
  URL.revokeObjectURL(url)
}

const exportPdf = async () => {
  if (activeTab.value !== 'report') {
    activeTab.value = 'report'
    await nextTick()
  }

  if (!reportMarkdown.value) {
    await loadMarkdownReport()
    await nextTick()
  }

  const reportNode = reportExportRef.value
  if (!reportNode) {
    ElMessage.warning('\u672a\u627e\u5230\u53ef\u5bfc\u51fa\u7684\u62a5\u544a\u5185\u5bb9')
    return
  }

  const printWindow = window.open('', '_blank', 'width=1200,height=900')
  if (!printWindow) {
    ElMessage.warning('\u6d4f\u89c8\u5668\u62e6\u622a\u4e86\u5f39\u7a97\uff0c\u8bf7\u5141\u8bb8\u5f39\u7a97\u540e\u91cd\u8bd5')
    return
  }

  const title = finalReportData.value?.name || ('\u65b9\u6848\u62a5\u544a_' + solutionId.value)
  printWindow.document.write(
    '<!DOCTYPE html>' +
    '<html lang="zh-CN">' +
    '<head>' +
    '<meta charset="UTF-8" />' +
    '<title>' + title + '</title>' +
    '<style>' +
    '* { box-sizing: border-box; }' +
    "body { margin: 0; padding: 32px; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; color: #1f2d26; line-height: 1.65; background: #fff; }" +
    'h1, h2, h3 { color: #10241a; margin: 0 0 14px; }' +
    'h1 { font-size: 28px; }' +
    'h2 { font-size: 20px; margin-top: 28px; padding-bottom: 8px; border-bottom: 1px solid #dfe9e3; }' +
    'h3 { font-size: 16px; }' +
    'p, li, span, div { font-size: 13px; }' +
    'ul, ol { padding-left: 20px; }' +
    'table { width: 100%; border-collapse: collapse; margin: 12px 0 18px; }' +
    'th, td { border: 1px solid #d9e3dc; padding: 10px 12px; text-align: left; vertical-align: top; }' +
    'th { background: #f4f8f5; }' +
    '.report-meta { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; color: #5d6d65; }' +
    '.executive-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }' +
    '.executive-item { border: 1px solid #dfe9e3; border-radius: 10px; padding: 12px 14px; background: #f8fbf9; }' +
    '.executive-label { color: #6c7a73; margin-bottom: 6px; }' +
    '.executive-value { color: #10241a; font-size: 18px; font-weight: 700; }' +
    '.report-chapter { break-inside: avoid; page-break-inside: avoid; margin-bottom: 20px; }' +
    '.markdown-rendered code { padding: 2px 6px; background: #f2f4f3; border-radius: 4px; }' +
    '.markdown-table-wrap { overflow: visible; }' +
    '@media print { body { padding: 18px; } .report-chapter { page-break-inside: avoid; } }' +
    '</style>' +
    '</head>' +
    '<body>' + reportNode.innerHTML + '</body>' +
    '</html>'
  )
  printWindow.document.close()
  printWindow.focus()
  setTimeout(() => {
    printWindow.print()
  }, 300)
}

const initPowerBalanceChart = () => {
  if (!powerBalanceChartRef.value) return
  if (charts.powerBalance) charts.powerBalance.dispose()
  const chart = echarts.init(powerBalanceChartRef.value)
  const totalGreenRatio = Math.max(0, Math.min(100, toNumber(greenProcurementPlan.value.total_green_power_ratio, keyMetrics.value.green_power_ratio) * 100))
  const directRatio = Math.max(0, Math.min(totalGreenRatio, toNumber(greenProcurementPlan.value.actual_direct_connection_ratio, keyMetrics.value.direct_connection_ratio) * 100))
  const procuredRatio = Math.max(0, Math.min(totalGreenRatio - directRatio, toNumber(greenProcurementPlan.value.procured_green_ratio, keyMetrics.value.procured_green_ratio) * 100))
  const nonGreenRatio = Math.max(0, 100 - totalGreenRatio)
  const source = [
    { name: '直连绿电', value: Number(directRatio.toFixed(1)), color: '#1fbf84' },
    { name: '采购补足', value: Number(procuredRatio.toFixed(1)), color: '#29b6d8' },
    { name: '非绿电', value: Number(nonGreenRatio.toFixed(1)), color: '#d7e6de' }
  ].filter(item => item.value > 0)
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: ({ name, value }) => `${name}<br/>${value}%`
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: true,
      label: {
        formatter: '{b}',
        color: '#2f3f38'
      },
      data: source.map(item => ({
        name: item.name,
        value: item.value,
        itemStyle: { color: item.color }
      }))
    }],
    graphic: [
      {
        type: 'group',
        left: 'center',
        top: '43%',
        children: [
          {
            type: 'text',
            style: {
              text: '总绿电',
              fill: '#64756d',
              fontSize: 12,
              textAlign: 'center'
            }
          },
          {
            type: 'text',
            top: 18,
            style: {
              text: `${totalGreenRatio.toFixed(1)}%`,
              fill: '#10241a',
              fontSize: 20,
              fontWeight: 700,
              textAlign: 'center'
            }
          }
        ]
      }
    ]
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
  if (tabName === 'green') initPowerBalanceChart()
  if (tabName === 'economic') initCostChart()
  if (tabName === 'report' && !reportMarkdown.value) await loadMarkdownReport()
}

const handleResize = () => {
  Object.values(charts).forEach(chart => chart && chart.resize())
}

onMounted(async () => {
  savedProjectConfig.value = normalizeRequirementFields(loadSavedProjectConfig())
  await loadSolutionData()
  await nextTick()
  if (activeTab.value === 'green') initPowerBalanceChart()
  if (activeTab.value === 'economic') initCostChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  Object.values(charts).forEach(chart => chart && chart.dispose())
})

watch(
  () => route.params.id,
  async (newId) => {
    if (!newId || newId === solutionId.value) return
    solutionId.value = newId
    solutionData.value = {}
    reportMarkdown.value = ''
    savedProjectConfig.value = normalizeRequirementFields(loadSavedProjectConfig())
    await loadSolutionData()
    await nextTick()
    await handleTabChange(activeTab.value)
  }
)
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

.artifact-card-panel {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 18px;
  border: 1px solid var(--border-light);
}

.artifact-panel-header h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.artifact-panel-header p {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.artifact-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.artifact-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%);
}

.artifact-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.artifact-item-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.artifact-item-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.artifact-item-desc,
.artifact-item-meta,
.artifact-item-path,
.artifact-preview-note {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.artifact-item-meta {
  font-weight: 600;
  color: var(--primary-dark);
}

.artifact-item-path {
  word-break: break-all;
  padding: 10px 12px;
  border-radius: 12px;
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border: 1px solid var(--border-light);
}

.artifact-item-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.artifact-item-actions a {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-dark);
  text-decoration: none;
}

.artifact-item-actions a:hover {
  color: var(--primary-color);
}

.artifact-image-shell,
.artifact-csv-shell {
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%);
  overflow: hidden;
}

.artifact-image {
  display: block;
  width: 100%;
  height: auto;
  max-height: none;
  object-fit: fill;
  background: rgba(255, 255, 255, 0.96);
}

.artifact-placeholder {
  padding: 24px 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
}

.artifact-placeholder.is-error {
  color: var(--danger-color);
}

.artifact-preview-note {
  padding: 12px 14px 0;
}

.artifact-table-wrap {
  overflow-x: auto;
  padding: 12px 14px 14px;
}

.artifact-table {
  width: 100%;
  min-width: 280px;
  border-collapse: collapse;
  border-radius: 12px;
  overflow: hidden;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.artifact-table td {
  padding: 8px 10px;
  border: 1px solid var(--border-light);
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.artifact-table-index {
  width: 56px;
  text-align: center;
  font-weight: 700;
  color: var(--text-primary);
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
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

.report-header-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-header-copy h3 {
  margin: 0;
  font-size: 22px;
  color: rgba(244, 252, 247, 0.99);
}

.report-header-copy p {
  max-width: 58ch;
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: rgba(211, 235, 224, 0.72);
}

.report-header-tools {
  width: min(320px, 100%);
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
  padding: 28px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%) 0%, color-mix(in oklab, var(--bg-panel) 97%, var(--primary-color) 3%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
}

.report-preview-shell {
  padding: 14px;
  border-radius: 24px;
}

.report-title-section {
  text-align: left;
  padding: 26px 26px 24px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 24%, var(--border-default));
  margin-bottom: 24px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, transparent 100%);
  border-radius: 18px;
}

.report-cover-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  margin-bottom: 14px;
  border-radius: 999px;
  border: 1px solid rgba(121, 239, 171, 0.16);
  background: rgba(7, 26, 22, 0.72);
  color: rgba(154, 247, 196, 0.94);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.report-cover-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px;
  gap: 22px;
  align-items: start;
}

.report-cover-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-decision-banner {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: end;
  padding: 18px 20px;
  border-radius: 18px;
  border: 1px solid rgba(121, 239, 171, 0.16);
  background: linear-gradient(180deg, rgba(15, 51, 38, 0.84), rgba(10, 31, 24, 0.72));
  box-shadow: inset 0 1px 0 rgba(232, 255, 241, 0.05);
}

.report-decision-banner.is-caution {
  border-color: rgba(246, 197, 106, 0.18);
  background: linear-gradient(180deg, rgba(52, 43, 22, 0.72), rgba(17, 25, 20, 0.72));
}

.report-decision-banner.is-warning {
  border-color: rgba(255, 132, 132, 0.16);
  background: linear-gradient(180deg, rgba(58, 27, 27, 0.74), rgba(24, 19, 19, 0.72));
}

.report-decision-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.report-decision-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(183, 230, 202, 0.76);
}

.report-decision-copy strong {
  font-size: 24px;
  line-height: 1.2;
  color: rgba(244, 252, 247, 0.98);
}

.report-decision-copy p {
  margin: 0;
  max-width: 56ch;
  font-size: 13px;
  line-height: 1.7;
  color: rgba(213, 236, 222, 0.78);
}

.report-decision-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: right;
  font-size: 12px;
  color: rgba(189, 225, 203, 0.76);
}

.report-cover-subtitle {
  max-width: 62ch;
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: rgba(216, 238, 224, 0.78);
}

.report-cover-score {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 16px;
  border-radius: 20px;
  border: 1px solid rgba(121, 239, 171, 0.14);
  background:
    radial-gradient(circle at top, rgba(121, 239, 171, 0.12), transparent 55%),
    linear-gradient(180deg, rgba(24, 73, 57, 0.68), rgba(12, 36, 29, 0.68));
  box-shadow: inset 0 1px 0 rgba(230, 255, 239, 0.04);
}

.report-cover-score-label,
.report-cover-score small {
  font-size: 12px;
  line-height: 1.5;
}

.report-cover-score-label {
  color: rgba(211, 235, 224, 0.72);
}

.report-cover-score strong {
  font-size: 30px;
  line-height: 1;
  color: rgba(121, 239, 171, 0.98);
}

.report-cover-score small {
  color: rgba(188, 225, 203, 0.76);
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
  justify-content: flex-start;
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

.report-input-summary {
  margin-bottom: 24px;
  padding: 22px 24px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 0%, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 100%);
}

.report-input-primary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 14px;
}

.report-chapter-head {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 18px;
}

.report-chapter-head h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.report-chapter-head p {
  margin: 0;
  max-width: 72ch;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.report-input-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.report-input-item {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-default));
  background: color-mix(in oklab, var(--bg-panel) 98%, var(--primary-color) 2%);
  box-shadow: inset 0 1px 0 color-mix(in oklab, var(--primary-light) 5%, transparent);
}

.report-input-item--primary {
  padding: 18px 18px 16px;
  border-color: color-mix(in oklab, var(--primary-color) 16%, var(--border-default));
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 100%);
  box-shadow:
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 7%, transparent),
    0 10px 20px rgba(8, 24, 17, 0.06);
}

.report-input-label {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-secondary);
}

.report-input-value {
  margin-top: 8px;
  font-size: 16px;
  line-height: 1.45;
  font-weight: 600;
  color: var(--text-primary);
}

.report-input-item--primary .report-input-value {
  font-size: 22px;
  line-height: 1.25;
}

.report-executive-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 20px;
  align-items: start;
}

.report-executive-main {
  display: flex;
  flex-direction: column;
}

.report-executive-main h2 {
  margin-top: 0;
}

.report-summary-points {
  margin: 16px 0 0;
  padding-left: 20px;
}

.report-summary-points li {
  margin-bottom: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.7;
}

.report-executive-side .executive-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.report-appendix {
  margin-top: 10px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 97%, var(--primary-color) 3%);
}

.report-appendix summary {
  padding: 16px 18px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  list-style: none;
}

.report-appendix summary::-webkit-details-marker {
  display: none;
}

.report-section-item--appendix {
  padding: 0 18px 18px;
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

.report-section-item--table,
.report-data-table {
  margin-top: 14px;
}

.report-data-table,
.report-section-item--table {
  padding: 12px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top left, rgba(121, 239, 171, 0.05), transparent 34%),
    linear-gradient(180deg, rgba(8, 27, 22, 0.72), rgba(4, 15, 12, 0.82));
  border: 1px solid rgba(121, 239, 171, 0.12);
  box-shadow: inset 0 1px 0 rgba(230, 255, 239, 0.03);
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

.arbitration-revision-list,
.revision-report-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}

.arbitration-revision-item,
.revision-report-item {
  padding: 12px 14px;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%);
  border: 1px solid var(--border-light);
}

.arbitration-revision-head,
.revision-report-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.arbitration-revision-reason,
.revision-report-reason {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
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
  .artifact-item-header,
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

/* Deep-green solution cockpit overrides */
.detail-page {
  position: relative;
  gap: 26px;
  color: rgba(228, 235, 232, 0.94);
  --detail-ink-strong: rgba(242, 246, 244, 0.97);
  --detail-ink: rgba(226, 233, 230, 0.9);
  --detail-muted: rgba(182, 194, 189, 0.74);
  --detail-line: rgba(132, 167, 152, 0.16);
  --detail-line-strong: rgba(147, 190, 168, 0.24);
  --detail-shell:
    linear-gradient(180deg, rgba(29, 35, 35, 0.96), rgba(22, 27, 27, 0.98));
  --detail-panel:
    linear-gradient(180deg, rgba(35, 42, 41, 0.94), rgba(28, 34, 34, 0.97));
  --detail-panel-soft:
    linear-gradient(180deg, rgba(41, 48, 47, 0.9), rgba(32, 38, 38, 0.95));
  --detail-panel-quiet:
    linear-gradient(180deg, rgba(31, 37, 37, 0.9), rgba(25, 30, 30, 0.95));
}

.detail-page::before {
  content: '';
  position: fixed;
  inset: var(--header-height) 0 0 var(--sidebar-width);
  pointer-events: none;
  background:
    linear-gradient(rgba(124, 158, 144, 0.014) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124, 158, 144, 0.014) 1px, transparent 1px),
    radial-gradient(circle at 16% 8%, rgba(95, 158, 128, 0.06), transparent 24%),
    radial-gradient(circle at 86% 14%, rgba(178, 156, 98, 0.04), transparent 20%),
    linear-gradient(180deg, rgba(20, 24, 24, 0.98), rgba(14, 17, 18, 0.995));
  background-size: 48px 48px, 48px 48px, auto, auto;
  z-index: 0;
}

.detail-page > * {
  position: relative;
  z-index: 1;
}

.detail-header {
  position: relative;
  overflow: hidden;
  padding: 24px 28px;
  background:
    radial-gradient(circle at 18% 18%, rgba(112, 170, 139, 0.08), transparent 28%),
    linear-gradient(145deg, rgba(36, 42, 43, 0.95), rgba(27, 32, 33, 0.98));
  border: 1px solid var(--detail-line-strong);
  border-radius: 26px;
  box-shadow: 0 22px 46px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.025);
}

.detail-header::after {
  content: '';
  position: absolute;
  left: 26px;
  right: 26px;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(132, 186, 156, 0.28), rgba(132, 186, 156, 0.08), transparent);
}

.detail-header h1 {
  color: var(--detail-ink-strong);
  font-size: 28px;
}

.header-actions :deep(.el-button:not(.el-button--primary)) {
  background: rgba(39, 45, 45, 0.84);
  border-color: rgba(135, 171, 156, 0.18);
  color: rgba(225, 232, 229, 0.9);
}

.detail-tabs {
  overflow: visible;
}

.detail-tabs :deep(.el-tabs__header) {
  position: sticky;
  top: 0;
  z-index: 4;
  padding: 8px 12px 0;
  background:
    radial-gradient(circle at top left, rgba(105, 163, 134, 0.05), transparent 32%),
    linear-gradient(180deg, rgba(34, 40, 40, 0.94), rgba(26, 31, 32, 0.97));
  border: 1px solid var(--detail-line);
  border-radius: 20px;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22);
}

.detail-tabs :deep(.el-tabs__item) {
  color: var(--detail-muted);
}

.detail-tabs :deep(.el-tabs__item.is-active) {
  color: rgba(214, 229, 221, 0.98);
}

.detail-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, rgba(132, 177, 152, 0.96), rgba(196, 173, 112, 0.92));
  box-shadow: none;
}

.detail-tabs :deep(.el-tabs__item:hover) {
  color: rgba(230, 237, 234, 0.94);
}

.overview-section {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(360px, 0.95fr);
  gap: 22px;
  align-items: start;
}

.overview-section .metrics-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.overview-hero {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px 24px;
  border-radius: 24px;
  border: 1px solid rgba(138, 170, 156, 0.16);
  background:
    radial-gradient(circle at top left, rgba(108, 161, 133, 0.07), transparent 34%),
    linear-gradient(145deg, rgba(35, 41, 42, 0.94), rgba(26, 31, 32, 0.97));
  box-shadow: 0 20px 44px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.025);
}

.overview-hero-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px;
  gap: 18px;
  align-items: start;
}

.overview-kicker,
.report-header-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(148, 175, 163, 0.2);
  background: rgba(41, 47, 47, 0.88);
  color: rgba(204, 217, 211, 0.9);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.overview-hero-copy h2 {
  margin: 12px 0 10px;
  font-size: 30px;
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: rgba(244, 247, 246, 0.99);
}

.overview-hero-summary {
  max-width: 62ch;
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: rgba(192, 203, 199, 0.82);
}

.overview-hero-badge {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px 16px;
  border-radius: 20px;
  border: 1px solid rgba(148, 176, 163, 0.16);
  background:
    radial-gradient(circle at top, rgba(173, 154, 101, 0.12), transparent 58%),
    linear-gradient(180deg, rgba(38, 43, 44, 0.95), rgba(27, 31, 32, 0.97));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.025);
}

.overview-hero-badge-label,
.overview-hero-badge-note,
.summary-section-tag,
.info-section-note {
  font-size: 12px;
  line-height: 1.5;
}

.overview-hero-badge-label {
  color: rgba(176, 189, 185, 0.74);
}

.overview-hero-badge strong {
  font-size: 30px;
  line-height: 1;
  color: rgba(137, 245, 179, 0.98);
}

.overview-hero-badge-note {
  color: rgba(162, 178, 172, 0.76);
}

.revision-overview {
  margin-top: 18px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(148, 176, 163, 0.14);
  background: linear-gradient(180deg, rgba(33, 37, 37, 0.94), rgba(24, 28, 29, 0.98));
}

.revision-overview h5 {
  margin: 0 0 14px;
  font-size: 14px;
  color: rgba(240, 244, 241, 0.96);
}

.revision-overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.revision-overview-column {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(148, 176, 163, 0.12);
}

.revision-overview-column--draft {
  background: rgba(18, 30, 23, 0.96);
}

.revision-overview-column--revised {
  background: rgba(17, 28, 31, 0.96);
}

.revision-overview-title {
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 700;
  color: rgba(240, 244, 241, 0.96);
}

.revision-overview-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.revision-overview-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  line-height: 1.6;
  color: rgba(192, 203, 199, 0.8);
}

.revision-overview-item strong {
  color: rgba(240, 244, 241, 0.96);
}

.overview-section .summary-section {
  min-height: 100%;
}

.overview-section .info-section {
  grid-column: 1 / -1;
}

.summary-section-head,
.info-section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 16px;
}

.summary-section-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(109, 232, 160, 0.16);
  background: rgba(28, 34, 40, 0.8);
  color: rgba(145, 244, 185, 0.92);
  font-weight: 600;
}

.info-section-note {
  color: rgba(211, 235, 224, 0.62);
}

.cooling-section,
.green-section,
.power-section,
.economic-section {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(340px, 0.9fr);
  gap: 22px;
  align-items: start;
}

.green-insight-grid {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(380px, 0.92fr);
  gap: 22px;
  align-items: stretch;
}

.cooling-section .system-trace-shell,
.green-section .system-trace-shell,
.power-section .system-trace-shell,
.economic-cost-panel,
.report-section {
  grid-column: 1 / -1;
}

.param-cards {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.cooling-section .table-card,
.power-section .power-architecture-card,
.green-section .artifact-card-panel,
.power-section .power-kpi-card,
.economic-section .economic-metrics-card {
  grid-column: 1 / -1;
}

.table-card,
.power-architecture-card,
.artifact-card-panel,
.power-kpi-card,
.economic-metrics-card {
  width: 100%;
  max-width: none;
}

.power-section .power-architecture-card,
.power-section .power-kpi-card {
  justify-self: stretch;
}

.metrics-grid,
.param-cards,
.trace-fact-grid,
.trace-weight-grid,
.economic-kpi-grid {
  align-items: stretch;
}

.metric-card,
.summary-section,
.info-section,
.param-card,
.green-summary-card,
.system-trace-shell,
.green-section :deep(.el-card),
.power-section :deep(.el-card),
.economic-section :deep(.el-card),
.economic-cost-main,
.economic-cost-summary,
.economic-kpi-card,
.economic-cost-item,
.economic-summary-row,
.trace-block,
.trace-fact-item,
.trace-weight-item,
.trace-ranking-item,
.artifact-card-panel,
.report-header,
.report-content {
  background:
    radial-gradient(circle at top left, rgba(100, 153, 126, 0.055), transparent 32%),
    radial-gradient(circle at 88% 10%, rgba(178, 157, 104, 0.045), transparent 18%),
    var(--detail-shell);
  border-color: var(--detail-line);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.022);
}

.report-title-section,
.report-executive-summary,
.executive-item,
.report-chapter,
.report-section-item,
.arbitration-result,
.debate-round,
.expert-opinion-card {
  background:
    radial-gradient(circle at top left, rgba(98, 150, 124, 0.035), transparent 32%),
    var(--detail-panel);
  border-color: rgba(138, 171, 157, 0.12);
}

.metric-card {
  position: relative;
  overflow: hidden;
}

.metric-card::after {
  content: '';
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(121, 239, 171, 0.34), transparent);
}

.metric-card:hover {
  border-color: rgba(121, 239, 171, 0.32);
  box-shadow: 0 26px 68px rgba(2, 24, 16, 0.28);
}

.metric-value,
.summary-section h3,
.info-section h3,
.param-card h4,
.system-trace-header h4,
.trace-block-title,
.economic-cost-header h4,
.economic-kpi-value,
.economic-cost-value,
.economic-summary-value,
.artifact-item-title,
.report-title,
.report-header-copy h3,
.report-chapter h2,
.executive-value {
  color: rgba(242, 246, 245, 0.98);
}

.report-cover-kicker {
  border-color: rgba(148, 176, 163, 0.18);
  background: rgba(39, 45, 45, 0.84);
  color: rgba(206, 219, 212, 0.9);
}

.report-cover-score {
  border-color: rgba(147, 176, 163, 0.16);
  background:
    radial-gradient(circle at top, rgba(178, 157, 104, 0.14), transparent 55%),
    linear-gradient(180deg, rgba(36, 43, 43, 0.78), rgba(27, 33, 33, 0.84));
  box-shadow: inset 0 1px 0 rgba(230, 255, 239, 0.03);
}

.report-cover-score strong {
  color: rgba(227, 209, 156, 0.96);
}

.report-decision-banner {
  border-color: rgba(145, 177, 163, 0.16);
  background:
    radial-gradient(circle at top left, rgba(116, 164, 138, 0.14), transparent 40%),
    linear-gradient(180deg, rgba(39, 48, 46, 0.94), rgba(30, 38, 37, 0.97));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.028);
}

.report-decision-banner.is-caution {
  border-color: rgba(196, 170, 112, 0.22);
  background:
    radial-gradient(circle at top left, rgba(196, 170, 112, 0.12), transparent 40%),
    linear-gradient(180deg, rgba(49, 44, 35, 0.95), rgba(36, 32, 28, 0.97));
}

.report-decision-banner.is-warning {
  border-color: rgba(178, 126, 116, 0.22);
  background:
    radial-gradient(circle at top left, rgba(178, 126, 116, 0.12), transparent 40%),
    linear-gradient(180deg, rgba(53, 39, 37, 0.95), rgba(38, 30, 29, 0.97));
}

.report-decision-label {
  color: rgba(191, 204, 198, 0.75);
}

.report-decision-copy p,
.report-decision-meta {
  color: rgba(196, 206, 202, 0.78);
}

.report-input-summary {
  background:
    radial-gradient(circle at top left, rgba(106, 159, 132, 0.05), transparent 34%),
    linear-gradient(180deg, rgba(37, 44, 44, 0.92), rgba(29, 35, 35, 0.96));
  border-color: rgba(141, 172, 158, 0.14);
}

.report-input-item {
  background: linear-gradient(180deg, rgba(40, 46, 46, 0.94), rgba(33, 39, 39, 0.97));
  border-color: rgba(134, 165, 151, 0.14);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

.report-input-item--primary {
  border-color: rgba(173, 156, 110, 0.18);
  background:
    radial-gradient(circle at top left, rgba(173, 156, 110, 0.08), transparent 38%),
    linear-gradient(180deg, rgba(45, 43, 38, 0.95), rgba(35, 35, 31, 0.98));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.024),
    0 12px 24px rgba(0, 0, 0, 0.12);
}

.executive-item {
  background:
    radial-gradient(circle at top left, rgba(105, 158, 132, 0.045), transparent 34%),
    linear-gradient(180deg, rgba(40, 46, 46, 0.94), rgba(32, 38, 38, 0.97));
  border-color: rgba(139, 169, 156, 0.13);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

.report-chapter {
  padding: 20px 22px 18px;
  border: 1px solid rgba(136, 167, 153, 0.12);
  border-radius: 22px;
  background:
    radial-gradient(circle at top left, rgba(96, 148, 123, 0.04), transparent 34%),
    linear-gradient(180deg, rgba(36, 43, 42, 0.92), rgba(28, 34, 34, 0.96));
}

.report-chapter--document {
  padding: 24px;
  border-color: rgba(164, 190, 176, 0.18);
  background:
    radial-gradient(circle at top left, rgba(139, 181, 155, 0.065), transparent 34%),
    radial-gradient(circle at 96% 0%, rgba(202, 174, 108, 0.05), transparent 22%),
    linear-gradient(180deg, rgba(38, 45, 44, 0.95), rgba(28, 34, 34, 0.98));
}

.report-section-item {
  padding: 0;
}

.report-section-item--document {
  margin-top: 16px;
}

.markdown-rendered--document {
  padding: 24px;
  background:
    linear-gradient(180deg, rgba(25, 31, 31, 0.96), rgba(20, 25, 25, 0.98));
  border-color: rgba(143, 174, 160, 0.16);
}

.markdown-rendered--document :deep(h2) {
  margin-top: 26px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(135, 170, 154, 0.16);
}

.markdown-rendered--document :deep(h2:first-child) {
  margin-top: 0;
}

.markdown-rendered--document :deep(p) {
  max-width: 88ch;
  color: rgba(202, 212, 208, 0.86);
}

.markdown-rendered--document :deep(table) {
  margin: 14px 0 22px;
}

.report-appendix {
  border-color: rgba(133, 163, 150, 0.13);
  background: linear-gradient(180deg, rgba(31, 36, 37, 0.9), rgba(25, 30, 31, 0.95));
}

.report-appendix summary {
  color: rgba(216, 224, 220, 0.92);
}

.metric-value.highlight,
.trace-ranking-order,
.system-trace-badge,
.economic-kpi-value.success {
  color: rgba(171, 214, 189, 0.98);
}

.metric-label,
.metric-unit,
.summary-text,
.expert-recommendations li,
.info-item,
.param-item,
.system-trace-header p,
.trace-chip,
.trace-fact-label,
.trace-step-desc,
.trace-evidence-list li,
.economic-cost-desc,
.economic-kpi-note,
.economic-chart-note,
.artifact-item-desc,
.artifact-item-path,
.report-header-copy p,
.report-meta,
.report-section-item p,
.report-section-item li,
.markdown-rendered,
.expert-summary,
.expert-metrics,
.debate-message .content,
.arbitration-summary {
  color: rgba(188, 198, 194, 0.82);
}

.info-value,
.trace-fact-value,
.trace-weight-value,
.trace-ranking-name,
.economic-cost-title,
.economic-kpi-label,
.economic-summary-label,
.expert-name,
.debate-message .speaker {
  color: rgba(232, 238, 236, 0.92);
}

.system-trace-shell {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
}

.system-trace-shell::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(88, 232, 144, 0.04), transparent 18%, transparent 82%, rgba(88, 232, 144, 0.03)),
    linear-gradient(rgba(88, 232, 144, 0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(88, 232, 144, 0.022) 1px, transparent 1px);
  background-size: auto, 36px 36px, 36px 36px;
}

.system-trace-header,
.system-trace-topology,
.trace-block {
  position: relative;
  z-index: 1;
}

.trace-chip,
.artifact-item-actions a {
  border-color: rgba(136, 170, 155, 0.16);
  background: rgba(35, 40, 41, 0.9);
}

.chart-container,
.economic-chart-shell,
.artifact-image-shell,
.artifact-placeholder,
.markdown-rendered,
.report-preview-shell {
  background: rgba(24, 29, 30, 0.82);
  border-color: rgba(134, 165, 151, 0.12);
}

.green-chart-card,
.table-card,
.report-section-item--table,
.report-data-table {
  position: relative;
  overflow: hidden;
}

.green-summary-card,
.green-chart-card {
  min-height: 100%;
}

.green-chart-card::before,
.table-card::before,
.report-section-item--table::before,
.report-data-table::before {
  content: '';
  position: absolute;
  left: 18px;
  right: 18px;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(162, 190, 156, 0.18), transparent);
  pointer-events: none;
}

.green-chart-card,
.economic-cost-main {
  padding: 20px;
}

.green-summary-card {
  padding: 18px;
  background:
    radial-gradient(circle at top left, rgba(101, 155, 128, 0.04), transparent 30%),
    linear-gradient(180deg, rgba(43, 49, 49, 0.9), rgba(33, 39, 39, 0.95));
}

.green-chart-card h4,
.table-card h4,
.economic-cost-header h4 {
  margin-bottom: 14px;
}

.green-chart-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background:
    radial-gradient(circle at 50% 0%, rgba(136, 181, 153, 0.09), transparent 42%),
    linear-gradient(180deg, rgba(39, 45, 46, 0.91), rgba(29, 34, 35, 0.96));
}

.chart-container,
.economic-cost-chart {
  border-radius: 18px;
  background:
    radial-gradient(circle at top, rgba(133, 176, 150, 0.055), transparent 55%),
    linear-gradient(180deg, rgba(30, 35, 36, 0.92), rgba(22, 26, 27, 0.95));
  box-shadow:
    inset 0 0 0 1px rgba(139, 172, 158, 0.07),
    inset 0 1px 0 rgba(255, 255, 255, 0.025);
}

.chart-container {
  padding: 10px;
  min-height: 320px;
}

.economic-chart-shell {
  padding: 10px;
  border-radius: 22px;
  background:
    radial-gradient(circle at top left, rgba(104, 155, 129, 0.05), transparent 34%),
    linear-gradient(180deg, rgba(32, 37, 38, 0.9), rgba(23, 27, 28, 0.95));
  box-shadow:
    inset 0 0 0 1px rgba(138, 170, 156, 0.07),
    0 12px 28px rgba(0, 0, 0, 0.18);
}

.economic-cost-chart {
  height: 360px;
}

.economic-chart-note {
  margin-top: 14px;
  background: rgba(37, 42, 43, 0.84);
  border: 1px solid rgba(136, 168, 154, 0.1);
  color: rgba(196, 205, 202, 0.82);
}

.economic-cost-summary {
  padding: 0;
  background:
    radial-gradient(circle at top left, rgba(107, 161, 133, 0.05), transparent 38%),
    linear-gradient(180deg, rgba(34, 39, 40, 0.94), rgba(25, 29, 30, 0.97));
}

.economic-summary-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 100%;
  padding: 18px;
}

.table-card {
  padding: 18px;
  background:
    radial-gradient(circle at top left, rgba(100, 153, 126, 0.03), transparent 32%),
    linear-gradient(180deg, rgba(41, 47, 47, 0.88), rgba(31, 36, 36, 0.94));
}

.report-section-item--table,
.report-data-table {
  padding: 14px;
  border-radius: 22px;
  background:
    radial-gradient(circle at top left, rgba(100, 154, 127, 0.026), transparent 30%),
    linear-gradient(180deg, rgba(44, 50, 51, 0.94), rgba(34, 39, 40, 0.97));
  border: 1px solid rgba(137, 169, 156, 0.11);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.018);
}

.green-section :deep(.el-table),
.cooling-section :deep(.el-table),
.power-section :deep(.el-table),
.report-section :deep(.el-table) {
  --el-table-border-color: rgba(132, 161, 148, 0.12);
  --el-table-header-bg-color: rgba(47, 53, 53, 0.98);
  --el-table-row-hover-bg-color: rgba(62, 69, 69, 0.96);
  background: rgba(31, 36, 37, 0.92);
  color: rgba(228, 234, 231, 0.92);
  box-shadow: inset 0 0 0 1px rgba(135, 166, 152, 0.05);
}

.green-section :deep(.el-table__inner-wrapper),
.cooling-section :deep(.el-table__inner-wrapper),
.power-section :deep(.el-table__inner-wrapper),
.report-section :deep(.el-table__inner-wrapper) {
  border-radius: 16px;
  overflow: hidden;
  background: transparent;
}

.green-section :deep(.el-table th),
.cooling-section :deep(.el-table th),
.power-section :deep(.el-table th),
.report-section :deep(.el-table th) {
  color: rgba(239, 243, 241, 0.95);
  font-weight: 600;
  letter-spacing: 0.03em;
}

.green-section :deep(.el-table td),
.cooling-section :deep(.el-table td),
.power-section :deep(.el-table td),
.report-section :deep(.el-table td) {
  background: rgba(43, 49, 49, 0.95);
  color: rgba(228, 234, 232, 0.93);
  border-color: rgba(132, 161, 148, 0.08);
}

.green-section :deep(.el-table__row:nth-child(even) td),
.cooling-section :deep(.el-table__row:nth-child(even) td),
.power-section :deep(.el-table__row:nth-child(even) td),
.report-section :deep(.el-table__row:nth-child(even) td) {
  background: rgba(47, 53, 53, 0.97);
}

.green-section :deep(.el-table__row:hover > td),
.cooling-section :deep(.el-table__row:hover > td),
.power-section :deep(.el-table__row:hover > td),
.report-section :deep(.el-table__row:hover > td) {
  background: rgba(58, 66, 66, 0.98) !important;
}

.green-section :deep(.el-table::before),
.cooling-section :deep(.el-table::before),
.power-section :deep(.el-table::before),
.report-section :deep(.el-table::before) {
  background: rgba(136, 167, 154, 0.1);
}

.report-content :deep(.el-table__inner-wrapper::before),
.report-content :deep(.el-table--border::before),
.report-content :deep(.el-table--border::after) {
  background: rgba(135, 166, 152, 0.12);
}

.report-content :deep(.el-table) {
  --el-table-border-color: rgba(134, 164, 151, 0.13);
  --el-table-header-bg-color: rgba(46, 52, 52, 0.98);
  --el-table-row-hover-bg-color: rgba(61, 68, 68, 0.96);
  border-radius: 16px;
  overflow: hidden;
  background: rgba(31, 36, 37, 0.95);
  box-shadow: inset 0 0 0 1px rgba(135, 166, 152, 0.06);
}

.report-content :deep(.el-table__inner-wrapper) {
  background: transparent;
  border-radius: 16px;
  overflow: hidden;
}

.report-content :deep(.el-table__header-wrapper),
.report-content :deep(.el-table__body-wrapper) {
  background: transparent;
}

.report-content :deep(.el-table th) {
  padding-top: 12px;
  padding-bottom: 12px;
  background:
    linear-gradient(180deg, rgba(49, 55, 55, 0.98), rgba(41, 47, 47, 0.98));
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: none;
  color: rgba(238, 242, 240, 0.95);
  border-bottom-color: rgba(136, 167, 154, 0.12) !important;
}

.report-content :deep(.el-table td) {
  padding-top: 14px;
  padding-bottom: 14px;
  background: rgba(42, 48, 48, 0.97);
  color: rgba(227, 232, 230, 0.93);
  border-color: rgba(132, 162, 149, 0.08);
}

.report-content :deep(.el-table__row:nth-child(even) td) {
  background: rgba(46, 52, 52, 0.97);
}

.report-content :deep(.el-table__row:hover > td) {
  background: rgba(57, 64, 64, 0.98) !important;
}

.report-content :deep(.el-table td:first-child) {
  background:
    linear-gradient(180deg, rgba(40, 46, 46, 0.98), rgba(34, 39, 39, 0.98));
  color: rgba(240, 244, 242, 0.96);
  font-weight: 600;
}

.report-content :deep(.el-table th:first-child) {
  background:
    linear-gradient(180deg, rgba(52, 58, 58, 0.98), rgba(43, 49, 49, 0.98));
}

.report-content :deep(.el-table tr td + td),
.report-content :deep(.el-table tr th + th) {
  box-shadow: inset 1px 0 0 rgba(136, 166, 153, 0.09);
}

.architecture-diagram {
  padding: 18px;
  border-radius: 18px;
  background:
    linear-gradient(rgba(121, 239, 171, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(121, 239, 171, 0.03) 1px, transparent 1px),
    rgba(20, 24, 29, 0.82);
  background-size: 34px 34px;
  border: 1px solid rgba(121, 239, 171, 0.13);
}

.arch-item,
.stat-item {
  background: rgba(34, 40, 47, 0.92);
  border-color: rgba(121, 239, 171, 0.14);
  color: rgba(236, 243, 240, 0.92);
}

.arch-arrow {
  color: rgba(121, 239, 171, 0.9);
  text-shadow: 0 0 16px rgba(121, 239, 171, 0.26);
}

.economic-cost-panel {
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
}

.economic-cost-item:hover {
  border-color: rgba(121, 239, 171, 0.32);
  background: rgba(42, 58, 49, 0.86);
}

.economic-cost-chart {
  min-height: 360px;
}

@media (max-width: 1200px) {
  .overview-section,
  .green-insight-grid,
  .cooling-section,
  .green-section,
  .power-section,
  .economic-section,
  .economic-cost-panel,
  .report-input-grid,
  .report-executive-layout {
    grid-template-columns: 1fr;
  }

  .overview-section .metrics-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .overview-hero-head {
    grid-template-columns: 1fr;
  }

  .report-cover-grid {
    grid-template-columns: 1fr;
  }

  .report-input-primary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .param-cards,
  .overview-section .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .detail-page::before {
    left: 0;
  }

  .green-insight-grid,
  .param-cards,
  .overview-section .metrics-grid {
    grid-template-columns: 1fr;
  }

  .revision-overview-grid {
    grid-template-columns: 1fr;
  }

  .summary-section-head,
  .info-section-head,
  .report-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .report-decision-banner {
    grid-template-columns: 1fr;
  }

  .report-decision-meta {
    text-align: left;
  }

  .report-content,
  .report-title-section {
    padding: 18px;
  }

  .report-input-summary {
    padding: 18px;
  }
}
</style>
