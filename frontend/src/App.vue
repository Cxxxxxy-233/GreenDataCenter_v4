<template>
  <div class="app-container">
    <!-- 顶部栏 -->
    <header class="top-header">
      <div class="header-decoration"></div>
      <div class="header-glow"></div>
      
      <div class="header-left">
        <div class="logo-area">
          <div class="logo-icon" @mouseenter="logoHover = true" @mouseleave="logoHover = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
            <div class="logo-pulse" v-if="logoHover"></div>
          </div>
          <div class="logo-text">
            <span class="system-name">数据中心绿电一体化方案</span>
            <span class="system-subtitle">智能规划系统</span>
          </div>
        </div>
      </div>
      
      <div class="header-center">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentPageName }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      
      <div class="header-right">
        <el-button type="text" class="header-btn" circle @click="showNotification = !showNotification">
          <el-badge :value="3" :max="9" class="badge-item">
            <el-icon><Bell /></el-icon>
          </el-badge>
        </el-button>
        <el-button type="text" class="header-btn" circle @click="goToHelp">
          <el-icon><QuestionFilled /></el-icon>
        </el-button>
        <el-divider direction="vertical" />
        <el-dropdown trigger="click" @visible-change="handleDropdownVisible">
          <div class="user-info">
            <div class="user-avatar">
              <el-icon><User /></el-icon>
            </div>
            <span class="user-name">管理员</span>
            <el-icon class="arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToSettings">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 通知弹窗 -->
    <transition name="slide-down">
      <div v-if="showNotification" class="notification-panel">
        <div class="notification-header">
          <h3>通知消息</h3>
          <el-button type="text" @click="showNotification = false"><el-icon><Close /></el-icon></el-button>
        </div>
        <div class="notification-list">
          <div class="notification-item" v-for="(item, index) in notifications" :key="index">
            <div class="notification-icon" :class="item.type"></div>
            <div class="notification-content">
              <div class="notification-title">{{ item.title }}</div>
              <div class="notification-desc">{{ item.desc }}</div>
              <div class="notification-time">{{ item.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <div class="project-selector">
            <el-select 
              v-model="currentProject" 
              placeholder="选择项目" 
              size="default"
              class="project-select"
            >
              <el-option label="乌兰察布示范项目" value="乌兰察布示范项目" />
              <el-option label="贵安数据中心" value="贵安数据中心" />
              <el-option label="中卫算力基地" value="中卫算力基地" />
            </el-select>
          </div>
        </div>

        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          mode="vertical"
          :collapse="sidebarCollapsed"
        >
          <el-menu-item index="Home" @click="navigateTo('Home')">
            <template #title>
              <el-icon><PieChart /></el-icon>
              <span>项目概览</span>
            </template>
          </el-menu-item>
          <el-menu-item index="Workflow" @click="navigateTo('Workflow')">
            <template #title>
              <el-icon><Briefcase /></el-icon>
              <span>工作流</span>
            </template>
          </el-menu-item>
          <el-menu-item index="Config" @click="navigateTo('Config')">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>参数配置</span>
            </template>
          </el-menu-item>
          <el-menu-item index="Generate" @click="navigateTo('Generate')">
            <template #title>
              <el-icon><RefreshRight /></el-icon>
              <span>方案生成</span>
            </template>
          </el-menu-item>
          <el-menu-item index="Detail" @click="navigateTo('Detail')">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>方案详情</span>
            </template>
          </el-menu-item>
          <el-menu-item index="History" @click="navigateTo('History')">
            <template #title>
              <el-icon><FolderOpened /></el-icon>
              <span>历史项目</span>
            </template>
          </el-menu-item>

          <el-divider />

          <el-menu-item index="Settings" @click="navigateTo('Settings')">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>系统设置</span>
            </template>
          </el-menu-item>
          <el-menu-item index="Help" @click="navigateTo('Help')">
            <template #title>
              <el-icon><QuestionFilled /></el-icon>
              <span>帮助文档</span>
            </template>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <el-button
            class="collapse-btn"
            type="text"
            @click="sidebarCollapsed = !sidebarCollapsed"
          >
            <el-icon v-if="sidebarCollapsed"><DArrowRight /></el-icon>
            <el-icon v-else><DArrowLeft /></el-icon>
          </el-button>
        </div>
      </aside>

      <!-- 内容区 -->
      <main class="content-area">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade-slide" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Bell,
  QuestionFilled,
  User,
  ArrowDown,
  SwitchButton,
  PieChart,
  Setting,
  RefreshRight,
  Document,
  FolderOpened,
  Tools,
  DArrowLeft,
  DArrowRight,
  Briefcase,
  Close
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const sidebarCollapsed = ref(false)
const currentProject = ref('乌兰察布示范项目')
const logoHover = ref(false)
const showNotification = ref(false)
const dropdownVisible = ref(false)

const notifications = ref([
  { type: 'success', title: '方案生成完成', desc: '您的乌兰察布示范项目方案已生成完成', time: '刚刚' },
  { type: 'warning', title: '预算提醒', desc: '当前方案预算接近上限，建议优化配置', time: '5分钟前' },
  { type: 'info', title: '系统更新', desc: '系统已更新至v2.1.0版本，新增多项功能', time: '1小时前' }
])

const activeMenu = computed(() => route.name)

const currentPageName = computed(() => {
  const routeNames = {
    Home: '项目概览',
    Workflow: '工作流',
    Config: '参数配置',
    Generate: '方案生成',
    Detail: '方案详情',
    History: '历史项目',
    Settings: '系统设置',
    Help: '帮助文档'
  }
  return routeNames[route.name] || '首页'
})

const navigateTo = (name) => {
  router.push({ name })
}

const goToHelp = () => {
  router.push('/help')
}

const goToSettings = () => {
  router.push('/settings')
}

const handleDropdownVisible = (visible) => {
  dropdownVisible.value = visible
}
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background:
    radial-gradient(circle at 12% 12%, color-mix(in oklab, var(--primary-color) 12%, transparent), transparent 28%),
    radial-gradient(circle at 88% 0%, color-mix(in oklab, var(--accent-color) 10%, transparent), transparent 22%),
    radial-gradient(circle at 50% 100%, color-mix(in oklab, var(--primary-dark) 16%, transparent), transparent 30%),
    linear-gradient(180deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: calc(var(--header-height) + 2px);
  padding: 0 28px;
  background:
    radial-gradient(circle at 78% 35%, color-mix(in oklab, var(--primary-light) 18%, transparent), transparent 26%),
    radial-gradient(circle at 12% 0%, color-mix(in oklab, var(--accent-color) 12%, transparent), transparent 20%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-stage-soft) 82%, var(--primary-color) 18%) 0%, var(--bg-stage) 100%);
  color: color-mix(in oklab, white 94%, var(--primary-color) 6%);
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 24%, transparent);
  box-shadow: 0 18px 40px rgba(2, 11, 8, 0.34);
  z-index: var(--z-sticky);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  isolation: isolate;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, color-mix(in oklab, var(--primary-light) 65%, white) 50%, transparent 100%);
}

