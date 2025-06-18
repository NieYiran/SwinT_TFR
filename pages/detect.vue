<template>
  <div class="container">
    <h1 class="title">隧道损伤检测分析</h1>

    <div class="grid-area">
      <!-- 文件输入框 -->
      <input type="file" accept="image/*" @change="handleFileChange($event, 'A')" ref="fileInputA" style="display: none;" />
      <input type="file" accept="image/*" @change="handleFileChange($event, 'B')" ref="fileInputB" style="display: none;" />
      <input type="file" accept="image/*" @change="handleFileChange($event, 'C')" ref="fileInputC" style="display: none;" />

      <!-- 上传按钮 -->
      <div class="upload-section">
        <button class="upload-btn" @click="selectZone">选择时频图</button>
        <p class="upload-tip">依次上传 A/B/C 区段图像</p>
      </div>

      <!-- 文件名 + 操作按钮 -->
      <div class="file-info">
        <div v-for="zone in zones" :key="zone" class="file-row">
          <div class="file-label">
            {{ zone }} 区段：
            <span v-if="imageFiles[zone]">{{ imageFiles[zone]?.name }}</span>
            <span v-else class="file-placeholder">未上传</span>
          </div>
          <div v-if="imageFiles[zone]">
            <button class="preview-btn" @click="previewImage = imageUrls[zone]">查看</button>
            <button class="delete-btn" @click="removeImage(zone)">删除</button>
          </div>
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="submit-btn-box">
        <button class="submit-btn" :disabled="!canSubmit" @click="analyzeImages">
          开始检测
        </button>
      </div>
    </div>
    <!-- 模型分析结果 -->
    <div class="result-box">
      <div class="result-title">模型分析结果</div>

      <!-- 结果显示部分 -->
      <div class="result-container">
        <div v-if="result && result.length" class="result-grid">
          <div v-for="(res, index) in result" :key="index" class="result-column">
            <p><strong>位置：</strong> {{ res.location }}</p>
            <div>
              <p v-for="(probability, level) in res.result" :key="level">
                {{ level }}级：概率{{ probability.toFixed(4) }}
              </p>
            </div>
            <!-- 显示初步结论 -->
            <p>
              <strong>初步结论：</strong>
              {{ res.location }}位置{{ getMaxLevel(res.result) }}级
            </p>
          </div>
        </div>
        <!-- 综合结论显示 -->
        <div v-if="mostLikelyDamage" class="final-result">
          <p><strong>综合结论：</strong> 最有可能的损伤位置是「{{ mostLikelyDamage.location }}」，损伤等级为 {{ mostLikelyDamage.level }} 级（概率 {{ mostLikelyDamage.probability.toFixed(4) }}）</p>
        </div>
      </div>
    </div>
    <!-- 浮动预览窗口 -->
    <Teleport to="body">
      <div v-if="previewImage" class="overlay" @click.self="previewImage = null">
        <div class="preview-window">
          <button class="close-btn" @click="previewImage = null">✖</button>
          <img :src="previewImage" class="preview-img" />
        </div>
      </div>
    </Teleport>
  </div>
</template>


<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import {useAuthStore} from "~/stores/auth";
const authStore = useAuthStore()
const user = authStore.user
const user_id = user?.username ?? ''

const zones = ['A', 'B', 'C']
const fileInputA = ref<HTMLInputElement | null>(null)
const fileInputB = ref<HTMLInputElement | null>(null)
const fileInputC = ref<HTMLInputElement | null>(null)

const imageFiles = ref<Record<string, File | null>>({ A: null, B: null, C: null })
const imageUrls = ref<Record<string, string | null>>({ A: null, B: null, C: null })

const previewImage = ref<string | null>(null)
const result = ref<{ location: string; result: any }[] | null>(null)

const canSubmit = computed(() => zones.every((zone) => imageFiles.value[zone] !== null))

const selectZone = () => {
  const nextZone = zones.find((zone) => !imageFiles.value[zone])
  if (nextZone === 'A') fileInputA.value?.click()
  else if (nextZone === 'B') fileInputB.value?.click()
  else if (nextZone === 'C') fileInputC.value?.click()
  else alert('已上传全部图片')
}

