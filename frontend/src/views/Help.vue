<template>
  <div class="help-page">
    <div class="help-layout">
      <aside class="help-sidebar">
        <el-menu :default-active="activeSection" class="help-menu" mode="vertical">
          <el-menu-item index="quickstart" @click="activeSection = 'quickstart'">
            <el-icon><Link /></el-icon>
            <span>快速入门</span>
          </el-menu-item>
          <el-menu-item index="params" @click="activeSection = 'params'">
            <el-icon><Document /></el-icon>
            <span>参数说明</span>
          </el-menu-item>
          <el-menu-item index="agents" @click="activeSection = 'agents'">
            <el-icon><Setting /></el-icon>
            <span>多智能体机制</span>
          </el-menu-item>
          <el-menu-item index="faq" @click="activeSection = 'faq'">
            <el-icon><Bell /></el-icon>
            <span>常见问题</span>
          </el-menu-item>
          <el-menu-item index="errors" @click="activeSection = 'errors'">
            <el-icon><Tools /></el-icon>
            <span>错误码说明</span>
          </el-menu-item>
          <el-menu-item index="contact" @click="activeSection = 'contact'">
            <el-icon><Phone /></el-icon>
            <span>联系支持</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <main class="help-content">
        <div v-show="activeSection === 'quickstart'" class="content-section">
          <div class="section-header">
            <h2>快速入门</h2>
            <p class="section-desc">按四个步骤完成一个可展示的数据中心初稿方案。</p>
          </div>

          <div class="step-cards">
            <div class="step-card" v-for="(step, index) in quickStartSteps" :key="index">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <h3>{{ step.title }}</h3>
                <p>{{ step.desc }}</p>
              </div>
              <div class="step-icon" :style="{ background: step.bgColor }">
                <el-icon :style="{ color: step.color }"><component :is="step.icon" /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <div v-show="activeSection === 'params'" class="content-section">
          <div class="section-header">
            <h2>参数说明</h2>
            <p class="section-desc">下面列出影响方案结果的关键输入及推荐填写口径。</p>
          </div>

          <el-card class="param-card">
            <h3 class="card-title">基础信息</h3>
            <div class="param-list">
              <div class="param-item">
                <span class="param-label">项目名称</span>
                <span class="param-desc">用于标识方案与历史记录，建议与园区或节点名称一致。</span>
              </div>
              <div class="param-item">
                <span class="param-label">建设地点</span>
                <span class="param-desc">决定资源曲线、气候条件、制冷策略以及绿电采购方式。</span>
              </div>
              <div class="param-item">
                <span class="param-label">建设优先级</span>
                <span class="param-desc">决定仲裁时更偏向经济性、低碳性还是供电可靠性。</span>
              </div>
            </div>
          </el-card>

          <el-card class="param-card">
            <h3 class="card-title">算力与负荷</h3>
            <div class="param-list">
              <div class="param-item">
                <span class="param-label">单机柜功率密度</span>
                <span class="param-desc">影响制冷架构与供配电容量冗余，演示时建议保持 20 至 40kW。</span>
              </div>
              <div class="param-item">
                <span class="param-label">IT 总负荷</span>
                <span class="param-desc">决定三类方案的核心规模参数，也是经济性测算的基础。</span>
              </div>
              <div class="param-item">
                <span class="param-label">目标绿电占比</span>
                <span class="param-desc">系统会先匹配绿电直连能力，再由绿电交易或绿证补足剩余占比。</span>
              </div>
            </div>
          </el-card>

          <el-card class="param-card">
            <h3 class="card-title">环境与资源</h3>
            <div class="param-list">
              <div class="param-item">
                <span class="param-label">年平均温度</span>
                <span class="param-desc">影响自然冷却可用时长和全年 PUE 表现。</span>
              </div>
              <div class="param-item">
                <span class="param-label">水资源紧缺指数</span>
                <span class="param-desc">指数越高，系统越倾向少水或无水制冷方案。</span>
              </div>
              <div class="param-item">
                <span class="param-label">风光资源条件</span>
                <span class="param-desc">用于测算风电、光伏、储能的推荐容量和直连占比上限。</span>
              </div>
            </div>
          </el-card>
        </div>

        <div v-show="activeSection === 'agents'" class="content-section">
          <div class="section-header">
            <h2>多智能体机制</h2>
            <p class="section-desc">三类智能体并行生成、交叉约束，最后由仲裁器输出统一方案。</p>
          </div>

          <div class="agent-grid">
            <el-card class="agent-card" v-for="(agent, index) in agents" :key="index">
              <div class="agent-header">
                <div class="agent-icon" :style="{ background: agent.bgColor }">
                  <el-icon :style="{ color: agent.color }"><component :is="agent.icon" /></el-icon>
                </div>
                <div class="agent-info">
                  <h3>{{ agent.title }}</h3>
                  <p class="agent-desc">{{ agent.desc }}</p>
                </div>
              </div>
              <div class="agent-detail">
                <p>{{ agent.detail }}</p>
              </div>
              <div class="agent-factors">
                <h4>核心考虑因素</h4>
                <div class="factor-tags">
                  <span v-for="(factor, i) in agent.factors" :key="i" class="factor-tag">{{ factor }}</span>
                </div>
              </div>
            </el-card>
          </div>

          <el-card class="mechanism-card">
            <h3 class="card-title">协同仲裁逻辑</h3>
            <div class="mechanism-content">
              <div class="mechanism-diagram">
                <div class="mechanism-node">绿电配置</div>
                <div class="mechanism-arrow">↔</div>
                <div class="mechanism-node">制冷方案</div>
                <div class="mechanism-arrow">↔</div>
                <div class="mechanism-node">供配电架构</div>
              </div>
              <p>
                系统会对三类方案的容量、能效、投资、碳排和约束条件进行横向校核，
                若某一子方案导致总目标失衡，仲裁器会回调对应模块重新寻优，直到形成可落地的一致性方案。
              </p>
            </div>
          </el-card>
        </div>

        <div v-show="activeSection === 'faq'" class="content-section">
          <div class="section-header">
            <h2>常见问题</h2>
            <p class="section-desc">用于答辩演示时快速解释关键疑问。</p>
          </div>

          <el-collapse class="faq-collapse" v-model="activeFaq">
            <el-collapse-item v-for="(faq, index) in faqs" :key="index" :title="faq.q" :name="`faq-${index}`">
              <div class="faq-answer">{{ faq.a }}</div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <div v-show="activeSection === 'errors'" class="content-section">
          <div class="section-header">
            <h2>错误码说明</h2>
            <p class="section-desc">便于定位前后端联调、数据缺失和模型调用异常。</p>
          </div>

          <el-card class="error-table-card">
            <el-table :data="errorCodes" border>
              <el-table-column prop="code" label="错误码">
                <template #default="{ row }">
                  <span class="error-code">{{ row.code }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="错误信息" />
              <el-table-column prop="solution" label="建议处理方式" />
            </el-table>
          </el-card>
        </div>

        <div v-show="activeSection === 'contact'" class="content-section">
          <div class="section-header">
            <h2>联系支持</h2>
            <p class="section-desc">如果展示过程中遇到问题，可以在这一页说明联络路径。</p>
          </div>

          <div class="contact-grid">
            <el-card class="contact-card">
              <div class="contact-icon-wrapper">
                <el-icon class="contact-icon"><Phone /></el-icon>
              </div>
              <h3>技术支持</h3>
              <div class="contact-info">
                <p>邮箱：support@example.com</p>
                <p>电话：400-123-4567</p>
                <p>服务时间：周一至周五 9:00-18:00</p>
              </div>
            </el-card>

            <el-card class="contact-card">
              <div class="contact-icon-wrapper feedback">
                <el-icon class="contact-icon"><Message /></el-icon>
              </div>
              <h3>反馈建议</h3>
              <div class="contact-info">
                <p>如果你希望补充更多城市、算法或展示口径，可以通过反馈邮箱提交建议。</p>
                <p class="email-highlight">feedback@example.com</p>
              </div>
            </el-card>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Link,
  Document,
  Setting,
  Bell,
  Phone,
  PieChart,
  RefreshRight,
  Briefcase,
  Tools,
  FolderOpened,
  Message
} from '@element-plus/icons-vue'

