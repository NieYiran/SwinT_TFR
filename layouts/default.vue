<template>
  <div class="dashboard">
    <!-- 左侧可折叠面板 -->
    <div class="sidebar">
      <!-- 顶部导航栏 -->
      <div class="sidebar-header">
        <div class="web-info">
          <div class="logo">🚇 MetroSense</div>
        </div>
      </div>

      <!-- 侧边栏链接 -->
      <div class="sidebar-links">
        <ul>
          <li v-for="link in mainLinks" :key="link.id">
            <router-link :to="link.to">
              <i :class="link.icon"></i>
              {{ link.label }}
            </router-link>
          </li>
        </ul>
      </div>

      <!-- 页脚 -->
      <div class="sidebar-footer">
        <div class="user-dropdown" @click="toggleDropdown">
          <span class="avatar-text">👤 {{ username }}</span>
          <div v-if="dropdownOpen" class="dropdown-menu">
            <a href="/profile">个人中心</a>
            <a href="/settings">设置</a>
            <a @click="logout">退出登录</a>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-content">
      <!-- 页面内容 -->
      <slot />

      <!-- 帮助面板 -->
      <div class="help-slideover">
        <button v-if="showLogout" @click="showHelp = !showHelp">❓帮助</button>
        <div v-if="showHelp" class="help-content">
          <h3>帮助信息</h3>
          <p>检测分析</p>
          <p>在导航栏打开“检测分析”页面。先上传不同部位的图片，如上传错误可以点击“删除”并重传；点击“查看”可预览选中的图片。上传成功后，点击“开始检测”，显示检测结果。</p>
        </div>
        <button v-if="showLogout" @click="logout">
          <i class="i-heroicons-arrow-left-on-rectangle"></i> 退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const mainLinks = [
  { id: 1, to: '/', icon: 'i-heroicons-home', label: '首页' },
  { id: 2, to: '/getpic', icon: 'i-heroicons-cog-6-tooth', label: '时频图制作' },
  { id: 3, to: '/detect', icon: 'i-heroicons-magnifying-glass-circle', label: '检测分析' },
  { id: 4, to: '/historydata', icon: 'i-heroicons-cog-6-tooth', label: '历史数据查询' },
  { id: 5, to: '/admin', icon: 'i-heroicons-magnifying-glass-circle', label: '用户管理' }
]

const username = 'Admin'
const dropdownOpen = ref(false)
const searchQuery = ref('')
const selectedGroup = ref('全部')
const showHelp = ref(false)
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const searchGroups = ['全部', '损伤类型', '损伤位置']

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}
const logout = () => {
  router.push('/login')
}
const showLogout = computed(() => {
  return !['/login', '/register'].includes(route.path)
})
const handleSearch = () => {
  console.log('搜索内容：', searchQuery.value, '分类：', selectedGroup.value)
}

</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
}
.sidebar {
  width: 240px;
  background: #1f2937;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.sidebar-header {
  padding: 1rem;
}
.logo {
  font-size: 1.5rem;
  font-weight: bold;
}
.sidebar-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-links li {
  padding: 0.75rem 1rem;
}
.sidebar-links li:hover {
  background-color: #374151;
}
.router-link-exact-active {
  font-weight: bold;
}
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #374151;
}
.user-dropdown {
  position: relative;
  cursor: pointer;
}
.avatar-text {
  font-size: 1rem;
  vertical-align: middle;
}
.dropdown-menu {
  position: absolute;
  top: 40px;
  left: 0;
  background: #fff;
  color: #000;
  border: 1px solid #ccc;
  padding: 0.5rem;
  z-index: 100;
}
.main-content {
  flex: 1;
  padding: 1rem;
  position: relative;
}
.search-box {
  margin-top: 2rem;
  display: flex;
  gap: 0.5rem;
}
.help-slideover {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
.help-content {
  position: absolute;
  top: 2.5rem;
  right: 0;
  background: #f9fafb;
  border: 1px solid #ccc;
  padding: 1rem;
  width: 200px;
}
.info-content {
  position: absolute;
  top: 2.5rem;
  right: 0;
  background: #f9fafb;
  border: 1px solid #ccc;
  padding: 1rem;
  width: 200px;
}
</style>

