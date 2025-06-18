<template>
  <div class="container">
    <h1 class="title">CSV 文件上传与下载</h1>

    <!-- 文件输入框 -->
    <input
      type="file"
      accept=".csv"
      multiple
      @change="handleFileChange"
      ref="fileInput"
      style="display: none;"
    />

    <!-- 上传按钮 -->
    <div class="upload-section">
      <button class="upload-btn" @click="triggerFileInput">选择CSV文件</button>
      <p class="upload-tip">请选择一个或多个CSV文件上传</p>
    </div>

    <!-- 文件信息 -->
    <div class="file-info" v-if="csvFiles.length > 0">
      <div class="file-label">
        选择的文件：
        <ul>
          <li v-for="(file, index) in csvFiles" :key="index">{{ file.name }}</li>
        </ul>
      </div>
      <div class="file-actions">
        <button class="upload-btn" @click="uploadFile">上传文件</button>
      </div>
    </div>

    <!-- 下载链接 -->
    <div v-if="downloadUrl" class="download-section">
      <p>文件上传成功！</p>
      <a :href="downloadUrl" class="download-btn" download>点击下载</a>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
const user = authStore.user
const user_id = user?.username ?? ''
// 绑定 input 与上传文件
const fileInput = ref<HTMLInputElement | null>(null)
const csvFiles = ref<File[]>([])
const downloadUrl = ref<string | null>(null)

// 打开文件选择框
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件变更事件
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    csvFiles.value = Array.from(target.files)
    console.log('选中文件：', csvFiles.value.map(f => f.name))
  }
}


// 上传文件函数
const uploadFile = async () => {
  if (csvFiles.value.length === 0) {
    alert('请先选择CSV文件')
    return
  }

  const formData = new FormData()
  csvFiles.value.forEach(file => {
    formData.append('files', file)  // 注意这里和后端字段名保持一致
  })

  try {
    const response = await fetch('http://127.0.0.1:8000/upload-csv', {
      method: 'POST',
      body: formData,
    })

    const data = await response.json()

    if (response.ok) {
      const downloadPath = data.download_url
      downloadUrl.value = `http://127.0.0.1:8000${downloadPath}`
      console.log('上传成功，下载地址：', downloadUrl.value)

      // 下载生成的文件为 blob
      const fileResponse = await fetch(downloadUrl.value)
      const blob = await fileResponse.blob()

      // 上传记录
      const recordForm = new FormData()
      recordForm.append('user_id', user_id)
      recordForm.append('operation', 'upload-csv')
      recordForm.append('records', new File([blob], 'result.zip'))

      const recordResponse = await fetch('http://127.0.0.1:8000/upload-record', {
        method: 'POST',
        body: recordForm
      })

      if (!recordResponse.ok) {
        console.warn('历史记录写入失败')
      } else {
        console.log('记录上传成功')
      }

    } else {
      console.error('上传失败:', data)
      alert('上传失败，请检查后台日志')
    }
  } catch (error) {
    console.error('请求失败:', error)
    alert('上传请求失败，请检查网络或后端是否启动')
  }
}
</script>


<style scoped>
.container {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem;
}

.title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 1.5rem;
}

.upload-section {
  text-align: center;
  margin-bottom: 1rem;
}

.upload-btn {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  transition: background-color 0.3s;
}

.upload-btn:hover {
  background-color: #2563eb;
}

.upload-tip {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
}

.file-label {
  font-size: 1rem;
  color: #374151;
}

.file-actions {
  text-align: center;
}

.download-section {
  text-align: center;
  margin-top: 1.5rem;
}

.download-btn {
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: white;
  border-radius: 0.375rem;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #059669;
}
</style>



