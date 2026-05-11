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
          <div class="draft-overview-panel">
            <div class="draft-overview-copy">
              <span class="draft-eyebrow">Draft Generation Trace</span>
              <h4>初稿结果由三个后端 Tool 顺序生成，而不是直接给出结论</h4>
              <p>
                后端 `DraftPlanAgent` 会按固定顺序调用 `green_power_allocation`、`cooling-scheme-generator`
                和 `power_supply_config`。下面每张卡片都对应一个真实 Tool，展示它的输入条件、推导过程、
                判断依据和最终输出。
              </p>
            </div>
            <div class="draft-overview-metrics">
              <div class="draft-overview-metric primary">
                <span class="draft-overview-label">调用顺序</span>
                <span class="draft-overview-value">绿电 → 制冷 → 供电</span>
              </div>
              <div class="draft-overview-metric">
                <span class="draft-overview-label">输入基线</span>
                <span class="draft-overview-value">{{ draftPlanTraceOverview.inputBaseline }}</span>
              </div>
              <div class="draft-overview-metric">
                <span class="draft-overview-label">生成原则</span>
                <span class="draft-overview-value">{{ draftPlanTraceOverview.guidingRule }}</span>
              </div>
            </div>
          </div>

          <div class="draft-process-grid">
            <article
              v-for="card in draftPlanTraceCards"
              :key="card.id"
              class="draft-process-card"
              :class="card.toneClass"
            >
              <div class="draft-card-head">
                <div class="draft-card-title-wrap">
                  <span class="draft-card-icon">
                    <el-icon><component :is="card.icon" /></el-icon>
                  </span>
                  <div>
                    <div class="draft-card-title-row">
                      <span class="draft-card-title">{{ card.title }}</span>
                      <span class="draft-card-order">{{ card.order }}</span>
                    </div>
                    <div class="draft-card-tool">{{ card.tool }}</div>
                  </div>
                </div>
                <p class="draft-card-summary">{{ card.summary }}</p>
              </div>

              <section class="draft-card-section">
                <div class="draft-section-title">输出结果</div>
                <div class="draft-result-grid">
                  <div
                    v-for="metric in card.metrics"
                    :key="metric.label"
                    class="draft-result-item"
                  >
                    <span class="draft-result-label">{{ metric.label }}</span>
                    <span class="draft-result-value">{{ metric.value }}</span>
                  </div>
                </div>
              </section>

              <section class="draft-card-section">
                <div class="draft-section-title">输入条件</div>
                <div class="draft-chip-list">
                  <span
                    v-for="input in card.inputs"
                    :key="input"
                    class="draft-chip"
                  >
                    {{ input }}
                  </span>
                </div>
              </section>

              <section
                v-if="card.traceFacts"
                class="draft-card-section"
              >
                <div class="draft-section-title">{{ card.traceFactsTitle || '关键参数' }}</div>
                <div class="draft-fact-grid">
                  <div
                    v-for="fact in card.traceFacts"
                    :key="fact.label"
                    class="draft-fact-item"
                  >
                    <span class="draft-fact-label">{{ fact.label }}</span>
                    <span class="draft-fact-value">{{ fact.value }}</span>
                  </div>
                </div>
              </section>

              <section class="draft-card-section">
                <div class="draft-section-title">生成过程</div>
                <div class="draft-step-list">
                  <div
                    v-for="(step, index) in card.steps"
                    :key="step.title"
                    class="draft-step-item"
                  >
                    <span class="draft-step-index">{{ index + 1 }}</span>
                    <div class="draft-step-copy">
                      <div class="draft-step-title">{{ step.title }}</div>
                      <div class="draft-step-desc">{{ step.description }}</div>
                    </div>
                  </div>
                </div>
              </section>

              <section class="draft-card-section">
                <div class="draft-section-title">判断依据</div>
                <ul class="draft-evidence-list">
                  <li
                    v-for="evidence in card.evidences"
                    :key="evidence"
                  >
                    {{ evidence }}
                  </li>
                </ul>
              </section>

              <section
                v-if="card.optimization"
                class="draft-card-section draft-card-section-optimization"
              >
                <div class="draft-section-title">多目标寻优</div>
                <div class="draft-weight-grid">
                  <div
                    v-for="weight in card.optimization.weights"
                    :key="weight.label"
                    class="draft-weight-item"
                  >
                    <span class="draft-weight-label">{{ weight.label }}</span>
                    <span class="draft-weight-value">{{ weight.value }}</span>
                  </div>
                </div>
                <div class="draft-ranking-list">
                  <div
                    v-for="candidate in card.optimization.ranking"
                    :key="candidate.name"
                    class="draft-ranking-item"
                    :class="{ 'is-winner': candidate.isWinner }"
                  >
                    <div class="draft-ranking-head">
                      <span class="draft-ranking-order">#{{ candidate.rank }}</span>
                      <span class="draft-ranking-name">{{ candidate.name }}</span>
                      <span class="draft-ranking-score">综合得分 {{ candidate.score }}</span>
                    </div>
                    <div class="draft-ranking-tags">
                      <span
                        v-for="tag in candidate.tags"
                        :key="tag"
                        class="draft-ranking-tag"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </div>
                </div>
              </section>
            </article>
          </div>
        </div>
      </div>

      <div v-if="currentNodeIndex >= 2 || anyNodeCompleted(2)" class="stage-panel" :class="{ active: currentNodeIndex === 2 }">
        <div class="stage-header">
          <h3><el-icon class="stage-icon"><Tools /></el-icon> {{ workflowNodes[2].name }}</h3>
          <el-tag :type="getNodeTagType(2)">{{ getNodeStatus(2) }}</el-tag>
        </div>
        <div v-if="nodeResults.costCalculation" class="cost-panel">
          <el-card class="cost-card">
            <div class="cost-layout">
              <section class="cost-visual-block">
                <div class="cost-block-header">
                  <div>
                    <div class="cost-block-title">成本项视图</div>
                    <div class="cost-block-subtitle">点击扇区查看该部分的成本细化与测算口径</div>
                  </div>
                  <el-tag effect="plain" round>总投资与预算口径保留原始计算结果</el-tag>
                </div>
                <div class="cost-chart-shell">
                  <div ref="costChartRef" class="cost-chart"></div>
                </div>
                <div class="cost-chart-note">
                  当前总投资口径已统一为供电系统、绿电系统与制冷系统三部分之和，点击任一扇区可查看该部分的真实成本细化。
                </div>
                <div class="cost-legend">
                  <button
                    v-for="segment in costStructureSegments"
                    :key="segment.key"
                    type="button"
                    class="cost-legend-item"
                    @click="openCostDetail(segment.key)"
                  >
                    <span class="legend-swatch" :style="{ background: segment.color }"></span>
                    <span class="legend-copy">
                      <span class="legend-title">{{ segment.name }}</span>
                      <span class="legend-desc">{{ segment.shortDescription }}</span>
                    </span>
                    <span class="legend-meta">
                      <span class="legend-value">{{ formatWithUnit(segment.amount, '万元', 0) }}</span>
                      <span class="legend-tag">
                        纳入总投资
                      </span>
                    </span>
                  </button>
                </div>
              </section>

              <aside class="cost-summary-panel">
                <div class="cost-kpi-grid">
                  <div class="cost-kpi-card strong span-wide">
                    <span class="kpi-label">项目总投资</span>
                    <span class="kpi-value">{{ formatWithUnit(nodeResults.costCalculation.totalCost, '万元', 0) }}</span>
                    <span class="kpi-note">经济分析口径</span>
                  </div>
                  <div class="cost-kpi-card">
                    <span class="kpi-label">预算约束</span>
                    <span class="kpi-value" :class="nodeResults.costCalculation.isOverBudget ? 'over-budget' : 'under-budget'">
                      {{ formatWithUnit(nodeResults.costCalculation.budget, '万元', 0) }}
                    </span>
                    <span class="kpi-note">配置参数基准</span>
                  </div>
                  <div class="cost-kpi-card">
                    <span class="kpi-label">预算差额</span>
                    <span class="kpi-value" :class="nodeResults.costCalculation.isOverBudget ? 'over-budget' : 'under-budget'">
                      {{ formatWithUnit(Math.abs(nodeResults.costCalculation.budgetDelta), '万元', 0) }}
                    </span>
                    <span class="kpi-note">
                      {{
                        nodeResults.costCalculation.isOverBudget
                          ? '超预算'
                          : Number(nodeResults.costCalculation.budgetDelta) === 0
                            ? '预算持平'
                            : '预算结余'
                      }}
                    </span>
                  </div>
                </div>

                <div class="cost-summary-heading">
                  <span class="summary-heading-title">成本清单</span>
                  <span class="summary-heading-note">与左侧图表使用同一投资口径</span>
                </div>
                <div class="cost-summary-strip">
                  <div
                    v-for="segment in includedCostSegments"
                    :key="segment.key"
                    class="cost-summary-row"
                  >
                    <span class="summary-dot" :style="{ background: segment.color }"></span>
                    <span class="summary-label">{{ segment.name }}</span>
                    <span class="summary-value">{{ formatWithUnit(segment.amount, '万元', 0) }}</span>
                  </div>
                </div>
              </aside>
            </div>

            <div v-if="nodeResults.costCalculation.isOverBudget" class="budget-warning">
              <el-icon class="warning-icon"><Warning /></el-icon>
              <span>超出预算 {{ nodeResults.costCalculation.budgetDelta }} 万元，正在重新优化方案...</span>
            </div>
            <div v-else class="budget-success">
              <el-icon class="success-icon"><Check /></el-icon>
              <span>
                {{
                  Number(nodeResults.costCalculation.budgetDelta) === 0
                    ? '预算校验通过，当前方案与预算上限持平'
                    : `预算校验通过，结余 ${Math.abs(nodeResults.costCalculation.budgetDelta)} 万元`
                }}
              </span>
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
          <section class="debate-overview">
            <div class="debate-overview-copy">
              <span class="debate-eyebrow">Multi-Agent Debate Review</span>
              <h4>专家观点在这里完成交叉校验与共识收敛</h4>
              <p>
                以轮次为单位展示多位专家的发言、观点冲突与收束结果，让辩论过程从流水记录变成可读的评审面板。
              </p>
            </div>
            <div class="debate-metrics">
              <div class="debate-metric primary">
                <span class="debate-metric-label">当前轮次</span>
                <span class="debate-metric-value">第 {{ debateResults.currentRound }} 轮</span>
              </div>
              <div class="debate-metric">
                <span class="debate-metric-label">共识度</span>
                <span class="debate-metric-value consensus">{{ formatPercent(debateResults.consensusScore, 0) }}</span>
              </div>
              <div class="debate-metric">
                <span class="debate-metric-label">发言条数</span>
                <span class="debate-metric-value">{{ debateStatementCount }}</span>
              </div>
            </div>
          </section>

          <div v-if="debateParticipants.length" class="debate-participant-strip">
            <div
              v-for="participant in debateParticipants"
              :key="participant.name"
              class="debate-participant"
              :class="participant.className"
            >
              <span class="participant-dot" :style="{ background: participant.color }"></span>
              <span class="participant-name">{{ participant.name }}</span>
            </div>
          </div>

          <div class="debate-board">
            <section class="debate-main-column">
              <div ref="debateChatRef" class="debate-chat-messages">
                <template v-for="(round, roundIndex) in debateResults.rounds" :key="roundIndex">
                  <article class="debate-round-block">
                    <div class="round-divider">
                      <div class="round-badge">Round {{ String(round.number).padStart(2, '0') }}</div>
                      <div class="round-copy">
                        <span class="round-label">第 {{ round.number }} 轮辩论</span>
                        <span class="round-meta">{{ round.statements.length }} 条发言</span>
                      </div>
                    </div>
                    <div class="round-statements">
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
                          <div class="speaker-meta">
                            <span class="speaker-name">{{ statement.speaker }}</span>
                            <span class="speaker-role">{{ getExpertRole(statement.speaker) }}</span>
                          </div>
                        </div>
                        <div class="message-bubble">
                          <span class="message-content">{{ statement.content }}</span>
                        </div>
                      </div>
                    </div>
                  </article>
                </template>
                <div v-if="debateResults.rounds.length === 0" class="empty-chat">
                  <p>辩论尚未开始...</p>
                </div>
              </div>
            </section>

            <aside
              v-if="debateResults.summary && debateResults.summary.suggestions.length > 0"
              class="debate-summary-card"
            >
              <div class="debate-summary-header">
                <div class="debate-summary-title">
                  <h4><el-icon><Lightbulb /></el-icon> 辩论纪要</h4>
                  <p>汇总仲裁前保留下来的关键建议，用于快速查看辩论输出。</p>
                </div>
                <div class="debate-summary-badge">共 {{ debateResults.summary.suggestions.length }} 条</div>
              </div>
              <div class="suggestions-list">
                <div v-for="(suggestion, i) in debateResults.summary.suggestions" :key="i" class="suggestion-item">
                  <el-icon class="suggestion-icon"><CheckCircle /></el-icon>
                  <span>{{ suggestion }}</span>
                </div>
              </div>
            </aside>
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

    <el-dialog
      v-model="costDetailDialogVisible"
      width="560px"
      destroy-on-close
      class="cost-detail-dialog"
    >
      <template #header>
        <div class="cost-detail-header">
          <span class="detail-dot" :style="{ background: activeCostSegment.color }"></span>
          <div class="detail-header-copy">
            <div class="detail-title">{{ activeCostSegment.name }}</div>
            <div class="detail-subtitle">{{ activeCostSegment.summary }}</div>
          </div>
        </div>
      </template>

      <div class="cost-detail-body">
        <div class="cost-detail-kpi">
          <div class="detail-kpi-item">
            <span class="detail-kpi-label">当前金额</span>
            <span class="detail-kpi-value">{{ formatWithUnit(activeCostSegment.amount, '万元', 0) }}</span>
          </div>
          <div class="detail-kpi-item">
            <span class="detail-kpi-label">计入口径</span>
            <span class="detail-kpi-value">纳入项目总投资</span>
          </div>
        </div>

        <div class="cost-detail-list">
          <div
            v-for="detail in activeCostSegment.details"
            :key="detail.label"
            class="cost-detail-row"
          >
            <span class="detail-row-label">{{ detail.label }}</span>
            <span class="detail-row-value">{{ detail.value }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
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
const costChartRef = ref(null)
const workflowId = ref('mock-workflow-001')
const completedNodes = ref(new Set())
let mockTimer = null
let currentStepIndex = 0
let costChart = null

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
const costDetailDialogVisible = ref(false)
const activeCostDetailKey = ref('green_power')

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

const coolingCostSnapshot = computed(() => {
  const coolingEco = mockSolutionData.intermediate_results.draft_plan_agent.full_output.cooling_result.economic_indicators || {}
  return {
    initialInvestment: toNumber(coolingEco.initial_investment, 0),
    annualOpCost: toNumber(coolingEco.annual_op_cost, 0),
    annualElectricityCost: toNumber(coolingEco.annual_electricity_cost, 0),
    lcoe: toNumber(coolingEco.lcoe, null)
  }
})

const draftPlanTraceOverview = computed(() => {
  const req = mockSolutionData.intermediate_results.requirement_parser.requirement || {}
  return {
    inputBaseline: `${req.location || '--'} · ${formatNumber(toNumber(req.planned_load_kw, 0) / 1000, 2)} MW · 绿电目标 ${formatPercent(req.green_power_ratio, 0)}`,
    guidingRule: '先满足目标约束，再生成可执行初稿'
  }
})

const draftPlanTraceCards = computed(() => {
  const req = mockSolutionData.intermediate_results.requirement_parser.requirement || {}
  const draft = mockSolutionData.intermediate_results.draft_plan_agent.full_output || {}
  const greenFull = draft.green_power_result || {}
  const green = greenFull.optimization || {}
  const greenInputs = greenFull.inputs || {}
  const greenFiles = greenFull.generated_files || {}
  const cooling = draft.cooling_result || {}
  const power = draft.power_supply_plan || {}
  const coolingOptimization = cooling.optimization_summary || {}
  const coolingWeights = coolingOptimization.objective_weights || {}
  const coolingRanking = Array.isArray(cooling.all_strategy_scores) ? cooling.all_strategy_scores : []
  const greenLoadMw = toNumber(req.planned_load_kw, 0) / 1000
  const annualTemperature = 15
  const powerRaw = power.raw_json || {}
  const powerFactor = toNumber(powerRaw.power_factor, 0.9)
  const totalLoadMw = toNumber(powerRaw.total_load_mw, greenLoadMw)
  const totalLoadMva = toNumber(powerRaw.total_load_mva, totalLoadMw / powerFactor)
  const voltageCriteria = totalLoadMva >= 100
    ? '命中 220kV 阈值（>=100MVA）'
    : totalLoadMva >= 40
      ? '命中 110kV 阈值（>=40MVA）'
      : totalLoadMva >= 30
        ? '命中 66kV 阈值（>=30MVA）'
        : '命中 35kV 阈值（<30MVA）'

  return [
    {
      id: 'green-power',
      order: 'Tool 01',
      title: '绿电分配方案',
      tool: 'green_power_allocation',
      icon: Edit,
      toneClass: 'tone-green',
      summary: '先根据项目所在地生成风光出力曲线，再在绿电目标约束下优化风电、光伏和储能装机配比。',
      metrics: [
        { label: '光伏容量', value: `${formatNumber(green.pv_capacity_mw, 2)} MW` },
        { label: '风电容量', value: `${formatNumber(green.wind_capacity_mw, 2)} MW` },
        { label: '储能容量', value: `${formatNumber(green.storage_capacity_mwh, 2)} MWh` },
        { label: '绿电占比', value: formatPercent(green.achieved_green_ratio) }
      ],
      inputs: [
        `项目位置：${req.location || '--'}`,
        `负荷规模：${formatNumber(greenLoadMw, 2)} MW`,
        `绿电目标：${formatPercent(req.green_power_ratio, 0)}`,
        `仿真时长：${greenInputs.sim_hours || req.sim_hours || 168} h`,
        `气象年份：${greenInputs.year || req.year || 2025}`,
        '容量边界：风电/光伏 1-500MW，储能 20-500MWh'
      ],
      traceFactsTitle: '优化设定',
      traceFacts: [
        { label: '仿真模式', value: greenFull.pv_profile?.mode || '--' },
        { label: '资源曲线', value: '先生成 PV/Wind 单位出力曲线' },
        { label: '负荷文件', value: greenFiles.load_csv ? '已载入负荷系数 CSV' : '使用默认负荷曲线' },
        { label: 'DE 参数', value: `maxiter ${greenInputs.maxiter || 60} · popsize ${greenInputs.popsize || 10} · seed ${greenInputs.seed || 42}` },
        { label: '搜索边界', value: `风/光 ${greenInputs.bounds?.wind_capacity_bounds?.[0] || 1}-${greenInputs.bounds?.wind_capacity_bounds?.[1] || 500}MW，储能 ${greenInputs.bounds?.storage_capacity_bounds?.[0] || 20}-${greenInputs.bounds?.storage_capacity_bounds?.[1] || 500}MWh` },
        { label: '结果文件', value: greenFiles.balance_plot ? '同步输出绿电平衡图' : '仅返回优化结果' }
      ],
      steps: [
        {
          title: '根据仿真时长决定模拟模式',
          description: `当仿真时长大于 24h 时切换到 8760h 年度模式，当前按照 ${greenInputs.sim_hours || req.sim_hours || 168}h 输入进入资源曲线生成流程。`
        },
        {
          title: '分别生成光伏与风电出力曲线',
          description: 'Tool 会先调用 PV 与 Wind 子工具，按地点、年份以及风机/光伏参数生成单位出力 CSV。'
        },
        {
          title: '载入负荷曲线并解析装机边界',
          description: '将数据中心总负荷、默认或指定的负荷 CSV、风光储容量边界和展示起始小时一起整理成优化输入。'
        },
        {
          title: '执行差分进化容量优化',
          description: '在风电、光伏、储能三维搜索空间内迭代求解，目标是在满足绿电比例约束下最小化总投资成本。'
        },
        {
          title: '输出装机结果与平衡图',
          description: '在得到最优容量组合后，同时返回风光储装机结果、目标达成情况以及绿电功率平衡图文件。'
        }
      ],
      evidences: [
        '后端 Tool 先生成 PV/Wind 曲线，再进入容量优化，不是直接对装机容量做静态估算。',
        `当前输入负荷为 ${formatNumber(greenLoadMw, 2)} MW，会直接影响风光储的容量上限需求。`,
        `绿电目标设置为 ${formatPercent(req.green_power_ratio, 0)}，目标越高，通常需要更大的装机与储能。`,
        `DE 优化器当前使用 maxiter ${greenInputs.maxiter || 60}、popsize ${greenInputs.popsize || 10}、seed ${greenInputs.seed || 42}。`,
        'Tool 使用差分进化算法进行容量优化，而不是手工指定风光储配比。'
      ]
    },
    {
      id: 'cooling-scheme',
      order: 'Tool 02',
      title: '制冷方案',
      tool: 'cooling-scheme-generator',
      icon: Tools,
      toneClass: 'tone-cooling',
      summary: '结合负荷密度、PUE/WUE 目标、环境条件和优先级，筛选可行制冷技术并给出 KPI 与经济指标。',
      metrics: [
        { label: '推荐技术', value: cooling.cooling_technology || '--' },
        { label: '预测 PUE', value: formatNumber(cooling.estimated_pue, 2) },
        { label: '预测 WUE', value: formatNumber(cooling.predicted_wue, 2) },
        { label: '制冷功耗', value: `${formatNumber(cooling.cooling_power_consumption, 0)} kW` }
      ],
      inputs: [
        `项目位置：${req.location || '--'}`,
        `年均温度：${annualTemperature.toFixed(1)} ℃`,
        `IT 负荷：${formatNumber(toNumber(req.planned_load_kw, 0), 0)} kW`,
        `功率密度：${formatNumber(req.computing_power_density, 2)} kW/机柜`,
        `PUE 目标：${formatNumber(req.pue_target, 2)}`,
        `优先级：${req.priority || 'economic'}`,
        '优化目标：PUE / WUE / TCO / CUE / WHR'
      ],
      steps: [
        {
          title: '归并用户需求与显式参数',
          description: 'Tool 会先合并需求解析结果和显式传入参数，统一得到负荷、功率密度、PUE/WUE 与优先级。'
        },
        {
          title: '筛选可行制冷技术路线',
          description: '结合环境温度、算力密度与目标能效，先排除不适合当前工况的制冷方案，只保留可比较候选。'
        },
        {
          title: '执行多目标加权寻优',
          description: '对每个可行候选同时评估 PUE、WUE、TCO、CUE 与余热回收能力，根据优先级动态加权并选出综合得分最优的方案。'
        },
        {
          title: '输出 KPI 与经济指标',
          description: '在最优技术确定后，再同步计算预测 PUE、WUE、制冷功耗、初始投资和运维成本。'
        }
      ],
      evidences: [
        '后端代码明确指出：PUE/WUE 目标越严格，越倾向选择能效更高的方案。',
        `当前功率密度为 ${formatNumber(req.computing_power_density, 2)} kW/机柜，会影响可行技术的筛选范围。`,
        `环境侧输入包含年均温度 ${annualTemperature.toFixed(1)} ℃，会影响制冷工况和余热回收判断。`,
        `最终输出不仅给出“技术名称”，还返回 PUE、WUE、功耗和经济指标，因此结果具备可追溯性。`,
        '后端寻优目标明确包含 PUE、WUE、TCO、CUE、WHR 五项，不是单一能效排序。'
      ],
      optimization: {
        weights: [
          { label: 'PUE 权重', value: formatPercent(coolingWeights.PUE, 0) },
          { label: 'WUE 权重', value: formatPercent(coolingWeights.WUE, 0) },
          { label: 'TCO 权重', value: formatPercent(coolingWeights.TCO, 0) },
          { label: 'CUE 权重', value: formatPercent(coolingWeights.CUE, 0) },
          { label: 'WHR 权重', value: formatPercent(coolingWeights.WHR, 0) }
        ],
        ranking: coolingRanking.slice(0, 4).map(item => ({
          rank: item.ranking ?? '-',
          name: item.strategy || '--',
          score: formatNumber(item.total_score, 2),
          isWinner: (item.strategy || '') === (coolingOptimization.selected_strategy || cooling.cooling_technology),
          tags: [
            `PUE ${formatNumber(item.pue, 2)}`,
            `WUE ${formatNumber(item.wue, 2)}`,
            `TCO ${formatNumber(item.tco, 2)}`,
            `WHR ${formatNumber(item.whr, 2)}`
          ]
        }))
      }
    },
    {
      id: 'power-supply',
      order: 'Tool 03',
      title: '供电方案',
      tool: 'power_supply_config',
      icon: Files,
      toneClass: 'tone-power',
      summary: '依据机房等级、总负荷与 PUE 目标，按标准化规则自动匹配外部电压、冗余结构和母线方案。',
      metrics: [
        { label: '方案名称', value: power.scheme_name || '--' },
        { label: '外部电压', value: power.external_voltage || '--' },
        { label: '冗余配置', value: power.redundancy_logic || '--' },
        { label: '母线类型', value: power.bus_type || '--' }
      ],
      inputs: [
        `机房等级：${powerRaw.machine_room_grade || req.machine_room_grade || '--'}`,
        `总负荷：${formatNumber(totalLoadMw, 2)} MW`,
        `PUE 目标：${formatNumber(req.pue_target, 2)}`,
        `功率因数：${formatNumber(powerFactor, 2)}`,
        '依据标准：GB 50174-2017 / YD-T 5235-2019'
      ],
      traceFactsTitle: '规则命中',
      traceFacts: [
        { label: '等级模板', value: `${powerRaw.machine_room_grade || 'A'} 级标准化供电模板` },
        { label: '负荷折算', value: `${formatNumber(totalLoadMw, 2)} MW ÷ ${formatNumber(powerFactor, 2)} = ${formatNumber(totalLoadMva, 2)} MVA` },
        { label: '电压阈值', value: voltageCriteria },
        { label: '外部接入', value: power.external_source_type || '--' },
        { label: '次级配电', value: power.secondary_voltage || '10 kV' },
        { label: '单位成本', value: `${formatNumber(powerRaw.cost_per_mw, 2)} 万元/MW` }
      ],
      steps: [
        {
          title: '读取机房等级对应的标准模板',
          description: 'Tool 首先从内置方案库读取 A+/A/B/C 四类标准模板，锁定外部电源、主配变冗余、母线与柴油机策略基线。'
        },
        {
          title: '将总负荷从 MW 折算为 MVA',
          description: `后端按功率因数 ${formatNumber(powerFactor, 2)} 进行折算，当前 ${formatNumber(totalLoadMw, 2)} MW 约等于 ${formatNumber(totalLoadMva, 2)} MVA。`
        },
        {
          title: '按阈值匹配外部电压等级',
          description: '系统会依次检查 220kV、110kV、66kV、35kV 的容量阈值，命中的首个档位即成为外部电压方案。'
        },
        {
          title: '确定次级配电与配变组织方式',
          description: '若未显式指定次级电压，默认采用 10kV，并按照机房等级匹配 2.5MVA 配变组织方式。'
        },
        {
          title: '拼接详细理由并输出结构化配置',
          description: '最终返回方案名称、外部电压、冗余逻辑、母线接线、柴油机策略，以及 reasons/raw_json 两层可追溯结果。'
        }
      ],
      evidences: [
        '后端 Tool 不是自由生成文案，而是先从标准化方案库中选择等级模板。',
        `当前总负荷约为 ${formatNumber(totalLoadMw, 2)} MW，会参与 MW→MVA 折算并决定外部电压档位。`,
        `折算后的容量约为 ${formatNumber(totalLoadMva, 2)} MVA，因此当前命中规则为“${voltageCriteria}”。`,
        '当外部电压和次级配电没有 override 时，工具会完全按阈值和默认策略自动选择。',
        '最终结果包含 detailed reasons 文本和 raw_json 结构，因此每个配置项都能追溯到标准规则。'
      ]
    }
  ]
})

const costStructureSegments = computed(() => {
  if (!nodeResults.costCalculation) return []

  const draft = mockSolutionData.intermediate_results.draft_plan_agent.full_output
  const cost = mockSolutionData.intermediate_results.cost_calculation.full_output.economic_analysis_result
  const greenDetails = cost.capex_breakdown?.details || {}
  const coolingEco = draft.cooling_result?.economic_indicators || {}

  return [
    {
      key: 'power_supply',
      name: '供电系统成本',
      amount: toNumber(cost.capex_breakdown?.power_supply_system_lakh, 0),
      color: '#16b8c4',
      includedInTotal: true,
      shortDescription: '35kV 双路接入与高可靠供配电架构',
      summary: '当前总投资口径中的供电系统建设成本，反映电压等级、冗余与配电架构带来的 CAPEX。',
      details: [
        { label: '系统方案', value: draft.power_supply_plan?.scheme_name || '--' },
        { label: '外部电压', value: draft.power_supply_plan?.external_voltage || '--' },
        { label: '冗余配置', value: draft.power_supply_plan?.redundancy_logic || '--' },
        { label: '母线类型', value: draft.power_supply_plan?.bus_type || '--' },
        { label: '单位成本', value: `${formatNumber(draft.power_supply_plan?.raw_json?.cost_per_mw, 2)} 万元/MW` }
      ]
    },
    {
      key: 'green_power',
      name: '绿电系统成本',
      amount: toNumber(cost.capex_breakdown?.green_power_system_lakh, 0),
      color: '#18b26b',
      includedInTotal: true,
      shortDescription: '风光储协同配置的绿电建设成本',
      summary: '当前总投资口径中的绿电系统建设成本，点击后可查看风电、光伏和储能的真实拆分。',
      details: [
        { label: '风电 CAPEX', value: `${formatNumber(greenDetails.wind_capex_lakh, 0)} 万元` },
        { label: '光伏 CAPEX', value: `${formatNumber(greenDetails.pv_capex_lakh, 0)} 万元` },
        { label: '储能 CAPEX', value: `${formatNumber(greenDetails.storage_capex_lakh, 0)} 万元` },
        { label: '风电装机容量', value: `${formatNumber(draft.green_power_result?.optimization?.wind_capacity_mw, 2)} MW` },
        { label: '光伏装机容量', value: `${formatNumber(draft.green_power_result?.optimization?.pv_capacity_mw, 2)} MW` },
        { label: '储能容量', value: `${formatNumber(draft.green_power_result?.optimization?.storage_capacity_mwh, 2)} MWh` }
      ]
    },
    {
      key: 'cooling',
      name: '制冷系统成本',
      amount: toNumber(coolingEco.initial_investment, 0),
      color: '#d99a27',
      includedInTotal: true,
      shortDescription: '制冷方案经济指标中的建设投入',
      summary: '制冷系统投资现已并入总投资口径，用于与供电、绿电系统共同构成完整 CAPEX 视图。',
      details: [
        { label: '推荐技术', value: draft.cooling_result?.cooling_technology || '--' },
        { label: '初始投资', value: `${formatNumber(coolingEco.initial_investment, 0)} 万元` },
        { label: '年运维成本', value: `${formatNumber(coolingEco.annual_op_cost, 0)} 万元` },
        { label: '年电费', value: `${formatNumber(coolingEco.annual_electricity_cost, 0)} 万元` },
        { label: 'LCOE', value: coolingEco.lcoe != null ? `${formatNumber(coolingEco.lcoe, 2)} 元/kWh` : '--' }
      ]
    }
  ]
})

const includedCostSegments = computed(() => costStructureSegments.value.filter(segment => segment.includedInTotal))

const totalInvestmentWithCooling = computed(() => {
  return includedCostSegments.value.reduce((sum, segment) => sum + toNumber(segment.amount, 0), 0)
})

const activeCostSegment = computed(() => {
  return costStructureSegments.value.find(segment => segment.key === activeCostDetailKey.value) || costStructureSegments.value[0] || {
    key: '',
    name: '--',
    amount: 0,
    color: '#18b26b',
    includedInTotal: true,
    summary: '',
    details: []
  }
})

const debateStatementCount = computed(() => {
  return debateResults.value?.rounds?.reduce((sum, round) => sum + round.statements.length, 0) ?? 0
})

const debateParticipants = computed(() => {
  const speakers = debateResults.value?.rounds?.flatMap(round => round.statements.map(statement => statement.speaker)) ?? []
  return Array.from(new Set(speakers)).map((name) => ({
    name,
    color: getExpertColor(name),
    className: getExpertClass(name)
  }))
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

const openCostDetail = (segmentKey) => {
  activeCostDetailKey.value = segmentKey
  costDetailDialogVisible.value = true
}

const initCostChart = () => {
  if (!costChartRef.value || !nodeResults.costCalculation || !costStructureSegments.value.length) return
  if (costChart) {
    costChart.dispose()
  }

  costChart = echarts.init(costChartRef.value)
  costChart.setOption({
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
          `<div>金额：${formatWithUnit(segment.amount, '万元', 0)}</div>`,
          `<div style="margin-top:4px;color:#9fe3bf;">纳入项目总投资</div>`
        ].join('')
      }
    },
    series: [
      {
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
          value: segment.amount,
          name: segment.name,
          itemStyle: { color: segment.color }
        }))
      }
    ],
    graphic: [
      {
        type: 'group',
        left: 'center',
        top: '40%',
        children: [
          {
            type: 'text',
            style: {
              text: '成本项视图',
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
              text: formatWithUnit(totalInvestmentWithCooling.value, '万元', 0),
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
              text: '当前总投资',
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

  costChart.off('click')
  costChart.on('click', (params) => {
    const segment = costStructureSegments.value.find(item => item.name === params.name)
    if (segment) {
      openCostDetail(segment.key)
    }
  })
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
      const coolingInvestment = toNumber(mockSolutionData.intermediate_results.draft_plan_agent.full_output.cooling_result?.economic_indicators?.initial_investment, 0)
      const recalculatedTotal = toNumber(cost.capex_breakdown.power_supply_system_lakh, 0) +
        toNumber(cost.capex_breakdown.green_power_system_lakh, 0) +
        coolingInvestment
      const budgetConstraint = toNumber(cost.budget_constraint_lakh, 0)
      const budgetDelta = budgetConstraint - recalculatedTotal
      nodeResults.costCalculation = {
        powerSupplyCost: cost.capex_breakdown.power_supply_system_lakh,
        greenPowerCost: cost.capex_breakdown.green_power_system_lakh,
        coolingCost: coolingInvestment,
        totalCost: recalculatedTotal,
        budget: budgetConstraint,
        isOverBudget: budgetDelta < 0,
        budgetDelta
      }
      addLog(`成本计算: 总投资${recalculatedTotal}万元`, budgetDelta < 0 ? 'warning' : 'success')
      nextTick(() => {
        activeCostDetailKey.value = 'green_power'
        initCostChart()
      })
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
      finalSolution.totalCost = nodeResults.costCalculation?.totalCost ?? totalInvestmentWithCooling.value
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
  activeCostDetailKey.value = 'green_power'
  costDetailDialogVisible.value = false
  if (costChart) {
    costChart.dispose()
    costChart = null
  }
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

const getExpertRole = (speaker) => {
  if (speaker.includes('Economic') || speaker.includes('Zhang') || speaker.includes('经济性')) return '经济性视角'
  if (speaker.includes('Reliability') || speaker.includes('Li') || speaker.includes('可靠性')) return '供电可靠性视角'
  if (speaker.includes('Environmental') || speaker.includes('Wang') || speaker.includes('环保性')) return '环保性视角'
  return '综合评审视角'
}

const goToDetail = () => {
  const solutionId = localStorage.getItem('currentSolutionId') || workflowId.value
  if (!solutionId) {
    ElMessage.error('未找到可用方案ID，请稍后重试')
    return
  }
  router.push(`/detail/${solutionId}`)
}

const handleResize = () => {
  if (costChart) {
    costChart.resize()
  }
}

onMounted(() => {
  startMockWorkflow()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (mockTimer) clearTimeout(mockTimer)
  window.removeEventListener('resize', handleResize)
  if (costChart) {
    costChart.dispose()
    costChart = null
  }
})
</script>

<style scoped>
.generate-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
  min-height: calc(100% - 20px);
  overflow-y: auto;
}

.progress-section {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border-radius: 22px;
  padding: 24px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.progress-header h2 {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.progress-percent {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-dark);
}

.full-workflow {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 26px;
  position: relative;
  padding-bottom: 36px;
}

.full-workflow::before {
  content: '';
  position: absolute;
  top: 18px;
  left: 3%;
  right: 3%;
  height: 2px;
  background: linear-gradient(90deg, color-mix(in oklab, var(--primary-color) 20%, var(--border-default)) 0%, var(--border-default) 100%);
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
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: color-mix(in oklab, var(--bg-panel) 84%, var(--border-default) 16%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: var(--text-placeholder);
  font-weight: 600;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-light);
}

.workflow-node.active .node-icon {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: rgba(249, 253, 250, 0.98);
  border-color: color-mix(in oklab, var(--primary-color) 32%, transparent);
  box-shadow: 0 14px 24px color-mix(in oklab, var(--primary-color) 20%, transparent);
}

.workflow-node.completed .node-icon {
  background: linear-gradient(180deg, color-mix(in oklab, var(--accent-color) 86%, white) 0%, var(--accent-dark) 100%);
  color: rgba(249, 253, 250, 0.98);
  border-color: color-mix(in oklab, var(--accent-color) 28%, transparent);
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
  color: var(--text-secondary);
  text-align: center;
  max-width: 80px;
  line-height: 1.5;
}

.workflow-node.active .node-name,
.workflow-node.completed .node-name {
  color: var(--text-primary);
  font-weight: 500;
}

.node-tooltip {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: #1F2329;
  color: rgba(247, 252, 248, 0.96);
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-fast);
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
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.stage-panel {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 20px;
  padding: 22px;
  border: 1px solid var(--border-light);
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.stage-panel.active {
  border-color: color-mix(in oklab, var(--primary-color) 22%, var(--border-default));
  box-shadow: var(--shadow-hover);
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.stage-header h3 {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.stage-icon {
  color: var(--primary-dark);
}

.result-card {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.result-content p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 16px;
}

.result-metrics {
  display: flex;
  gap: 30px;
}

.draft-overview-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.95fr);
  gap: 18px;
  padding: 20px;
  margin-bottom: 18px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 34%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 0%, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 14%, var(--border-default));
}

.draft-overview-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 64ch;
}

.draft-eyebrow {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.draft-overview-copy h4 {
  font-size: 24px;
  line-height: 1.22;
  font-weight: 700;
  color: var(--text-primary);
  text-wrap: balance;
}

.draft-overview-copy p {
  font-size: 13px;
  line-height: 1.75;
  color: var(--text-secondary);
}

.draft-overview-metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.draft-overview-metric {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  min-height: 94px;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.draft-overview-metric.primary {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 10%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.draft-overview-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.draft-overview-value {
  font-size: 16px;
  line-height: 1.5;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-process-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.draft-process-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 100%;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.draft-process-card.tone-green {
  background: linear-gradient(180deg, color-mix(in oklab, #18b26b 7%, var(--bg-card)) 0%, color-mix(in oklab, #18b26b 3%, var(--bg-panel)) 100%);
}

.draft-process-card.tone-cooling {
  background: linear-gradient(180deg, color-mix(in oklab, #16b8c4 7%, var(--bg-card)) 0%, color-mix(in oklab, #16b8c4 3%, var(--bg-panel)) 100%);
}

.draft-process-card.tone-power {
  background: linear-gradient(180deg, color-mix(in oklab, #9b8cff 7%, var(--bg-card)) 0%, color-mix(in oklab, #9b8cff 3%, var(--bg-panel)) 100%);
}

.draft-card-head {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.draft-card-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.draft-card-icon {
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
  color: var(--primary-dark);
}

.draft-card-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.draft-card-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-card-order {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-placeholder);
  font-weight: 700;
}

.draft-card-tool {
  margin-top: 4px;
  font-size: 12px;
  color: var(--primary-dark);
  font-weight: 600;
}

.draft-card-summary {
  font-size: 13px;
  line-height: 1.75;
  color: var(--text-secondary);
}

.draft-card-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.draft-section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.draft-result-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 84px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.draft-result-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.draft-result-value {
  font-size: 14px;
  line-height: 1.55;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.draft-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  font-size: 12px;
  line-height: 1.4;
  color: var(--text-secondary);
}

.draft-fact-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.draft-fact-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 78px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.draft-fact-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.draft-fact-value {
  font-size: 13px;
  line-height: 1.6;
  font-weight: 600;
  color: var(--text-primary);
}

.draft-step-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.draft-step-item {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  align-items: flex-start;
}

.draft-step-index {
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

.draft-step-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 2px 0 0;
}

.draft-step-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.draft-step-desc {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.draft-evidence-list {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.draft-evidence-list li {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.draft-card-section-optimization {
  padding-top: 4px;
  border-top: 1px solid color-mix(in oklab, var(--border-light) 88%, var(--primary-color) 12%);
}

.draft-weight-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.draft-weight-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 74px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.draft-weight-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.draft-weight-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.draft-ranking-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.draft-ranking-item.is-winner {
  border-color: color-mix(in oklab, var(--primary-color) 24%, var(--border-default));
  background: color-mix(in oklab, var(--primary-color) 8%, var(--bg-card));
}

.draft-ranking-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 10px;
  align-items: baseline;
}

.draft-ranking-order {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.draft-ranking-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-ranking-score {
  font-size: 12px;
  color: var(--text-secondary);
}

.draft-ranking-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.draft-ranking-tag {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 8px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
  font-size: 11px;
  color: var(--text-secondary);
}

.cost-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cost-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.85fr);
  gap: 18px;
}

.cost-visual-block,
.cost-summary-panel {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border: 1px solid var(--border-light);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  flex-direction: column;
}

.cost-block-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.cost-block-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.cost-block-subtitle {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.cost-chart-shell {
  min-height: 320px;
}

.cost-chart {
  width: 100%;
  height: 320px;
}

.cost-chart-note {
  margin-top: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border: 1px solid var(--border-light);
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.cost-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.cost-legend-item {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  width: 100%;
  padding: 12px 14px;
  text-align: left;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border: 1px solid var(--border-light);
  border-radius: 14px;
  transition: background var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
}

.cost-legend-item:hover {
  background: color-mix(in oklab, var(--primary-color) 6%, var(--bg-card));
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
  transform: translateY(-1px);
}

.legend-swatch {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.6);
}

.legend-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.legend-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.legend-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.legend-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.legend-tag {
  padding: 4px 8px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  color: var(--primary-dark);
  font-size: 11px;
  font-weight: 600;
}

.legend-tag.muted {
  background: color-mix(in oklab, var(--warning-color) 12%, var(--bg-card));
  color: var(--warning-color);
}

.cost-kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.cost-kpi-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 108px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.cost-kpi-card.strong {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 10%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.cost-kpi-card.span-wide {
  grid-column: 1 / -1;
  min-height: 124px;
  justify-content: center;
}

.kpi-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.kpi-value {
  font-size: 24px;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text-primary);
}

.kpi-note {
  font-size: 12px;
  color: var(--text-placeholder);
}

.cost-summary-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 10px;
  padding: 0 4px;
}

.summary-heading-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-heading-note {
  font-size: 12px;
  color: var(--text-placeholder);
}

.cost-summary-strip {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cost-summary-row {
  display: grid;
  grid-template-columns: 10px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 12px 14px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border: 1px solid var(--border-light);
  border-radius: 14px;
}

.summary-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.summary-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border-radius: 14px;
  border: 1px solid var(--border-light);
}

.cost-row.total {
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  font-weight: 600;
}

.cost-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.cost-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.over-budget {
  color: var(--danger-color) !important;
}

.under-budget {
  color: var(--success-color) !important;
}

.budget-warning,
.budget-success {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  border-radius: 14px;
}

.budget-warning {
  background: var(--danger-bg);
  color: var(--danger-color);
}

.budget-success {
  background: var(--success-bg);
  color: var(--success-color);
}

.cost-detail-dialog :deep(.el-dialog) {
  border-radius: 22px;
}

.cost-detail-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-dot {
  width: 14px;
  height: 14px;
  margin-top: 4px;
  border-radius: 50%;
}

.detail-header-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.detail-subtitle {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.cost-detail-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cost-detail-kpi {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.detail-kpi-item {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.detail-kpi-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.detail-kpi-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.5;
}

.cost-detail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cost-detail-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.detail-row-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.detail-row-value {
  font-size: 13px;
  line-height: 1.65;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

.expert-card {
  height: 100%;
  transition: all var(--transition-normal);
  border-radius: 18px;
}

.expert-card.waiting {
  opacity: 0.6;
}

.expert-card.running {
  border: 1px solid color-mix(in oklab, var(--warning-color) 44%, var(--border-default));
  box-shadow: 0 12px 24px color-mix(in oklab, var(--warning-color) 16%, transparent);
}

.expert-card.completed {
  border: 1px solid color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
}

.expert-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.expert-icon {
  color: var(--primary-dark);
}

.expert-name {
  font-weight: 600;
  font-size: 14px;
}

.expert-status {
  margin-bottom: 12px;
}

.expert-score {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  padding: 12px;
  border-radius: 14px;
  text-align: center;
  margin-bottom: 12px;
}

.score-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.score-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-dark);
}

.expert-summary {
  font-size: 13px;
  color: var(--text-secondary);
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
  color: var(--text-primary);
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
  color: var(--text-secondary);
  margin-bottom: 4px;
  line-height: 1.6;
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
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border-radius: 10px;
  font-size: 12px;
}

.metric-key {
  color: var(--text-secondary);
}

.metric-val {
  color: var(--text-primary);
  font-weight: 500;
}

.debate-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.debate-overview {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.9fr);
  gap: 16px;
  padding: 20px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 12%, transparent), transparent 34%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 0%, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 14%, var(--border-default));
}

.debate-overview-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 62ch;
}

.debate-eyebrow {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.debate-overview-copy h4 {
  font-size: 24px;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text-primary);
  text-wrap: balance;
}

.debate-overview-copy p {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.debate-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-self: stretch;
}

.debate-metric {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  min-height: 110px;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.debate-metric.primary {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 10%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.debate-metric-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.debate-metric-value {
  font-size: 22px;
  line-height: 1.15;
  font-weight: 700;
  color: var(--text-primary);
}

.debate-metric-value.consensus {
  color: var(--primary-dark);
}

.debate-participant-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.debate-participant {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: 999px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.participant-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--bg-card) 86%, white);
}

.participant-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.debate-participant.expert-economic {
  background: color-mix(in oklab, #00b894 10%, var(--bg-card));
}

.debate-participant.expert-reliability {
  background: color-mix(in oklab, #00cec9 10%, var(--bg-card));
}

.debate-participant.expert-environmental {
  background: color-mix(in oklab, #f39c12 10%, var(--bg-card));
}

.debate-board {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.78fr);
  gap: 18px;
  align-items: start;
}

.debate-main-column,
.debate-summary-card {
  border-radius: 20px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%);
}

.debate-main-column {
  padding: 18px;
}

.debate-chat-messages {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.round-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.debate-round-block {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.round-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--primary-color) 12%, var(--bg-card));
  color: var(--primary-dark);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
}

.round-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.round-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.round-meta {
  font-size: 12px;
  color: var(--text-placeholder);
}

.round-statements {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  gap: 12px;
}

.avatar-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border-radius: 16px;
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border: 1px solid color-mix(in oklab, var(--border-light) 88%, var(--primary-color) 12%);
}

.avatar {
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(249, 253, 250, 0.98);
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 10px 22px color-mix(in oklab, var(--primary-color) 16%, transparent);
}

.speaker-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.speaker-name {
  font-size: 12px;
  line-height: 1.5;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-word;
}

.speaker-role {
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-placeholder);
}

.message-bubble {
  min-width: 0;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 0%, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 100%);
}

.message-content {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.72;
}

.chat-message.expert-economic .avatar-wrapper {
  background: color-mix(in oklab, #00b894 8%, var(--bg-panel));
}

.chat-message.expert-economic .message-bubble {
  background: linear-gradient(180deg, color-mix(in oklab, #00b894 7%, var(--bg-panel)) 0%, color-mix(in oklab, #00b894 4%, var(--bg-card)) 100%);
  border-color: color-mix(in oklab, #00b894 20%, var(--border-default));
}

.chat-message.expert-reliability .avatar-wrapper {
  background: color-mix(in oklab, #00cec9 8%, var(--bg-panel));
}

.chat-message.expert-reliability .message-bubble {
  background: linear-gradient(180deg, color-mix(in oklab, #00cec9 7%, var(--bg-panel)) 0%, color-mix(in oklab, #00cec9 4%, var(--bg-card)) 100%);
  border-color: color-mix(in oklab, #00cec9 20%, var(--border-default));
}

.chat-message.expert-environmental .avatar-wrapper {
  background: color-mix(in oklab, #f39c12 8%, var(--bg-panel));
}

.chat-message.expert-environmental .message-bubble {
  background: linear-gradient(180deg, color-mix(in oklab, #f39c12 9%, var(--bg-panel)) 0%, color-mix(in oklab, #f39c12 4%, var(--bg-card)) 100%);
  border-color: color-mix(in oklab, #f39c12 22%, var(--border-default));
}

.empty-chat {
  text-align: center;
  color: var(--text-placeholder);
  padding: 40px;
}

.debate-summary-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  position: sticky;
  top: 18px;
}

.debate-summary-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.debate-summary-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.debate-summary-title h4 {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
}

.debate-summary-title p {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.debate-summary-badge {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  padding: 6px 10px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  color: var(--primary-dark);
  font-size: 11px;
  font-weight: 700;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  line-height: 1.7;
}

.suggestion-icon {
  color: var(--primary-dark);
  margin-top: 3px;
}

.arbitrator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.arbitrator-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.confidence-badge {
  background: color-mix(in oklab, var(--success-color) 10%, var(--bg-card));
  color: var(--success-color);
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
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border-radius: 14px;
  margin-bottom: 20px;
}

.consensus-indicator .label {
  color: var(--text-secondary);
  font-size: 14px;
}

.consensus-indicator .value {
  font-size: 22px;
  font-weight: 600;
  color: var(--warning-color);
}

.consensus-indicator .value.high {
  color: var(--success-color);
}

.decision-summary {
  margin-bottom: 24px;
}

.decision-summary p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.overall-scores h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.score-card {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  padding: 20px;
  border-radius: 16px;
  text-align: center;
}

.score-card.highlight {
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
}

.score-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.score-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.score-card.highlight .score-value {
  color: var(--primary-dark);
}

.trade-offs {
  margin-top: 24px;
}

.trade-offs h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.trade-offs ul {
  margin: 0;
  padding-left: 20px;
}

.trade-offs li {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 8px;
}

.report-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-preview h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
}

.report-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 20px;
}

.report-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.report-metric {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  padding: 16px;
  border-radius: 14px;
  text-align: center;
}

.report-metric .metric-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.report-metric .metric-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.report-metric .metric-value.success {
  color: var(--success-color);
}

.solution-preview h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.preview-item {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  padding: 16px;
  border-radius: 14px;
  text-align: center;
}

.preview-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.preview-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-value.highlight {
  color: var(--primary-dark);
}

.logs-section {
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 24%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 88%, var(--primary-color) 12%) 0%, var(--bg-stage) 100%);
  border-radius: 22px;
  padding: 24px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 18%, transparent);
  box-shadow: var(--shadow-lg);
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logs-header h3 {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(243, 251, 245, 0.96);
}

.logs-actions {
  display: flex;
  gap: 8px;
}

.logs-container {
  background: rgba(8, 19, 14, 0.52);
  border-radius: 18px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid rgba(234, 246, 239, 0.1);
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 6px 0;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.log-time {
  color: rgba(214, 228, 219, 0.56);
  min-width: 80px;
}

.log-type {
  min-width: 60px;
  font-weight: 600;
}

.log-item.info .log-type { color: var(--primary-light); }
.log-item.success .log-type { color: var(--accent-light); }
.log-item.warning .log-type { color: color-mix(in oklab, var(--warning-color) 82%, white); }
.log-item.error .log-type { color: color-mix(in oklab, var(--danger-color) 78%, white); }

.log-content {
  flex: 1;
  color: rgba(240, 248, 243, 0.88);
  line-height: 1.5;
}

.generate-footer {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
  padding: 20px 0;
}

.primary-btn {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
  border-color: var(--primary-color) !important;
}

.primary-btn:hover {
  background: linear-gradient(180deg, var(--primary-light) 0%, var(--primary-color) 100%) !important;
  border-color: var(--primary-light) !important;
}

@media (max-width: 1200px) {
  .draft-overview-panel,
  .cost-layout {
    grid-template-columns: 1fr;
  }

  .draft-process-grid {
    grid-template-columns: 1fr;
  }

  .preview-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .report-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .full-workflow {
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .workflow-node {
    flex: 0 0 calc(33.333% - 14px);
  }
  
  .preview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .report-metrics {
    grid-template-columns: repeat(2, 1fr);
  }

  .cost-kpi-grid,
  .cost-detail-kpi,
  .draft-result-grid,
  .draft-fact-grid {
    grid-template-columns: 1fr;
  }

  .cost-kpi-card.span-wide {
    grid-column: auto;
    min-height: 108px;
  }

  .progress-section,
  .stage-panel,
  .logs-section {
    padding: 18px;
  }

  .stage-header,
  .progress-header,
  .logs-header,
  .arbitrator-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .result-metrics {
    flex-direction: column;
    gap: 12px;
  }

  .cost-visual-block,
  .cost-summary-panel,
  .draft-process-card {
    padding: 16px;
  }

  .cost-block-header,
  .draft-card-title-row {
    flex-direction: column;
  }

  .draft-overview-panel {
    padding: 18px;
  }

  .draft-overview-copy h4 {
    font-size: 20px;
  }

  .cost-summary-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .cost-chart {
    height: 280px;
  }

  .debate-overview,
  .debate-board,
  .debate-metrics {
    grid-template-columns: 1fr;
  }

  .debate-main-column,
  .debate-summary-card {
    padding: 16px;
  }

  .chat-message {
    grid-template-columns: 1fr;
  }

  .avatar-wrapper {
    align-items: center;
  }

  .debate-summary-card {
    position: static;
  }

  .cost-legend-item,
  .cost-summary-row,
  .cost-detail-row {
    grid-template-columns: 12px 1fr;
  }

  .legend-meta,
  .detail-row-value {
    align-items: flex-start;
    text-align: left;
  }
}

@media (max-width: 560px) {
  .workflow-node {
    flex: 0 0 calc(50% - 10px);
  }

  .preview-grid,
  .report-metrics,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
