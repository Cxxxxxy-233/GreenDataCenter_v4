<template>
  <div class="history-page">
    <div class="filter-section">
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="按项目名称搜索"
          prefix-icon="Search"
        />
      </div>
      <div class="filter-options">
        <el-select v-model="statusFilter" placeholder="状态筛选">
          <el-option label="全部" value="" />
          <el-option label="待配置" value="待配置" />
          <el-option label="生成中" value="生成中" />
          <el-option label="已完成" value="已完成" />
          <el-option label="失败" value="失败" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />
        <el-select v-model="sortBy" placeholder="排序方式">
          <el-option label="创建时间降序" value="createTimeDesc" />
          <el-option label="创建时间升序" value="createTimeAsc" />
          <el-option label="PUE升序" value="pueAsc" />
          <el-option label="PUE降序" value="pueDesc" />
          <el-option label="LCOE升序" value="lcoeAsc" />
          <el-option label="LCOE降序" value="lcoeDesc" />
        </el-select>
      </div>
    </div>

    <div class="table-section">
      <el-table
        :data="filteredProjects"
        border
        @selection-change="handleSelectionChange"
        class="project-table"
      >
        <el-table-column type="selection" />
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-name-cell">
              <div class="project-icon" :style="{ background: getProjectIconBg(row.status) }">
                <el-icon><Document /></el-icon>
              </div>
              <span class="project-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small" round>
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cabinetPower" label="单机柜功率(kW)" width="140" />
        <el-table-column prop="pue" label="预测PUE" width="100">
          <template #default="scope">
            <span :class="{ highlight: isGoodPue(scope.row.pue) }">{{ scope.row.pue }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="greenRate" label="绿电消纳率(%)" width="130">
          <template #default="scope">
            <span :class="{ highlight: isGoodGreenRate(scope.row.greenRate) }">{{ scope.row.greenRate }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="investment" label="总投资(万元)" width="130" />
        <el-table-column prop="actions" label="操作" width="240">
          <template #default="scope">
            <div class="actions-cell">
              <el-button type="primary" link size="small" @click="viewDetail(scope.row)">
                查看详情
              </el-button>
              <el-button type="primary" link size="small" @click="editParams(scope.row)">
                编辑参数
              </el-button>
              <el-button type="primary" link size="small" @click="copyProject(scope.row)">
                复制项目
              </el-button>
              <el-popconfirm title="确定要删除该项目吗？" @confirm="deleteProject(scope.row)">
                <template #reference>
                  <el-button type="danger" link size="small" @click.stop>删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-section">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        :total="totalProjects"
        layout="total, sizes, prev, pager, next, jumper"
      />
      <div v-if="selectedProjects.length > 0" class="batch-actions">
        <span>已选择 {{ selectedProjects.length }} 项</span>
        <el-button danger @click="batchDelete">批量删除</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Document } from '@element-plus/icons-vue'
import { solutionApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()

const searchKeyword = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const sortBy = ref('createTimeDesc')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedProjects = ref([])

const projects = ref([])

const parseDate = (dateStr) => {
  if (!dateStr) return null
  const date = new Date(dateStr)
  return Number.isNaN(date.getTime()) ? null : date
}

const toNumber = (value, fallback = null) => {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

const filteredAndSortedProjects = computed(() => {
  let result = [...projects.value]

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    result = result.filter(p => String(p.name || '').toLowerCase().includes(keyword))
  }

  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }

  if (Array.isArray(dateRange.value) && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    const startTime = parseDate(start)?.getTime()
    const endDate = parseDate(end)
    const endTime = endDate ? new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate(), 23, 59, 59, 999).getTime() : null
    result = result.filter((project) => {
      const createdAt = parseDate(project.created_at)?.getTime()
      if (createdAt === null || createdAt === undefined) return false
      if (startTime && createdAt < startTime) return false
      if (endTime && createdAt > endTime) return false
      return true
    })
  }

  const sorters = {
    createTimeDesc: (a, b) => (parseDate(b.created_at)?.getTime() || 0) - (parseDate(a.created_at)?.getTime() || 0),
    createTimeAsc: (a, b) => (parseDate(a.created_at)?.getTime() || 0) - (parseDate(b.created_at)?.getTime() || 0),
    pueAsc: (a, b) => (toNumber(a.pue, Infinity) - toNumber(b.pue, Infinity)),
    pueDesc: (a, b) => (toNumber(b.pue, -Infinity) - toNumber(a.pue, -Infinity)),
    lcoeAsc: (a, b) => (toNumber(a.investment, Infinity) - toNumber(b.investment, Infinity)),
    lcoeDesc: (a, b) => (toNumber(b.investment, -Infinity) - toNumber(a.investment, -Infinity))
  }

  const sorter = sorters[sortBy.value] || sorters.createTimeDesc
  result.sort(sorter)

  return result
})

const totalProjects = computed(() => filteredAndSortedProjects.value.length)

const filteredProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = currentPage.value * pageSize.value
  return filteredAndSortedProjects.value.slice(start, end)
})

