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
import { ref, computed, onMounted } from 'vue'
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

const totalProjects = computed(() => projects.value.length)

const filteredProjects = computed(() => {
  let result = [...projects.value]

  if (searchKeyword.value) {
    result = result.filter(p => p.name.includes(searchKeyword.value))
  }

  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }

  return result.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value)
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
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const viewDetail = (project) => {
  router.push(`/detail/${project.id}`)
}

const editParams = (project) => {
  router.push('/config')
}

const copyProject = (project) => {
  console.log('Copy project:', project.id)
}

const deleteProject = (project) => {
  projects.value = projects.value.filter(p => p.id !== project.id)
  ElMessage.success(`项目"${project.name}"已删除`)
}

const batchDelete = () => {
  const count = selectedProjects.value.length
  projects.value = projects.value.filter(p => !selectedProjects.value.find(sp => sp.id === p.id))
  selectedProjects.value = []
  ElMessage.success(`已批量删除 ${count} 个项目`)
}

const loadProjects = async () => {
  try {
    const response = await solutionApi.getAll()
    const solutions = response.data || []
    
    if (solutions.length > 0) {
      projects.value = solutions.map(solution => ({
        id: solution.id,
        name: solution.name || '未命名方案',
        createTime: solution.created_at ? formatDate(solution.created_at) : '--',
        status: solution.success ? '已完成' : '失败',
        cabinetPower: solution.key_metrics?.computing_power_density || '--',
        pue: solution.key_metrics?.pue || '--',
        greenRate: solution.key_metrics?.green_power_ratio ? (solution.key_metrics.green_power_ratio * 100).toFixed(1) : '--',
        investment: solution.key_metrics?.total_cost || '--'
      }))
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  height: calc(100% - 20px);
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  border-radius: 14px;
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.08);
}

.search-box {
  width: 320px;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-color: rgba(16, 185, 129, 0.1);
}

.search-box :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.08);
}

.filter-options {
  display: flex;
  gap: 16px;
}

.filter-options :deep(.el-select) {
  min-width: 140px;
}

.filter-options :deep(.el-select .el-input__wrapper) {
  border-radius: 10px;
  border-color: rgba(16, 185, 129, 0.1);
}

.filter-options :deep(.el-date-picker .el-input__wrapper) {
  border-radius: 10px;
  border-color: rgba(16, 185, 129, 0.1);
}

.table-section {
  flex: 1;
  background: white;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.08);
}

.project-table :deep(.el-table__header th) {
  background: linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%) !important;
  color: #4B5563;
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid rgba(16, 185, 129, 0.1);
}

.project-table :deep(.el-table__body td) {
  border-color: rgba(16, 185, 129, 0.06);
}

.project-table :deep(.el-table__body tr:hover) {
  background: rgba(16, 185, 129, 0.03);
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.project-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  flex-shrink: 0;
}

.project-name {
  font-weight: 500;
  color: #1F2937;
  font-size: 14px;
}

.highlight {
  color: var(--primary-color);
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
  padding: 20px 24px;
  background: white;
  border-radius: 14px;
  margin-top: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.08);
}

.pagination-section :deep(.el-pagination) {
  --el-pagination-button-bg-color: transparent;
}

.pagination-section :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  border-radius: 8px;
}

.pagination-section :deep(.el-pagination button:hover:not(.is-disabled)) {
  color: var(--primary-color);
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4B5563;
  font-size: 14px;
}

.batch-actions :deep(.el-button) {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  border: none;
  color: white;
}

.batch-actions :deep(.el-button:hover) {
  background: linear-gradient(135deg, #F87171 0%, #EF4444 100%);
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }

  .filter-options {
    flex-wrap: wrap;
  }
}
</style>