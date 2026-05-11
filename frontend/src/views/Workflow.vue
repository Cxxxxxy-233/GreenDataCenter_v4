<template>
  <div class="workflow-container">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">方案工作流</h1>
          <p class="page-subtitle">按后端真实编排展示多智能体协同生成方案的完整运行逻辑</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="startWorkflow">
            <el-icon><RefreshRight /></el-icon>
            开始方案生成
          </el-button>
        </div>
      </div>
    </div>

    <section class="workflow-card card">
      <div class="workflow-card-header">
        <div>
          <h3 class="workflow-card-title">工作流运行全景</h3>
          <p class="workflow-card-desc">从输入、解析、顺序专家分析，到辩论收敛、仲裁决策和报告输出，完整展示整个工作流的执行路径。</p>
        </div>
        <div class="workflow-badges">
          <span class="workflow-badge">7 个核心阶段</span>
          <span class="workflow-badge">顺序专家分析</span>
          <span class="workflow-badge">最多 5 轮辩论</span>
        </div>
      </div>

      <div class="workflow-focus-bar">
        <div class="focus-copy">
          <span class="focus-label">当前聚焦阶段</span>
          <span class="focus-title">{{ activeStage.title }}</span>
          <span class="focus-desc">{{ activeStage.subtitle }}</span>
        </div>
        <div class="focus-meta">
          <span class="focus-code">{{ activeStage.backendRef }}</span>
          <span class="focus-hint">点击节点可展开该阶段的输入、输出与路由关系</span>
        </div>
      </div>

      <div class="workflow-canvas">
        <section class="flow-lane flow-lane-entry">
          <div class="lane-caption">入口阶段</div>
          <button
            type="button"
            class="flow-stage stage-entry"
            :class="{ active: currentStageId === 'input' }"
            @click="selectStage('input')"
          >
            <div class="stage-index">00</div>
            <div class="stage-main">
              <div class="stage-eyebrow">Input</div>
              <div class="stage-title">用户输入需求</div>
              <div class="stage-text">项目参数、约束条件、优先级与目标进入工作流。</div>
            </div>
          </button>
          <div class="flow-arrow vertical">↓</div>
          <button
            type="button"
            class="flow-stage stage-parser"
            :class="{ active: currentStageId === 'requirement-parser' }"
            @click="selectStage('requirement-parser')"
          >
            <div class="stage-index">01</div>
            <div class="stage-main">
              <div class="stage-eyebrow">Parser</div>
              <div class="stage-title">需求解析器节点</div>
              <div class="stage-text">补全缺失参数，生成结构化需求对象，作为后续所有节点的统一输入。</div>
            </div>
          </button>
        </section>

        <section class="flow-lane flow-lane-analysis">
          <div class="lane-caption">顺序专家分析</div>
          <div class="analysis-shell">
            <div class="analysis-rail"></div>
            <div class="analysis-sequence">
              <button
                v-for="stage in analysisStages"
                :key="stage.id"
                type="button"
                class="flow-stage stage-analysis"
                :class="[{ active: currentStageId === stage.id }, stage.tone]"
                @click="selectStage(stage.id)"
              >
                <div class="stage-index">{{ stage.index }}</div>
                <div class="stage-main">
                  <div class="stage-eyebrow">{{ stage.eyebrow }}</div>
                  <div class="stage-title">{{ stage.title }}</div>
                  <div class="stage-text">{{ stage.description }}</div>
                  <div class="stage-meta">{{ stage.meta }}</div>
                </div>
              </button>
            </div>
          </div>
          <div class="lane-note">说明：后端为避免流式输出互相干扰，三个专家节点采用顺序执行，而不是并行执行。</div>
        </section>

        <section class="flow-lane flow-lane-debate">
          <div class="lane-caption">辩论与路由</div>
          <div class="debate-grid">
            <button
              type="button"
              class="flow-stage stage-debate"
              :class="{ active: currentStageId === 'debate-round' }"
              @click="selectStage('debate-round')"
            >
              <div class="stage-index">05</div>
              <div class="stage-main">
                <div class="stage-eyebrow">Debate</div>
                <div class="stage-title">多轮辩论节点</div>
                <div class="stage-text">经济、供电、环境专家轮流发言，比较评分分歧并尝试收敛意见。</div>
              </div>
            </button>

            <div class="debate-loop-card">
              <div class="loop-title">条件循环</div>
              <div class="loop-rule">共识度 >= 0.8，提前停止</div>
              <div class="loop-rule">未达成共识且轮次 < 5，继续辩论</div>
              <div class="loop-rule">达到 5 轮，强制停止并进入仲裁</div>
            </div>

            <div class="debate-route">
              <div class="route-branch">
                <span class="branch-chip success">共识达成</span>
                <span class="branch-arrow">进入仲裁</span>
              </div>
              <div class="route-branch">
                <span class="branch-chip warning">继续辩论</span>
                <span class="branch-arrow">回到本轮循环</span>
              </div>
            </div>
          </div>
        </section>

        <section class="flow-lane flow-lane-output">
          <div class="lane-caption">决策与输出</div>
          <div class="decision-grid">
            <button
              type="button"
              class="flow-stage stage-arbitrator"
              :class="{ active: currentStageId === 'arbitrator' }"
              @click="selectStage('arbitrator')"
            >
              <div class="stage-index">06</div>
              <div class="stage-main">
                <div class="stage-eyebrow">Arbitrator</div>
                <div class="stage-title">仲裁者节点</div>
                <div class="stage-text">汇总专家意见、冲突分析与权衡项，生成最终综合方案。</div>
              </div>
            </button>
            <div class="flow-arrow horizontal">→</div>
            <button
              type="button"
              class="flow-stage stage-output"
              :class="{ active: currentStageId === 'output' }"
              @click="selectStage('output')"
            >
              <div class="stage-index">07</div>
              <div class="stage-main">
                <div class="stage-eyebrow">Output</div>
                <div class="stage-title">输出节点</div>
                <div class="stage-text">产出最终方案、关键指标和可行性研究报告，工作流结束。</div>
              </div>
            </button>
          </div>
        </section>
      </div>

      <div class="workflow-support-grid">
        <section class="support-card support-card-wide">
          <div class="support-header">
            <h4 class="support-title">后端 LangGraph 映射说明</h4>
            <p class="support-desc">前端展示节点与后端 `graph/nodes.py`、`graph/edges.py`、`graph/build.py` 的对应关系。</p>
          </div>
          <div class="mapping-list">
            <div v-for="item in graphMappings" :key="item.stage" class="mapping-row">
              <div class="mapping-stage">
                <div class="mapping-stage-name">{{ item.stage }}</div>
                <div class="mapping-stage-desc">{{ item.description }}</div>
              </div>
              <div class="mapping-target">
                <div class="mapping-code">{{ item.backend }}</div>
                <div class="mapping-note">{{ item.note }}</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </section>

    <div class="detail-panel" v-if="selectedStage" @click.self="closeDetail">
      <div class="detail-content">
        <div class="detail-header">
          <div class="detail-icon" :class="activeStage.toneClass">
            <el-icon><component :is="activeStage.icon" /></el-icon>
          </div>
          <div class="detail-title-area">
            <h3 class="detail-title">{{ activeStage.title }}</h3>
            <p class="detail-subtitle">{{ activeStage.subtitle }}</p>
          </div>
          <button class="close-btn" @click="closeDetail">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <div class="detail-body">
          <div class="detail-section">
            <h4 class="section-title">阶段职责</h4>
            <p class="detail-copy">{{ activeStage.responsibility }}</p>
          </div>

          <div class="detail-grid">
            <div class="detail-section">
              <h4 class="section-title">输入</h4>
              <ul class="detail-list">
                <li v-for="item in activeStage.inputs" :key="item">{{ item }}</li>
              </ul>
            </div>

            <div class="detail-section">
              <h4 class="section-title">输出</h4>
              <ul class="detail-list">
                <li v-for="item in activeStage.outputs" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>

          <div class="detail-grid">
            <div class="detail-section">
              <h4 class="section-title">关键逻辑</h4>
              <ul class="detail-list">
                <li v-for="item in activeStage.logic" :key="item">{{ item }}</li>
              </ul>
            </div>

            <div class="detail-section">
              <h4 class="section-title">路由关系</h4>
              <ul class="detail-list">
                <li v-for="item in activeStage.routing" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  RefreshRight,
  EditPen,
  DataAnalysis,
  Coin,
  Opportunity,
  Monitor,
  ChatLineSquare,
  Connection,
  Finished,
  Close
} from '@element-plus/icons-vue'