.header-glow {
  position: absolute;
  inset: auto -80px -160px auto;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, color-mix(in oklab, var(--primary-light) 26%, transparent) 0%, transparent 68%);
  border-radius: 50%;
  pointer-events: none;
  opacity: 0.95;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 4px 0;
}

.logo-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 24%, var(--bg-panel)) 0%, color-mix(in oklab, var(--primary-dark) 32%, transparent) 100%);
  border: 1px solid color-mix(in oklab, var(--primary-light) 34%, transparent);
  border-radius: 12px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 12px 26px rgba(2, 12, 8, 0.24);
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.logo-icon:hover {
  transform: translateY(-1px);
  border-color: color-mix(in oklab, var(--primary-light) 52%, transparent);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 16px 30px rgba(8, 26, 18, 0.24);
}

.logo-icon svg {
  width: 22px;
  height: 22px;
  color: #eefaf3;
}

.logo-pulse {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.14), transparent);
  animation: logoSweep 1.4s linear;
}

@keyframes logoSweep {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(110%); }
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.system-name {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.2px;
  color: color-mix(in oklab, white 93%, var(--primary-light) 7%);
  line-height: 1.3;
}

.system-subtitle {
  font-size: 11px;
  color: rgba(224, 241, 232, 0.64);
  letter-spacing: 0.36px;
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.header-center :deep(.el-breadcrumb) {
  color: rgba(244, 252, 246, 0.92);
}

.header-center :deep(.el-breadcrumb__inner) {
  color: rgba(244, 252, 246, 0.72) !important;
  font-size: 13px;
  font-weight: 500;
}

.header-center :deep(.el-breadcrumb__separator) {
  color: rgba(244, 252, 246, 0.34);
  margin: 0 8px;
  font-size: 12px;
}

.header-center :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: rgba(248, 253, 249, 0.98) !important;
  font-weight: 500;
}