const activeSection = ref('quickstart')
const activeFaq = ref(['faq-0'])

const quickStartSteps = [
  {
    title: '创建项目',
    desc: '在首页或参数配置页创建项目，确定建设城市、负荷规模和展示目标。',
    icon: FolderOpened,
    color: '#8be8b8',
    bgColor: 'rgba(45, 166, 110, 0.18)'
  },
  {
    title: '填写参数',
    desc: '输入 IT 负荷、目标绿电占比、气候与水资源条件，形成初始约束。',
    icon: Setting,
    color: '#9fe6d7',
    bgColor: 'rgba(50, 138, 132, 0.18)'
  },
  {
    title: '生成方案',
    desc: '系统启动绿电、制冷、供配电三类智能体并行计算，并自动进行仲裁。',
    icon: RefreshRight,
    color: '#f3dc93',
    bgColor: 'rgba(172, 138, 56, 0.18)'
  },
  {
    title: '查看详情',
    desc: '在方案详情页查看关键指标、成本结构、图表和完整方案报告。',
    icon: Document,
    color: '#8ad4ff',
    bgColor: 'rgba(54, 122, 160, 0.18)'
  }
]

const agents = [
  {
    title: '绿电智能体',
    desc: '资源配置与低碳优化',
    detail: '基于风光资源、目标绿电占比与购电补足逻辑，给出风电、光伏、储能及绿电采购建议。',
    icon: PieChart,
    color: '#9bf0bf',
    bgColor: 'rgba(45, 166, 110, 0.18)',
    factors: ['风光资源曲线', '绿电直连比例', '绿证补足', '碳减排目标']
  },
  {
    title: '制冷智能体',
    desc: '能效与气候适配',
    detail: '综合温度、水资源紧缺程度与算力密度，对多种制冷架构进行评分，输出推荐技术路径。',
    icon: Briefcase,
    color: '#a8f0df',
    bgColor: 'rgba(50, 138, 132, 0.18)',
    factors: ['PUE 目标', 'WUE 约束', '自然冷却时长', '余热回收潜力']
  },
  {
    title: '供配电智能体',
    desc: '架构与可靠性配置',
    detail: '结合标准规范、容量等级和可靠性要求，确定接入电压、主接线方式、变压器冗余和备电策略。',
    icon: Tools,
    color: '#f1d991',
    bgColor: 'rgba(172, 138, 56, 0.18)',
    factors: ['供电等级', 'N/N+1 冗余', '柴油机配置', '标准规范约束']
  }
]

