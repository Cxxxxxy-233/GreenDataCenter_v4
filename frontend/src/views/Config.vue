<template>
  <div class="config-page">
    <div class="config-layout">
      <aside class="config-sidebar">
        <div class="config-sidebar-head">
          <span class="sidebar-eyebrow">Parameter Setup</span>
          <h2>参数配置</h2>
          <p>保留现有配置内容，通过更清晰的模块引导和表单层次提升录入体验。</p>
        </div>

        <el-menu
          :default-active="activeModule"
          class="config-menu"
          mode="vertical"
        >
          <el-menu-item
            v-for="module in moduleList"
            :key="module.key"
            :index="module.key"
            @click="activeModule = module.key"
          >
            <div class="menu-item-shell">
              <span class="menu-item-icon">
                <el-icon><component :is="module.icon" /></el-icon>
              </span>
              <span class="menu-item-copy">
                <span class="menu-item-title-row">
                  <span class="menu-item-title">{{ module.title }}</span>
                  <span class="menu-item-order">{{ module.order }}</span>
                </span>
                <span class="menu-item-note">{{ module.note }}</span>
              </span>
            </div>
          </el-menu-item>
        </el-menu>
        <div class="config-sidebar-note">
          按模块补齐参数后即可进入方案生成，当前内容会按页面操作保存与复用。
        </div>
      </aside>

      <main class="config-content">
        <section class="config-active-hero">
          <div class="active-hero-copy">
            <span class="active-hero-eyebrow">当前配置模块</span>
            <div class="active-hero-title-row">
              <span class="active-hero-icon">
                <el-icon><component :is="activeModuleMeta.icon" /></el-icon>
              </span>
              <div>
                <h2>{{ activeModuleMeta.title }}</h2>
                <p>{{ activeModuleMeta.note }}</p>
              </div>
            </div>
          </div>
          <div class="active-hero-meta-grid">
            <div class="active-hero-metric">
              <span class="hero-meta-label">阶段进度</span>
              <span class="hero-meta-value">{{ activeModuleMeta.order }} / {{ moduleList.length }}</span>
            </div>
            <div
              v-for="item in pageHighlights"
              :key="item.label"
              class="active-hero-metric"
            >
              <span class="hero-meta-label">{{ item.label }}</span>
              <span class="hero-meta-value compact">{{ item.value }}</span>
            </div>
          </div>
        </section>

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
      <div class="config-footer-status">
        <span class="footer-status-label">当前状态</span>
        <span class="footer-status-value">{{ canProceed ? '核心参数已满足生成条件' : '仍有核心参数待完善' }}</span>
      </div>
      <div class="config-footer-actions">
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
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Files, Location, Aim, Operation, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { workflowApi } from '@/api'

const router = useRouter()

const activeModule = ref('basic')

const moduleList = [
  { key: 'basic', title: '项目基础', icon: Files, note: '负荷、功率密度与面积等基础参数', order: '01' },
  { key: 'environment', title: '环境地域', icon: Location, note: '项目所在地域与机房等级条件', order: '02' },
  { key: 'target', title: '目标约束', icon: Aim, note: 'PUE、绿电目标与预算边界', order: '03' },
  { key: 'green', title: '绿电规划', icon: Operation, note: '风光储与碳排相关规划参数', order: '04' },
  { key: 'advanced', title: '高级参数', icon: Setting, note: '仿真时长、价格与优化算法配置', order: '05' }
]

const activeModuleMeta = computed(() => {
  return moduleList.find(module => module.key === activeModule.value) || moduleList[0]
})

const pageHighlights = computed(() => [
  { label: '项目所在地', value: formData.location || '-' },
  { label: '机柜总数', value: `${cabinetCount.value} 个` },
  { label: '预算约束', value: `${formData.budget_constraint} 万元` }
])

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
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100% - 20px);
}

.config-layout {
  display: flex;
  flex: 1;
  gap: 22px;
  overflow: hidden;
  min-height: 0;
}

.config-sidebar {
  width: 252px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 100%);
  border-radius: 20px;
  padding: 16px;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.config-sidebar-head {
  padding: 10px 10px 14px;
  margin-bottom: 8px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 16%, var(--border-default));
}

.sidebar-eyebrow {
  display: inline-flex;
  margin-bottom: 8px;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.config-sidebar-head h2 {
  font-size: 20px;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text-primary);
}

.config-sidebar-head p {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
  max-width: 20ch;
}

.config-menu {
  border: none;
  background: transparent;
}

.config-menu :deep(.el-menu-item) {
  height: auto;
  line-height: normal;
  margin: 4px 0;
  padding: 0 !important;
  border-radius: 16px;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
  font-weight: 500;
}

