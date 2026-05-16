<template>
  <div class="config-page">
    <div class="config-shell">
      <aside class="workflow-rail">
        <div class="rail-head">
          <span class="rail-kicker">Planning Console</span>
          <h1>参数配置控制舱</h1>
        </div>

        <div class="rail-track" aria-label="参数配置流程">
          <button
            v-for="module in moduleList"
            :key="module.key"
            type="button"
            class="rail-step"
            :class="{
              'is-active': activeModule === module.key,
              'is-complete': moduleCompletion[module.key] >= 0.99
            }"
            @click="activeModule = module.key"
          >
            <span class="rail-step-index">{{ module.order }}</span>
            <span class="rail-step-copy">
              <span class="rail-step-title-row">
                <span class="rail-step-title">{{ module.title }}</span>
                <span class="rail-step-percent">{{ Math.round(moduleCompletion[module.key] * 100) }}%</span>
              </span>
              <span class="rail-step-note">{{ module.note }}</span>
            </span>
          </button>
        </div>

        <div class="rail-presets">
          <span class="rail-section-title">展示预设</span>
          <button type="button" class="preset-chip" @click="applyDemoPreset('ulanqab')">
            乌兰察布高绿电口径
          </button>
          <button type="button" class="preset-chip" @click="applyDemoPreset('guiyang')">
            贵阳均衡能效口径
          </button>
        </div>
      </aside>

      <main class="workbench-stage">
        <header class="stage-head">
          <div class="stage-head-main">
            <span class="stage-kicker">当前工作段</span>
            <div class="stage-title-row">
              <span class="stage-icon">
                <el-icon><component :is="activeModuleMeta.icon" /></el-icon>
              </span>
              <div>
                <h2>{{ activeModuleMeta.title }}</h2>
              </div>
            </div>
          </div>

          <div class="stage-progress-board">
            <div class="stage-progress-meta">
              <span>总体完成度</span>
              <strong>{{ Math.round(readinessScore * 100) }}%</strong>
            </div>
            <div class="stage-progress-bar">
              <span class="stage-progress-fill" :style="{ width: `${readinessScore * 100}%` }"></span>
            </div>
            <div class="stage-meta-strip">
              <span class="meta-pill">
                <i></i>
                所在地 {{ formData.location || '未设置' }}
              </span>
              <span class="meta-pill">
                <i></i>
                机柜 {{ cabinetCount }} 柜
              </span>
              <span class="meta-pill">
                <i></i>
                预算 {{ formatWan(formData.budget_constraint) }}
              </span>
            </div>
          </div>
        </header>

        <section class="stage-plane">
          <div class="plane-intro">
            <div>
              <span class="plane-label">模块目标</span>
              <h3>{{ activeModuleMeta.goal }}</h3>
            </div>
          </div>

          <div class="form-river">
            <section v-show="activeModule === 'basic'" class="module-surface">
              <div class="surface-block">
                <div class="block-head">
                  <span class="block-kicker">项目规模</span>
                  <h4>建立基础建设画像</h4>
                </div>
                <el-form :model="formData" label-position="top" class="module-form two-columns">
                  <el-form-item label="数据中心总负荷（kW）" required>
                    <el-input-number v-model="formData.planned_load_kw" :min="100" :max="100000" :step="100" />
                  </el-form-item>
                  <el-form-item label="单机柜算力功率密度（kW/柜）" required>
                    <el-input-number v-model="formData.computing_power_density" :min="5" :max="80" :step="1" />
                  </el-form-item>
                  <el-form-item label="机柜总数">
                    <el-input :value="`${cabinetCount} 柜`" disabled class="disabled-input" />
                  </el-form-item>
                  <el-form-item label="规划建筑面积（m²）" required>
                    <el-input-number v-model="formData.planned_area" :min="100" :max="100000" :step="100" />
                  </el-form-item>
                </el-form>
              </div>
            </section>

            <section v-show="activeModule === 'environment'" class="module-surface">
              <div class="surface-block">
                <div class="block-head">
                  <span class="block-kicker">区位条件</span>
                  <h4>确定环境与标准边界</h4>
                </div>
                <el-form :model="formData" label-position="top" class="module-form two-columns">
                  <el-form-item label="项目所在地" required>
                    <el-select v-model="formData.location" placeholder="请选择项目所在地">
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
                  </el-form-item>
                </el-form>
              </div>
            </section>

            <section v-show="activeModule === 'target'" class="module-surface">
              <div class="surface-block">
                <div class="block-head">
                  <span class="block-kicker">目标与边界</span>
                  <h4>锁定能效、绿电与预算目标</h4>
                </div>
                <el-form :model="formData" label-position="top" class="module-form two-columns">
                  <el-form-item label="PUE 目标" required>
                    <el-input-number v-model="formData.pue_target" :min="1.05" :max="3" :step="0.01" />
                  </el-form-item>
                  <el-form-item label="绿电总占比目标（%）" required>
                    <el-input-number v-model="formData.green_power_ratio" :min="0" :max="100" :step="1" />
                  </el-form-item>
                  <el-form-item label="绿电直连占比（%）">
                    <el-input-number v-model="formData.direct_connection_ratio" :min="0" :max="100" :step="1" />
                  </el-form-item>
                  <el-form-item label="预算约束（万元）" required>
                    <el-input-number v-model="formData.budget_constraint" :min="100" :max="100000" :step="100" />
                  </el-form-item>
                  <el-form-item label="制冷技术路线">
                    <el-select v-model="formData.cooling_technology">
                      <el-option label="浸没式液冷" value="浸没式液冷" />
                      <el-option label="冷板式液冷" value="冷板式液冷" />
                      <el-option label="蒸发冷却" value="蒸发冷却" />
                      <el-option label="风冷" value="风冷" />
                      <el-option label="混合制冷" value="混合制冷" />
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>
            </section>

            <section v-show="activeModule === 'green'" class="module-surface">
              <div class="surface-block">
                <div class="block-head">
                  <span class="block-kicker">绿电规划</span>
                  <h4>补全风光储与碳排放假设</h4>
                </div>
                <el-form :model="formData" label-position="top" class="module-form two-columns">
                  <el-form-item label="光伏倾角（度）">
                    <el-input-number v-model="formData.pv_tilt" :min="0" :max="90" :step="1" />
                  </el-form-item>
                  <el-form-item label="光伏方位角（度）">
                    <el-input-number v-model="formData.pv_azimuth" :min="0" :max="360" :step="5" />
                  </el-form-item>
                  <el-form-item label="风机切入风速（m/s）">
                    <el-input-number v-model="formData.wind_cut_in_ms" :min="1" :max="10" :step="0.5" />
                  </el-form-item>
                  <el-form-item label="风机额定风速（m/s）">
                    <el-input-number v-model="formData.wind_rated_ms" :min="5" :max="30" :step="0.5" />
                  </el-form-item>
                  <el-form-item label="风机切出风速（m/s）">
                    <el-input-number v-model="formData.wind_cut_out_ms" :min="15" :max="40" :step="1" />
                  </el-form-item>
                  <el-form-item label="电网碳排放因子（kgCO2/kWh）">
                    <el-input-number v-model="formData.carbon_emission_factor" :min="0" :max="2" :step="0.01" />
                  </el-form-item>
                </el-form>
              </div>
            </section>

            <section v-show="activeModule === 'advanced'" class="module-surface">
              <div class="surface-block">
                <div class="block-head">
                  <span class="block-kicker">仿真与求解</span>
                  <h4>控制推演精度与时效</h4>
                </div>
                <el-form :model="formData" label-position="top" class="module-form two-columns">
                  <el-form-item label="仿真时长（小时）">
                    <el-input-number v-model="formData.sim_hours" :min="24" :max="8760" :step="24" />
                  </el-form-item>
                  <el-form-item label="气象数据年份">
                    <el-input-number v-model="formData.year" :min="2010" :max="2025" />
                  </el-form-item>
                  <el-form-item label="仿真日期">
                    <el-date-picker v-model="formData.date" type="date" placeholder="选择日期" />
                  </el-form-item>
                  <div class="block-subgrid full-span">
                    <div class="subgrid-title">电价参数（元/kWh）</div>
                    <div class="price-grid">
                      <el-form-item label="尖峰">
                        <el-input-number v-model="formData.electricity_prices.尖峰电价" :min="0" :max="2" :step="0.01" />
                      </el-form-item>
                      <el-form-item label="高峰">
                        <el-input-number v-model="formData.electricity_prices.高峰电价" :min="0" :max="2" :step="0.01" />
                      </el-form-item>
                      <el-form-item label="平段">
                        <el-input-number v-model="formData.electricity_prices.平段电价" :min="0" :max="2" :step="0.01" />
                      </el-form-item>
                      <el-form-item label="低谷">
                        <el-input-number v-model="formData.electricity_prices.低谷电价" :min="0" :max="2" :step="0.01" />
                      </el-form-item>
                      <el-form-item label="深谷">
                        <el-input-number v-model="formData.electricity_prices.深谷电价" :min="0" :max="2" :step="0.01" />
                      </el-form-item>
                    </div>
                  </div>
                  <div class="block-subgrid full-span">
                    <div class="subgrid-title">优化算法参数</div>
                    <div class="price-grid algorithm-grid">
                      <el-form-item label="最大迭代次数">
                        <el-input-number v-model="formData.maxiter" :min="10" :max="200" :step="10" />
                      </el-form-item>
                      <el-form-item label="种群大小">
                        <el-input-number v-model="formData.popsize" :min="5" :max="50" :step="1" />
                      </el-form-item>
                      <el-form-item label="随机种子">
                        <el-input-number v-model="formData.seed" :min="1" :max="1000" />
                      </el-form-item>
                    </div>
                  </div>
                </el-form>
              </div>
            </section>
          </div>
        </section>

        <footer class="stage-actions">
          <div class="stage-actions-copy">
            <span class="actions-label">当前状态</span>
            <strong>{{ canProceed ? '核心参数已满足生成条件' : '仍有关键参数待完善' }}</strong>
          </div>
          <div class="stage-actions-buttons">
            <el-button @click="saveParams">保存参数</el-button>
            <el-button @click="resetParams">恢复默认</el-button>
            <el-button @click="applyDemoPreset('ulanqab')">加载乌兰察布示例</el-button>
            <el-button class="primary-btn" @click="nextStep" :disabled="!canProceed">
              下一步：生成方案
            </el-button>
          </div>
        </footer>
      </main>

      <aside class="impact-panel">
        <section class="impact-surface readiness-surface">
          <div class="impact-head">
            <span class="impact-kicker">状态回声</span>
            <h3>推演前检查</h3>
          </div>
          <div class="readiness-ring">
            <div class="readiness-ring-core">
              <strong>{{ Math.round(readinessScore * 100) }}%</strong>
              <span>已就绪</span>
            </div>
          </div>
          <div class="check-list">
            <div
              v-for="item in readinessItems"
              :key="item.label"
              class="check-item"
              :class="{ 'is-ok': item.ready }"
            >
              <span class="check-dot"></span>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </section>

        <section class="impact-surface metric-surface">
          <div class="impact-head">
            <span class="impact-kicker">参数影响</span>
            <h3>派生指标预览</h3>
          </div>
          <div class="impact-metric-grid">
            <div v-for="metric in derivedMetrics" :key="metric.label" class="impact-metric">
              <span class="impact-metric-label">{{ metric.label }}</span>
              <strong>{{ metric.value }}</strong>
            </div>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Aim, Files, Location, Operation, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { workflowApi } from '@/api'

