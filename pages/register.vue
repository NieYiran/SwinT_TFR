<template>
  <div class="container">
    <h2>注册</h2>
    <input v-model="user_id" type="text" placeholder="用户名" class="input" />
    <input v-model="password" type="password" placeholder="密码" class="input" />
    <button :disabled="!user_id || !password" @click="register" :class="['button', (!user_id || !password) ? 'button-disabled' : 'button-primary']">
      注册
    </button>
    <p class="tip">
      用户已注册？
      <span class="link" @click="navigateTo('/login')">点击前往登录</span>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user_id = ref('')
const password = ref('')

const apiBase = 'http://localhost:8000'

const register = async () => {
  const formData = new FormData()
  formData.append('user_id', user_id.value)
  formData.append('password', password.value)

  const res = await $fetch(`${apiBase}/admin/regist`, {
    method: 'POST',
    body: formData,
  })

  if (res === 1) {
    alert('注册成功，请登录')
    router.push('/login')
  } else {
    alert('用户名已存在，请重新输入')
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
.button-primary {
  background-color: #3b82f6;
}
.button-primary:hover {
  background-color: #2563eb;
}
.button-disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
.tip {
  margin-top: 1rem;
}
.link {
  color: #3b82f6;
  cursor: pointer;
}
</style>

