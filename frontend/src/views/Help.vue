<template>
  <div class="help-page">
    <div class="help-layout">
      <aside class="help-sidebar">
        <el-menu
          :default-active="activeSection"
          class="help-menu"
          mode="vertical"
        >
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
            <span>智能体工作原理</span>
          </el-menu-item>
          <el-menu-item index="faq" @click="activeSection = 'faq'">
            <el-icon><Bell /></el-icon>
            <span>常见问题</span>
          </el-menu-item>
          <el-menu-item index="errors" @click="activeSection = 'errors'">
            <el-icon><Setting /></el-icon>
            <span>错误码说明</span>
          </el-menu-item>
          <el-menu-item index="contact" @click="activeSection = 'contact'">
            <el-icon><Phone /></el-icon>
            <span>联系我们</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <main class="help-content">
        <div v-show="activeSection === 'quickstart'" class="content-section">
          <div class="section-header">
            <h2>快速入门</h2>
            <p class="section-desc">简单四步，快速生成最优方案</p>
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
            <p class="section-desc">详细的参数配置说明</p>
          </div>
          
          <el-card class="param-card">
            <h3 class="card-title">基础信息</h3>
            <div class="param-list">
              <div class="param-item">
                <span class="param-label">项目名称</span>
                <span class="param-desc">必填，用于标识项目</span>
              </div>
              <div class="param-item">
                <span class="param-label">项目描述</span>
                <span class="param-desc">选填，项目的详细说明</span>
              </div>
              <div class="param-item">
                <span class="param-label">项目负责人</span>
                <span class="param-desc">选填，项目负责人姓名</span>
              </div>
            </div>
          </el-card>

          <el-card class="param-card">
            <h3 class="card-title">算力与负荷</h3>
            <div class="param-list">
              <div class="param-item">
                <span class="param-label">单机柜算力密度</span>
                <span class="param-desc">范围5-800kW，默认30kW</span>
              </div>
              <div class="param-item">
                <span class="param-label">IT总负荷</span>
                <span class="param-desc">范围100-100000kW，默认1000kW</span>
              </div>
              <div class="param-item">
                <span class="param-label">机柜总数</span>
                <span class="param-desc">自动计算，不可编辑</span>
              </div>
            </div>
          </el-card>

          <el-card class="param-card">
            <h3 class="card-title">环境与地域</h3>
            <div class="param-list">
              <div class="param-item">
                <span class="param-label">项目所在地</span>
                <span class="param-desc">影响温度、CWSI等参数</span>
              </div>
              <div class="param-item">
                <span class="param-label">年均温度</span>
                <span class="param-desc">影响制冷方案选择</span>
              </div>
              <div class="param-item">
                <span class="param-label">CWSI</span>
                <span class="param-desc">水资源紧缺指数，值越小越缺水</span>
              </div>
            </div>
          </el-card>
        </div>

        <div v-show="activeSection === 'agents'" class="content-section">
          <div class="section-header">
            <h2>智能体工作原理</h2>
            <p class="section-desc">多智能体协同优化机制</p>
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
                <h4>考虑因素</h4>
                <div class="factor-tags">
                  <span v-for="(factor, i) in agent.factors" :key="i" class="factor-tag">{{ factor }}</span>
                </div>
              </div>
            </el-card>
          </div>

          <el-card class="mechanism-card">
            <h3 class="card-title">协同博弈机制</h3>
            <div class="mechanism-content">
              <div class="mechanism-diagram">
                <div class="mechanism-node">绿电分配</div>
                <div class="mechanism-arrow">↔</div>
                <div class="mechanism-node">制冷方案</div>
                <div class="mechanism-arrow">↔</div>
                <div class="mechanism-node">供电方案</div>
              </div>
              <p>三个智能体通过协同博弈进行方案优化，最终达成全局最优解。</p>
            </div>
          </el-card>
        </div>

        <div v-show="activeSection === 'faq'" class="content-section">
          <div class="section-header">
            <h2>常见问题</h2>
            <p class="section-desc">解答您的疑问</p>
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
            <p class="section-desc">错误处理指南</p>
          </div>

          <el-card class="error-table-card">
            <el-table :data="errorCodes" border>
              <el-table-column prop="code" label="错误码">
                <template #default="{ row }">
                  <span class="error-code">{{ row.code }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="错误信息" />
              <el-table-column prop="solution" label="解决方法" />
            </el-table>
          </el-card>
        </div>

        <div v-show="activeSection === 'contact'" class="content-section">
          <div class="section-header">
            <h2>联系我们</h2>
            <p class="section-desc">获取技术支持</p>
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
                <p>工作时间：周一至周五 9:00-18:00</p>
              </div>
            </el-card>

            <el-card class="contact-card">
              <div class="contact-icon-wrapper feedback">
                <el-icon class="contact-icon"><Message /></el-icon>
              </div>
              <h3>反馈建议</h3>
              <div class="contact-info">
                <p>如有任何问题或建议，请发送邮件至</p>
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
import { Link, Document, Setting, Bell, Phone, PieChart, RefreshRight, Briefcase, Tools, FolderOpened } from '@element-plus/icons-vue'

const activeSection = ref('quickstart')
const activeFaq = ref(['faq-0'])

const quickStartSteps = [
  { title: '创建项目', desc: '点击首页的"快速创建项目"按钮，进入参数配置页面', icon: PieChart, color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.1)' },
  { title: '填写参数', desc: '根据实际情况填写项目参数，包括基础信息、算力负荷、地域环境等', icon: Setting, color: '#06B6D4', bgColor: 'rgba(6, 182, 212, 0.1)' },
  { title: '生成方案', desc: '点击"下一步：生成方案"按钮，系统将启动多智能体协同优化流程', icon: RefreshRight, color: '#F59E0B', bgColor: 'rgba(245, 158, 11, 0.1)' },
  { title: '查看报告', desc: '方案生成完成后，可查看详细的方案报告，支持PDF和Markdown导出', icon: Briefcase, color: '#8B5CF6', bgColor: 'rgba(139, 92, 246, 0.1)' }
]

const agents = [
  { title: '绿电分配智能体', desc: '风光储优化专家', detail: '负责优化风光储配置，最大化绿电消纳率', factors: ['当地风光资源', '电价政策', '储能成本'], icon: Tools, color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.1)' },
  { title: '制冷方案智能体', desc: '高效制冷专家', detail: '从26种制冷方案库中选择最优方案', factors: ['PUE', 'WUE', '投资成本', '运维成本'], icon: FolderOpened, color: '#06B6D4', bgColor: 'rgba(6, 182, 212, 0.1)' },
  { title: '供电方案智能体', desc: '可靠供电专家', detail: '设计主备供电架构，确保系统可靠性', factors: ['可用性要求', '设备冗余', '极端场景'], icon: Setting, color: '#F59E0B', bgColor: 'rgba(245, 158, 11, 0.1)' }
]

const faqs = [
  { q: '方案生成时间需要多久？', a: '通常需要30-60秒，具体取决于参数复杂度和服务器负载。系统会实时显示生成进度，您可以在生成过程中查看各阶段的详细结果。' },
  { q: '如果API调用失败怎么办？', a: '系统会自动切换至纯规则兜底模式，生成标准化报告。即使API不可用，您仍然可以获得合理的方案建议。' },
  { q: '如何导出报告？', a: '在方案详情页点击"导出PDF报告"或"导出Markdown报告"按钮。系统支持多种格式导出，方便您进行文档归档和分享。' },
  { q: '参数如何保存？', a: '系统每30秒自动保存一次，也可手动点击"保存参数"按钮。您可以随时返回继续编辑未完成的项目配置。' }
]

const errorCodes = [
  { code: 'E001', message: 'API调用失败', solution: '检查API Key是否正确，网络是否正常' },
  { code: 'E002', message: '参数校验失败', solution: '检查必填参数是否填写完整' },
  { code: 'E003', message: '方案生成超时', solution: '重新生成方案，或联系技术支持' },
  { code: 'E004', message: '预算超支', solution: '调整参数或增加预算' },
  { code: 'E005', message: '数据存储失败', solution: '检查网络连接，刷新页面重试' }
]
</script>

<style scoped>
.help-page {
  height: calc(100% - 20px);
}

.help-layout {
  display: flex;
  height: 100%;
  gap: 20px;
}

/* 侧边栏 - 科技绿色主题 */
.help-sidebar {
  width: 200px;
  background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%);
  border-radius: 14px;
  padding: 12px;
  border: 1px solid #D1FAE5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.help-menu {
  border: none;
}