const router = useRouter()

const activeModule = ref('basic')

const moduleList = [
  {
    key: 'basic',
    order: '01',
    title: '项目基础',
    note: '负荷、密度与建筑规模',
    icon: Files,
    fields: ['planned_load_kw', 'computing_power_density', 'planned_area'],
    goal: '让项目规模可量化',
    guidance: '先建立负荷、面积、机柜规模三条主线，后续所有方案都以此为基准展开。'
  },
  {
    key: 'environment',
    order: '02',
    title: '环境地域',
    note: '所在地区与机房等级',
    icon: Location,
    fields: ['location', 'machine_room_grade'],
    goal: '锁定资源与标准边界',
    guidance: '地区会改变风光出力、碳排放因子和电价口径，也会影响制冷技术优先级。'
  },
  {
    key: 'target',
    order: '03',
    title: '目标约束',
    note: 'PUE、绿电比例与预算',
    icon: Aim,
    fields: ['pue_target', 'green_power_ratio', 'budget_constraint'],
    goal: '明确最终考核口径',
    guidance: '总绿电目标决定项目叙事，直连占比决定工程实现路径，预算决定推荐解的可落地性。'
  },
  {
    key: 'green',
    order: '04',
    title: '绿电规划',
    note: '风光储与碳排边界',
    icon: Operation,
    fields: ['pv_tilt', 'pv_azimuth', 'wind_cut_in_ms', 'wind_rated_ms', 'wind_cut_out_ms', 'carbon_emission_factor'],
    goal: '让绿电工具读到可信边界',
    guidance: '这里的参数不是要手工算出方案，而是给算法提供贴近现实的资源与排放假设。'
  },
  {
    key: 'advanced',
    order: '05',
    title: '高级参数',
    note: '仿真时长、电价与优化',
    icon: Setting,
    fields: ['sim_hours', 'year', 'maxiter', 'popsize', 'seed'],
    goal: '平衡求解速度与结果稳定性',
    guidance: '展示场景优先兼顾速度和观感，最终论证则可拉长仿真并提高优化精度。'
  }
]

