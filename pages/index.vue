<template>
  <div class="welcome-container">
    <div class="overlay">
      <h1 class="title">地铁隧道损伤识别系统</h1>
      <p class="subtitle">
        本系统支持上传时频图或原始列车加速度传感器数据，通过深度学习模型自动识别损伤位置与等级。
      </p>
      <div class="button-group">
        <button @click="$router.push('/getpic')">制作时频图</button>
        <button @click="$router.push('/detect')">损伤检测</button>
        <button @click="$router.push('/history')">查看历史记录</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.welcome-container {
  background-image: url('../subway-tunnel.png'); /* 替换为合适的图片路径 */
  background-size: cover;
  background-position: center;
  height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.overlay {
  background: rgba(0, 0, 0, 0.55);
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  max-width: 700px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.6);
}

.title {
  font-size: 2.8rem;
  font-weight: bold;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 1.2rem;
  margin-bottom: 30px;
  line-height: 1.6;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.button-group button {
  background-color: #1e90ff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.button-group button:hover {
  background-color: #3ba0ff;
}

@media (min-width: 640px) {
  .button-group {
    flex-direction: row;
    justify-content: center;
  }
}
</style>