const router = useRouter()
const selectedStage = ref(null)

const workflowStages = {
  input: {
    id: 'input',
    title: '用户输入需求',
    subtitle: '工作流入口，承接项目基础参数与目标',
    icon: EditPen,
    toneClass: 'tone-entry',
    backendRef: 'GraphState.input',
    responsibility: '接收项目名称、总功率、Tier 等级、PUE 目标、绿电比例、预算等约束条件，形成原始需求数据。',
    inputs: ['用户填写的项目参数', '目标约束与优先级', '机柜规模、面积、预算等基础信息'],
    outputs: ['原始需求对象', '待解析参数集'],
    logic: ['不直接生成方案，只负责触发工作流', '作为需求解析器节点的唯一上游输入'],
    routing: ['进入需求解析器节点']
  },
  'requirement-parser': {
    id: 'requirement-parser',
    title: '需求解析器节点',
    subtitle: '将原始需求转换为结构化、完整的标准输入',
    icon: DataAnalysis,
    toneClass: 'tone-parser',
    backendRef: 'RequirementParserNode',
    responsibility: '补全缺失字段、设置合理默认值，并输出一个带完整字段的结构化需求 JSON，供后续专家与流程节点共享。',
    inputs: ['原始需求数据', '行业默认值规则'],
    outputs: ['结构化需求对象', '完整字段 JSON'],
    logic: ['补充缺失参数', '校准单位和字段格式', '为专家分析准备统一输入'],
    routing: ['进入经济分析节点，开启顺序专家分析']
  },
  economic: {
    id: 'economic',
    index: '02',
    eyebrow: 'Expert 01',
    title: '经济分析节点',
    description: '计算总成本、ROI、回收期等经济指标。',
    meta: '输出成本效益与投资回报观点',
    tone: 'tone-economic',
    icon: Coin,
    backendRef: 'EconomicAnalysisNode',
    subtitle: '顺序专家分析的第一站，先形成经济视角',
    responsibility: '基于结构化需求分析 CAPEX、单位机柜成本、ROI 与投资回收期，生成经济专家观点与评分。',
    inputs: ['结构化需求对象', '成本参数', '共享上下文'],
    outputs: ['economic_opinion', '经济评分', 'ROI / total_cost / payback_period'],
    logic: ['关注成本效益和投资回报', '为后续专家与辩论阶段提供经济基线'],
    routing: ['完成后进入供电可靠性分析节点']
  },
  power: {
    id: 'power',
    index: '03',
    eyebrow: 'Expert 02',
    title: '供电可靠性分析节点',
    description: '评估 Tier、可用性、UPS 架构与年宕机时间。',
    meta: '输出可靠性评分与供配电建议',
    tone: 'tone-power',
    icon: Opportunity,
    backendRef: 'PowerReliabilityAnalysisNode',
    subtitle: '顺序专家分析的第二站，聚焦供电可靠性',
    responsibility: '评估供电架构、UPS 配置、系统冗余、可用性和年宕机时间，形成可靠性观点与分数。',
    inputs: ['结构化需求对象', '经济分析上下文'],
    outputs: ['power_reliability_opinion', '可靠性评分', 'Tier / availability / downtime'],
    logic: ['温度参数更低，偏确定性分析', '依赖已完成的上游状态，避免并行输出互相干扰'],
    routing: ['完成后进入环境分析节点']
  },
  environmental: {
    id: 'environmental',
    index: '04',
    eyebrow: 'Expert 03',
    title: '环境分析节点',
    description: '计算 PUE、绿电比例、碳排放与环境得分。',
    meta: '输出环保表现与能效观点',
    tone: 'tone-environment',
    icon: Monitor,
    backendRef: 'EnvironmentalAnalysisNode',
    subtitle: '顺序专家分析的第三站，收敛环境与能效视角',
    responsibility: '分析 PUE、绿电比例、年碳排放等指标，形成环境评分和节能减排建议。',
    inputs: ['结构化需求对象', '前两位专家观点'],
    outputs: ['environmental_opinion', '环境评分', 'PUE / 绿电比例 / 年碳排放'],
    logic: ['平衡分析稳定性与创造力', '为辩论阶段提供第三组专业视角'],
    routing: ['完成后进入多轮辩论节点']
  },
  'debate-round': {
    id: 'debate-round',
    title: '多轮辩论节点',
    subtitle: '让三位专家围绕分歧进行轮流陈述与收敛',
    icon: ChatLineSquare,
    toneClass: 'tone-debate',
    backendRef: 'DebateRoundNode + edges.py',
    responsibility: '组织经济、供电、环境三位专家轮流发言，对关键冲突点展开辩论，并根据评分方差计算共识度。',
    inputs: ['三位专家意见', '共享记忆与辩论历史', '当前辩论轮次'],
    outputs: ['debate_history', 'consensus_score', 'should_continue_debate'],
    logic: ['专家发言顺序固定：经济 -> 供电 -> 环境', '共识度 >= 0.8 时提前停止', '最多进行 5 轮辩论'],
    routing: ['若未达成共识且轮次未满，继续辩论', '否则进入仲裁者节点']
  },
  arbitrator: {
    id: 'arbitrator',
    title: '仲裁者节点',
    subtitle: '综合专家意见与冲突分析，形成最终方案',
    icon: Connection,
    toneClass: 'tone-arbitrator',
    backendRef: 'ArbitratorNode',
    responsibility: '整合专家意见、分析冲突、生成权衡方案，并输出总分、关键指标、风险、建议和最终置信度。',
    inputs: ['三位专家观点', '辩论历史', '共识得分'],
    outputs: ['最终方案 JSON', 'trade_offs', 'risks', 'recommendations', 'confidence'],
    logic: ['不简单平均，而是结合冲突与权衡进行裁决', '生成最终综合方案结构'],
    routing: ['进入输出节点']
  },
  output: {
    id: 'output',
    title: '输出节点',
    subtitle: '结束工作流并展示最终方案成果',
    icon: Finished,
    toneClass: 'tone-output',
    backendRef: 'OutputNode',
    responsibility: '标记工作流完成，输出最终方案、关键指标和可行性研究报告内容，供前端页面展示与后续导出。',
    inputs: ['最终方案对象', '关键指标与报告内容'],
    outputs: ['页面展示结果', '可导出的报告内容'],
    logic: ['工作流在此结束', '前端在此阶段展示最终方案、报告和详情'],
    routing: ['无后续节点，流程结束']
  }
}

