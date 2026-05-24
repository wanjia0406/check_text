<template>
  <div class="app-container">
    <!-- 详情页面 -->
    <ErrorDetail
      v-if="showDetail"
      :result="result"
      :fileName="selectedFile?.name || '未命名文档'"
      :checkType="currentCheckType"
      :originalFile="selectedFile"
      @back="showDetail = false"
      @file-fixed="handleFileFixed"
    />
    
    <!-- 主页面 -->
    <div v-else>
      <!-- 顶部导航栏 -->
      <header class="header">
        <div class="header-left">
          <h1>智能文本检测与格式批注系统</h1>
        </div>
        <div class="header-right">
          <button class="btn btn-secondary" @click="exportReport">
            <i class="icon">📄</i> 导出报告
          </button>
        </div>
      </header>

      <div class="main-content">
        <!-- 左侧导航栏 -->
        <aside class="sidebar">
          <div class="sidebar-section">
            <h3>检测功能</h3>
            <ul>
              <li 
                :class="{ active: currentCheckType === 'text' }"
                @click="switchCheckType('text')"
              >
                <i class="icon">📝</i> 文本错误检测
              </li>
              <li 
                :class="{ active: currentCheckType === 'reference' }"
                @click="switchCheckType('reference')"
              >
                <i class="icon">📚</i> 参考文献校验
              </li>
              <li 
                :class="{ active: currentCheckType === 'image' }"
                @click="switchCheckType('image')"
              >
                <i class="icon">📊</i> 图表与表格检查
              </li>
            </ul>
          </div>
          
          <div class="sidebar-section">
            <h3>结果管理</h3>
            <ul>
              <li 
                :class="{ active: currentCheckType === 'annotation' }"
                @click="switchCheckType('annotation')"
              >
                <i class="icon">📝</i> 批注列表
              </li>
              <li 
                :class="{ active: currentCheckType === 'report' }"
                @click="switchCheckType('report')"
              >
                <i class="icon">📊</i> 统计报告
              </li>
            </ul>
          </div>
        </aside>

        <!-- 主内容区域 -->
        <main class="content">
          <!-- 批注列表 -->
          <AnnotationList 
            v-if="currentCheckType === 'annotation'"
            :annotations="annotations"
            @update-annotation="updateAnnotation"
            @delete-annotation="deleteAnnotation"
            @refresh="loadAnnotations"
          />
          
          <!-- 统计报告 -->
          <StatisticsReport 
            v-else-if="currentCheckType === 'report'"
            :report-data="reportData"
            @generate="generateReport"
          />
          
          <!-- 检测功能 -->
          <template v-else>
          <!-- 上传区域 -->
        <div class="upload-section">
          <div 
            class="upload-area" 
            @dragover.prevent 
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input 
              type="file" 
              ref="fileInput" 
              style="display: none" 
              @change="handleFileChange"
              accept=".docx,.pdf,.txt"
            />
            <i class="upload-icon">📁</i>
            <p>上传文件或拖放文件到此处</p>
            <p class="upload-hint">目前支持Word、PDF格式</p>
          </div>

          <!-- 检测进度 -->
          <div class="progress-section" v-if="progress > 0">
            <div class="progress-info">
              <span>检测进度:</span>
              <span>{{ progress }}%</span>
            </div>
            <div v-if="detectionMessage" class="progress-message">{{ detectionMessage }}</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button 
              class="btn btn-primary" 
              @click="startDetection"
              :disabled="!selectedFile"
            >
              <i class="icon">▶</i> 开始检测
            </button>
          </div>

          <!-- 文件信息展示区域 -->
          <div v-if="fileInfo" class="file-info-section">
            <h3>📄 文档信息</h3>
            <div class="file-info-grid">
              <div class="file-info-item">
                <span class="file-info-label">文件名:</span>
                <span class="file-info-value">{{ fileInfo.filename }}</span>
              </div>
              <div class="file-info-item">
                <span class="file-info-label">文件类型:</span>
                <span class="file-info-value">{{ fileInfo.type }}</span>
              </div>
              <div class="file-info-item">
                <span class="file-info-label">文件大小:</span>
                <span class="file-info-value">{{ fileInfo.size_formatted }}</span>
              </div>
              <div class="file-info-item">
                <span class="file-info-label">文件格式:</span>
                <span class="file-info-value">{{ fileInfo.extension }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 检测结果 -->
        <div class="result-section">
          <h2>检测结果</h2>
          <div v-if="!result" class="no-result">
            <i class="no-result-icon">💬</i>
            <p>请上传文档开始检测</p>
          </div>
          
          <div v-else class="result-content">
            <!-- 统计信息 -->
            <div class="result-stats">
              <template v-if="currentCheckType === 'image' && result">
                <div class="stat-item">
                  <span class="stat-label">图片数量:</span>
                  <span class="stat-value image">{{ result.image_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">表格数量:</span>
                  <span class="stat-value table">{{ result.table_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">检测问题:</span>
                  <span class="stat-value total">{{ result.total_errors || 0 }}</span>
                </div>
              </template>
              <template v-else-if="currentCheckType === 'image' && !result">
                <div class="stat-item">
                  <span class="stat-label">图片数量:</span>
                  <span class="stat-value image">0</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">表格数量:</span>
                  <span class="stat-value table">0</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">检测问题:</span>
                  <span class="stat-value total">0</span>
                </div>
              </template>
              <template v-else-if="currentCheckType === 'reference'">
                <div class="stat-item">
                  <span class="stat-label">参考文献错误:</span>
                  <span class="stat-value warning">{{ mergedErrors.filter(e => e.type === 'reference').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">提取文献数:</span>
                  <span class="stat-value success">{{ result?.references?.length || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总错误:</span>
                  <span class="stat-value total">{{ displayedErrors.length }}</span>
                </div>
              </template>
              <template v-else>
                <div class="stat-item">
                  <span class="stat-label">错别字:</span>
                  <span class="stat-value error">{{ mergedErrors.filter(e => e.type === 'spell').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">语法错误:</span>
                  <span class="stat-value grammar">{{ mergedErrors.filter(e => e.type === 'grammar').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">语义错误:</span>
                  <span class="stat-value danger">{{ mergedErrors.filter(e => e.type === 'semantic').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">图表错误:</span>
                  <span class="stat-value image">{{ mergedErrors.filter(e => e.type === 'image').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">表格错误:</span>
                  <span class="stat-value table">{{ mergedErrors.filter(e => e.type === 'table').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">参考文献错误:</span>
                  <span class="stat-value warning">{{ mergedErrors.filter(e => e.type === 'reference').length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总错误:</span>
                  <span class="stat-value total">{{ mergedErrors.length }}</span>
                </div>
              </template>
            </div>

            <!-- 参考文献列表 -->
            <div v-if="currentCheckType === 'reference' && result && result.references && result.references.length > 0" class="reference-list">
              <div class="reference-list-header">
                <h3>提取的参考文献</h3>
                <span class="reference-count">共 {{ result.references.length }} 条</span>
              </div>
              <div class="reference-list-content">
                <div 
                  v-for="(ref, index) in result.references" 
                  :key="index" 
                  class="reference-item"
                >
                  <span class="reference-index">{{ index + 1 }}.</span>
                  <span class="reference-text">{{ ref }}</span>
                </div>
              </div>
            </div>

            <!-- 查看详情按钮 - 图表与表格检查 -->
            <div v-if="currentCheckType === 'image' && result" class="action-section" style="margin-bottom: 1rem;">
              <button class="btn btn-primary btn-block" @click="showDetail = true">
                <i class="icon">🔍</i> 查看详情
              </button>
            </div>

            <!-- 详细错误列表 -->
            <div v-if="currentCheckType !== 'image' && displayedErrors.length > 0" class="error-list">
              <div class="error-list-header">
                <h3>详细错误</h3>
                <div class="error-list-actions">
                  <button 
                    class="btn btn-sm btn-primary" 
                    @click="showDetail = true"
                    :disabled="!result"
                  >
                    <i class="icon">🔍</i> 查看详情
                  </button>
                </div>
              </div>
              
              <div class="error-list-content">
                <div v-if="displayedErrors.length === 0" class="no-errors">
                  <i class="icon">✅</i>
                  <p>未检测到错误</p>
                </div>
                <div 
                  v-for="(error, index) in displayedErrors.slice(0, 5)" 
                  :key="index" 
                  class="error-item"
                >
                  <div class="error-header">
                    <span class="error-type" :class="error.type">{{ getErrorTypeLabel(error.type) }}</span>
                    <span class="error-position">位置: {{ error.pos || '未知' }}</span>
                  </div>
                  
                  <div class="error-content">
                    <div class="error-text">
                      <span class="label">错误:</span>
                      <span class="text-error">{{ error.error }}</span>
                    </div>
                    <div v-if="error.correct" class="suggestion-text">
                      <span class="label">建议:</span>
                      <span class="text-success">{{ error.correct }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="displayedErrors.length > 5" class="more-errors">
                  <p>还有 {{ displayedErrors.length - 5 }} 个错误，<button @click="showDetail = true" class="link-btn">点击查看全部</button></p>
                </div>
              </div>
            </div>

            <!-- 图表与表格问题列表 -->
            <div v-if="currentCheckType === 'image' && displayedErrors.length > 0" class="error-list">
              <div class="error-list-header">
                <h3>检测到的问题</h3>
                <div class="error-list-actions">
                  <button 
                    class="btn btn-sm btn-primary" 
                    @click="showDetail = true"
                  >
                    <i class="icon">🔍</i> 查看详情
                  </button>
                </div>
              </div>
              
              <div class="error-list-content">
                <div 
                  v-for="(error, index) in displayedErrors.slice(0, 10)" 
                  :key="index" 
                  class="error-item"
                >
                  <div class="error-header">
                    <span class="error-type" :class="error.type">{{ getErrorTypeLabel(error.type) }}</span>
                  </div>
                  <div class="error-content">
                    <div class="error-text">
                      <span class="text-error">{{ error.error }}</span>
                    </div>
                    <div v-if="error.correct" class="suggestion-text">
                      <span class="label">建议:</span>
                      <span class="text-success">{{ error.correct }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="displayedErrors.length > 10" class="more-errors">
                  <p>还有 {{ displayedErrors.length - 10 }} 个问题，<button @click="showDetail = true" class="link-btn">点击查看全部</button></p>
                </div>
              </div>
            </div>

            <!-- 无内容提示 -->
            <div v-if="currentCheckType === 'image' && result && result.image_count === 0 && result.table_count === 0" class="no-content">
              <i class="icon">📭</i>
              <p>未在文档中发现图片或表格</p>
            </div>

            <!-- 操作按钮 -->
            <div class="action-section">
              <button class="btn btn-secondary" @click="downloadResult">
                <i class="icon">📥</i> 下载修复文档
              </button>
              <button 
                class="btn btn-primary" 
                @click="generateCorrectedDocument"
                :disabled="!hasReplaceableErrors"
              >
                <i class="icon">✨</i> 生成修正版文档
              </button>
            </div>
          </div>
        </div>
          </template>
      </main>

      <!-- 右侧检测结果面板 -->
      <aside class="right-panel">
        <h3>检测结果</h3>
        
        <!-- 图表展示 - 始终显示容器以便初始化 -->
        <div class="chart-container">
          <h4>错误分布</h4>
          <div ref="chart" style="width: 100%; height: 200px;"></div>
        </div>
        
        <!-- 快捷操作 -->
        <div class="quick-actions">
          <h4>快捷操作</h4>
          <button 
            class="btn btn-block btn-primary" 
            @click="replaceAllErrors"
            :disabled="!hasReplaceableErrors"
          >
            一键替换全部错误
          </button>
          <button 
            class="btn btn-block btn-secondary" 
            @click="downloadResult"
          >
            下载修复文档
          </button>
        </div>
      </aside>
      </div>
    </div>
  </div>
</template>

<script>
import { uploadFile, downloadFile, downloadFixedFile, getFileInfo, checkTextErrors, checkReferences, checkImages, fixAllErrors } from "./api";
import { parseDetails, mergeParsedErrors, filterMergedByCheckType } from "./utils/detailParsing";
import * as echarts from "echarts";
import ErrorDetail from "./components/ErrorDetail.vue";
import AnnotationList from "./components/AnnotationList.vue";
import StatisticsReport from "./components/StatisticsReport.vue";

export default {
  components: {
    ErrorDetail,
    AnnotationList,
    StatisticsReport
  },
  data() {
    return {
      selectedFile: null,
      result: null,
      progress: 0,
      detectionMessage: '',
      chartInstance: null,
      showDetail: false,
      currentCheckType: 'text', // text, reference, image, table, annotation, report
      fileInfo: null,
      annotations: [],
      reportData: {
        totalErrors: 0,
        spellErrors: 0,
        grammarErrors: 0,
        semanticErrors: 0,
        referenceErrors: 0,
        imageErrors: 0,
        tableErrors: 0,
        correctedCount: 0,
        documentCount: 0,
        averageErrorRate: 0,
        errorDensity: 0,
        correctionRate: 0
      }
    };
  },
  computed: {
    parsedErrors() {
      if (!this.result || !this.result.details) return [];
      return parseDetails(this.result.details).map((row) => ({
        ...row,
        error: this.cleanErrorData(row.error),
        correct: this.cleanErrorData(row.correct),
        message: this.cleanErrorData(row.message),
      }));
    },

    mergedErrors() {
      return mergeParsedErrors(this.parsedErrors);
    },
    displayedErrors() {
      return filterMergedByCheckType(this.mergedErrors, this.currentCheckType);
    },
    hasReplaceableErrors() {
      return this.parsedErrors.some(err => err.correct);
    }
  },
  mounted() {
    this.initChart();
    // 监听窗口大小变化，确保图表自适应
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
    window.removeEventListener('resize', this.handleResize);
  },
  watch: {
    result: {
      handler(newResult) {
        if (newResult) {
          this.updateChart();
        }
      },
      deep: true
    },
    currentCheckType(newType) {
      if (newType !== 'annotation' && newType !== 'report') {
        this.$nextTick(() => {
          if (this.chartInstance) {
            this.chartInstance.resize();
          } else if (this.result) {
            this.initChart();
          }
        });
      }
    }
  },
  methods: {
    cleanErrorData(text) {
      if (!text) return '';
      let result = text;

      result = result.replace(/style\s*=\s*["'][^"']*(?:background-color[^"']*#fff2f0|color[^"']*#d93026|cursor[^"']*pointer)[^"']*["']/gi, '');
      result = result.replace(/style\s*=\s*'[^']*(?:background-color[^']*#fff2f0|color[^']*#d93026|cursor[^']*pointer)[^']*'/gi, '');

      result = result.replace(/background-color\s*:\s*#fff2f0/gi, '');
      result = result.replace(/color\s*:\s*#d93026/gi, '');
      result = result.replace(/cursor\s*:\s*pointer/gi, '');

      result = result.replace(/(?<!<)\s*["']+\s*(?!>)/g, '');

      result = result.replace(/<[^>]*>/g, '');
      result = result.replace(/\s*\w+\s*=\s*["'][^"']*["']/gi, '');
      result = result.replace(/\s+/g, ' ').trim();

      return result;
    },

    getErrorTypeLabel(type) {
      const labels = {
        'spell': '错别字',
        'grammar': '语法错误',
        'semantic': '语义错误',
        'text': '文本错误',
        'reference': '参考文献',
        'image': '图表错误',
        'table': '表格错误',
        'unknown': '其他错误'
      };
      return labels[type] || type;
    },

    switchCheckType(type) {
      this.currentCheckType = type;
      this.progress = 0;
      
      if (type === 'annotation') {
        this.loadAnnotations();
      } else if (type === 'report') {
        this.loadReportData();
      }
    },
    
    loadAnnotations() {
      const stored = localStorage.getItem('annotations');
      if (stored) {
        this.annotations = JSON.parse(stored);
      } else {
        this.annotations = [];
      }
    },
    
    updateAnnotation({ index, annotation }) {
      this.annotations[index] = annotation;
      localStorage.setItem('annotations', JSON.stringify(this.annotations));
    },
    
    deleteAnnotation(index) {
      this.annotations.splice(index, 1);
      localStorage.setItem('annotations', JSON.stringify(this.annotations));
    },
    
    generateAnnotationsFromResult() {
      if (!this.result || !this.displayedErrors) return;
      
      const fileName = this.selectedFile?.name || '未知文件';
      const newAnnotations = this.displayedErrors.map(err => ({
        error: err.error || '',
        correct: Array.isArray(err.corrections) ? err.corrections[0] : (err.correct || ''),
        type: err.type || 'spell',
        message: Array.isArray(err.messages) ? err.messages[0] : (err.message || ''),
        position: err.pos || '未知位置',
        filename: fileName,
        createdAt: new Date().toISOString()
      }));
      
      this.annotations = [...this.annotations, ...newAnnotations];
      localStorage.setItem('annotations', JSON.stringify(this.annotations));
    },
    
    loadReportData() {
      const currentReport = this.result?.report || {};
      const history = JSON.parse(sessionStorage.getItem('detectionHistory') || '[]');
      const lastEntry = history.length > 0 ? history[history.length - 1] : null;
      const spellErrors = currentReport['错别字'] || currentReport['spellErrors'] || (lastEntry ? lastEntry.spellErrors : 0) || 0;
      const grammarErrors = currentReport['语法错误'] || currentReport['grammarErrors'] || (lastEntry ? lastEntry.grammarErrors : 0) || 0;
      const semanticErrors = currentReport['语义错误'] || currentReport['semanticErrors'] || 0;
      const referenceErrors = currentReport['参考文献错误'] || currentReport['referenceErrors'] || (lastEntry ? lastEntry.referenceErrors : 0) || 0;
      const imageErrors = currentReport['图表错误'] || currentReport['imageErrors'] || (lastEntry ? lastEntry.imageErrors : 0) || 0;
      const tableErrors = currentReport['表格错误'] || currentReport['tableErrors'] || (lastEntry ? lastEntry.tableErrors : 0) || 0;
      const totalErrors = currentReport['总错误'] || currentReport['totalErrors'] || (lastEntry ? lastEntry.totalErrors : 0) || (spellErrors + grammarErrors + semanticErrors + referenceErrors + imageErrors + tableErrors);

      const originalText = this.result?.original_text || '';
      const textLength = originalText.length || 1;

      // 当前文档的已修正数
      const currentCorrected = lastEntry ? (lastEntry.correctedCount || 0) : 0;

      this.reportData = {
        totalErrors: totalErrors,
        spellErrors: spellErrors,
        grammarErrors: grammarErrors,
        semanticErrors: semanticErrors,
        referenceErrors: referenceErrors,
        imageErrors: imageErrors,
        tableErrors: tableErrors,
        correctedCount: currentCorrected,
        documentCount: 1,
        averageErrorRate: totalErrors,
        errorDensity: parseFloat((totalErrors / (textLength / 1000 + 1)).toFixed(1)),
        correctionRate: totalErrors > 0 ? parseFloat(((currentCorrected / totalErrors) * 100).toFixed(1)) : 0
      };
    },
    
    generateReport() {
      this.loadReportData();
    },

    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    
    async handleFileChange(e) {
      this.selectedFile = e.target.files[0];
      this.result = null;
      this.fileInfo = null;
      
      if (this.selectedFile) {
        try {
          const response = await getFileInfo(this.selectedFile);
          this.fileInfo = response.data;
        } catch (error) {
          console.error('获取文件信息失败:', error);
        }
      }
    },
    
    async handleDrop(e) {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.selectedFile = files[0];
        this.result = null;
        this.fileInfo = null;
        
        try {
          const response = await getFileInfo(this.selectedFile);
          this.fileInfo = response.data;
        } catch (error) {
          console.error('获取文件信息失败:', error);
        }
      }
    },
    
    async startDetection() {
      if (!this.selectedFile) return;
      
      this.progress = 0;
      this.result = null;
      this.detectionMessage = '准备开始检测...';
      
      try {
        let response;
        const stages = [
          { progress: 10, message: '正在初始化检测...' },
          { progress: 25, message: '正在上传文件...' },
          { progress: 40, message: '正在解析文档...' },
          { progress: 55, message: '正在进行文本纠错...' },
          { progress: 70, message: '正在检测语法语义错误...' },
          { progress: 85, message: '正在生成报告...' },
          { progress: 95, message: '正在整理结果...' }
        ];
        
        // 逐步显示进度
        let stageIndex = 0;
        const progressInterval = setInterval(() => {
          if (stageIndex < stages.length) {
            this.progress = stages[stageIndex].progress;
            this.detectionMessage = stages[stageIndex].message;
            stageIndex++;
          }
        }, 200);
        
        switch(this.currentCheckType) {
          case 'text':
            // 文本错误检测 - 执行完整检测（包含所有检测项）
            response = await uploadFile(this.selectedFile);
            break;
          case 'reference':
            // 参考文献校验 - 单独检测
            response = await checkReferences(this.selectedFile);
            break;
          case 'image':
            // 图表与表格检查 - 专门检测
            response = await checkImages(this.selectedFile);
            break;
          default:
            response = await uploadFile(this.selectedFile);
        }
        
        // 清除进度间隔
        clearInterval(progressInterval);
        
        // 完成阶段
        this.progress = 100;
        this.detectionMessage = '检测完成！';
        
        // 设置结果
        this.result = response.data;

        // 累计：检测文档计数（sessionStorage：刷新页面后重置）
        const storedCount = sessionStorage.getItem('detectedDocCount');
        const currentCount = storedCount ? parseInt(storedCount) : 0;
        sessionStorage.setItem('detectedDocCount', currentCount + 1);

        // 累计：总检测错误数
        const stored = sessionStorage.getItem('reportStats');
        const stats = stored ? JSON.parse(stored) : { totalDetectedErrors: 0, totalCorrected: 0 };
        const currentErrorCount = (response.data?.errors || []).length;
        stats.totalDetectedErrors = (stats.totalDetectedErrors || 0) + currentErrorCount;
        sessionStorage.setItem('reportStats', JSON.stringify(stats));

        // 记录检测历史（用于趋势图，保留最近30条）
        const report = response.data?.report || {};
        const historyEntry = {
          time: new Date().toLocaleString('zh-CN'),
          timestamp: Date.now(),
          totalErrors: report['总错误'] || report['totalErrors'] || currentErrorCount,
          spellErrors: report['错别字'] || report['spellErrors'] || 0,
          grammarErrors: report['语法错误'] || report['grammarErrors'] || 0,
          referenceErrors: report['参考文献错误'] || report['referenceErrors'] || 0,
          imageErrors: report['图表错误'] || report['imageErrors'] || 0,
          tableErrors: report['表格错误'] || report['tableErrors'] || 0,
          filename: this.selectedFile?.name || '',
          correctedCount: 0
        };
        const history = JSON.parse(sessionStorage.getItem('detectionHistory') || '[]');
        history.push(historyEntry);
        if (history.length > 30) history.splice(0, history.length - 30);
        sessionStorage.setItem('detectionHistory', JSON.stringify(history));
        
        // 自动生成批注
        this.generateAnnotationsFromResult();
        
        setTimeout(() => {
          this.progress = 0;
          this.detectionMessage = '';
        }, 2000);
        
      } catch (error) {
        console.error('检测失败:', error);
        alert('检测失败，请重试');
        this.progress = 0;
        this.detectionMessage = '';
      }
    },
    
    downloadResult() {
      if (this.result && this.result.file_id && this.result.original_filename) {
        const images = this.result.images || [];
        const tables = this.result.tables || [];
        downloadFixedFile(this.result.file_id, this.result.original_filename, images, tables);
      }
    },

    handleFileFixed({ fileId, filename, originalFilename, correctedCount }) {
      console.log('[App] 文件已修正:', fileId, filename, originalFilename);
      this.result = {
        ...this.result,
        file_id: fileId,
        original_filename: originalFilename  // 使用原始文件名，不要改！
      };
      // 更新历史记录中的修正数
      if (correctedCount !== undefined && correctedCount > 0) {
        const history = JSON.parse(sessionStorage.getItem('detectionHistory') || '[]');
        if (history.length > 0) {
          history[history.length - 1].correctedCount = (history[history.length - 1].correctedCount || 0) + correctedCount;
          sessionStorage.setItem('detectionHistory', JSON.stringify(history));
        }
      }
      this.$message({
        type: 'success',
        message: '文件已成功修正，现在可以下载修正后的文档'
      });
    },
    
    generateCorrectedDocument() {
      if (!this.result) {
        this.$message({ type: 'warning', message: '请先上传文件并完成检测' });
        return;
      }
      if (!this.hasReplaceableErrors) {
        this.$message({ type: 'info', message: '当前文档没有可替换的错误' });
        return;
      }
      this.showDetail = true;
    },

    async replaceAllErrors() {
      if (!this.result) {
        this.$message({ type: 'warning', message: '请先上传文件并完成检测' });
        return;
      }
      if (!this.hasReplaceableErrors) {
        this.$message({ type: 'info', message: '当前文档没有可替换的错误' });
        return;
      }
      if (!this.selectedFile) {
        this.$message({ type: 'error', message: '原始文件不存在，请重新上传' });
        return;
      }
      try {
        this.$message({ type: 'info', message: '正在批量修正，请稍候...' });
        const response = await fixAllErrors(this.selectedFile, null);
        if (response?.data?.file_id) {
          this.result = {
            ...this.result,
            file_id: response.data.file_id,
            original_filename: response.data.original_filename || this.selectedFile.name  // 使用原始文件名
          };
          this.$message({ type: 'success', message: '全部更换成功' });
        }
      } catch (err) {
        console.error('批量修正失败:', err);
        this.$message({ type: 'error', message: '批量修正失败，请重试' });
      }
    },
    
    exportReport() {
      if (this.result) {
        const report = {
          file: this.selectedFile?.name || '未知文件',
          report: this.result.report,
          details: this.result.details,
          generatedAt: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'detection_report.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        alert('请先完成检测');
      }
    },
    
    initChart() {
      if (!this.$refs.chart) {
        console.log('等待图表容器...');
        setTimeout(() => this.initChart(), 100);
        return;
      }
      try {
        this.chartInstance = echarts.init(this.$refs.chart);
        this.updateChart();
      } catch (e) {
        console.error('图表初始化失败:', e);
      }
    },
    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },
    
    updateChart() {
      if (!this.$refs.chart) {
        console.log('图表容器不存在，等待...');
        setTimeout(() => this.updateChart(), 100);
        return;
      }
      
      if (!this.chartInstance) {
        try {
          this.chartInstance = echarts.init(this.$refs.chart);
        } catch (e) {
          console.error('图表初始化失败:', e);
          return;
        }
      }
      
      const report = this.result && this.result.report;
      let chartData = [];
      let totalErrors = 0;
      
      if (report) {
        totalErrors = report["总错误"] || 0;
        chartData = [
          { name: '字词错误', value: report["错别字"] || 0 },
          { name: '语义错误', value: report["语义错误"] || 0 },
          { name: '文献错误', value: report["参考文献错误"] || 0 },
          { name: '图表错误', value: (report["图表错误"] || 0) + (report["表格错误"] || 0) }
        ].filter(item => item.value > 0);
      }
      
      if (chartData.length === 0) {
        chartData = [{ name: '暂无错误', value: 1 }];
      }
      
      console.log('更新图表:', { chartData, totalErrors });
      
      this.chartInstance.setOption({
        title: {
          text: '错误统计',
          left: 'center',
          textStyle: { fontSize: 14, fontWeight: 'bold', color: '#333' }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const percent = totalErrors > 0 ? ((params.value / totalErrors) * 100).toFixed(1) : 0;
            return `${params.name}<br/>数量: ${params.value} (${percent}%)`;
          }
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'middle',
          itemWidth: 10,
          itemHeight: 10,
          textStyle: { fontSize: 11 }
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['55%', '55%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 4,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: false
          },
          data: chartData,
          color: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        }]
      }, true);
    }
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: Arial, sans-serif;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 1rem;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  background-color: #ffffff;
  border-right: 1px solid #e0e0e0;
  padding: 1.5rem 0;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 2rem;
}

.sidebar-section h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  padding: 0 1.5rem 0.5rem;
  margin: 0;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-section li {
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.sidebar-section li:hover {
  background-color: #f5f7fa;
}

.sidebar-section li.active {
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: 500;
}

.icon {
  font-size: 1rem;
}

.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.upload-section {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 4px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #1890ff;
  background-color: #f0f7ff;
}

.upload-icon {
  font-size: 3rem;
  color: #999;
  margin-bottom: 1rem;
}

.upload-area p {
  margin: 0.5rem 0;
  color: #666;
}

.upload-hint {
  font-size: 0.9rem;
  color: #999;
}

.progress-section {
  margin: 1.5rem 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
  color: #666;
}

.progress-message {
  font-size: 0.85rem;
  color: #1890ff;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #1890ff;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.file-info-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.file-info-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.file-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.file-info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-info-label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.file-info-value {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
}

.btn {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.btn-sm {
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
}

.btn-block {
  width: 100%;
  justify-content: center;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #40a9ff;
}

.btn-primary:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-success {
  background-color: #52c41a;
  color: white;
}

.btn-success:hover {
  background-color: #73d13d;
}

.result-section {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.result-section h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.no-result {
  text-align: center;
  padding: 3rem 0;
  color: #999;
}

.no-result-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-stats {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background-color: #fafafa;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1890ff;
}

.stat-value.error { color: #ff4d4f; }
.stat-value.warning { color: #faad14; }
.stat-value.danger { color: #cf1322; }
.stat-value.total { color: #1890ff; }
.stat-value.success { color: #52c41a; }
.stat-value.grammar { color: #722ed1; }
.stat-value.image { color: #13c2c2; }
.stat-value.table { color: #eb2f96; }

.reference-list {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 1rem;
}

.reference-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #e8f4f8 0%, #d4e8f0 100%);
  border-bottom: 1px solid #b8d4de;
}

.reference-list-header h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e88e5;
  margin: 0;
}

.reference-count {
  font-size: 0.85rem;
  color: #666;
  background-color: #fff;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.reference-list-content {
  max-height: 300px;
  overflow-y: auto;
}

.reference-item {
  display: flex;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f7fa;
  background-color: #fff;
  transition: background-color 0.2s ease;
}

.reference-item:hover {
  background-color: #f8fcfe;
}

.reference-item:last-child {
  border-bottom: none;
}

.reference-index {
  font-weight: 600;
  color: #1e88e5;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.reference-text {
  font-size: 0.9rem;
  color: #333;
  line-height: 1.6;
  word-break: break-word;
}

.image-list {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 1rem;
}

.image-list-header,
.table-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #e6fffb 0%, #f0f9f8 100%);
  border-bottom: 1px solid #b8e6e6;
}

.image-list-header h3,
.table-list-header h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #13c2c2;
  margin: 0;
}

.image-count,
.table-count {
  font-size: 0.85rem;
  color: #666;
  background-color: #fff;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.image-list-content,
.table-list-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 1rem;
  background-color: #fff;
}

.image-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  background-color: #fafafa;
}

.image-preview {
  flex-shrink: 0;
  width: 120px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.image-index {
  font-weight: 600;
  color: #13c2c2;
}

.image-caption {
  font-size: 0.85rem;
  color: #666;
}

.table-list {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 1rem;
}

.table-list-header {
  background: linear-gradient(135deg, #fff0f6 0%, #fff5f8 100%);
  border-bottom: 1px solid #f0c6db;
}

.table-list-header h3 {
  color: #eb2f96;
}

.table-item {
  padding: 0.75rem;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  background-color: #fafafa;
}

.table-info {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.table-index {
  font-weight: 600;
  color: #eb2f96;
}

.table-size {
  font-size: 0.85rem;
  color: #666;
}

.table-preview {
  overflow-x: auto;
}

.table-preview table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.table-preview th,
.table-preview td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
}

.table-preview th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.error-list {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.error-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-bottom: 1px solid #e0e0e0;
}

.error-list-header h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #444;
  margin: 0;
}

.error-list-actions {
  display: flex;
  gap: 0.5rem;
}

.error-list-content {
  max-height: 350px;
  overflow-y: auto;
}

.error-item {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid #f5f5f5;
  background-color: #fff;
  transition: background-color 0.2s ease;
}

.error-item:hover {
  background-color: #fafafa;
}

.error-item:last-child {
  border-bottom: none;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.error-type {
  padding: 0.1875rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: capitalize;
}

.error-type.spell {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.error-type.grammar {
  background-color: #f9f0ff;
  color: #722ed1;
}

.error-type.semantic {
  background-color: #fff2e8;
  color: #cf1322;
}

.error-type.reference {
  background-color: #f6ffed;
  color: #52c41a;
}

.error-type.image {
  background-color: #e6fffb;
  color: #13c2c2;
}

.error-type.table {
  background-color: #fff0f6;
  color: #eb2f96;
}

.error-type.text {
  background-color: #fff7e6;
  color: #fa8c16;
}

.error-type.unknown {
  background-color: #f5f5f5;
  color: #666;
}

.error-position {
  font-size: 0.8rem;
  color: #999;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.error-content .label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.text-error {
  color: #ff4d4f;
  font-weight: 500;
  background-color: #fff1f0;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
}

.text-success {
  color: #52c41a;
  font-weight: 500;
  background-color: #f6ffed;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
}

.text-warning {
  color: #faad14;
  background-color: #fffbe6;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
}

.error-actions {
  display: flex;
  justify-content: flex-end;
}

.no-errors {
  text-align: center;
  padding: 2rem;
  color: #52c41a;
}

.preview-section {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.preview-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  padding: 1rem;
  background-color: #fafafa;
  border-bottom: 1px solid #e0e0e0;
}

.preview-content {
  padding: 1rem;
  background-color: #fff;
  min-height: 80px;
}

.preview-text {
  font-size: 0.9rem;
  line-height: 1.6;
}

.preview-text .original {
  color: #ff4d4f;
  text-decoration: line-through;
  margin-right: 0.5rem;
}

.preview-text .replaced {
  color: #52c41a;
  font-weight: 500;
  margin-right: 0.5rem;
}

.action-section {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.link-btn {
  background: none;
  border: none;
  color: #1890ff;
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.9rem;
  padding: 0;
}

.link-btn:hover {
  color: #40a9ff;
}

.more-errors {
  padding: 1rem;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

.right-panel {
  width: 300px;
  background-color: #ffffff;
  border-left: 1px solid #e0e0e0;
  padding: 1.5rem;
  overflow-y: auto;
}

.right-panel h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-container {
  background-color: #fafafa;
  border-radius: 4px;
  padding: 1rem;
}

.chart-container h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  margin: 0 0 1rem 0;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quick-actions h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  margin: 0 0 0.5rem 0;
}

@media (max-width: 1200px) {
  .right-panel {
    width: 250px;
  }
}

@media (max-width: 992px) {
  .sidebar {
    width: 180px;
  }
  
  .right-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .sidebar-section ul {
    display: flex;
    overflow-x: auto;
  }
  
  .sidebar-section li {
    white-space: nowrap;
    border-right: 1px solid #f0f0f0;
  }
  
  .content {
    padding: 1rem;
  }
  
  .upload-area {
    padding: 2rem;
  }
  
  .result-stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .error-list-header {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
}
</style>

