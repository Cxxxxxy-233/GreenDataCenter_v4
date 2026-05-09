<template>
  <div class="app-container">
    <!-- 顶部栏 -->
    <header class="top-header">
      <div class="header-left">
        <div class="logo-area">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
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
        <el-button type="text" class="header-btn" circle>
          <el-badge :value="3" :max="9" class="badge-item">
            <el-icon><Bell /></el-icon>
          </el-badge>
        </el-button>
        <el-button type="text" class="header-btn" circle>
          <el-icon><QuestionFilled /></el-icon>
        </el-button>
        <el-divider direction="vertical" />
        <el-dropdown trigger="click">
          <div class="user-info">
            <div class="user-avatar">
              <el-icon><User /></el-icon>
            </div>
            <span class="user-name">管理员</span>
            <el-icon class="arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>
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

    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <div class="project-selector">
            <el-select v-model="currentProject" placeholder="选择项目" size="default">
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
  DArrowRight
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const sidebarCollapsed = ref(false)
const currentProject = ref('乌兰察布示范项目')

const activeMenu = computed(() => route.name)

const currentPageName = computed(() => {
  const routeNames = {
    Home: '项目概览',
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
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-page);
}

/* 顶部栏 */
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 var(--spacing-2xl);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  box-shadow: var(--shadow-md);
  z-index: var(--z-fixed);
}

.header-left {
  flex: 1;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-md);
}

.logo-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.system-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.system-subtitle {
  font-size: var(--font-size-xs);
  opacity: 0.85;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-center :deep(.el-breadcrumb) {
  color: rgba(255, 255, 255, 0.9);
}

.header-center :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.85) !important;
}

.header-center :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6);
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
  gap: var(--spacing-md);
}

.header-btn {
  color: white;
  font-size: var(--font-size-xl);
  width: 36px;
  height: 36px;
  transition: all var(--transition-fast);
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  transform: scale(1.05);
}

.badge-item {
  display: flex;
}

.badge-item :deep(.el-badge__content) {
  background: var(--accent-color);
  border: none;
}

.el-divider {
  height: 24px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 var(--spacing-sm);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.15);
}

.user-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-md);
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.arrow {
  font-size: var(--font-size-xs);
  opacity: 0.8;
}

/* 主内容包装 */
.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-container);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  overflow: hidden;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
}

.project-selector {
  width: 100%;
}

.project-selector :deep(.el-select) {
  width: 100%;
}

.project-selector :deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  background: var(--bg-page);
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: var(--spacing-sm) 0;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 2px var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: var(--bg-hover);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: var(--primary-bg);
  color: var(--primary-color);
  position: relative;
}

.sidebar-menu :deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 3px;
  background: var(--primary-color);
  border-radius: 0 2px 2px 0;
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  font-size: var(--font-size-lg);
  margin-right: var(--spacing-md);
}

.sidebar-menu :deep(.el-divider) {
  margin: var(--spacing-md) var(--spacing-lg);
  border-color: var(--border-light);
}

.sidebar-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  width: 32px;
  height: 32px;
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  color: var(--primary-color);
  background: var(--primary-bg);
  border-radius: var(--radius-md);
}

/* 内容区 */
.content-area {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-page);
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