.help-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  border-radius: 8px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
}

.help-menu :deep(.el-menu-item:hover) {
  background: rgba(16, 185, 129, 0.06);
  color: var(--primary-color);
}

.help-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
  color: var(--primary-color);
  font-weight: 600;
}

/* 内容区 */
.help-content {
  flex: 1;
  background: white;
  border-radius: 14px;
  padding: 28px;
  overflow-y: auto;
  border: 1px solid rgba(16, 185, 129, 0.08);
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
  color: #6B7280;
}

/* 步骤卡片 */
.step-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.step-card {
  position: relative;
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  border-radius: 14px;
  padding: 20px;
  border: 1px solid rgba(16, 185, 129, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12);
}

.step-number {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
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
  color: #6B7280;
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

/* 参数卡片 */
.param-card {
  margin-bottom: 20px;
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.08);
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
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
  padding: 12px;
  background: white;
  border-radius: 10px;
}

.param-label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.param-desc {
  font-size: 13px;
  color: #6B7280;
}

/* 智能体网格 */
.agent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.agent-card {
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.08);
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12);
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
  color: #9CA3AF;
}

.agent-detail p {
  font-size: 14px;
  color: #4B5563;
  line-height: 1.6;
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
  background: rgba(16, 185, 129, 0.08);
  color: var(--primary-color);
  border-radius: 20px;
  font-size: 12px;
}

