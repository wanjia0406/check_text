<template>
  <div class="box">
    <h2>智能文本检测系统</h2>

    <!-- 文件选择区域 -->
    <div class="upload-area">
      <input 
        type="file" 
        @change="handleFile" 
        accept=".docx,.pdf,.png,.jpg,.jpeg,.bmp,.tiff,.gif"
        class="file-input"
      />
      <label for="file" class="upload-label">
        <span class="upload-icon">📁</span>
        <span>{{ selectedFile ? '重新选择文件' : '点击或拖拽上传文件' }}</span>
      </label>
    </div>

    <!-- 文件信息展示区域 -->
    <div v-if="selectedFile" class="file-info">
      <div class="file-info-header">
        <span class="file-icon">📄</span>
        <h3>已选择的文件</h3>
      </div>
      <div class="file-details">
        <div class="detail-item">
          <span class="detail-label">文件名：</span>
          <span class="detail-value">{{ selectedFile.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">文件大小：</span>
          <span class="detail-value">{{ formatFileSize(selectedFile.size) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">文件类型：</span>
          <span class="detail-value">{{ getFileExtension(selectedFile.name) }}</span>
        </div>
      </div>
      <button class="remove-btn" @click="removeFile">✕ 移除文件</button>
    </div>

    <!-- 上传按钮 -->
    <button 
      @click="upload" 
      :disabled="!selectedFile || isLoading"
      class="upload-btn"
    >
      {{ isLoading ? '处理中...' : '上传并分析' }}
    </button>

    <!-- 进度条区域 -->
    <div v-if="isLoading" class="progress-container">
      <div class="progress-header">
        <span class="progress-title">检测进度</span>
        <span class="progress-percent">{{ progressPercent }}%</span>
      </div>
      <div class="progress-bar-container">
        <div 
          class="progress-bar" 
          :style="{ width: progressPercent + '%' }"
          :class="progressStage"
        ></div>
      </div>
      <p class="progress-message">{{ progressMessage }}</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ errorMessage }}</span>
    </div>
  </div>
</template>

<script>
import { uploadFile } from "../api";

export default {
  name: 'UploadPanel',
  data() {
    return {
      selectedFile: null,
      isLoading: false,
      progressPercent: 0,
      progressMessage: '',
      progressStage: 'uploading', // uploading, processing, completed, error
      errorMessage: ''
    };
  },
  methods: {
    handleFile(e) {
      const file = e.target.files[0];
      if (file) {
        // 检查文件类型
        const validExtensions = ['.docx', '.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'];
        const extension = this.getFileExtension(file.name).toLowerCase();
        
        if (!validExtensions.includes(extension)) {
          this.errorMessage = `不支持的文件类型: ${extension}。支持的类型: ${validExtensions.join(', ')}`;
          this.selectedFile = null;
          return;
        }
        
        // 检查文件大小（限制100MB）
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (file.size > maxSize) {
          this.errorMessage = '文件大小超过限制（最大100MB）';
          this.selectedFile = null;
          return;
        }
        
        this.selectedFile = file;
        this.errorMessage = '';
      }
    },

    removeFile() {
      this.selectedFile = null;
      this.errorMessage = '';
      // 重置文件输入
      const input = document.querySelector('.file-input');
      if (input) {
        input.value = '';
      }
    },

    async upload() {
      if (!this.selectedFile || this.isLoading) return;

      // 重置状态
      this.isLoading = true;
      this.progressPercent = 0;
      this.progressMessage = '准备上传...';
      this.progressStage = 'uploading';
      this.errorMessage = '';

      try {
        // 上传文件，同时显示进度
        const response = await uploadFile(this.selectedFile, (progressData) => {
          // 上传阶段进度
          this.progressPercent = progressData.progress;
          this.progressMessage = progressData.message;
          this.progressStage = progressData.stage;
        });

        // 上传完成，开始处理阶段
        this.progressStage = 'processing';
        this.progressMessage = '正在处理文件...';
        
        // 处理阶段的进度（模拟）
        const processingStages = [
          { progress: 25, message: '正在读取文件内容...' },
          { progress: 40, message: '正在进行文本纠错...' },
          { progress: 55, message: '正在检测参考文献...' },
          { progress: 70, message: '正在检测图片表格...' },
          { progress: 85, message: '正在生成报告...' },
          { progress: 100, message: '处理完成!' }
        ];

        for (const stage of processingStages) {
          await this.sleep(600 + Math.random() * 400); // 模拟处理时间
          this.progressPercent = stage.progress;
          this.progressMessage = stage.message;
        }

        this.progressStage = 'completed';
        
        // 通知父组件处理完成
        this.$emit("result", response.data);
        
      } catch (err) {
        console.error('上传失败:', err);
        this.progressStage = 'error';
        this.errorMessage = err.response?.data?.detail || '上传失败，请检查网络连接后重试';
      } finally {
        // 延迟一点时间让用户看到完成状态
        await this.sleep(500);
        this.isLoading = false;
      }
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    getFileExtension(filename) {
      return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  }
};
</script>

<style scoped>
.box {
  padding: 30px;
  max-width: 500px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 24px;
}

.upload-area {
  margin-bottom: 20px;
}

.file-input {
  display: none;
}

.upload-label {
  display: block;
  padding: 30px;
  border: 2px dashed #ccc;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.upload-label:hover {
  border-color: #4CAF50;
  background-color: #f0f8f0;
}

.upload-icon {
  display: block;
  font-size: 48px;
  margin-bottom: 10px;
}

.file-info {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.file-info-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.file-icon {
  font-size: 24px;
  margin-right: 10px;
}

.file-info-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.file-details {
  margin-bottom: 10px;
}

.detail-item {
  display: flex;
  padding: 5px 0;
}

.detail-label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.detail-value {
  color: #333;
  word-break: break-all;
}

.remove-btn {
  background: #f44336;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.remove-btn:hover {
  background: #d32f2f;
}

.upload-btn {
  width: 100%;
  padding: 15px;
  font-size: 16px;
  font-weight: bold;
  color: white;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.upload-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress-container {
  margin-top: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-title {
  font-weight: 600;
  color: #333;
}

.progress-percent {
  font-weight: bold;
  color: #4CAF50;
  font-size: 18px;
}

.progress-bar-container {
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-bar {
  height: 100%;
  border-radius: 6px;
  transition: width 0.3s ease, background 0.3s ease;
}

.progress-bar.uploading {
  background: linear-gradient(90deg, #2196F3, #1976D2);
}

.progress-bar.processing {
  background: linear-gradient(90deg, #FF9800, #F57C00);
}

.progress-bar.completed {
  background: linear-gradient(90deg, #4CAF50, #388E3C);
}

.progress-bar.error {
  background: linear-gradient(90deg, #f44336, #d32f2f);
}

.progress-message {
  margin: 0;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.error-message {
  margin-top: 15px;
  padding: 12px;
  background: #ffebee;
  border: 1px solid #ef5350;
  border-radius: 4px;
  color: #c62828;
  display: flex;
  align-items: center;
}

.error-icon {
  margin-right: 8px;
}
</style>
