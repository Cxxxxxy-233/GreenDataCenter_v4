<template>
  <div class="config-page">
    <div class="config-layout">
      <aside class="config-sidebar">
        <el-menu
          :default-active="activeModule"
          class="config-menu"
          mode="vertical"
        >
          <el-menu-item index="basic" @click="activeModule = 'basic'">
            <el-icon><Files /></el-icon>
            <span>项目基础</span>
          </el-menu-item>
          <el-menu-item index="environment" @click="activeModule = 'environment'">
            <el-icon><Location /></el-icon>
            <span>环境地域</span>
          </el-menu-item>
          <el-menu-item index="target" @click="activeModule = 'target'">
            <el-icon><Aim /></el-icon>
            <span>目标约束</span>
          </el-menu-item>
          <el-menu-item index="green" @click="activeModule = 'green'">
            <el-icon><Operation /></el-icon>
            <span>绿电规划</span>
          </el-menu-item>
          <el-menu-item index="advanced" @click="activeModule = 'advanced'">
            <el-icon><Setting /></el-icon>
            <span>高级参数</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <main class="config-content">
        <!-- 基础信息 -->
        <el-card class="config-card" v-show="activeModule === 'basic'">
          <template #header>
            <span class="card-title">项目基础信息</span>
          </template>
          <el-form :model="formData" label-width="140px">
            <el-form-item label="数据中心总负荷(kW)" required>
              <el-input-number
                v-model="formData.planned_load_kw"
                :min="100"
                :max="100000"
                :step="10"
                placeholder="如：12000"
              />
              <span class="form-hint">总IT设备功率需求</span>
            </el-form-item>
            <el-form-item label="单机柜算力功率密度(kW/机柜)" required>
              <el-input-number
                v-model="formData.computing_power_density"
                :min="5"
                :max="80"
                :step="1"
                placeholder="如：8"
              />
              <span class="form-hint">推荐值：8-30 kW/机柜</span>
            </el-form-item>
            <el-form-item label="机柜总数">
              <el-input
                :value="cabinetCount"
                disabled
                class="disabled-input"
              />
              <span class="form-hint">由总负荷和功率密度自动计算</span>
            </el-form-item>
            <el-form-item label="数据中心计划建筑面积(m²)" required>
              <el-input-number
                v-model="formData.planned_area"
                :min="100"
                :max="100000"
                :step="10"
                placeholder="如：18000"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 环境与地域 -->
        <el-card class="config-card" v-show="activeModule === 'environment'">
          <template #header>
            <span class="card-title">环境与地域参数</span>
          </template>
          <el-form :model="formData" label-width="140px">
            <el-form-item label="项目所在地" required>
              <el-select
                v-model="formData.location"
                placeholder="请选择项目所在地"
              >
                <el-option label="乌兰察布" value="乌兰察布" />
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="广州" value="广州" />
                <el-option label="深圳" value="深圳" />
                <el-option label="杭州" value="杭州" />
                <el-option label="成都" value="成都" />
                <el-option label="贵阳" value="贵阳" />
              </el-select>
            </el-form-item>
            <el-form-item label="机房等级">
              <el-select v-model="formData.machine_room_grade">
                <el-option label="A+" value="A+" />
                <el-option label="A" value="A" />
                <el-option label="B" value="B" />
                <el-option label="C" value="C" />
              </el-select>
              <span class="form-hint">对应 GB 50174-2017 标准</span>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 目标与约束 -->
        <el-card class="config-card" v-show="activeModule === 'target'">
          <template #header>
            <span class="card-title">目标与约束</span>
          </template>
          <el-form :model="formData" label-width="140px">
            <el-form-item label="PUE目标" required>
              <el-input-number
                v-model="formData.pue_target"
                :min="1.05"
                :max="3.0"
                :step="0.01"
                placeholder="如：1.3"
              />
              <span class="form-hint">传统>1.8，高效<=1.3，超高效<=1.2</span>
            </el-form-item>
            <el-form-item label="绿电消纳率目标(%)" required>
              <el-input-number
                v-model="formData.green_power_ratio"
                :min="0"
                :max="100"
                :step="1"
                placeholder="如：70"
              />
              <span class="form-hint">优秀>=80%，良好>=60%，可接受>=40%</span>
            </el-form-item>
            <el-form-item label="预算约束(万元)" required>
              <el-input-number
                v-model="formData.budget_constraint"
                :min="100"
                :max="100000"
                :step="10"
                placeholder="如：2000"
              />
              <span class="form-hint">项目总投资预算上限</span>
            </el-form-item>
            <el-form-item label="制冷技术">
              <el-select v-model="formData.cooling_technology">
                <el-option label="浸没式液冷" value="浸没式液冷" />
                <el-option label="冷板式液冷" value="冷板式液冷" />
                <el-option label="蒸发冷却" value="蒸发冷却" />
                <el-option label="风冷" value="风冷" />
                <el-option label="混合制冷" value="混合制冷" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 绿电规划 -->
        <el-card class="config-card" v-show="activeModule === 'green'">
          <template #header>
            <span class="card-title">绿电规划参数</span>
          </template>
          <el-form :model="formData" label-width="160px">
            <el-form-item label="光伏倾角(度)">
              <el-input-number
                v-model="formData.pv_tilt"
                :min="0"
                :max="90"
                :step="1"
                placeholder="留空则取当地纬度"
              />
              <span class="form-hint">推荐值：等于当地纬度</span>
            </el-form-item>
            <el-form-item label="光伏方位角(度)">
              <el-input-number
                v-model="formData.pv_azimuth"
                :min="0"
                :max="360"
                :step="5"
              />
              <span class="form-hint">180度为正南</span>
            </el-form-item>
            <el-form-item label="风机切入风速(m/s)">
              <el-input-number
                v-model="formData.wind_cut_in_ms"
                :min="1"
                :max="10"
                :step="0.5"
              />
            </el-form-item>
            <el-form-item label="风机额定风速(m/s)">
              <el-input-number
                v-model="formData.wind_rated_ms"
                :min="5"
                :max="30"
                :step="0.5"
              />
            </el-form-item>
            <el-form-item label="风机切出风速(m/s)">
              <el-input-number
                v-model="formData.wind_cut_out_ms"
                :min="15"
                :max="40"
                :step="1"
              />
            </el-form-item>
            <el-form-item label="电网碳排放因子(kg CO2/kWh)">
              <el-input-number
                v-model="formData.carbon_emission_factor"
                :min="0"
                :max="2"
                :step="0.1"
              />
              <span class="form-hint">中国平均约0.5</span>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 高级参数 -->
        <el-card class="config-card" v-show="activeModule === 'advanced'">
          <template #header>
            <span class="card-title">高级参数</span>
          </template>
          <el-form :model="formData" label-width="140px">
            <el-form-item label="仿真时长(小时)">
              <el-input-number
                v-model="formData.sim_hours"
                :min="24"
                :max="8760"
                :step="24"
              />
              <span class="form-hint">8760小时为全年仿真</span>
            </el-form-item>
            <el-form-item label="气象数据年份">
              <el-input-number
                v-model="formData.year"
                :min="2010"
                :max="2025"
              />
            </el-form-item>
            <el-form-item label="仿真日期">
              <el-date-picker
                v-model="formData.date"
                type="date"
                placeholder="选择日期"
              />
              <span class="form-hint">仅仿真时长<=24小时时生效</span>
            </el-form-item>
            <el-form-item label="电价参数">
              <el-row :gutter="16">
                <el-col :span="5">
                  <el-form-item label="尖峰电价">
                    <el-input-number
                      v-model="formData.electricity_prices.尖峰电价"
                      :min="0"
                      :max="2"
                      :step="0.01"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="5">
                  <el-form-item label="高峰电价">
                    <el-input-number
                      v-model="formData.electricity_prices.高峰电价"
                      :min="0"
                      :max="2"
                      :step="0.01"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="5">
                  <el-form-item label="平段电价">
                    <el-input-number
                      v-model="formData.electricity_prices.平段电价"
                      :min="0"
                      :max="2"
                      :step="0.01"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="5">
                  <el-form-item label="低谷电价">
                    <el-input-number
                      v-model="formData.electricity_prices.低谷电价"
                      :min="0"
                      :max="2"
                      :step="0.01"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="深谷电价">
                    <el-input-number
                      v-model="formData.electricity_prices.深谷电价"
                      :min="0"
                      :max="2"
                      :step="0.01"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item label="差分进化参数">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="最大迭代次数">
                    <el-input-number
                      v-model="formData.maxiter"
                      :min="10"
                      :max="200"
                      :step="10"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="种群大小">
                    <el-input-number
                      v-model="formData.popsize"
                      :min="5"
                      :max="50"
                      :step="1"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="随机种子">
                    <el-input-number
                      v-model="formData.seed"
                      :min="1"
                      :max="1000"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form-item>
          </el-form>
        </el-card>
      </main>
    </div>

    <div class="config-footer">
      <el-button @click="saveParams">保存参数</el-button>
      <el-button @click="resetParams">重置为默认值</el-button>
      <el-button @click="loadSampleParams">加载示例参数</el-button>
      <el-button 
        class="primary-btn" 
        @click="nextStep" 
        :disabled="!canProceed"
      >下一步：生成方案</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Files, Lightning, Location, Aim, Operation, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { workflowApi } from '@/api'