/* 机制卡片 */
.mechanism-card {
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.08);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%);
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
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  border-radius: 10px;
  font-weight: 500;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25);
}

.mechanism-arrow {
  font-size: 20px;
  color: #9CA3AF;
}

.mechanism-content p {
  font-size: 14px;
  color: #4B5563;
  text-align: center;
}

/* FAQ折叠面板 */
.faq-collapse {
  border-radius: 14px;
  overflow: hidden;
}

.faq-collapse :deep(.el-collapse-item__header) {
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  border-bottom: 1px solid rgba(16, 185, 129, 0.08);
  font-weight: 500;
  color: var(--text-primary);
}

.faq-collapse :deep(.el-collapse-item__header:hover) {
  background: rgba(16, 185, 129, 0.05);
}

.faq-answer {
  font-size: 14px;
  color: #4B5563;
  line-height: 1.8;
  padding: 12px 0;
}

/* 错误码表格 */
.error-table-card {
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.08);
}

.error-code {
  font-family: monospace;
  font-weight: 600;
  color: #EF4444;
}

/* 联系卡片 */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.contact-card {
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.08);
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  text-align: center;
  padding: 24px;
}

.contact-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.contact-icon-wrapper.feedback {
  background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
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

.contact-info p {
  font-size: 14px;
  color: #4B5563;
  margin-bottom: 6px;
}

.email-highlight {
  color: var(--primary-color);
  font-weight: 500;
}

/* 响应式 */
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
  
  .step-cards {
    grid-template-columns: 1fr;
  }
  
  .agent-grid {
    grid-template-columns: 1fr;
  }
  
  .mechanism-diagram {
    flex-wrap: wrap;
  }
}
</style>