const activeModuleMeta = computed(() => {
  return moduleList.find((item) => item.key === activeModule.value) || moduleList[0]
})

const formData = reactive({
  location: '乌兰察布',
  planned_load_kw: 30000,
  green_power_ratio: 60,
  direct_connection_ratio: null,
  planned_area: 15000,
  budget_constraint: 32000,
  cooling_technology: '浸没式液冷',
  machine_room_grade: 'A',
  pue_target: 1.22,
  sim_hours: 168,
  year: 2025,
  date: null,
  pv_tilt: 41,
  pv_azimuth: 180,
  wind_cut_in_ms: 3,
  wind_rated_ms: 12,
  wind_cut_out_ms: 25,
  computing_power_density: 20,
  carbon_emission_factor: 0.57,
  electricity_prices: {
    尖峰电价: 0.48,
    高峰电价: 0.42,
    平段电价: 0.35,
    低谷电价: 0.27,
    深谷电价: 0.22
  },
  maxiter: 60,
  popsize: 10,
  seed: 42
})

const presets = {
  ulanqab: {
    location: '乌兰察布',
    planned_load_kw: 30000,
    direct_connection_ratio: null,
    computing_power_density: 20,
    planned_area: 15000,
    cooling_technology: '浸没式液冷',
    machine_room_grade: 'A',
    pue_target: 1.22,
    green_power_ratio: 30,
    budget_constraint: 32000,
    pv_tilt: 41,
    pv_azimuth: 180,
    wind_cut_in_ms: 3,
    wind_rated_ms: 12,
    wind_cut_out_ms: 25,
    carbon_emission_factor: 0.57,
    sim_hours: 168,
    year: 2025,
    date: null,
    electricity_prices: {
      尖峰电价: 0.48,
      高峰电价: 0.42,
      平段电价: 0.35,
      低谷电价: 0.27,
      深谷电价: 0.22
    },
    maxiter: 60,
    popsize: 10,
    seed: 42
  },
  guiyang: {
    location: '贵阳',
    planned_load_kw: 12000,
    direct_connection_ratio: null,
    computing_power_density: 10,
    planned_area: 18000,
    cooling_technology: '冷板式液冷',
    machine_room_grade: 'A',
    pue_target: 1.25,
    green_power_ratio: 30,
    budget_constraint: 15000,
    pv_tilt: 26,
    pv_azimuth: 180,
    wind_cut_in_ms: 3,
    wind_rated_ms: 12,
    wind_cut_out_ms: 25,
    carbon_emission_factor: 0.5,
    sim_hours: 168,
    year: 2025,
    date: null,
    electricity_prices: {
      尖峰电价: 0.62,
      高峰电价: 0.56,
      平段电价: 0.49,
      低谷电价: 0.39,
      深谷电价: 0.31
    },
    maxiter: 60,
    popsize: 10,
    seed: 42
  }
}