const analysisStages = ['economic', 'power', 'environmental'].map(id => workflowStages[id])
const currentStageId = computed(() => selectedStage.value || 'requirement-parser')

const graphMappings = [
  {
    stage: '用户输入需求',
    description: '前端与 CLI/接口接收项目参数的入口层。',
    backend: 'GraphState.input / coordinator.generate_solution()',
    note: '不属于 LangGraph 核心节点，但构成图的上游输入。'
  },
  {
    stage: '需求解析器节点',
    description: '将原始需求补全并标准化。',
    backend: 'RequirementParserNode / requirement_parser',
    note: '图构建器中的入口点。'
  },
  {
    stage: '经济分析节点',
    description: '第一位顺序专家，输出成本与 ROI 观点。',
    backend: 'EconomicAnalysisNode',
    note: '按 build.py 中顺序执行链路开始。'
  },
  {
    stage: '供电可靠性分析节点',
    description: '第二位顺序专家，输出可靠性观点。',
    backend: 'PowerReliabilityAnalysisNode',
    note: '依赖上游经济分析完成后的共享状态。'
  },
  {
    stage: '环境分析节点',
    description: '第三位顺序专家，输出能效与碳排放观点。',
    backend: 'EnvironmentalAnalysisNode',
    note: '顺序专家分析的最后一环。'
  },
  {
    stage: '多轮辩论节点',
    description: '组织三位专家轮流发言并计算共识度。',
    backend: 'DebateRoundNode',
    note: '由 edges.py 的条件函数控制是否继续循环。'
  },
  {
    stage: '条件循环',
    description: '判断继续辩论还是停止辩论。',
    backend: 'should_continue_debate() / check_debate_status()',
    note: '返回 continue / stop / end 等条件分支。'
  },
  {
    stage: '仲裁者节点 -> 输出节点',
    description: '综合裁决并产出最终方案。',
    backend: 'ArbitratorNode -> OutputNode',
    note: '对应 build_data_center_graph() 的流程末段。'
  }
]

