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
      >
        <el-table-column type="selection" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cabinetPower" label="单机柜功率(kW)" />
        <el-table-column prop="pue" label="预测PUE" />
        <el-table-column prop="greenRate" label="绿电消纳率(%)" />
        <el-table-column prop="investment" label="总投资(万元)" />
        <el-table-column prop="actions" label="操作">
          <template #default="scope">
            <el-button type="text" @click="viewDetail(scope.row)">查看详情</el-button>
            <el-button type="text" @click="editParams(scope.row)">编辑参数</el-button>
            <el-button type="text" @click="copyProject(scope.row)">复制项目</el-button>
            <el-button type="text" danger @click="deleteProject(scope.row)">删除</el-button>
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
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.search-box {
  width: 300px;
}

.filter-options {
  display: flex;
  gap: 16px;
}

.table-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  margin-top: 20px;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
