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
  background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
}

/* 顶部栏 - 科技绿色主题 */
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
  padding: 0 32px;
  background: linear-gradient(145deg, #059669 0%, #10B981 40%, #34D399 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
  z-index: 100;
  position: relative;
  overflow: hidden;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.5) 20%, rgba(255, 255, 255, 0.8) 50%, rgba(255, 255, 255, 0.5) 80%, transparent 100%);
}

.header-glow {
  position: absolute;
  top: -50%;
  right: -10%;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.03) 50%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 6px 0;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.08) 100%);
  border-radius: 10px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.logo-icon:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.logo-icon svg {
  width: 22px;
  height: 22px;
  color: white;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.25));
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-icon:hover svg {
  transform: rotate(5deg) scale(1.1);
}

.logo-pulse {
  position: absolute;
  inset: -2px;
  border-radius: 12px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.system-name {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.4px;
  color: white;
  line-height: 1.3;
  background: linear-gradient(90deg, #ffffff, rgba(255, 255, 255, 0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.system-subtitle {
  font-size: 11.5px;
  opacity: 0.85;
  letter-spacing: 0.6px;
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.header-center :deep(.el-breadcrumb) {
  color: rgba(255, 255, 255, 0.95);
}

.header-center :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.85) !important;
  font-size: 14px;
  font-weight: 400;
}

.header-center :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.55);
  margin: 0 10px;
  font-size: 14px;
}

.header-center :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: white !important;
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
  color: rgba(255, 255, 255, 0.9);
  font-size: 20px;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.18);
  color: white;
  transform: translateY(-2px);
}

.header-btn:active {
  transform: translateY(-1px);
}

.badge-item {
  display: flex;
}

.badge-item :deep(.el-badge__content) {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  border: 2px solid #10B981;
  box-shadow: 0 3px 10px rgba(245, 158, 11, 0.5);
  font-size: 11px;
  font-weight: 600;
  padding: 1px 5px;
  min-width: 19px;
  height: 19px;
  line-height: 14px;
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.el-divider {
  height: 30px;
  width: 1px;
  background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.4) 30%, rgba(255, 255, 255, 0.4) 70%, transparent 100%);
  margin: 0 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 7px 15px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.08);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-2px);
}

.user-info:active {
  transform: translateY(-1px);
}

.user-avatar {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-radius: 50%;
  font-size: 16px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.18);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.arrow {
  font-size: 14px;
  opacity: 0.72;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-info:hover .arrow {
  transform: rotate(180deg);
}

/* 通知面板 */
.notification-panel {
  position: fixed;
  top: 72px;
  right: 24px;
  width: 360px;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  border: 1px solid rgba(16, 185, 129, 0.1);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #E5E7EB;
}

.notification-header h3 {
  font-size: 15px;
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
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.notification-item:hover {
  background: var(--bg-hover);
}

.notification-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 主内容包装 */
.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 - 科技绿色主题 */
.sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%);
  border-right: 1px solid #D1FAE5;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 2px 0 15px rgba(16, 185, 129, 0.08);
  position: relative;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-light) 50%, var(--primary-color) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sidebar:hover::before {
  opacity: 1;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: 20px 18px 16px;
  border-bottom: 1px solid #D1FAE5;
  background: rgba(240, 253, 244, 0.8);
}

.project-selector {
  width: 100%;
}

.project-selector :deep(.el-select) {
  width: 100%;
}

.project-selector :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: white;
  border-color: #D1FAE5;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.06);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.project-selector :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-color);
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.15);
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 12px 12px 16px;
  overflow-y: auto;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 46px;
  line-height: 46px;
  margin: 3px 0;
  border-radius: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  font-weight: 500;
  color: #4B5563;
  position: relative;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.02) 100%);
  color: var(--primary-color);
  transform: translateX(3px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: white;
  border-radius: 0 3px 3px 0;
  opacity: 0.9;
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
  margin-right: 12px;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-menu :deep(.el-menu-item:hover .el-icon) {
  transform: scale(1.1);
}

.sidebar-menu :deep(.el-divider) {
  margin: 16px 20px;
  border-color: #D1FAE5;
  position: relative;
}

.sidebar-menu :deep(.el-divider::before) {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.2), transparent);
}

.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid #D1FAE5;
  background: rgba(240, 253, 244, 0.8);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  color: #6B7280;
  font-size: 17px;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.collapse-btn:hover {
  color: var(--primary-color);
  background: rgba(16, 185, 129, 0.08);
  transform: scale(1.05);
}

/* 内容区 */
.content-area {
  flex: 1;
  overflow-y: auto;
  background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
}

.content-wrapper {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--spacing-2xl);
  min-height: 100%;
}

/* 路由过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-normal);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>