const activeStage = computed(() => workflowStages[currentStageId.value] || workflowStages['requirement-parser'])

const selectStage = (stageId) => {
  selectedStage.value = stageId
}

const closeDetail = () => {
  selectedStage.value = null
}

const startWorkflow = () => {
  router.push({ name: 'Generate' })
}
</script>

<style scoped>
.workflow-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 24px 26px;
  box-shadow: var(--shadow-sm);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  max-width: 66ch;
}

.workflow-card {
  padding: 24px;
  background:
    radial-gradient(circle at top left, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 24%),
    radial-gradient(circle at top right, color-mix(in oklab, var(--accent-color) 8%, transparent), transparent 22%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.workflow-card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 22px;
}

.workflow-card-title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.workflow-card-desc {
  margin: 0;
  max-width: 72ch;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.workflow-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.workflow-badge {
  padding: 7px 12px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 14%, var(--border-default));
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-ink);
}

.workflow-canvas {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px;
  border-radius: 22px;
  border: 1px solid var(--border-light);
  background:
    radial-gradient(circle at top, color-mix(in oklab, var(--primary-color) 4%, transparent), transparent 34%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%) 0%, color-mix(in oklab, var(--bg-panel) 97%, var(--primary-color) 3%) 100%);
}

.workflow-focus-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 16%, var(--border-default));
  background:
    linear-gradient(90deg, color-mix(in oklab, var(--primary-color) 9%, var(--bg-card)) 0%, color-mix(in oklab, var(--accent-color) 6%, var(--bg-card)) 52%, color-mix(in oklab, #a384ff 4%, var(--bg-card)) 100%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  box-shadow: var(--shadow-sm);
}

.focus-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.focus-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.focus-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.focus-desc {
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.focus-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.focus-code {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--primary-dark);
}

.focus-hint {
  font-size: 12px;
  color: var(--text-placeholder);
}

.workflow-support-grid {
  display: block;
  margin-top: 18px;
}

.support-card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.support-card-wide {
  padding: 20px;
}

.support-header {
  margin-bottom: 14px;
}

.support-title {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.support-desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.mapping-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mapping-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.9fr);
  gap: 14px;
  padding: 14px;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border: 1px solid var(--border-light);
}

