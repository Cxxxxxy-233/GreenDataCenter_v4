<template>
  <div class="settings-page">
    <el-card class="settings-card">
      <template #header>
        <span class="card-title">API 配置</span>
        <div class="card-icon">
          <el-icon><Setting /></el-icon>
        </div>
      </template>
      <el-form :model="apiConfig" label-width="180px">
        <el-form-item label="OpenAI API Key">
          <div class="api-input-group">
            <el-input
              v-model="apiConfig.apiKey"
              :type="showApiKey ? 'text' : 'password'"
              placeholder="请输入 API Key"
            />
            <el-button @click="showApiKey = !showApiKey" class="toggle-btn">
              {{ showApiKey ? '隐藏' : '显示' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button class="primary-btn" @click="testConnection">测试连接</el-button>
          <span :class="['connection-status', connectionStatus]">
            {{ connectionStatusText }}
          </span>
        </el-form-item>
        <el-form-item label="说明">
          <p class="help-text">
            该配置用于连接大模型服务，支撑多智能体协同生成绿电、制冷和供配电方案。展示时建议使用已验证可用的 Key，
            以确保方案生成流程完整、响应稳定。
          </p>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">经济性参数</span>
        <div class="card-icon cost-icon">
          <el-icon><PieChart /></el-icon>
        </div>
      </template>
      <el-form :model="costConfig" label-width="160px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电价（元/kWh）">
              <el-input-number
                v-model="costConfig.electricityPrice"
                :min="0.1"
                :max="2"
                :step="0.01"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="折现率（%）">
              <el-input-number
                v-model="costConfig.discountRate"
                :min="1"
                :max="20"
                :step="0.5"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备寿命（年）">
              <el-input-number
                v-model="costConfig.equipmentLife"
                :min="1"
                :max="30"
                :step="1"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="运维系数">
              <el-input-number
                v-model="costConfig.maintenanceCoeff"
                :min="0.1"
                :max="2"
                :step="0.1"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="text" class="text-btn">查看成本假设口径</el-button>
          <el-button type="text" class="text-btn">导出经济性配置</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="restoreCostDefaults">恢复默认值</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">决策权重</span>
        <div class="card-icon weight-icon">
          <el-icon><Briefcase /></el-icon>
        </div>
      </template>
      <el-form :model="weightConfig" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="经济性（%）">
              <el-slider
                v-model="weightConfig.economy"
                :min="0"
                :max="100"
                show-input
                @change="updateWeights"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="可靠性（%）">
              <el-slider
                v-model="weightConfig.reliability"
                :min="0"
                :max="100"
                show-input
                @change="updateWeights"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="低碳性（%）">
              <el-slider
                v-model="weightConfig.environment"
                :min="0"
                :max="100"
                show-input
                @change="updateWeights"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <span :class="['weight-sum', weightSum === 100 ? 'success' : 'error']">
            当前权重总和：{{ weightSum }}% {{ weightSum === 100 ? '（已平衡）' : '（建议调整至 100%）' }}
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">默认项目参数</span>
        <div class="card-icon default-icon">
          <el-icon><Document /></el-icon>
        </div>
      </template>
      <el-form :model="defaultConfig" label-width="160px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="默认地区">
              <el-select v-model="defaultConfig.location">
                <el-option label="乌兰察布" value="wulanchabu" />
                <el-option label="北京" value="beijing" />
                <el-option label="上海" value="shanghai" />
                <el-option label="广州" value="guangzhou" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认优先级">
              <el-select v-model="defaultConfig.priority">
                <el-option label="经济优先" value="经济优先" />
                <el-option label="低碳优先" value="低碳优先" />
                <el-option label="可靠优先" value="可靠优先" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认预算（万元）">
              <el-input-number
                v-model="defaultConfig.budget"
                :min="100"
                :max="100000"
                :step="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认 PUE 目标">
              <el-input-number
                v-model="defaultConfig.pueTarget"
                :min="1.05"
                :max="1.5"
                :step="0.01"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">系统信息</span>
        <div class="card-icon info-icon">
          <el-icon><QuestionFilled /></el-icon>
        </div>
      </template>
      <el-form label-width="140px">
        <el-form-item label="系统版本">
          <span class="info-value">v2.1.0</span>
        </el-form-item>
        <el-form-item label="最近更新时间">
          <span class="info-value">2024-01-15 10:00:00</span>
        </el-form-item>
        <el-form-item>
          <el-button class="primary-btn" @click="checkUpdate">检查更新</el-button>
          <span v-if="checkingUpdate" class="update-status loading">正在检查...</span>
          <span v-else-if="updateStatus" class="update-status success">{{ updateStatus }}</span>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Setting, PieChart, Briefcase, Document, QuestionFilled } from '@element-plus/icons-vue'

const showApiKey = ref(false)
const connectionStatus = ref('')
const connectionStatusText = ref('')
const checkingUpdate = ref(false)
const updateStatus = ref('')

const apiConfig = reactive({
  apiKey: '******'
})

const costConfig = reactive({
  electricityPrice: 0.65,
  discountRate: 8,
  equipmentLife: 10,
  maintenanceCoeff: 1
})

const weightConfig = reactive({
  economy: 35,
  reliability: 40,
  environment: 25
})

const defaultConfig = reactive({
  location: 'wulanchabu',
  priority: '低碳优先',
  budget: 1000,
  pueTarget: 1.18
})

const weightSum = computed(() => {
  return weightConfig.economy + weightConfig.reliability + weightConfig.environment
})

const testConnection = () => {
  connectionStatus.value = 'loading'
  connectionStatusText.value = '正在测试连接...'
  setTimeout(() => {
    connectionStatus.value = 'success'
    connectionStatusText.value = '连接成功，API 可正常调用'
  }, 1000)
}

const updateWeights = () => {}

const restoreCostDefaults = () => {
  costConfig.electricityPrice = 0.65
  costConfig.discountRate = 8
  costConfig.equipmentLife = 10
  costConfig.maintenanceCoeff = 1
}

const checkUpdate = () => {
  checkingUpdate.value = true
  setTimeout(() => {
    checkingUpdate.value = false
    updateStatus.value = '当前已是最新版本'
  }, 1500)
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 8px 0 36px;
}

.settings-card {
  margin-bottom: 0;
  border-radius: 24px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 14%, var(--border-light));
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 30%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 0%, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 100%);
  box-shadow: var(--shadow-glow);
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
  overflow: hidden;
}