const loadFromStorage = () => {
  const savedConfig = localStorage.getItem('projectConfig')
  if (!savedConfig) return
  try {
    const parsed = JSON.parse(savedConfig)
    Object.assign(formData, parsed)
    localStorage.removeItem('projectConfig')
    ElMessage.info('已加载上次保存的配置')
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

loadFromStorage()

const cabinetCount = computed(() => {
  if (!formData.planned_load_kw || !formData.computing_power_density) return 0
  return Math.ceil(formData.planned_load_kw / formData.computing_power_density)
})

const annualDemandMWh = computed(() => {
  return Math.round((formData.planned_load_kw * formData.pue_target * 8760) / 1000)
})

const recommendedDirectRatio = computed(() => {
  const greenRatio = Number(formData.green_power_ratio) || 0
  const byLocation = {
    乌兰察布: 32,
    贵阳: 14,
    北京: 12,
    上海: 10,
    广州: 11,
    深圳: 11,
    杭州: 12,
    成都: 13
  }
  const base = byLocation[formData.location] ?? 12
  if (greenRatio >= 90) return Math.min(base + 2, greenRatio)
  if (greenRatio <= 35) return Math.min(base, Math.max(10, greenRatio))
  return Math.min(base, greenRatio)
})

const resolvedDirectRatio = computed(() => {
  if (formData.direct_connection_ratio == null || formData.direct_connection_ratio === '') {
    return recommendedDirectRatio.value
  }
  return Math.min(Number(formData.direct_connection_ratio) || 0, Number(formData.green_power_ratio) || 0)
})

const greenPurchaseRatio = computed(() => {
  return Math.max((Number(formData.green_power_ratio) || 0) - resolvedDirectRatio.value, 0)
})

const directConnectionEnergyMWh = computed(() => {
  return Math.round((annualDemandMWh.value * resolvedDirectRatio.value) / 100)
})

const greenPurchaseEnergyMWh = computed(() => {
  return Math.round((annualDemandMWh.value * greenPurchaseRatio.value) / 100)
})

const estimatedAnnualCarbonTon = computed(() => {
  const residualGridRatio = Math.max(100 - (Number(formData.green_power_ratio) || 0), 0) / 100
  const ton = annualDemandMWh.value * 1000 * residualGridRatio * Number(formData.carbon_emission_factor || 0) / 1000
  return Math.round(ton)
})

const canProceed = computed(() => {
  return formData.planned_load_kw > 0 &&
    formData.planned_area > 0 &&
    Boolean(formData.location) &&
    formData.pue_target >= 1.05 &&
    formData.green_power_ratio >= 0 &&
    formData.green_power_ratio <= 100 &&
    (formData.direct_connection_ratio == null || formData.direct_connection_ratio <= formData.green_power_ratio) &&
    formData.budget_constraint > 0
})

const fieldValueMap = computed(() => ({
  planned_load_kw: formData.planned_load_kw,
  computing_power_density: formData.computing_power_density,
  planned_area: formData.planned_area,
  location: formData.location,
  machine_room_grade: formData.machine_room_grade,
  pue_target: formData.pue_target,
  green_power_ratio: formData.green_power_ratio,
  budget_constraint: formData.budget_constraint,
  pv_tilt: formData.pv_tilt,
  pv_azimuth: formData.pv_azimuth,
  wind_cut_in_ms: formData.wind_cut_in_ms,
  wind_rated_ms: formData.wind_rated_ms,
  wind_cut_out_ms: formData.wind_cut_out_ms,
  carbon_emission_factor: formData.carbon_emission_factor,
  sim_hours: formData.sim_hours,
  year: formData.year,
  maxiter: formData.maxiter,
  popsize: formData.popsize,
  seed: formData.seed
}))

const moduleCompletion = computed(() => {
  return moduleList.reduce((acc, module) => {
    const filled = module.fields.filter((field) => {
      const value = fieldValueMap.value[field]
      return value !== null && value !== '' && value !== undefined
    }).length
    acc[module.key] = module.fields.length ? filled / module.fields.length : 1
    return acc
  }, {})
})

const readinessItems = computed(() => [
  { label: '基础负荷已建立', ready: formData.planned_load_kw > 0 && formData.planned_area > 0 },
  { label: '区位条件已选择', ready: Boolean(formData.location) },
  { label: '目标边界已确定', ready: formData.green_power_ratio >= 0 && formData.budget_constraint > 0 && formData.pue_target >= 1.05 },
  { label: '绿电参数可用于推演', ready: formData.carbon_emission_factor > 0 && formData.wind_rated_ms > formData.wind_cut_in_ms },
  { label: '求解参数已完整', ready: formData.sim_hours > 0 && formData.maxiter > 0 && formData.popsize > 0 }
])

const readinessScore = computed(() => {
  const readyCount = readinessItems.value.filter((item) => item.ready).length
  return readyCount / readinessItems.value.length
})

const derivedMetrics = computed(() => [
  {
    label: '预计全年用电量',
    value: `${formatNumber(annualDemandMWh.value)} MWh`,
    note: '以总负荷和 PUE 粗估，作为绿电规模与碳排基准。'
  },
  {
    label: '建议直连绿电',
    value: `${formatNumber(directConnectionEnergyMWh.value)} MWh`,
    note: `${resolvedDirectRatio.value}% 口径${formData.direct_connection_ratio == null ? '（系统建议）' : '（手动设定）'}。`
  },
  {
    label: '购绿电或绿证补足',
    value: `${formatNumber(greenPurchaseEnergyMWh.value)} MWh`,
    note: `用于补足 ${greenPurchaseRatio.value}% 的剩余绿电目标。`
  },
  {
    label: '年碳排放估算',
    value: `${formatNumber(estimatedAnnualCarbonTon.value)} 吨`,
    note: '按未被绿电覆盖的剩余电量乘电网碳因子估算。'
  }
])

const insightMap = {
  basic: [
    {
      title: '规模建议',
      body: '如果是答辩演示，30MW 级负荷既能体现项目难度，也更容易得到有说服力的风光储容量结果。'
    },
    {
      title: '面积口径',
      body: '面积过小会显得建设强度失真，30MW 级项目通常需要更充足的园区与机房空间。'
    }
  ],
  environment: [
    {
      title: '地区选择',
      body: '乌兰察布适合展示高绿电占比和直连潜力，贵阳更适合强调制冷和综合能效。'
    },
    {
      title: '等级解释',
      body: 'A级及以上更符合数据中心主流建设口径，也方便供配电工具输出更合理的冗余架构。'
    }
  ],
  target: [
    {
      title: '绿电口径',
      body: '建议把总绿电占比作为最终考核指标，把绿电直连占比作为工程实现路径，二者不要混为一谈。'
    },
    {
      title: '预算展示',
      body: '预算过低会压缩方案可信度，过高又会显得不经济，建议与项目规模同步调整。'
    }
  ],
  green: [
    {
      title: '碳因子设置',
      body: '碳因子直接影响年碳排展示值，建议采用与地区电网结构一致的保守口径。'
    },
    {
      title: '直连与购电组合',
      body: '当前系统会把直连与购绿电分开显示，这样更贴近真实项目的能源实现路径。'
    }
  ],
  advanced: [
    {
      title: '演示速度',
      body: '168 小时仿真通常能兼顾响应速度和图表稳定性，适合现场录屏与评委演示。'
    },
    {
      title: '优化稳定性',
      body: '种群太小容易波动，迭代太少会让结果不稳，当前默认组合更适合展示。'
    }
  ]
}

const activeInsights = computed(() => insightMap[activeModule.value] || [])

const actionHint = computed(() => {
  if (!canProceed.value) {
    return '请优先补齐负荷、地区、PUE、绿电目标和预算约束。'
  }
  return `当前口径下，系统将按总绿电 ${formData.green_power_ratio}% 目标推演，其中直连按 ${resolvedDirectRatio.value}% 处理。`
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

  if (formData.direct_connection_ratio != null && formData.direct_connection_ratio !== '') {
    data.direct_connection_ratio = formData.direct_connection_ratio / 100
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
  Object.assign(formData, JSON.parse(JSON.stringify(presets.ulanqab)))
  ElMessage.info('已恢复默认展示参数')
}

const applyDemoPreset = (presetKey) => {
  const preset = presets[presetKey]
  if (!preset) return
  Object.assign(formData, JSON.parse(JSON.stringify(preset)))
  ElMessage.success(presetKey === 'ulanqab' ? '已加载乌兰察布展示参数' : '已加载贵阳展示参数')
}

const nextStep = async () => {
  try {
    const response = await workflowApi.startDirect(transformToBackendFormat())
    const workflowId = response.data.workflow_id
    localStorage.setItem('currentWorkflowId', workflowId)
    localStorage.setItem('projectConfig', JSON.stringify(formData))
    router.push('/generate')
  } catch (error) {
    ElMessage.error('启动方案生成失败，请检查参数后重试')
    console.error(error)
  }
}

function formatNumber(value) {
  return new Intl.NumberFormat('zh-CN').format(Number(value) || 0)
}

function formatWan(value) {
  return `${formatNumber(value)} 万元`
}
</script>

<style scoped>
.config-page {
  min-height: calc(100vh - 132px);
  padding: 6px 0 14px;
  color: var(--text-primary);
}

.config-shell {
  position: relative;
  display: flex;
  align-items: stretch;
  width: 100%;
  gap: 0;
  min-height: calc(100vh - 156px);
  border: 1px solid color-mix(in oklab, var(--primary-color) 22%, var(--border-default));
  border-radius: 26px;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, color-mix(in oklab, var(--primary-color) 12%, transparent), transparent 24%),
    radial-gradient(circle at 88% 12%, color-mix(in oklab, var(--accent-color) 10%, transparent), transparent 20%),
    linear-gradient(135deg, color-mix(in oklab, var(--bg-stage) 95%, oklch(0.08 0.018 160) 5%) 0%, color-mix(in oklab, var(--bg-card) 82%, var(--primary-dark) 18%) 46%, color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%) 100%);
  box-shadow: 0 22px 54px rgba(4, 26, 18, 0.3);
}

.config-shell::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent 0, color-mix(in oklab, var(--primary-color) 8%, transparent) 18%, transparent 34%, transparent 100%),
    linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 7%, transparent), transparent 12%),
    repeating-linear-gradient(90deg, transparent 0 119px, color-mix(in oklab, var(--primary-color) 3%, transparent) 119px 120px);
  opacity: 0.78;
  pointer-events: none;
}