.mapping-stage-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.mapping-stage-desc {
  font-size: 12px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.mapping-target {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mapping-code {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
  color: var(--primary-dark);
}

.mapping-note {
  font-size: 12px;
  line-height: 1.65;
  color: var(--text-placeholder);
}

.flow-lane {
  position: relative;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%);
}

.flow-lane-entry {
  background: linear-gradient(180deg, color-mix(in oklab, var(--accent-color) 5%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 98%, var(--accent-color) 2%) 100%);
}

.flow-lane-analysis {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 6%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 97%, var(--primary-color) 3%) 100%);
}

.flow-lane-debate {
  background: linear-gradient(180deg, color-mix(in oklab, #a384ff 5%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 98%, #a384ff 2%) 100%);
}

.flow-lane-output {
  background: linear-gradient(180deg, color-mix(in oklab, var(--accent-color) 4%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 98%, var(--primary-color) 2%) 100%);
}

.lane-caption {
  margin-bottom: 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.flow-lane-entry {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.flow-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  font-size: 22px;
  line-height: 1;
}

.flow-arrow.vertical {
  margin: 8px 0;
}

.flow-arrow.horizontal {
  min-width: 40px;
}

.flow-stage {
  position: relative;
  display: flex;
  gap: 14px;
  width: 100%;
  text-align: left;
  padding: 18px 18px 18px 16px;
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 99%, var(--primary-color) 1%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.flow-stage:hover,
.flow-stage.active {
  transform: translateY(-2px);
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
  box-shadow:
    0 0 0 1px color-mix(in oklab, var(--primary-color) 8%, transparent),
    var(--shadow-md);
}

.flow-stage:focus-visible,
.close-btn:focus-visible {
  outline: none;
  box-shadow:
    0 0 0 2px rgba(244, 251, 247, 0.95),
    0 0 0 5px color-mix(in oklab, var(--primary-color) 28%, transparent),
    var(--shadow-md);
}

.stage-index {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  color: var(--primary-dark);
  font-size: 12px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 22%, transparent);
}

.stage-entry .stage-index,
.stage-parser .stage-index {
  background: linear-gradient(180deg, color-mix(in oklab, var(--accent-light) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--accent-color) 12%, var(--bg-card)) 100%);
  color: var(--accent-dark);
}

.stage-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.stage-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: color-mix(in oklab, var(--text-placeholder) 86%, var(--primary-dark) 14%);
}

.stage-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.stage-text {
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.stage-meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--primary-dark);
  font-weight: 600;
}

.stage-entry,
.stage-parser {
  max-width: 760px;
}

.analysis-shell {
  position: relative;
}

.analysis-rail {
  position: absolute;
  top: 30px;
  left: 18px;
  right: 18px;
  height: 2px;
  background: linear-gradient(90deg, rgba(50, 183, 195, 0.22), rgba(24, 154, 98, 0.2), rgba(211, 154, 49, 0.18));
}

