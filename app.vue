<template>
  <div>
    <NuxtLoadingIndicator />

    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: '地铁隧道损伤检测系统',
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    { name: 'theme-color', content: "#ffffff" },
    { name: 'author', content: '你的名字/团队' },
    { name: 'description', content: '基于列车加速度数据的隧道结构损伤检测平台' }
  ],
  link: [
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
  ],
  htmlAttrs: {
    lang: 'zh-CN'
  }
})

useSeoMeta({
  title: '地铁隧道损伤检测系统',
  description: '本系统基于列车加速度数据识别地铁隧道结构损伤类型和位置',
  ogTitle: '地铁隧道损伤检测系统',
  ogDescription: '利用深度学习模型处理时频图，实现地铁隧道损伤分级和定位',
  ogImage: '', // 不引用任何图片
  twitterImage: '',
  twitterCard: 'summary_large_image'
})
</script>