.workflow-rail,
.impact-panel {
  position: relative;
  z-index: 1;
  padding: 28px 22px 24px;
}

.workflow-rail {
  width: 248px;
  min-width: 248px;
  flex: 0 0 248px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  border-right: 1px solid color-mix(in oklab, var(--primary-color) 10%, transparent);
  background:
    radial-gradient(circle at top left, color-mix(in oklab, var(--primary-color) 12%, transparent), transparent 28%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage) 76%, var(--primary-dark) 24%) 0%, color-mix(in oklab, var(--bg-card) 92%, var(--primary-dark) 8%) 100%);
}

.rail-head {
  padding: 2px 2px 12px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 12%, transparent);
}

.rail-head h1 {
  margin: 8px 0 10px;
  font-size: 1.95rem;
  line-height: 0.98;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.rail-head p,
.rail-tip p {
  margin: 0;
  color: color-mix(in oklab, var(--text-secondary) 72%, white);
  font-size: 13px;
  line-height: 1.75;
}

.rail-kicker,
.rail-section-title,
.stage-kicker,
.plane-label,
.block-kicker,
.impact-kicker,
.actions-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: color-mix(in oklab, var(--primary-light) 72%, var(--text-secondary));
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  font-weight: 700;
}

.rail-track {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rail-step {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  padding: 12px 12px 12px 10px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 11%, transparent);
  border-radius: 16px;
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 72%, transparent) 0%, color-mix(in oklab, var(--bg-panel) 68%, transparent) 100%);
  color: inherit;
  cursor: pointer;
  appearance: none;
  transition: transform var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast);
}