const router = useRouter()

const activeModule = ref('basic')

const formData = reactive({
  location: '乌兰察布',
  planned_load_kw: 500,
  green_power_ratio: 70,
  planned_area: 500,
  budget_constraint: 2000,
  cooling_technology: '浸没式液冷',
  machine_room_grade: 'A',
  pue_target: 1.3,
  sim_hours: 160,
  year: 2025,
  date: null,
  pv_tilt: null,
  pv_azimuth: 180.0,
  wind_cut_in_ms: 3.0,
  wind_rated_ms: 12.0,
  wind_cut_out_ms: 25.0,
  computing_power_density: 8.0,
  carbon_emission_factor: 0.5,
  electricity_prices: {
    '尖峰电价': 0.5,
    '高峰电价': 0.4,
    '平段电价': 0.3,
    '低谷电价': 0.25,
    '深谷电价': 0.2
  },
  maxiter: 60,
  popsize: 10,
  seed: 42
})

const loadFromStorage = () => {
  const savedConfig = localStorage.getItem('projectConfig')
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig)
      Object.assign(formData, config)
      localStorage.removeItem('projectConfig')
      ElMessage.info('已加载保存的配置')
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }
}

loadFromStorage()

const cabinetCount = computed(() => {
  if (formData.planned_load_kw && formData.computing_power_density) {
    return Math.ceil(formData.planned_load_kw / formData.computing_power_density)
  }
  return 0
})

