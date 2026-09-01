import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('./views/HomePage.vue'),
    meta: { title: '个人主页', layout: 'home' },
  },
  { path: '/app', redirect: '/app/hot' },
  {
    path: '/app/hot',
    name: 'hot',
    component: () => import('./views/HotItems.vue'),
    meta: { title: '热点列表', layout: 'app' },
  },
  {
    path: '/app/tags',
    name: 'tags',
    component: () => import('./views/Tags.vue'),
    meta: { title: '标签管理', layout: 'app' },
  },
  {
    path: '/app/trend',
    name: 'trend',
    component: () => import('./views/Trend.vue'),
    meta: { title: '趋势分析', layout: 'app' },
  },
  {
    path: '/app/jobs',
    name: 'jobs',
    component: () => import('./views/Jobs.vue'),
    meta: { title: '任务日志', layout: 'app' },
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