.rail-step:hover {
  transform: translateY(-2px);
  border-color: color-mix(in oklab, var(--primary-color) 22%, transparent);
  box-shadow: 0 14px 24px color-mix(in oklab, var(--primary-color) 10%, transparent);
}

.rail-step.is-active {
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%) 100%);
  border-color: color-mix(in oklab, var(--primary-color) 30%, transparent);
  box-shadow:
    inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 24%, transparent),
    0 10px 22px color-mix(in oklab, var(--primary-color) 12%, transparent);
}

.rail-step.is-complete .rail-step-index {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: oklch(0.2 0.02 160);
}

.rail-step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  background: color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%);
  color: var(--text-primary);
  font: 700 13px/1 var(--font-family-mono, "JetBrains Mono", monospace);
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 16%, transparent);
}

.rail-step-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.rail-step-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.rail-step-title {
  font-size: 16px;
  font-weight: 650;
  color: var(--text-primary);
}

.rail-step-percent,
.rail-step-note {
  color: color-mix(in oklab, var(--text-secondary) 70%, white);
  font-size: 13px;
}

.rail-step-note {
  line-height: 1.6;
}

.rail-presets {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preset-chip {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 16%, transparent);
  border-radius: 14px;
  background: color-mix(in oklab, var(--bg-panel) 66%, transparent);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.45;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast), border-color var(--transition-fast);
}

.preset-chip:hover {
  transform: translateY(-1px);
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-panel));
  border-color: color-mix(in oklab, var(--primary-color) 24%, transparent);
}

.rail-tip {
  margin-top: auto;
  padding-top: 8px;
}

.workbench-stage {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-width: 0;
  background:
    radial-gradient(circle at 18% 0%, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 24%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 91%, var(--primary-color) 9%) 100%);
}

.stage-head {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 22px;
  padding: 24px 26px 18px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 14%, transparent);
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 86%, var(--primary-color) 14%) 0%, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 100%);
}

.stage-head-main {
  flex: 1 1 540px;
  min-width: 320px;
}

.stage-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 8px;
}

.stage-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 16%, var(--bg-card)) 0%, color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%) 100%);
  color: var(--primary-light);
  box-shadow:
    inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 22%, transparent),
    0 18px 28px color-mix(in oklab, var(--primary-color) 14%, transparent);
}

.stage-title-row h2 {
  margin: 0;
  font-size: 1.95rem;
  line-height: 1.02;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.stage-title-row p,
.plane-intro p,
.block-head p,
.impact-metric p,
.insight-item p,
.stage-actions-copy p {
  margin: 8px 0 0;
  color: color-mix(in oklab, var(--text-secondary) 74%, white);
  font-size: 13px;
  line-height: 1.75;
}

.stage-progress-board {
  display: flex;
  flex-direction: column;
  flex: 0 0 320px;
  width: 320px;
  gap: 12px;
  padding: 16px 16px 14px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--accent-color) 15%, transparent), transparent 30%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 84%, var(--primary-color) 16%) 0%, color-mix(in oklab, var(--bg-stage) 94%, var(--primary-dark) 6%) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 20%, transparent);
  box-shadow: inset 0 1px 0 color-mix(in oklab, var(--primary-light) 16%, transparent);
}

.stage-progress-meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  color: color-mix(in oklab, var(--text-secondary) 72%, white);
  font-size: 14px;
}

.stage-progress-meta strong {
  color: var(--text-primary);
  font-size: 32px;
  line-height: 1;
}

.stage-progress-bar {
  height: 8px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--bg-card) 80%, transparent);
  overflow: hidden;
}

.stage-progress-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--primary-dark) 0%, var(--primary-color) 55%, var(--accent-color) 100%);
  box-shadow: 0 0 20px color-mix(in oklab, var(--primary-color) 28%, transparent);
}

.stage-meta-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 11px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--bg-panel) 64%, transparent);
  color: color-mix(in oklab, var(--text-primary) 94%, white);
  font-size: 13px;
}

.meta-pill i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(180deg, var(--primary-light) 0%, var(--primary-color) 100%);
  box-shadow: 0 0 12px color-mix(in oklab, var(--primary-color) 36%, transparent);
}

.stage-plane {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-height: 0;
  flex: 1;
  padding: 0 26px 14px;
}

.plane-intro {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  width: 100%;
  gap: 18px;
  padding: 18px 0 16px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 10%, transparent);
}

.plane-intro > div {
  flex: 0 1 240px;
}

.plane-intro > p {
  flex: 1 1 420px;
}

.plane-intro h3 {
  margin: 10px 0 0;
  color: var(--text-primary);
  font-size: 24px;
  line-height: 1.12;
}

.form-river {
  width: 100%;
  max-width: 940px;
  flex: 0 0 auto;
  min-height: auto;
  padding-top: 18px;
}

.module-surface {
  height: auto;
}