const canProceed = computed(() => {
  return formData.planned_load_kw > 0 &&
    formData.planned_area > 0 &&
    formData.location &&
    formData.pue_target >= 1.05 &&
    formData.green_power_ratio >= 0 &&
    formData.budget_constraint > 0
})

const transformToBackendFormat = () => {
  const data = {
    location: formData.location,
    planned_load_kw: formData.planned_load_kw,
    green_power_ratio: formData.green_power_ratio / 100,
    planned_area: formData.planned_area,
    budget_constraint: formData.budget_constraint,
    cooling_technology: formData.cooling_technology,
    machine_room_grade: formData.machine_room_grade,
    pue_target: formData.pue_target,
    sim_hours: formData.sim_hours,
    year: formData.year,
    pv_tilt: formData.pv_tilt,
    pv_azimuth: formData.pv_azimuth,
    wind_cut_in_ms: formData.wind_cut_in_ms,
    wind_rated_ms: formData.wind_rated_ms,
    wind_cut_out_ms: formData.wind_cut_out_ms,
    computing_power_density: formData.computing_power_density,
    carbon_emission_factor: formData.carbon_emission_factor,
    electricity_prices: { ...formData.electricity_prices },
    maxiter: formData.maxiter,
    popsize: formData.popsize,
    seed: formData.seed
  }
  if (formData.date) {
    const d = new Date(formData.date)
    data.date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }
  return data
}

