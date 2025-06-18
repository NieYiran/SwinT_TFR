import { useAuthStore } from '~/stores/auth'
import { defineNuxtRouteMiddleware, navigateTo } from '#app'

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  // 登录和注册页不拦截
  if (to.path === '/login' || to.path === '/register') return

  // 未登录跳转
  if (!auth.isLoggedIn()) {
    return navigateTo('/login')
  }

  // 管理员权限判断
  if (to.path.startsWith('/admin')) {
    const user = auth.user
    console.log('当前用户信息:', user)

    // user 可能为 null，先判断
    if (!user || user.role !== 0) {
      alert('只有管理员才能访问该页面！')
      return navigateTo('/')
    }
  }
})