.surface-block {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: auto;
  padding: 18px 18px 16px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 14%, var(--border-default));
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 28%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 100%);
  box-shadow:
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 10%, transparent),
    0 12px 28px rgba(5, 20, 14, 0.14);
}

.surface-block::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background:
    linear-gradient(90deg, color-mix(in oklab, var(--primary-color) 10%, transparent), transparent 16%);
  opacity: 0.55;
  pointer-events: none;
}

.block-head {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.block-head h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 22px;
  line-height: 1.12;
}

.module-form {
  position: relative;
  z-index: 1;
}

.module-form::before {
  content: '';
  position: absolute;
  inset: -8px;
  border-radius: 22px;
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 4%, transparent), transparent 40%);
  pointer-events: none;
  opacity: 0.7;
}

.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.full-span {
  grid-column: 1 / -1;
}

.block-subgrid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 30%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 0%, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-default));
  box-shadow: inset 0 1px 0 color-mix(in oklab, var(--primary-light) 8%, transparent);
}

.subgrid-title {
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 650;
  letter-spacing: 0.02em;
}

.price-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.algorithm-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.field-hint {
  display: block;
  margin-top: 8px;
  color: color-mix(in oklab, var(--text-secondary) 68%, white);
  font-size: 13px;
  line-height: 1.65;
}

.stage-actions {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  width: 100%;
  padding: 16px 26px 18px;
  border-top: 1px solid color-mix(in oklab, var(--primary-color) 12%, transparent);
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-panel) 97%, transparent) 0%, color-mix(in oklab, var(--bg-card) 94%, var(--primary-color) 6%) 100%);
}

.stage-actions-copy strong {
  display: block;
  margin-top: 8px;
  color: var(--text-primary);
  font-size: 18px;
}

.stage-actions-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.impact-panel {
  width: 280px;
  min-width: 280px;
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-left: 1px solid color-mix(in oklab, var(--primary-color) 12%, transparent);
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--accent-color) 10%, transparent), transparent 24%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage) 76%, var(--primary-dark) 24%) 0%, color-mix(in oklab, var(--bg-card) 90%, var(--primary-dark) 10%) 100%);
}

.impact-surface {
  padding: 14px;
  border-radius: 18px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 14%, transparent);
  background:
    radial-gradient(circle at top right, color-mix(in oklab, var(--accent-color) 12%, transparent), transparent 28%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 80%, transparent) 0%, color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%) 100%);
  box-shadow: inset 0 1px 0 color-mix(in oklab, var(--primary-light) 10%, transparent);
}

.impact-head h3 {
  margin: 8px 0 0;
  color: var(--text-primary);
  font-size: 20px;
  line-height: 1.12;
}

.readiness-ring {
  display: flex;
  justify-content: center;
  margin: 14px 0;
}

.readiness-ring-core {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 30% 30%, color-mix(in oklab, var(--primary-light) 24%, transparent), transparent 34%),
    linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 14%, var(--bg-stage-soft)) 0%, color-mix(in oklab, var(--bg-stage) 92%, var(--primary-dark) 8%) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 24%, transparent);
  box-shadow:
    inset 0 0 0 8px color-mix(in oklab, var(--primary-color) 12%, transparent),
    0 0 28px color-mix(in oklab, var(--primary-color) 14%, transparent);
}

.readiness-ring-core strong {
  color: var(--text-primary);
  font-size: 24px;
  line-height: 1;
}

.readiness-ring-core span {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 13px;
}

.check-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: color-mix(in oklab, var(--text-secondary) 72%, white);
  font-size: 14px;
}

.check-item.is-ok {
  color: var(--text-primary);
}

.check-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: color-mix(in oklab, var(--text-muted) 60%, transparent);
}

.check-item.is-ok .check-dot {
  background: linear-gradient(180deg, var(--primary-light) 0%, var(--primary-color) 100%);
  box-shadow: 0 0 14px color-mix(in oklab, var(--primary-color) 30%, transparent);
}

.impact-metric-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-top: 14px;
}

.impact-metric {
  padding: 12px 12px 10px;
  border-radius: 16px;
  background: color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-default));
}

.impact-metric-label {
  display: block;
  color: color-mix(in oklab, var(--text-secondary) 72%, white);
  font-size: 13px;
}

.impact-metric strong {
  display: block;
  margin-top: 6px;
  color: var(--text-primary);
  font-size: 22px;
  line-height: 1.15;
}

.insight-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.insight-item {
  padding: 12px;
  border-radius: 16px;
  background: color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%);
  border: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-default));
}

.insight-item strong {
  color: var(--text-primary);
  font-size: 15px;
}

.disabled-input :deep(.el-input__wrapper) {
  background: color-mix(in oklab, var(--bg-panel) 90%, var(--border-default) 10%);
}

:deep(.el-form-item) {
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
  padding: 12px 12px 10px;
  border-radius: 16px;
  border: 1px solid color-mix(in oklab, var(--primary-color) 11%, var(--border-default));
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 95%, var(--primary-color) 5%) 100%);
  box-shadow:
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 6%, transparent),
    0 8px 18px rgba(6, 18, 13, 0.08);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast), background var(--transition-fast);
}

:deep(.el-form-item)::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, color-mix(in oklab, var(--primary-color) 7%, transparent), transparent 42%);
  opacity: 0.7;
  pointer-events: none;
}

:deep(.el-form-item:hover) {
  border-color: color-mix(in oklab, var(--primary-color) 18%, var(--border-default));
  box-shadow:
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 8%, transparent),
    0 12px 22px rgba(6, 18, 13, 0.12);
  transform: translateY(-1px);
}