.settings-card:hover {
  border-color: color-mix(in oklab, var(--primary-color) 24%, var(--border-default));
  box-shadow: 0 22px 52px rgba(8, 44, 28, 0.28);
  transform: translateY(-2px);
}

.settings-card :deep(.el-card__header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px 18px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  background:
    linear-gradient(90deg, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 32%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%), color-mix(in oklab, var(--bg-card) 92%, var(--primary-color) 8%));
}

.settings-card :deep(.el-card__body) {
  padding: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.01em;
  color: var(--text-primary);
}

.card-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 18%, transparent);
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 22%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 12%, var(--bg-panel)) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: color-mix(in oklab, white 88%, var(--primary-color) 12%);
  font-size: 17px;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 24%, transparent);
}

.card-icon.cost-icon {
  background: linear-gradient(180deg, color-mix(in oklab, var(--accent-color) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--accent-color) 8%, var(--bg-panel)) 100%);
}

.card-icon.weight-icon {
  background: linear-gradient(180deg, color-mix(in oklab, var(--warning-color) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--warning-color) 8%, var(--bg-panel)) 100%);
}

.card-icon.default-icon {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-light) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 10%, var(--bg-panel)) 100%);
}

.card-icon.info-icon {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--accent-color) 10%, var(--bg-panel)) 100%);
}

.api-input-group {
  display: flex;
  gap: 12px;
  width: min(620px, 100%);
}

