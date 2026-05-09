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
            <el-icon><Message /></el-icon>
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
          <h2>快速入门</h2>
          <div class="content-block">
            <h3>第一步：创建项目</h3>
            <p>点击首页的"快速创建项目"按钮，进入参数配置页面。</p>
          </div>
          <div class="content-block">
            <h3>第二步：填写参数</h3>
            <p>根据实际情况填写项目参数，包括基础信息、算力负荷、地域环境、目标优先级等。</p>
            <p>系统会根据地域自动填充部分参数，如年均温度、水资源紧缺指数等。</p>
          </div>
          <div class="content-block">
            <h3>第三步：生成方案</h3>
            <p>点击"下一步：生成方案"按钮，系统将启动多智能体协同优化流程。</p>
            <p>生成过程中可以查看实时进度和日志。</p>
          </div>
          <div class="content-block">
            <h3>第四步：查看报告</h3>
            <p>方案生成完成后，可查看详细的方案报告，包括制冷系统、绿电系统、供电系统等模块。</p>
            <p>支持导出PDF和Markdown格式的报告。</p>
          </div>
        </div>

        <div v-show="activeSection === 'params'" class="content-section">
          <h2>参数说明</h2>
          <div class="content-block">
            <h3>基础信息</h3>
            <ul>
              <li><strong>项目名称：</strong>必填，用于标识项目</li>
              <li><strong>项目描述：</strong>选填，项目的详细说明</li>
              <li><strong>项目负责人：</strong>选填，项目负责人姓名</li>
            </ul>
          </div>
          <div class="content-block">
            <h3>算力与负荷</h3>
            <ul>
              <li><strong>单机柜算力密度：</strong>范围5-800kW，默认30kW</li>
              <li><strong>IT总负荷：</strong>范围100-100000kW，默认1000kW</li>
              <li><strong>机柜总数：</strong>自动计算，不可编辑</li>
            </ul>
          </div>
          <div class="content-block">
            <h3>环境与地域</h3>
            <ul>
              <li><strong>项目所在地：</strong>影响温度、CWSI等参数</li>
              <li><strong>年均温度：</strong>影响制冷方案选择</li>
              <li><strong>CWSI：</strong>水资源紧缺指数，值越小越缺水</li>
            </ul>
          </div>
        </div>

        <div v-show="activeSection === 'agents'" class="content-section">
          <h2>智能体工作原理</h2>
          <div class="content-block">
            <h3>绿电分配智能体</h3>
            <p>负责优化风光储配置，最大化绿电消纳率。</p>
            <p>考虑因素：当地风光资源、电价政策、储能成本等。</p>
          </div>
          <div class="content-block">
            <h3>制冷方案智能体</h3>
            <p>从26种制冷方案库中选择最优方案。</p>
            <p>考虑因素：PUE、WUE、投资成本、运维成本等。</p>
          </div>
          <div class="content-block">
            <h3>供电方案智能体</h3>
            <p>设计主备供电架构，确保系统可靠性。</p>
            <p>考虑因素：可用性要求、设备冗余、极端场景保障等。</p>
          </div>
          <div class="content-block">
            <h3>协同博弈机制</h3>
            <p>三个智能体通过协同博弈进行方案优化，最终达成全局最优解。</p>
          </div>
        </div>

        <div v-show="activeSection === 'faq'" class="content-section">
          <h2>常见问题</h2>
          <div class="content-block">
            <h3>Q：方案生成时间需要多久？</h3>
            <p>A：通常需要30-60秒，具体取决于参数复杂度和服务器负载。</p>
          </div>
          <div class="content-block">
            <h3>Q：如果API调用失败怎么办？</h3>
            <p>A：系统会自动切换至纯规则兜底模式，生成标准化报告。</p>
          </div>
          <div class="content-block">
            <h3>Q：如何导出报告？</h3>
            <p>A：在方案详情页点击"导出PDF报告"或"导出Markdown报告"按钮。</p>
          </div>
          <div class="content-block">
            <h3>Q：参数如何保存？</h3>
            <p>A：系统每30秒自动保存一次，也可手动点击"保存参数"按钮。</p>
          </div>
        </div>

        <div v-show="activeSection === 'errors'" class="content-section">
          <h2>错误码说明</h2>
          <div class="content-block">
            <h3>错误码列表</h3>
            <el-table :data="errorCodes" border>
              <el-table-column prop="code" label="错误码" />
              <el-table-column prop="message" label="错误信息" />
              <el-table-column prop="solution" label="解决方法" />
            </el-table>
          </div>
        </div>

        <div v-show="activeSection === 'contact'" class="content-section">
          <h2>联系我们</h2>
          <div class="content-block">
            <h3>技术支持</h3>
            <p>邮箱：support@example.com</p>
            <p>电话：400-123-4567</p>
            <p>工作时间：周一至周五 9:00-18:00</p>
          </div>
          <div class="content-block">
            <h3>反馈建议</h3>
            <p>如有任何问题或建议，请发送邮件至 feedback@example.com</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Link, Document, Setting, Message, Phone } from '@element-plus/icons-vue'

const activeSection = ref('quickstart')

const errorCodes = ref([
  { code: 'E001', message: 'API调用失败', solution: '检查API Key是否正确，网络是否正常' },
  { code: 'E002', message: '参数校验失败', solution: '检查必填参数是否填写完整' },
  { code: 'E003', message: '方案生成超时', solution: '重新生成方案，或联系技术支持' },
  { code: 'E004', message: '预算超支', solution: '调整参数或增加预算' },
  { code: 'E005', message: '数据存储失败', solution: '检查网络连接，刷新页面重试' }
])
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

.help-sidebar {
  width: 200px;
  background: white;
  border-radius: 12px;
  padding: 10px;
}

.help-menu {
  border: none;
}

.help-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
}

.help-menu :deep(.el-menu-item.is-active) {
  background: #E8F0FE;
  color: #165DFF;
}

.help-content {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 24px;
  overflow-y: auto;
}

.content-section h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 24px;
}

.content-block {
  margin-bottom: 24px;
}

.content-block h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.content-block p {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.8;
}

.content-block ul {
  padding-left: 20px;
}

.content-block li {
  font-size: 14px;
  color: #4E5969;
  margin-bottom: 8px;
}
</style>