:deep(.el-form-item__label) {
  position: relative;
  z-index: 1;
  padding: 0 0 8px;
  color: color-mix(in oklab, var(--text-primary) 96%, white);
  font-size: 14px;
  font-weight: 650;
  line-height: 1.45;
}

:deep(.el-form-item__content) {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
}

:deep(.el-input-number),
:deep(.el-select),
:deep(.el-date-editor.el-input),
:deep(.el-date-editor.el-input__wrapper) {
  width: 100%;
}

:deep(.el-input),
:deep(.el-input-number),
:deep(.el-select),
:deep(.el-date-editor) {
  --el-text-color-regular: color-mix(in oklab, var(--text-primary) 95%, white);
  --el-text-color-placeholder: color-mix(in oklab, var(--text-secondary) 72%, white);
  --el-fill-color-blank: color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%);
}

:deep(.el-input__wrapper),
:deep(.el-input-number__wrapper),
:deep(.el-select__wrapper),
:deep(.el-textarea__inner) {
  min-height: 42px;
  border-radius: 11px !important;
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 76%, var(--primary-color) 24%) 0%, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 100%) !important;
  box-shadow:
    inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 14%, var(--border-default)),
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 10%, transparent) !important;
  transition: box-shadow var(--transition-fast), background var(--transition-fast), transform var(--transition-fast) !important;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover),
:deep(.el-input-number .el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 72%, var(--primary-color) 28%) 0%, color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%) 100%) !important;
  box-shadow:
    inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 20%, var(--border-default)),
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 12%, transparent) !important;
}

:deep(.el-input__inner),
:deep(.el-select__selected-item),
:deep(.el-date-editor input),
:deep(.el-input-number .el-input__inner) {
  color: color-mix(in oklab, var(--text-primary) 96%, white) !important;
  font-size: 15px !important;
  font-variant-numeric: tabular-nums;
}

:deep(.el-input-number .el-input__inner) {
  font-family: var(--font-family-mono, "JetBrains Mono", monospace);
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focused),
:deep(.el-textarea__inner:focus),
:deep(.el-input-number.is-controls-right .el-input__wrapper.is-focus) {
  box-shadow:
    inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 30%, var(--border-default)) !important,
    inset 0 1px 0 color-mix(in oklab, var(--primary-light) 16%, transparent),
    0 0 0 4px color-mix(in oklab, var(--primary-color) 11%, transparent),
    0 0 18px color-mix(in oklab, var(--primary-color) 14%, transparent) !important;
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 68%, var(--primary-color) 32%) 0%, color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%) 100%) !important;
}

:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 72%, var(--primary-color) 28%) 0%, color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%) 100%) !important;
  color: color-mix(in oklab, var(--text-primary) 92%, white) !important;
  border-color: color-mix(in oklab, var(--primary-color) 18%, transparent) !important;
  width: 26px;
}

:deep(.el-input-number__decrease:hover),
:deep(.el-input-number__increase:hover) {
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 28%, var(--bg-stage-soft)) 0%, color-mix(in oklab, var(--primary-color) 18%, var(--bg-panel)) 100%) !important;
  color: white !important;
}

:deep(.el-input-number__decrease-inner),
:deep(.el-input-number__increase-inner) {
  color: inherit !important;
}

:deep(.el-select__caret),
:deep(.el-input__icon),
:deep(.el-date-editor .el-input__prefix),
:deep(.el-date-editor .el-input__suffix) {
  color: color-mix(in oklab, var(--text-secondary) 70%, white) !important;
}

:deep(.el-select__wrapper),
:deep(.el-date-editor .el-input__wrapper),
:deep(.el-input-number .el-input__wrapper) {
  border: 1px solid transparent;
}

:deep(.el-form-item.is-error) {
  border-color: color-mix(in oklab, var(--danger-color, #ff6b6b) 44%, var(--border-default));
  box-shadow:
    inset 0 1px 0 color-mix(in oklab, white 8%, transparent),
    0 0 0 1px color-mix(in oklab, var(--danger-color, #ff6b6b) 20%, transparent);
}

.primary-btn {
  min-width: 154px;
}

@media (max-width: 1480px) {
  .config-shell {
    display: flex;
  }

  .stage-head {
    flex-direction: column;
  }

  .workflow-rail {
    width: 228px;
    min-width: 228px;
    flex-basis: 228px;
  }

  .impact-panel,
  .stage-progress-board {
    width: 280px;
    min-width: 280px;
    flex-basis: 280px;
  }

  .price-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1180px) {
  .config-page {
    padding-bottom: 20px;
  }

  .config-shell {
    flex-direction: column;
  }

  .workflow-rail,
  .impact-panel {
    border: none;
  }

  .workflow-rail {
    border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 12%, transparent);
  }

  .impact-panel {
    border-top: 1px solid color-mix(in oklab, var(--primary-color) 12%, transparent);
  }

  .plane-intro,
  .stage-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .two-columns {
    grid-template-columns: 1fr;
  }

  .workflow-rail,
  .impact-panel,
  .stage-progress-board,
  .stage-head-main {
    width: 100%;
    min-width: 0;
    flex-basis: auto;
  }

  .stage-actions-buttons {
    justify-content: flex-start;
  }
}

@media (max-width: 820px) {
  .config-shell {
    border-radius: 24px;
  }

  .workflow-rail,
  .impact-panel,
  .stage-head,
  .stage-plane,
  .stage-actions {
    padding-left: 16px;
    padding-right: 16px;
  }

  .surface-block {
    padding: 18px;
    border-radius: 22px;
  }

  .stage-icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .price-grid,
  .algorithm-grid {
    grid-template-columns: 1fr;
  }
}
</style>
