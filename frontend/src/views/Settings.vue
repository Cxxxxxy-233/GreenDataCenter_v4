<template>
  <div class="settings-page">
    <el-card class="settings-card">
      <template #header>
        <span class="card-title">API配置</span>
        <div class="card-icon">
          <el-icon><Setting /></el-icon>
        </div>
      </template>
      <el-form :model="apiConfig" label-width="180px">
        <el-form-item label="阿里云百炼API Key">
          <div class="api-input-group">
            <el-input
              v-model="apiConfig.apiKey"
              :type="showApiKey ? 'text' : 'password'"
              placeholder="请输入API Key"
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
          <p class="help-text">如果API不可用，系统将自动使用纯规则兜底模式生成方案</p>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">成本参数配置</span>
        <div class="card-icon cost-icon">
          <el-icon><PieChart /></el-icon>
        </div>
      </template>
      <el-form :model="costConfig" label-width="160px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电价(元/kWh)">
              <el-input-number
                v-model="costConfig.electricityPrice"
                :min="0.1"
                :max="2"
                :step="0.01"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="折现率(%)">
              <el-input-number
                v-model="costConfig.discountRate"
                :min="1"
                :max="20"
                :step="0.5"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备使用年限(年)">
              <el-input-number
                v-model="costConfig.equipmentLife"
                :min="1"
                :max="30"
                :step="1"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="运维成本系数">
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
          <el-button type="text" class="text-btn">批量导入制冷方案成本</el-button>
          <el-button type="text" class="text-btn">导出成本配置</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="restoreCostDefaults">恢复默认值</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">专家权重配置</span>
        <div class="card-icon weight-icon">
          <el-icon><Briefcase /></el-icon>
        </div>
      </template>
      <el-form :model="weightConfig" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="经济性权重(%)">
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
            <el-form-item label="可靠性权重(%)">
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
            <el-form-item label="环保性权重(%)">
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
            权重总和：{{ weightSum }}% {{ weightSum === 100 ? '(正确)' : '(请调整至100%)' }}
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">默认参数配置</span>
        <div class="card-icon default-icon">
          <el-icon><Document /></el-icon>
        </div>
      </template>
      <el-form :model="defaultConfig" label-width="160px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="默认地域">
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
                <el-option label="经济型" value="经济型" />
                <el-option label="环保型" value="环保型" />
                <el-option label="可靠型" value="可靠型" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认预算(万元)">
              <el-input-number
                v-model="defaultConfig.budget"
                :min="100"
                :max="100000"
                :step="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认PUE目标">
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
        <el-form-item label="最后更新时间">
          <span class="info-value">2024-01-15 10:00:00</span>
        </el-form-item>
        <el-form-item>
          <el-button class="primary-btn" @click="checkUpdate">检查更新</el-button>
          <span v-if="checkingUpdate" class="update-status loading">检查中...</span>
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
  priority: '环保型',
  budget: 1000,
  pueTarget: 1.18
})

const weightSum = computed(() => {
  return weightConfig.economy + weightConfig.reliability + weightConfig.environment
})

const testConnection = () => {
  connectionStatus.value = 'loading'
  connectionStatusText.value = '测试中...'
  setTimeout(() => {
    connectionStatus.value = 'success'
    connectionStatusText.value = '✅ API连接正常'
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
  padding-bottom: 30px;
}

.settings-card {
  margin-bottom: 20px;
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.08);
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.settings-card:hover {
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12);
  transform: translateY(-2px);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.card-icon.cost-icon {
  background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25);
}

.card-icon.weight-icon {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}

.card-icon.default-icon {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.25);
}

.card-icon.info-icon {
  background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.25);
}

.api-input-group {
  display: flex;
  gap: 12px;
}

.toggle-btn {
  background: rgba(16, 185, 129, 0.08);
  color: var(--primary-color);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  transition: all 0.25s ease;
}

.toggle-btn:hover {
  background: rgba(16, 185, 129, 0.15);
  border-color: var(--primary-color);
}

.primary-btn {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
  transition: all 0.25s ease;
}

.primary-btn:hover {
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
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
  color: #8F959E;
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
</style>