.header-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.header-btn {
  color: rgba(243, 251, 245, 0.88);
  font-size: 18px;
  width: 38px;
  height: 38px;
  border-radius: 11px;
  transition: all var(--transition-fast);
  position: relative;
}

.header-btn:hover {
  background: rgba(121, 239, 171, 0.1);
  color: white;
}

.badge-item {
  display: flex;
}

.badge-item :deep(.el-badge__content) {
  background: linear-gradient(180deg, color-mix(in oklab, var(--warning-color) 92%, white) 0%, var(--warning-color) 100%);
  border: 2px solid color-mix(in oklab, var(--bg-stage) 85%, var(--primary-color) 15%);
  box-shadow: 0 6px 14px rgba(217, 154, 39, 0.28);
  font-size: 11px;
  font-weight: 600;
  padding: 1px 5px;
  min-width: 19px;
  height: 19px;
  line-height: 14px;
}

.el-divider {
  height: 24px;
  width: 1px;
  background: linear-gradient(180deg, transparent 0%, rgba(244, 252, 246, 0.32) 30%, rgba(244, 252, 246, 0.32) 70%, transparent 100%);
  margin: 0 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: rgba(8, 28, 22, 0.68);
  border: 1px solid rgba(121, 239, 171, 0.12);
}

.user-info:hover {
  background: rgba(14, 45, 35, 0.78);
}

.user-avatar {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in oklab, var(--primary-light) 18%, transparent);
  border-radius: 50%;
  font-size: 15px;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: rgba(248, 253, 249, 0.94);
}

.arrow {
  font-size: 13px;
  opacity: 0.64;
  transition: transform var(--transition-fast);
}

.user-info:hover .arrow {
  transform: rotate(180deg);
}

.notification-panel {
  position: fixed;
  top: calc(var(--header-height) + 10px);
  right: 18px;
  width: 360px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 88%, var(--primary-color) 12%) 0%, color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%) 100%);
  border-radius: 18px;
  box-shadow: var(--shadow-lg);
  z-index: var(--z-popover);
  border: 1px solid color-mix(in oklab, var(--primary-color) 16%, var(--border-light));
  overflow: hidden;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  background: color-mix(in oklab, var(--bg-panel) 84%, var(--primary-color) 16%);
}

.notification-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.notification-list {
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 14px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.notification-item:hover {
  background: color-mix(in oklab, var(--primary-color) 6%, var(--bg-card));
}

.notification-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.notification-icon.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.notification-icon.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-color);
}