const getStatusType = (status) => {
  const types = {
    '已完成': 'success',
    '生成中': 'warning',
    '待配置': 'info',
    '失败': 'danger'
  }
  return types[status] || 'info'
}

const getProjectIconBg = (status) => {
  const colors = {
    '已完成': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
    '生成中': 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
    '待配置': 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)',
    '失败': 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)'
  }
  return colors[status] || colors['待配置']
}

const isGoodPue = (pue) => {
  const num = parseFloat(pue)
  return !isNaN(num) && num <= 1.3
}

const isGoodGreenRate = (rate) => {
  const num = parseFloat(rate)
  return !isNaN(num) && num >= 80
}

const handleSelectionChange = (val) => {
  selectedProjects.value = val
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const viewDetail = (project) => {
  router.push(`/detail/${project.id}`)
}

const editParams = (project) => {
  ElMessage.info(`方案"${project.name}"当前不支持自动回填参数，将跳转到配置页手动调整`)
  router.push('/config')
}

const copyProject = (project) => {
  ElMessage.warning(`后端暂未提供复制接口，无法复制项目"${project.name}"`)
}

const deleteProject = (project) => {
  ElMessage.warning(`后端暂未提供删除接口，无法删除项目"${project.name}"`)
}

const batchDelete = () => {
  const count = selectedProjects.value.length
  ElMessage.warning(`后端暂未提供批量删除接口，当前无法删除选中的 ${count} 个项目`)
}

const loadProjects = async () => {
  try {
    const response = await solutionApi.getAll()
    const solutions = response.data || []
    
    projects.value = solutions.map(solution => ({
      id: solution.id,
      name: solution.name || '未命名方案',
      created_at: solution.created_at || '',
      createTime: solution.created_at ? formatDate(solution.created_at) : '--',
      status: solution.success ? '已完成' : '失败',
      cabinetPower: '--',
      pue: solution.key_metrics?.pue ?? '--',
      greenRate: solution.key_metrics?.green_power_ratio != null ? (solution.key_metrics.green_power_ratio * 100).toFixed(1) : '--',
      investment: solution.key_metrics?.total_cost ?? '--',
      generationTime: solution.generation_time ?? null,
      raw: solution
    }))
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error(`加载项目列表失败: ${error.message}`)
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadProjects()
})

watch([searchKeyword, statusFilter, dateRange, sortBy], () => {
  currentPage.value = 1
})
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100% - 20px);
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border-radius: 22px;
  padding: 22px 24px;
  margin-bottom: 0;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.search-box {
  width: 320px;
}

.filter-options {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-options :deep(.el-select) {
  min-width: 140px;
}

.table-section {
  flex: 1;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 98%, var(--primary-color) 2%) 0%, color-mix(in oklab, var(--bg-panel) 96%, var(--primary-color) 4%) 100%);
  border-radius: 22px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.project-table :deep(.el-table__header th) {
  background: color-mix(in oklab, var(--bg-panel) 90%, var(--primary-color) 10%) !important;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid var(--border-light);
}

.project-table :deep(.el-table__body td) {
  border-color: var(--border-light);
}

.project-table :deep(.el-table__body tr:hover) {
  background: color-mix(in oklab, var(--primary-color) 6%, var(--bg-card));
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.project-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(248, 253, 249, 0.98);
  font-size: 14px;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
}

.project-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.highlight {
  color: var(--primary-dark);
  font-weight: 600;
}

.actions-cell {
  display: flex;
  gap: 4px;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px 22px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 97%, var(--primary-color) 3%) 0%, color-mix(in oklab, var(--bg-panel) 94%, var(--primary-color) 6%) 100%);
  border-radius: 20px;
  margin-top: 0;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  flex-wrap: wrap;
}

.pagination-section :deep(.el-pagination) {
  --el-pagination-button-bg-color: transparent;
}

.pagination-section :deep(.el-pager li.is-active) {
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: rgba(249, 253, 250, 0.98);
  border-radius: 10px;
}

.pagination-section :deep(.el-pagination button:hover:not(.is-disabled)) {
  color: var(--primary-dark);
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  flex-wrap: wrap;
}

.batch-actions :deep(.el-button) {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  border: none;
  color: rgba(249, 253, 250, 0.98);
}

.batch-actions :deep(.el-button:hover) {
  background: linear-gradient(135deg, #F87171 0%, #EF4444 100%);
}

@media (max-width: 1024px) {
  .filter-section,
  .pagination-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-box {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
    padding: 16px;
  }

  .search-box {
    width: 100%;
  }

  .filter-options {
    flex-wrap: wrap;
  }

  .filter-options :deep(.el-select),
  .filter-options :deep(.el-date-editor),
  .filter-options :deep(.el-date-editor.el-input) {
    width: 100%;
  }

  .pagination-section {
    padding: 16px;
  }

  .batch-actions,
  .pagination-section :deep(.el-pagination) {
    width: 100%;
    justify-content: center;
  }
}
</style>