.menu-item-shell {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  align-items: start;
  gap: 10px;
  width: 100%;
  min-height: 72px;
  padding: 12px;
  border-radius: 16px;
}

.menu-item-icon {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%);
  color: var(--primary-dark);
  border: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-default));
}

.menu-item-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.menu-item-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.menu-item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 0;
}

.menu-item-note {
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-placeholder);
  word-break: break-word;
}

.menu-item-order {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-placeholder);
  font-variant-numeric: tabular-nums;
  flex: 0 0 auto;
}

.config-menu :deep(.el-menu-item:hover) {
  background: color-mix(in oklab, var(--primary-color) 7%, var(--bg-card));
  color: var(--primary-dark);
}

.config-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 12%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 8%, var(--bg-panel)) 100%);
  color: var(--primary-ink);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 22%, var(--border-default));
}

.config-menu :deep(.el-menu-item.is-active) .menu-item-icon {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 16%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 10%, var(--bg-panel)) 100%);
  box-shadow: 0 10px 20px color-mix(in oklab, var(--primary-color) 12%, transparent);
}

.config-menu :deep(.el-menu-item.is-active) .menu-item-title {
  color: var(--primary-ink);
}

.config-menu :deep(.el-menu-item.is-active) .menu-item-note,
.config-menu :deep(.el-menu-item.is-active) .menu-item-order {
  color: color-mix(in oklab, var(--primary-ink) 72%, var(--text-secondary));
}

.config-content {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.config-sidebar-note {
  margin-top: 14px;
  padding: 14px 6px 2px;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.config-active-hero {
  display: grid;
  grid-template-columns: minmax(260px, 0.9fr) minmax(0, 1.35fr);
  align-items: center;
  gap: 18px;
  padding: 16px 20px;
  border-radius: 20px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 16%, var(--border-default));
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 32%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  box-shadow: var(--shadow-sm);
}

.active-hero-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.active-hero-eyebrow {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-dark);
  font-weight: 700;
}

.active-hero-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.active-hero-icon {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 14%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 10%, var(--bg-panel)) 100%);
  color: var(--primary-dark);
  border: 1px solid color-mix(in oklab, var(--primary-color) 20%, var(--border-default));
  box-shadow: 0 10px 22px color-mix(in oklab, var(--primary-color) 10%, transparent);
}

.active-hero-title-row h2 {
  font-size: 18px;
  line-height: 1.15;
  font-weight: 700;
  color: var(--text-primary);
  text-wrap: balance;
}

.active-hero-title-row p {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
  max-width: 42ch;
}

.active-hero-meta-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.active-hero-metric {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  min-height: 76px;
  padding: 12px 14px;
  border-radius: 16px;
  background: color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%);
  border: 1px solid var(--border-light);
  min-width: 0;
}

.active-hero-metric:first-child {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 10%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.hero-meta-label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.hero-meta-value {
  display: block;
  font-size: 16px;
  line-height: 1.1;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  min-width: 0;
}

.hero-meta-value.compact {
  font-size: 15px;
  line-height: 1.3;
  word-break: break-word;
}

.config-card {
  margin-bottom: 0;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.config-card :deep(.el-card__header) {
  padding: 18px 22px;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 9%, transparent), transparent 28%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%) 0%, color-mix(in oklab, var(--bg-card) 96%, var(--primary-color) 4%) 100%);
  border-bottom: 1px solid var(--border-light);
}

.config-card :deep(.el-card__body) {
  padding: 22px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
}

.config-card :deep(.el-form) {
  max-width: 1120px;
}

.config-card :deep(.el-form-item) {
  display: grid;
  grid-template-columns: minmax(168px, 220px) minmax(0, 1fr);
  align-items: flex-start;
  column-gap: 18px;
  row-gap: 8px;
  margin-bottom: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 0%, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-default));
  transition: border-color var(--transition-fast), transform var(--transition-fast), box-shadow var(--transition-fast);
}

.config-card :deep(.el-form-item:hover) {
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
  transform: translateY(-1px);
  box-shadow: 0 12px 24px color-mix(in oklab, var(--primary-color) 8%, transparent);
}

.config-card :deep(.el-form-item__label) {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.6;
  white-space: normal;
  text-align: left;
  width: auto !important;
  height: auto;
  padding: 0;
}

.config-card :deep(.el-form-item__label-wrap) {
  margin-left: 0 !important;
  width: auto !important;
}

.config-card :deep(.el-form-item__content) {
  display: flex;
  align-items: center;
  min-width: 0;
  flex-wrap: wrap;
  gap: 10px 12px;
  line-height: 1.6;
  margin-left: 0 !important;
}