const faqs = [
  {
    q: '为什么绿电占比不等于绿电直连占比？',
    a: '因为项目现已区分“直连绿电”和“采购绿电”两部分。直连受本地资源与消纳条件限制，剩余部分可通过绿电交易或绿证补足。'
  },
  {
    q: '为什么不同城市会推荐不同的制冷方式？',
    a: '制冷方案强依赖年平均温度、湿度、水资源条件和机柜功率密度，所以城市变化会直接影响 PUE、WUE 和经济性。'
  },
  {
    q: '年碳排放是如何得到的？',
    a: '系统按全年用电量乘以剩余非绿电部分的排放因子计算，并根据直连绿电和采购绿电占比进行扣减。'
  },
  {
    q: '为什么要做多智能体协同，而不是单一模型一次输出？',
    a: '因为绿电、制冷、供配电之间存在明显耦合关系。拆成多智能体后可以分别优化，再通过仲裁形成更接近工程逻辑的方案。'
  }
]

const errorCodes = [
  {
    code: 'E001',
    message: '模型服务连接失败',
    solution: '检查 API Key、网络连接和后端服务配置，确认大模型接口可正常访问。'
  },
  {
    code: 'E002',
    message: '关键输入参数缺失',
    solution: '补全项目地点、IT 负荷、优先级等必要参数后重新生成。'
  },
  {
    code: 'E003',
    message: '城市资源数据未命中',
    solution: '检查城市映射关系，必要时切换至已有样例城市或补充风光资源数据文件。'
  },
  {
    code: 'E004',
    message: '方案仲裁失败',
    solution: '通常是子方案约束冲突导致，可适当降低目标绿电占比或放宽 PUE 目标。'
  },
  {
    code: 'E005',
    message: '报告导出异常',
    solution: '检查报告内容是否为空、图表是否渲染完成，以及导出接口是否正常返回。'
  }
]
</script>

<style scoped>
.help-page {
  height: calc(100% - 20px);
  padding: 8px 0 28px;
}

.help-layout {
  display: flex;
  height: 100%;
  gap: 20px;
}

