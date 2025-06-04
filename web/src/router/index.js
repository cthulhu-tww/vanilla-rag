import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/chatView.vue'
import Login from '../views/LoginView.vue'
import Manager from '../views/ManagerView.vue'
import DocumentManager from '../views/DocumentManagerView.vue'
import KnowledgeBaseManager from '@/views/KnowledgeBaseManager.vue'
import NotFound from '@/views/NotFoundView.vue'
import store from '@/store' // 导入你的Vuex store

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'chat',
      meta: { requiresAuth: true },
      component: Chat,
    },
    {
      path: '/manager',
      name: 'manager',
      meta: { requiresAuth: true },
      component: Manager,
      children: [
        {
          path: 'document', // 实际访问路径为 /manager/document
          name: 'document-manager',
          component: DocumentManager
        },
        {
          path: 'knowledge', // 实际访问路径为 /manager/knowledge
          name: 'knowledge-base-manager',
          component: KnowledgeBaseManager
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { guestOnly: true },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFound,
    },
  ],
})

router.beforeEach((to, from, next) => {
  // 检查目标路由是否需要认证
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    // 使用Vuex getter检查认证状态
    if (store.getters['auth/isAuthenticated']) {
      next()
    } else {
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    }
  }
  // 处理仅限未登录用户访问的路由（如登录页）
  else if (to.matched.some((record) => record.meta.guestOnly)) {
    if (store.getters['auth/isAuthenticated']) {
      // 如果用户已登录，重定向到首页
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
