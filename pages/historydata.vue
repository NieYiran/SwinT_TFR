<template>
  <div class="container">
    <h2>历史记录查询</h2>

    <table v-if="records.length" class="history-table">
      <thead>
      <tr>
        <th>用户ID</th>
        <th>时间戳</th>
        <th>操作类型</th>
        <th>记录</th>
        <th>操作</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="record in records" :key="record.timestamp + record.user_id">
        <td>{{ record.user_id }}</td>
        <td>{{ formatTimestamp(record.timestamp) }}</td>
        <td>{{ record.operation }}</td>
        <td>
          <a
            v-if="record.records_base64"
            :href="getDownloadUrl(record.records_base64, record.mime_type)"
            :download="getFilename(record)"
          >
            下载文件
          </a>
        </td>
        <td>
          <button @click="deleteRecord(record.user_id, record.timestamp)">
            删除
          </button>
        </td>
      </tr>
      </tbody>
    </table>

    <p v-else>暂无记录</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const records = ref([])
const userStore = useAuthStore()
const user = computed(() => userStore.user)
const user_id = computed(() => user.value?.username ?? '')
const role = computed(() => user.value?.role ?? 1)
const apiBase = 'http://localhost:8000'

const fetchRecords = async () => {
  try {
    const { data } = await useFetch(`${apiBase}/query-records`, {
      method: 'GET',
      params: {
        user_id: user_id.value,
        role: role.value
      }
    })
    records.value = data.value.records
  } catch (e) {
    console.error('获取记录失败', e)
  }
}

const deleteRecord = async (user_id, timestamp) => {
  if (!confirm('确定删除该记录？')) return

  try {
    const formData = new FormData()
    formData.append('user_id', user_id)
    formData.append('timestamp', timestamp)

    await $fetch(`${apiBase}/delete-record`, {
      method: 'POST',
      body: formData
    })

    await fetchRecords()
  } catch (e) {
    alert('删除失败')
    console.error(e)
  }
}


const formatTimestamp = (ts) => {
  return ts.replace(/(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1-$2-$3 $4:$5:$6')
}

const getDownloadUrl = (base64, mimeType) => {
  const blob = base64ToBlob(base64, mimeType)
  return URL.createObjectURL(blob)
}

const base64ToBlob = (base64, mimeType = 'application/octet-stream') => {
  const binary = atob(base64)
  const array = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    array[i] = binary.charCodeAt(i)
  }
  return new Blob([array], { type: mimeType })
}

const getFilename = (record) => {
  return record.filename || `${record.user_id}_${record.timestamp}.bin`
}

onMounted(fetchRecords)
</script>

<style scoped>
.container {
  max-width: 960px;
  margin: auto;
  padding: 20px;
}
.history-table {
  width: 100%;
  border-collapse: collapse;
}
.history-table th,
.history-table td {
  border: 1px solid #ccc;
  padding: 8px;
}
.btn-del {
  background-color: red;
  color: white;
  border: none;
  padding: 6px 10px;
  cursor: pointer;
}
</style>