.config-card :deep(.el-input-number) {
  width: 220px;
}

.config-card :deep(.el-select),
.config-card :deep(.el-date-editor.el-input),
.config-card :deep(.el-date-editor.el-input__wrapper) {
  width: 220px;
}

.config-card :deep(.el-input-number),
.config-card :deep(.el-input__wrapper),
.config-card :deep(.el-select__wrapper),
.config-card :deep(.el-date-editor.el-input__wrapper) {
  border-radius: 14px;
  box-shadow: none;
}

.config-card :deep(.el-input-number.is-controls-right .el-input__wrapper),
.config-card :deep(.el-input__wrapper),
.config-card :deep(.el-select__wrapper),
.config-card :deep(.el-date-editor.el-input__wrapper) {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
}

.config-card :deep(.el-input-number:hover),
.config-card :deep(.el-input__wrapper:hover),
.config-card :deep(.el-select__wrapper:hover),
.config-card :deep(.el-date-editor.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
}

.config-card :deep(.el-input-number.is-focus),
.config-card :deep(.el-input__wrapper.is-focus),
.config-card :deep(.el-select__wrapper.is-focused),
.config-card :deep(.el-date-editor.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px color-mix(in oklab, var(--primary-color) 24%, var(--border-default)),
    0 0 0 4px color-mix(in oklab, var(--primary-color) 12%, transparent);
}

.config-card :deep(.el-input-number__decrease),
.config-card :deep(.el-input-number__increase) {
  background: transparent;
  color: var(--text-secondary);
}

.config-card :deep(.el-row) {
  width: 100%;
}

.config-card :deep(.el-col .el-form-item) {
  grid-template-columns: 1fr;
  margin-bottom: 12px;
  padding: 14px 14px 12px;
}

.config-card :deep(.el-col .el-form-item__content) {
  align-items: stretch;
}

.form-hint {
  display: block;
  width: 100%;
  margin-left: 0;
  margin-top: 2px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.disabled-input {
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  color: var(--text-placeholder);
}

.config-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  margin-top: auto;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 28%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
}

.config-footer-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 42ch;
}

.footer-status-label {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--text-placeholder);
}

.footer-status-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.config-footer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
}

.primary-btn {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
  border-color: var(--primary-color) !important;
  color: rgba(249, 253, 250, 0.98);
}

.primary-btn:hover:not(:disabled) {
  background: linear-gradient(180deg, var(--primary-light) 0%, var(--primary-color) 100%) !important;
  border-color: var(--primary-light) !important;
}

.primary-btn:disabled {
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--border-default) 12%);
  color: var(--text-placeholder);
  box-shadow: none;
  cursor: not-allowed;
  border-color: var(--border-light);
}

.config-footer :deep(.primary-btn.is-disabled),
.config-footer :deep(.primary-btn.is-disabled:hover),
.config-footer :deep(.primary-btn:disabled),
.config-footer :deep(.primary-btn:disabled:hover) {
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--border-default) 12%) !important;
  border-color: var(--border-light) !important;
  color: var(--text-secondary) !important;
  opacity: 1 !important;
  box-shadow: none !important;
}

@media (max-width: 1024px) {
  .config-layout {
    flex-direction: column;
  }

  .config-active-hero {
    grid-template-columns: 1fr;
  }

  .active-hero-meta-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .config-sidebar {
    width: 100%;
  }

  .config-menu {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }

  .config-sidebar-head p {
    max-width: none;
  }

  .config-menu :deep(.el-menu-item) {
    margin: 0;
  }
}

@media (max-width: 768px) {
  .config-page {
    gap: 16px;
  }

  .config-active-hero,
  .config-card :deep(.el-card__header),
  .config-card :deep(.el-card__body),
  .config-footer {
    padding: 16px;
  }

  .active-hero-title-row,
  .config-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .menu-item-shell {
    min-height: auto;
  }

  .menu-item-title-row {
    align-items: flex-start;
  }

  .active-hero-meta-grid {
    grid-template-columns: 1fr;
  }

  .config-card :deep(.el-input-number),
  .config-card :deep(.el-select),
  .config-card :deep(.el-date-editor.el-input),
  .config-card :deep(.el-date-editor.el-input__wrapper) {
    width: 100%;
  }

  .config-card :deep(.el-form-item) {
    grid-template-columns: 1fr;
  }

  .config-menu {
    grid-template-columns: 1fr;
  }

  .config-footer-actions {
    width: 100%;
  }

  .config-footer {
    justify-content: stretch;
  }

  .config-footer :deep(.el-button) {
    width: 100%;
    margin-left: 0;
  }
}
</style>