const saveParams = () => {
  localStorage.setItem('projectConfig', JSON.stringify(formData))
  ElMessage.success('参数已保存')
}

const resetParams = () => {
  formData.location = '乌兰察布'
  formData.planned_load_kw = 500
  formData.computing_power_density = 8
  formData.planned_area = 500
  formData.cooling_technology = '浸没式液冷'
  formData.machine_room_grade = 'A'
  formData.pue_target = 1.3
  formData.green_power_ratio = 70
  formData.budget_constraint = 2000
  formData.pv_tilt = null
  formData.pv_azimuth = 180
  formData.wind_cut_in_ms = 3.0
  formData.wind_rated_ms = 12.0
  formData.wind_cut_out_ms = 25.0
  formData.carbon_emission_factor = 0.5
  formData.sim_hours = 160
  formData.year = 2025
  formData.date = null
  formData.electricity_prices = {
    '尖峰电价': 0.5,
    '高峰电价': 0.4,
    '平段电价': 0.3,
    '低谷电价': 0.25,
    '深谷电价': 0.2
  }
  formData.maxiter = 60
  formData.popsize = 10
  formData.seed = 42
  ElMessage.info('已重置为默认值')
}

const loadSampleParams = () => {
  formData.planned_load_kw = 12000
  formData.computing_power_density = 30
  formData.planned_area = 18000
  formData.location = '乌兰察布'
  formData.cooling_technology = '浸没式液冷'
  formData.machine_room_grade = 'A+'
  formData.pue_target = 1.18
  formData.green_power_ratio = 95
  formData.budget_constraint = 35000
  formData.sim_hours = 168
  ElMessage.success('已加载示例参数')
}

const nextStep = async () => {
  try {
    const backendData = transformToBackendFormat()
    const response = await workflowApi.startDirect(backendData)
    const workflowId = response.data.workflow_id
    localStorage.setItem('currentWorkflowId', workflowId)
    localStorage.setItem('projectConfig', JSON.stringify(formData))
    router.push('/generate')
  } catch (error) {
    ElMessage.error('启动方案生成失败，请检查参数后重试')
    console.error(error)
  }
}
</script>

<style scoped>
.config-page {
  height: calc(100% - 20px);
  display: flex;
  flex-direction: column;
}

.config-layout {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
}

.config-sidebar {
  width: 180px;
  background: white;
  border-radius: var(--radius-lg);
  padding: 10px;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  border: 1px solid #D1FAE5;
}

.config-menu {
  border: none;
}

.config-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  border-radius: 8px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.config-menu :deep(.el-menu-item:hover) {
  background: rgba(16, 185, 129, 0.06);
  color: var(--primary-color);
}

.config-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
  color: var(--primary-color);
  font-weight: 600;
}

.config-content {
  flex: 1;
  overflow-y: auto;
}

.config-card {
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.config-card:hover {
  box-shadow: var(--shadow-hover);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #6B7280;
}

.disabled-input {
  background: #F0FDF4;
  color: #9CA3AF;
}

.config-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #D1FAE5;
  margin-top: auto;
  background: white;
  padding: 16px 24px;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  box-shadow: 0 -2px 10px rgba(16, 185, 129, 0.05);
}

.primary-btn {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}

.primary-btn:hover {
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.primary-btn:disabled {
  background: #D1FAE5;
  color: #9CA3AF;
  box-shadow: none;
  cursor: not-allowed;
}
</style>