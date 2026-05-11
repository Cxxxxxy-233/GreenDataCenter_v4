import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Config from '@/views/Config.vue'
import Generate from '@/views/Generate.vue'
import Detail from '@/views/Detail.vue'
import History from '@/views/History.vue'
import Settings from '@/views/Settings.vue'
import Help from '@/views/Help.vue'
import Workflow from '@/views/Workflow.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/workflow', name: 'Workflow', component: Workflow },
  { path: '/config', name: 'Config', component: Config },
  { path: '/generate', name: 'Generate', component: Generate },
  { path: '/detail/:id', name: 'Detail', component: Detail },
  { path: '/history', name: 'History', component: History },
  { path: '/settings', name: 'Settings', component: Settings },
  { path: '/help', name: 'Help', component: Help }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
