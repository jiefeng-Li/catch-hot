import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/hot' },
  { path: '/hot', name: 'hot', component: () => import('./views/HotItems.vue'), meta: { title: '热点列表' } },
  { path: '/tags', name: 'tags', component: () => import('./views/Tags.vue'), meta: { title: '标签管理' } },
  { path: '/trend', name: 'trend', component: () => import('./views/Trend.vue'), meta: { title: '趋势分析' } },
  { path: '/jobs', name: 'jobs', component: () => import('./views/Jobs.vue'), meta: { title: '任务日志' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