.notification-icon.info {
  background: rgba(6, 182, 212, 0.1);
  color: var(--info-color);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.notification-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-time {
  font-size: 12px;
  color: var(--text-placeholder);
}

/* 侧边栏滑动动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all var(--transition-normal);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.sidebar {
  width: var(--sidebar-width);
  background:
    radial-gradient(circle at top, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 32%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-card) 86%, var(--primary-color) 14%) 0%, color-mix(in oklab, var(--bg-panel) 92%, var(--primary-color) 8%) 100%);
  border-right: 1px solid color-mix(in oklab, var(--primary-color) 12%, var(--border-light));
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  overflow: hidden;
  box-shadow: 14px 0 34px rgba(1, 8, 6, 0.24);
  position: relative;
  backdrop-filter: blur(8px);
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 28%, transparent) 0%, transparent 100%);
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: 18px 16px 14px;
  border-bottom: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-light));
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%);
}

.project-selector {
  width: 100%;
}

.project-selector :deep(.el-select) {
  width: 100%;
}

.project-selector :deep(.el-input__wrapper) {
  min-height: 40px;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 14px 12px 18px;
  overflow-y: auto;
  background: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 4px 0;
  border-radius: 12px;
  transition: all var(--transition-fast);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  position: relative;
  padding-left: 14px !important;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: color-mix(in oklab, var(--primary-color) 10%, var(--bg-card));
  color: var(--text-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(180deg, color-mix(in oklab, var(--primary-color) 18%, var(--bg-card)) 0%, color-mix(in oklab, var(--primary-color) 12%, var(--bg-panel)) 100%);
  color: rgba(246, 255, 249, 0.98);
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--primary-color) 28%, var(--border-default)), 0 0 0 1px rgba(121, 239, 171, 0.04);
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  background: var(--primary-color);
  border-radius: 50%;
  opacity: 1;
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  font-size: 17px;
  margin-right: 12px;
}

.sidebar-menu :deep(.el-divider) {
  margin: 16px 14px;
  border-color: color-mix(in oklab, var(--primary-color) 10%, var(--border-light));
  position: relative;
}

.sidebar-menu :deep(.el-divider::before) {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, color-mix(in oklab, var(--primary-color) 16%, transparent), transparent);
}

.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid color-mix(in oklab, var(--primary-color) 10%, var(--border-light));
  background: color-mix(in oklab, var(--bg-panel) 88%, var(--primary-color) 12%);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  color: var(--text-secondary);
  font-size: 16px;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  color: var(--primary-dark);
  background: color-mix(in oklab, var(--primary-color) 7%, transparent);
}

.content-area {
  flex: 1;
  overflow-y: auto;
  background:
    radial-gradient(circle at top, color-mix(in oklab, var(--accent-color) 8%, transparent), transparent 22%),
    radial-gradient(circle at 80% 0%, color-mix(in oklab, var(--primary-color) 8%, transparent), transparent 22%),
    linear-gradient(180deg, color-mix(in oklab, var(--bg-page) 92%, var(--primary-color) 8%) 0%, var(--bg-page) 100%);
  position: relative;
}

.content-wrapper {
  max-width: min(var(--content-max-width), calc(100vw - var(--sidebar-width)));
  margin: 0 auto;
  padding: 28px 28px 36px;
  min-height: 100%;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-normal);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 1200px) {
  .top-header {
    padding: 0 18px;
  }

  .content-wrapper {
    padding: 20px;
  }
}

@media (max-width: 960px) {
  .header-center {
    display: none;
  }

  .top-header {
    gap: 12px;
  }

  .header-left,
  .header-right {
    flex: initial;
  }
}

@media (max-width: 768px) {
  .main-wrapper {
    flex-direction: column;
  }

  .sidebar,
  .sidebar.collapsed {
    width: 100%;
  }

  .sidebar {
    max-height: 320px;
  }

  .notification-panel {
    left: 12px;
    right: 12px;
    width: auto;
  }

  .content-wrapper {
    padding: 16px;
  }

  .user-name {
    display: none;
  }
}
</style>
