import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  // 认证
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', guest: true }
  },
  // 学：鉴赏模块
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/learn/HomeView.vue'),
    meta: { title: '诗词雅韵' }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/learn/SearchView.vue'),
    meta: { title: '检索' }
  },
  {
    path: '/poems',
    name: 'PoemList',
    component: () => import('@/views/learn/PoemListView.vue'),
    meta: { title: '诗词库' }
  },
  {
    path: '/poem/:id',
    name: 'PoemDetail',
    component: () => import('@/views/learn/PoemDetailView.vue'),
    meta: { title: '鉴赏' }
  },
  {
    path: '/author/:name',
    name: 'Author',
    component: () => import('@/views/learn/AuthorView.vue'),
    meta: { title: '作者' }
  },
  // 练：挑战模块
  {
    path: '/challenge',
    name: 'ChallengeHome',
    component: () => import('@/views/practice/ChallengeHome.vue'),
    meta: { title: '诗词挑战' }
  },
  {
    path: '/challenge/chain',
    name: 'ChainGame',
    component: () => import('@/views/practice/ChainGame.vue'),
    meta: { title: '飞花令' }
  },
  {
    path: '/challenge/quiz',
    name: 'QuizGame',
    component: () => import('@/views/practice/QuizGame.vue'),
    meta: { title: '答题闯关' }
  },
  // 创：生成模块
  {
    path: '/create',
    name: 'Generate',
    component: () => import('@/views/create/GenerateView.vue'),
    meta: { title: '诗词生成' }
  },
  {
    path: '/create/mimic',
    name: 'Mimic',
    component: () => import('@/views/create/MimicView.vue'),
    meta: { title: '仿写工坊' }
  },
  {
    path: '/create/image',
    name: 'ImageCreate',
    component: () => import('@/views/create/ImageView.vue'),
    meta: { title: '诗画互生' }
  },
  {
    path: '/create/video',
    name: 'VideoCreate',
    component: () => import('@/views/create/VideoView.vue'),
    meta: { title: '诗境动画' }
  },
  {
    path: '/explore/imagery',
    name: 'Imagery',
    component: () => import('@/views/explore/ImageryView.vue'),
    meta: { title: '诗境漫游' }
  },
  // 404
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// 路由守卫（预留认证逻辑）
router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - 诗词雅韵` : '诗词雅韵'
})

export default router
