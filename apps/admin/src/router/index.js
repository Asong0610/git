import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('../views/device/index.vue'),
        meta: { title: '设备管理' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/order/index.vue'),
        meta: { title: '订单管理' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/user/index.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'deposit',
        name: 'Deposit',
        component: () => import('../views/deposit/index.vue'),
        meta: { title: '押金流水' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('../views/statistics/index.vue'),
        meta: { title: '数据统计' }
      },
      {
        path: 'faults',
        name: 'Faults',
        component: () => import('../views/fault/index.vue'),
        meta: { title: '故障工单' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.public) {
    next()
  } else if (!authStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