.help-sidebar {
  width: 220px;
  background:
    radial-gradient(circle at top, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 32%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 0%, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 100%);
  border-radius: 22px;
  padding: 12px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  box-shadow: var(--shadow-glow);
}

.help-menu {
  border: none;
  background: transparent;
}

.help-menu :deep(.el-menu-item) {
  height: 46px;
  line-height: 46px;
  border-radius: 12px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  color: var(--text-secondary);
}

.help-menu :deep(.el-menu-item:hover) {
  background: color-mix(in oklab, var(--primary-color) 8%, var(--bg-card));
  color: var(--primary-color);
}

.help-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 10%, var(--bg-panel)) 100%);
  color: var(--primary-color);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 20%, transparent);
}

.help-content {
  flex: 1;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 30%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 0%, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 100%);
  border-radius: 24px;
  padding: 28px;
  overflow-y: auto;
  border: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  box-shadow: var(--shadow-glow);
}

.section-header {
  margin-bottom: 28px;
}

.section-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.section-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

.step-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.step-card {
  position: relative;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border-radius: 18px;
  padding: 20px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px color-mix(in oklab, var(--primary-color) 14%, transparent);
}

.step-number {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.step-content h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.step-content p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.param-card,
.agent-card,
.mechanism-card,
.error-table-card,
.contact-card {
  border-radius: 18px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
}

.param-card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.param-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 12px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border-radius: 12px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 10%, transparent);
}

.param-label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
  min-width: 130px;
}

.param-desc {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: right;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.agent-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px color-mix(in oklab, var(--primary-color) 14%, transparent);
}

.agent-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.agent-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.agent-info h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.agent-desc {
  font-size: 12px;
  color: var(--text-placeholder);
}

.agent-detail p,
.mechanism-content p,
.faq-answer,
.contact-info p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.agent-detail p {
  margin-bottom: 16px;
}

.agent-factors h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.factor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.factor-tag {
  padding: 4px 12px;
  background: color-mix(in oklab, var(--primary-color) 8%, var(--bg-card));
  color: var(--primary-color);
  border-radius: 20px;
  font-size: 12px;
}

.mechanism-card {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 0%, color-mix(in oklab, var(--bg-panel) 90%, var(--accent-color) 10%) 100%);
}

.mechanism-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.mechanism-node {
  padding: 12px 24px;
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  border-radius: 10px;
  font-weight: 500;
  box-shadow: 0 10px 22px color-mix(in oklab, var(--primary-color) 22%, transparent);
}

.mechanism-arrow {
  font-size: 20px;
  color: var(--text-placeholder);
}

.faq-collapse {
  border-radius: 14px;
  overflow: hidden;
}

.faq-collapse :deep(.el-collapse-item__header) {
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-light));
  font-weight: 500;
  color: var(--text-primary);
}

.faq-collapse :deep(.el-collapse-item__header:hover) {
  background: color-mix(in oklab, var(--primary-color) 8%, var(--bg-card));
}

.faq-answer {
  padding: 12px 0;
}

.error-code {
  font-family: monospace;
  font-weight: 600;
  color: var(--danger-color);
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.contact-card {
  text-align: center;
  padding: 24px;
}

.contact-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.contact-icon-wrapper.feedback {
  background: linear-gradient(180deg, var(--accent-color) 0%, color-mix(in oklab, var(--accent-color) 72%, var(--primary-ink)) 100%);
}

.contact-icon {
  font-size: 28px;
  color: white;
}

.contact-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.email-highlight {
  color: var(--primary-color);
  font-weight: 500;
}

.help-content :deep(.el-card__body) {
  background: transparent;
}

.error-table-card :deep(.el-table) {
  --el-table-border-color: color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  --el-table-header-bg-color: color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%);
  --el-table-row-hover-bg-color: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  background: transparent;
  color: var(--text-primary);
}

.error-table-card :deep(.el-table th),
.error-table-card :deep(.el-table td) {
  background: transparent;
}

@media (max-width: 1024px) {
  .step-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .agent-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .contact-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .help-layout {
    flex-direction: column;
  }

  .help-sidebar {
    width: 100%;
  }

  .help-content {
    padding: 20px;
  }

  .step-cards,
  .agent-grid {
    grid-template-columns: 1fr;
  }

  .param-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .param-desc {
    text-align: left;
  }

  .mechanism-diagram {
    flex-wrap: wrap;
  }
}
</style>
