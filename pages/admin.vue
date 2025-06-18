<template>
  <div class="container">
    <h2>用户管理（管理员）</h2>
    <div class="form-row">
      <input v-model="newUserId" placeholder="用户ID" class="input" />
      <input v-model="newPassword" type="password" placeholder="密码" class="input" />
      <select v-model.number="newRole" class="select">
        <option :value="1">普通用户</option>
        <option :value="0">管理员</option>
      </select>
      <button @click="addUser" class="btn-add">添加用户</button>
    </div>

    <table class="user-table" v-if="users.length">
      <thead>
      <tr>
        <th>用户ID</th>
        <th>角色</th>
        <th>操作</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="user in users" :key="user.user_id || user._id || user.id || user">
        <td>{{ user.user_id || '未知ID' }}</td>
        <td>{{ user.role === 0 ? '管理员' : '普通用户' }}</td>
        <td>
          <button
            @click="deleteUser(user.user_id)"
            class="btn-del"
            :disabled="user.user_id === 'admin'"
          >删除</button>
        </td>
      </tr>
      </tbody>
    </table>

    <p v-else>暂无用户数据</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const newUserId = ref('')
const newPassword = ref('')
const newRole = ref(1)
const current_user = 'admin' // 可替换为登录用户变量

const apiBase = 'http://localhost:8000'

const fetchUsers = async () => {
  try {
    const res = await axios.get(`${apiBase}/admin/users`, {
      params: { current_user }
    })
    console.log('接口返回数据:', res.data)  // <-- 这里加打印

    if (Array.isArray(res.data)) {
      users.value = res.data
    } else if (res.data && Array.isArray(res.data.data)) {
      // 如果接口返回被包了一层data字段
      users.value = res.data.data
    } else {
      console.error('接口返回数据格式不正确:', res.data)
      users.value = []
    }
  } catch (err) {
    console.error('获取用户失败:', err)
    users.value = []
  }
}

const addUser = async () => {
  try {
    await axios.post(
      `${apiBase}/admin/users`,
      new URLSearchParams({
        user_id: newUserId.value,
        password: newPassword.value,
        role: newRole.value,
        current_user
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    await fetchUsers()
    newUserId.value = ''
    newPassword.value = ''
    newRole.value = 1
  } catch (err) {
    alert('添加失败：' + (err.response?.data?.detail || '未知错误'))
  }
}

const deleteUser = async (user_id) => {
  if (!confirm(`确认删除用户 ${user_id}？`)) return
  try {
    await axios.delete(`${apiBase}/admin/users/${user_id}`, {
      params: { current_user }
    })
    await fetchUsers()
  } catch (err) {
    alert('删除失败：' + (err.response?.data?.detail || '未知错误'))
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.container {
  padding: 1rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.form-row {
  margin-bottom: 1rem;
  display: flex;
  gap: 0.5rem;
}

.input {
  border: 1px solid #d1d5db; /* gray-300 */
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  flex: 1 1 auto;
}

.select {
  border: 1px solid #d1d5db;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  width: 120px;
}

.btn-add {
  background-color: #22c55e; /* green-500 */
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
}

.btn-add:hover {
  background-color: #16a34a; /* green-600 */
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #d1d5db; /* gray-300 */
  table-layout: fixed;
}

.user-table thead tr {
  background-color: #f3f4f6; /* gray-100 */
}

.user-table th,
.user-table td {
  border: 1px solid #d1d5db;
  padding: 0.5rem;
  text-align: left;
  word-break: break-word;
}

.btn-del {
  background-color: #ef4444; /* red-500 */
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
}

.btn-del:disabled {
  background-color: #fca5a5; /* red-300 */
  cursor: not-allowed;
}

.btn-del:hover:not(:disabled) {
  background-color: #dc2626; /* red-600 */
}
</style>