.analysis-sequence {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.tone-economic .stage-index,
.tone-economic.active .stage-index {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-light) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 12%, var(--bg-card)) 100%);
}

.tone-power .stage-index,
.tone-power.active .stage-index {
  background: linear-gradient(180deg, color-mix(in oklab, var(--accent-light) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--accent-color) 12%, var(--bg-card)) 100%);
  color: var(--accent-dark);
}

.tone-environment .stage-index,
.tone-environment.active .stage-index {
  background: linear-gradient(180deg, color-mix(in oklab, #ffd98c 28%, var(--bg-card)) 0%, color-mix(in oklab, var(--warning-color) 12%, var(--bg-card)) 100%);
  color: #9e6d13;
}

.lane-note {
  margin-top: 14px;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.debate-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(260px, 0.85fr) minmax(220px, 0.7fr);
  gap: 14px;
  align-items: stretch;
}

.stage-debate,
.stage-arbitrator,
.stage-output {
  min-height: 140px;
}

.debate-loop-card,
.debate-route {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid color-mix(in oklab, #a384ff 12%, var(--border-light));
  background:
    linear-gradient(180deg, color-mix(in oklab, #a384ff 6%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 98%, #a384ff 2%) 100%);
}

.loop-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.loop-rule {
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-secondary);
}

.route-branch {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-card) 98%, #a384ff 2%);
}

.branch-chip {
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.branch-chip.success {
  background: rgba(24, 178, 107, 0.16);
  color: #9fe3bf;
}

.branch-chip.warning {
  background: rgba(217, 154, 39, 0.16);
  color: #f6c56a;
}

.branch-arrow {
  font-size: 13px;
  color: var(--text-secondary);
}

.decision-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 14px;
  align-items: stretch;
}

.detail-panel {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at top, rgba(24, 178, 107, 0.08), transparent 30%),
    rgba(8, 22, 16, 0.38);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: 20px;
}

.detail-content {
  width: min(900px, 96vw);
  max-height: 84vh;
  overflow: hidden;
  border-radius: 22px;
  border: 1px solid var(--border-light);
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  box-shadow: var(--shadow-lg);
}

.detail-header {
  display: flex;
  align-items: center;
  padding: 20px 22px;
  background:
    radial-gradient(circle at right center, rgba(22, 184, 196, 0.08), transparent 28%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 84%, var(--primary-color) 16%) 0%, color-mix(in oklab, var(--bg-stage) 90%, var(--primary-dark) 10%) 100%);
  color: rgba(245, 252, 247, 0.96);
}

.detail-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 28px;
}

.tone-entry { background: rgba(22, 184, 196, 0.18); color: #7fdbe3; }
.tone-parser { background: rgba(24, 178, 107, 0.18); color: #93dcb1; }
.tone-economic { background: rgba(24, 178, 107, 0.18); color: #93dcb1; }
.tone-power { background: rgba(22, 184, 196, 0.18); color: #7fdbe3; }
.tone-environment { background: rgba(217, 154, 39, 0.2); color: #e8b85a; }
.tone-debate { background: rgba(163, 132, 255, 0.2); color: #c7b4ff; }
.tone-arbitrator { background: rgba(24, 178, 107, 0.18); color: #93dcb1; }
.tone-output { background: rgba(22, 184, 196, 0.18); color: #7fdbe3; }

.detail-title-area {
  flex: 1;
}

.detail-title {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 700;
}

.detail-subtitle {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: rgba(233, 246, 238, 0.74);
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(246, 252, 247, 0.88);
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.14);
}

.detail-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(84vh - 98px);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.detail-section {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
}

.section-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.detail-copy {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  color: var(--text-secondary);
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-left: 18px;
  margin: 0;
}

.detail-list li {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

@media (max-width: 1200px) {
  .workflow-card-header,
  .header-content,
  .debate-grid,
  .decision-grid {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .analysis-sequence {
    grid-template-columns: 1fr;
  }

  .mapping-row,
  .workflow-focus-bar {
    grid-template-columns: 1fr;
  }

  .focus-meta {
    align-items: flex-start;
  }

  .analysis-rail {
    display: none;
  }
}

@media (max-width: 768px) {
  .page-header,
  .workflow-card,
  .workflow-canvas,
  .flow-lane {
    padding: 16px;
  }

  .workflow-badges {
    justify-content: flex-start;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .flow-stage {
    padding: 16px 14px;
  }
}
</style>
