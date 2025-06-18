// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  // ✅ 添加 pinia 模块支持
  modules: ['@pinia/nuxt']
})
