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

/* 顶部栏 - 优化后 */
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
  padding: 0 32px;
  background: linear-gradient(145deg, #1e5fcc 0%, #0f4ca3 40%, #0a3f8f 100%);
  color: white;
  box-shadow: 0 2px 16px rgba(15, 76, 163, 0.25);
  z-index: 100;
  position: relative;
  overflow: hidden;
}

.top-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.4) 50%, transparent 100%);
}

.top-header::after {
  content: '';
  position: absolute;
  top: -60%;
  right: -15%;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 50%, transparent 70%);
  border-radius: 50%;
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
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.08) 100%);
  border-radius: 10px;
  backdrop-filter: blur(12px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.18);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-icon:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 14px rgba(0, 0, 0, 0.22);
}

.logo-icon svg {
  width: 22px;
  height: 22px;
  color: white;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.25));
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
}

.system-subtitle {
  font-size: 11.5px;
  opacity: 0.8;
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
  color: rgba(255, 255, 255, 0.88);
  font-size: 20px;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.14);
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
  background: linear-gradient(135deg, #ff5722 0%, #ff7043 100%);
  border: 2px solid #1e5fcc;
  box-shadow: 0 3px 10px rgba(255, 87, 34, 0.5);
  font-size: 11px;
  font-weight: 600;
  padding: 1px 5px;
  min-width: 19px;
  height: 19px;
  line-height: 14px;
}

.el-divider {
  height: 30px;
  width: 1px;
  background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.35) 30%, rgba(255, 255, 255, 0.35) 70%, transparent 100%);
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
  background: rgba(255, 255, 255, 0.06);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.14);
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
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.28) 0%, rgba(255, 255, 255, 0.1) 100%);
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

/* 主内容包装 */
.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 - 优化后 */
.sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-right: 1px solid #e8ecf0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.04);
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: 20px 18px 16px;
  border-bottom: 1px solid #eef2f6;
  background: rgba(248, 250, 252, 0.5);
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
  border-color: #e1e6ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.project-selector :deep(.el-input__wrapper:hover) {
  border-color: #165DFF;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.12);
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
  color: #4e5969;
  position: relative;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: linear-gradient(135deg, rgba(22, 93, 255, 0.06) 0%, rgba(22, 93, 255, 0.02) 100%);
  color: #165DFF;
  transform: translateX(2px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.25);
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
  transform: scale(1.08);
}

.sidebar-menu :deep(.el-divider) {
  margin: 16px 20px;
  border-color: #e8ecf0;
  position: relative;
}

.sidebar-menu :deep(.el-divider::before) {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(22, 93, 255, 0.15), transparent);
}

.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid #eef2f6;
  background: rgba(248, 250, 252, 0.5);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  color: #86909c;
  font-size: 17px;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.collapse-btn:hover {
  color: #165DFF;
  background: rgba(22, 93, 255, 0.06);
  transform: scale(1.05);
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
