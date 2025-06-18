<template>
  <div class="container">
    <h2>登录</h2>
    <input v-model="user_id" type="text" placeholder="用户名" class="input" />
    <input v-model="password" type="password" placeholder="密码" class="input" />
    <button :disabled="!user_id || !password" @click="login" :class="['button', (!user_id || !password) ? 'button-disabled' : 'button-success']">
      登录
    </button>
    <p class="tip">
      还没有账号？
      <span class="link" @click="navigateTo('/register')">点击前往注册</span>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const apiBase = 'http://localhost:8000'

const router = useRouter()
const auth = useAuthStore()

const user_id = ref('')
const password = ref('')

const login = async () => {
  const formData = new FormData()
  formData.append('user_id', user_id.value)
  formData.append('password', password.value)

  try {
    const res = await $fetch(`${apiBase}/admin/login`, {
      method: 'POST',
      body: formData,
    })

    // 登录成功，保存用户信息和“假token”
    auth.setUser(res, 'dummy-token') // res 包含 username 和 role
    router.push('/')
  } catch (error) {
    // 登录失败（如 401），弹出后端返回的 detail 提示
    alert(error?.data?.detail || '登录失败')
  }
}
</script>


<style scoped>
.container {
  padding: 1.5rem;
  max-width: 400px;
  margin: 0 auto;
}
h2 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}
.input {
  display: block;
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
}
.button {
  width: 100%;
  padding: 0.5rem;
  border-radius: 0.25rem;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}
.button-success {
  background-color: #10b981;
}
.button-success:hover {
  background-color: #059669;
}
.button-disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
.tip {
  margin-top: 1rem;
}
.link {
  color: #10b981;
  cursor: pointer;
}
</style>
