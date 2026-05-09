<template>
  <div class="settings-page">
    <el-card class="settings-card">
      <template #header>
        <span class="card-title">API配置</span>
      </template>
      <el-form :model="apiConfig" label-width="180px">
        <el-form-item label="阿里云百炼API Key">
          <div class="api-input-group">
            <el-input
              v-model="apiConfig.apiKey"
              :type="showApiKey ? 'text' : 'password'"
              placeholder="请输入API Key"
            />
            <el-button @click="showApiKey = !showApiKey">
              {{ showApiKey ? '隐藏' : '显示' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button @click="testConnection">测试连接</el-button>
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
          <el-button type="text">批量导入制冷方案成本</el-button>
          <el-button type="text">导出成本配置</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="restoreCostDefaults">恢复默认值</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span class="card-title">专家权重配置</span>
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
      </template>
      <el-form label-width="140px">
        <el-form-item label="系统版本">
          <span class="info-value">v2.1.0</span>
        </el-form-item>
        <el-form-item label="最后更新时间">
          <span class="info-value">2024-01-15 10:00:00</span>
        </el-form-item>
        <el-form-item>
          <el-button @click="checkUpdate">检查更新</el-button>
          <span v-if="checkingUpdate" class="update-status">检查中...</span>
          <span v-else-if="updateStatus" class="update-status success">{{ updateStatus }}</span>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

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
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.api-input-group {
  display: flex;
  gap: 12px;
}

.connection-status {
  margin-left: 12px;
  font-size: 14px;
}

.connection-status.success {
  color: #00B42A;
}

.connection-status.error {
  color: #F53F3F;
}

.connection-status.loading {
  color: #165DFF;
}

.help-text {
  font-size: 13px;
  color: #8F959E;
}

.weight-sum {
  font-size: 14px;
}

.weight-sum.success {
  color: #00B42A;
}

.weight-sum.error {
  color: #F53F3F;
}

.info-value {
  font-size: 14px;
  color: #1F2329;
}

.update-status {
  margin-left: 12px;
  font-size: 14px;
}

.update-status.success {
  color: #00B42A;
}
</style>