.toggle-btn {
  background: color-mix(in oklab, var(--bg-card) 88%, var(--primary-color) 12%);
  color: var(--primary-color);
  border: 1px solid color-mix(in oklab, var(--primary-color) 18%, transparent);
  border-radius: 12px;
  transition: all 0.25s ease;
}

.toggle-btn:hover {
  background: color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%);
  border-color: color-mix(in oklab, var(--primary-color) 26%, var(--border-default));
}

.primary-btn {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 22%, transparent);
  color: color-mix(in oklab, white 95%, var(--primary-color) 5%);
  box-shadow: 0 10px 24px color-mix(in oklab, var(--primary-color) 22%, transparent);
  transition: all 0.25s ease;
}

.primary-btn:hover {
  box-shadow: 0 14px 30px color-mix(in oklab, var(--primary-color) 26%, transparent);
  transform: translateY(-1px);
}

.text-btn {
  color: var(--primary-color);
  font-weight: 500;
  transition: all 0.25s ease;
}

.text-btn:hover {
  color: var(--primary-light);
}

.connection-status {
  margin-left: 12px;
  font-size: 14px;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}

.connection-status.success {
  color: var(--success-color);
}

.connection-status.error {
  color: var(--danger-color);
}

.connection-status.loading {
  color: var(--info-color);
}

.help-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.75;
}

.weight-sum {
  font-size: 14px;
  font-weight: 500;
}

.weight-sum.success {
  color: var(--success-color);
}

.weight-sum.error {
  color: var(--danger-color);
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.update-status {
  margin-left: 12px;
  font-size: 14px;
  font-weight: 500;
}

.update-status.success {
  color: var(--success-color);
}

.update-status.loading {
  color: var(--info-color);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-5px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.settings-page :deep(.el-form) {
  --el-text-color-regular: var(--text-secondary);
  --el-text-color-primary: var(--text-primary);
}

.settings-page :deep(.el-form-item) {
  margin-bottom: 22px;
}

.settings-page :deep(.el-form-item__label) {
  color: color-mix(in oklab, white 86%, var(--primary-color) 14%);
  font-weight: 600;
}

.settings-page :deep(.el-input__wrapper),
.settings-page :deep(.el-input-number),
.settings-page :deep(.el-select__wrapper),
.settings-page :deep(.el-textarea__inner) {
  background: color-mix(in oklab, var(--bg-card) 92%, var(--primary-color) 8%);
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 14%, var(--border-light)) !important;
  color: var(--text-primary);
  border-radius: 14px;
}

.settings-page :deep(.el-input__inner),
.settings-page :deep(.el-select__selected-item),
.settings-page :deep(.el-textarea__inner) {
  color: var(--text-primary);
}

.settings-page :deep(.el-input__inner::placeholder),
.settings-page :deep(.el-textarea__inner::placeholder) {
  color: var(--text-placeholder);
}

.settings-page :deep(.el-input-number__decrease),
.settings-page :deep(.el-input-number__increase) {
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%);
  color: color-mix(in oklab, white 88%, var(--primary-color) 12%);
  border-color: color-mix(in oklab, var(--primary-color) 10%, var(--border-light));
}

.settings-page :deep(.el-slider__runway) {
  background: color-mix(in oklab, var(--bg-panel) 86%, var(--border-light) 14%);
}

.settings-page :deep(.el-slider__bar) {
  background: linear-gradient(90deg, var(--primary-dark), var(--primary-light));
}

.settings-page :deep(.el-slider__button) {
  border-color: var(--primary-light);
  background: color-mix(in oklab, white 88%, var(--primary-color) 12%);
}

.settings-page :deep(.el-select),
.settings-page :deep(.el-input-number) {
  width: 100%;
}

@media (max-width: 768px) {
  .settings-card :deep(.el-card__header),
  .settings-card :deep(.el-card__body) {
    padding-left: 18px;
    padding-right: 18px;
  }

  .api-input-group {
    width: 100%;
    flex-direction: column;
  }
}
</style>