const handleFileChange = (event: Event, zone: string) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    imageFiles.value[zone] = target.files[0]
    imageUrls.value[zone] = URL.createObjectURL(target.files[0])
    result.value = null
  }
  target.value = '' // ← 关键代码，强制清空 input 的值
}

const removeImage = (zone: string) => {
  imageFiles.value[zone] = null
  imageUrls.value[zone] = null
  result.value = null
}

const analyzeImages = async () => {
  const formData = new FormData()
  zones.forEach(zone => {
    const file = imageFiles.value[zone]
    if (file) {
      formData.append(zone, file)
    }
  })

  try {
    const response = await axios.post('http://127.0.0.1:8000/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const documents = response.data.documents
    result.value = documents.map((doc: any) => ({
      location: doc.location,
      result: doc.result,
    }))

    // 👉 将结果保存为 Blob 文件（.json）
    const jsonContent = JSON.stringify(documents, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const jsonFile = new File([blob], 'detect_result.json', { type: 'application/json' })

    // 📤 构造上传记录的 FormData
    const recordForm = new FormData()
    recordForm.append('user_id', user_id)
    recordForm.append('operation', 'detect')
    recordForm.append('records', jsonFile)

    await axios.post('http://127.0.0.1:8000/upload-record', recordForm, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

  } catch (error) {
    console.error('Error during image analysis or upload record:', error)
  }
}


const getMaxLevel = (result: Record<string, number>) => {
  // 找出概率最大的等级
  const maxLevel = Object.entries(result)
    .reduce((max, [level, probability]) => {
      return probability > max.probability ? { level, probability } : max;
    }, { level: '', probability: -Infinity });

  return maxLevel.level;  // 返回最大概率对应的级别
}


const mostLikelyDamage = computed(() => {
  if (!result.value || !result.value.length) return null
  let highestLevel = -1
  let mostLikely = {
    location: '',
    level: '',
    probability: 0,
  }
  result.value.forEach((res) => {
    const entries = Object.entries(res.result as Record<string, number>)
    for (const [levelStr, probability] of entries) {
      const level = parseInt(levelStr)
      if (probability > 0 && level > highestLevel) {
        highestLevel = level
        mostLikely = {
          location: res.location,
          level: levelStr,
          probability,
        }
      }
    }
  })
  return mostLikely
})


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
.grid-area {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 768px) {
  .grid-area {
    grid-template-columns: repeat(3, 1fr);
  }
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
  gap: 0.5rem;
}
.file-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #e5e7eb;
  padding-top: 0.5rem;
}
.file-placeholder {
  color: #9ca3af;
}
.file-label {
  color: #374151;
  font-size: 0.875rem;
}
.preview-btn {
  color: #3b82f6;
  margin-right: 0.5rem;
}
.preview-btn:hover {
  text-decoration: underline;
}
.delete-btn {
  color: #ef4444;
}
.delete-btn:hover {
  text-decoration: underline;
}

/* 模型分析结果区域 */
.result-box {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  margin-top: 2rem; /* 将结果框移到下方 */
  height: 350px; /* 设置固定高度 */
  overflow-y: auto; /* 内容超出时显示滚动条 */
}
.result-title {
  font-weight: 600;
  font-size: 1.125rem;
  margin-bottom: 1rem;
}
.result-container {
  margin-top: 1rem;
}
.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr; /* 三栏布局 */
  gap: 1.5rem;
}
.result-column {
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.submit-btn-box {
  text-align: center;
  margin-bottom: 1rem;
}
.submit-btn {
  padding: 0.5rem 1.5rem;
  background-color: #10b981;
  color: white;
  border-radius: 0.375rem;
  transition: background-color 0.3s;
}
.submit-btn:hover {
  background-color: #059669;
}
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 悬浮图片预览窗口样式 */
.overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-window {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: relative;
  max-width: 768px;
  max-height: 80vh;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}
.preview-img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 0.25rem;
}
.close-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.75rem;
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1.25rem;
  cursor: pointer;
}
.close-btn:hover {
  color: #ef4444;
}
.final-result {
  background-color: #fef3c7;
  padding: 12px;
  border: 1px solid #facc15;
  border-radius: 8px;
  margin-top: 16px;
  font-weight: bold;
}
</style>



