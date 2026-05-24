<template>
  <div class="report-container">
    <div class="report-header">
      <h2>📊 统计报告</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="generateReport">
          <i class="icon">📄</i> 生成报告
        </button>
        <button class="btn btn-secondary" @click="downloadReport">
          <i class="icon">📥</i> 下载报告
        </button>
      </div>
    </div>

    <div class="report-body">
    <div v-if="!reportData || (reportData.totalErrors === 0 && reportData.documentCount === 0)" class="empty-state">
      <i class="empty-icon">📈</i>
      <p>暂无统计数据</p>
      <p class="empty-hint">完成文档检测后，统计报告会自动生成</p>
    </div>

    <div v-else class="report-content">
      <!-- 概览卡片 -->
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon total">📊</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.totalErrors }}</div>
            <div class="card-label">总错误数</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon spell">✏️</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.spellErrors }}</div>
            <div class="card-label">错别字</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon grammar">📚</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.grammarErrors }}</div>
            <div class="card-label">语法错误</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon semantic">⚠️</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.semanticErrors }}</div>
            <div class="card-label">语义错误</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon reference">📖</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.referenceErrors }}</div>
            <div class="card-label">参考文献错误</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon image">🖼️</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.imageErrors }}</div>
            <div class="card-label">图表错误</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon table">📋</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.tableErrors }}</div>
            <div class="card-label">表格错误</div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon corrected">✅</div>
          <div class="card-content">
            <div class="card-value">{{ displayData.correctedCount }}</div>
            <div class="card-label">已修正数</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="chart-section">
        <div class="chart-card">
          <h3>错误类型分布</h3>
          <div ref="pieChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
          <h3>检测趋势（最近7天）</h3>
          <div ref="lineChart" class="chart-container"></div>
        </div>
      </div>

      <!-- 详细统计 -->
      <div class="detail-section">
        <h3>详细统计</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">检测文档数</span>
            <span class="detail-value">{{ displayData.documentCount }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">平均错误数</span>
            <span class="detail-value">{{ displayData.averageErrorRate }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">错误密度</span>
            <span class="detail-value">{{ displayData.errorDensity }}/千字</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">修正率</span>
            <span class="detail-value">{{ displayData.correctionRate }}%</span>
          </div>
        </div>
      </div>

      <!-- 错误类型详情 -->
      <div class="type-detail-section">
        <h3>错误类型详情</h3>
        <div class="type-detail-table">
          <table>
            <thead>
              <tr>
                <th>错误类型</th>
                <th>数量</th>
                <th>占比</th>
                <th>常见问题</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in typeDetails" :key="index">
                <td>
                  <span class="type-badge" :class="item.type">{{ item.label }}</span>
                </td>
                <td>{{ item.count }}</td>
                <td>{{ item.percentage }}%</td>
                <td>{{ item.issues }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: {
    reportData: {
      type: Object,
      default: () => ({
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
      })
    }
  },
  computed: {
    displayData() {
      return this.reportData;
    }
  },
  data() {
    return {
      pieChart: null,
      lineChart: null,
      typeDetails: []
    };
  },
  mounted() {
    this.initCharts();
    this.updateTypeDetails();
  },
  watch: {
    reportData: {
      handler() {
        this.$nextTick(() => {
          this.updateCharts();
          this.updateTypeDetails();
        });
      },
      deep: true
    }
  },
  beforeUnmount() {
    if (this.pieChart) {
      this.pieChart.dispose();
    }
    if (this.lineChart) {
      this.lineChart.dispose();
    }
  },
  methods: {
    initCharts() {
      setTimeout(() => {
        if (this.$refs.pieChart) {
          this.pieChart = echarts.init(this.$refs.pieChart);
        }
        if (this.$refs.lineChart) {
          this.lineChart = echarts.init(this.$refs.lineChart);
        }
        this.updateCharts();
      }, 100);
    },

    updateCharts() {
      if (!this.pieChart || !this.lineChart) {
        this.initCharts();
        return;
      }

      const pieData = [
        { name: '错别字', value: this.displayData.spellErrors },
        { name: '语法错误', value: this.displayData.grammarErrors },
        { name: '语义错误', value: this.displayData.semanticErrors },
        { name: '参考文献', value: this.displayData.referenceErrors },
        { name: '图表错误', value: this.displayData.imageErrors },
        { name: '表格错误', value: this.displayData.tableErrors }
      ].filter(item => item.value > 0);

      this.pieChart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          itemWidth: 12,
          itemHeight: 12
        },
        series: [{
          type: 'pie',
          radius: ['45%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 14, fontWeight: 'bold' }
          },
          data: pieData,
          color: ['#ff6b6b', '#722ed1', '#cf1322', '#52c41a', '#13c2c2', '#eb2f96']
        }]
      });

      const history = JSON.parse(sessionStorage.getItem('detectionHistory') || '[]');
      const labels = history.map((h, i) => '#' + (i + 1));
      const errorSeries = history.map(h => h.totalErrors || 0);
      const correctedSeries = history.map(h => h.correctedCount || 0);

      if (history.length === 0) {
        labels.push('暂无数据');
        errorSeries.push(0);
        correctedSeries.push(0);
      }

      this.lineChart.setOption({
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['检测错误', '已修正'],
          bottom: 10,
          itemWidth: 12,
          itemHeight: 12
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLine: { lineStyle: { color: '#e0e0e0' } },
          axisLabel: { rotate: history.length > 7 ? 45 : 0 }
        },
        yAxis: {
          type: 'value',
          axisLine: { lineStyle: { color: '#e0e0e0' } },
          splitLine: { lineStyle: { color: '#f0f0f0' } }
        },
        series: [
          {
            name: '检测错误',
            type: 'line',
            data: errorSeries,
            smooth: true,
            lineStyle: { width: 3, color: '#1890ff' },
            itemStyle: { color: '#1890ff' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
              ])
            }
          },
          {
            name: '已修正',
            type: 'line',
            data: correctedSeries,
            smooth: true,
            lineStyle: { width: 3, color: '#52c41a' },
            itemStyle: { color: '#52c41a' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
                { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
              ])
            }
          }
        ]
      });
    },

    updateTypeDetails() {
      const total = this.displayData.totalErrors || 1;
      this.typeDetails = [
        {
          type: 'spell',
          label: '错别字',
          count: this.displayData.spellErrors,
          percentage: ((this.displayData.spellErrors / total) * 100).toFixed(1),
          issues: '常见错别字、用词错误、标点错误'
        },
        {
          type: 'grammar',
          label: '语法错误',
          count: this.displayData.grammarErrors,
          percentage: ((this.displayData.grammarErrors / total) * 100).toFixed(1),
          issues: '句子结构错误、搭配不当、语序问题'
        },
        {
          type: 'semantic',
          label: '语义错误',
          count: this.displayData.semanticErrors,
          percentage: ((this.displayData.semanticErrors / total) * 100).toFixed(1),
          issues: '逻辑矛盾、表达不清、歧义表述'
        },
        {
          type: 'reference',
          label: '参考文献',
          count: this.displayData.referenceErrors,
          percentage: ((this.displayData.referenceErrors / total) * 100).toFixed(1),
          issues: '格式不规范、引用缺失、编号错误'
        },
        {
          type: 'image',
          label: '图表错误',
          count: this.displayData.imageErrors,
          percentage: ((this.displayData.imageErrors / total) * 100).toFixed(1),
          issues: '图注缺失、编号不连续、分辨率不足'
        },
        {
          type: 'table',
          label: '表格错误',
          count: this.displayData.tableErrors,
          percentage: ((this.displayData.tableErrors / total) * 100).toFixed(1),
          issues: '表头不规范、数据错误、表注缺失'
        }
      ];
    },

    generateReport() {
      this.$emit('generate');
    },

    downloadReport() {
      this.$emit('generate');
      this.$nextTick(() => {
        this._doDownload();
      });
    },

    _doDownload() {
      const report = {
        title: '文档检测统计报告',
        generatedAt: new Date().toLocaleString('zh-CN'),
        data: this.reportData,
        typeDetails: this.typeDetails
      };

      const htmlContent = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>文档检测统计报告</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 2rem; background-color: #f5f5f5; }
    .report { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .report-title { text-align: center; color: #333; border-bottom: 2px solid #1890ff; padding-bottom: 1rem; }
    .overview-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0; }
    .overview-card { text-align: center; padding: 1rem; background: #fafafa; border-radius: 8px; }
    .card-value { font-size: 1.5rem; font-weight: bold; color: #1890ff; }
    .card-label { font-size: 0.85rem; color: #666; margin-top: 0.25rem; }
    .section { margin: 1.5rem 0; }
    .section-title { color: #333; border-bottom: 1px solid #e0e0e0; padding-bottom: 0.5rem; }
    .detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
    .detail-item { display: flex; justify-content: space-between; padding: 0.75rem; background: #fafafa; border-radius: 4px; }
    .detail-label { color: #666; }
    .detail-value { font-weight: bold; color: #333; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e0e0e0; }
    th { background: #fafafa; font-weight: 600; color: #333; }
    .type-badge { padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; }
    .type-badge.spell { background: #fff1f0; color: #ff4d4f; }
    .type-badge.grammar { background: #f9f0ff; color: #722ed1; }
    .type-badge.semantic { background: #fff2e8; color: #cf1322; }
    .type-badge.reference { background: #f6ffed; color: #52c41a; }
    .type-badge.image { background: #e6fffb; color: #13c2c2; }
    .type-badge.table { background: #fff0f6; color: #eb2f96; }
    .footer { text-align: center; color: #999; font-size: 0.85rem; margin-top: 2rem; border-top: 1px solid #e0e0e0; padding-top: 1rem; }
  </style>
</head>
<body>
  <div class="report">
    <h1 class="report-title">📊 文档检测统计报告</h1>
    <p style="text-align: center; color: #999; font-size: 0.9rem;">生成时间：${report.generatedAt}</p>
    
    <div class="overview-cards">
      <div class="overview-card"><div class="card-value">${report.data.totalErrors}</div><div class="card-label">总错误数</div></div>
      <div class="overview-card"><div class="card-value">${report.data.documentCount}</div><div class="card-label">检测文档数</div></div>
      <div class="overview-card"><div class="card-value">${report.data.correctionRate}%</div><div class="card-label">修正率</div></div>
      <div class="overview-card"><div class="card-value">${report.data.averageErrorRate}</div><div class="card-label">平均错误数</div></div>
    </div>
    
    <div class="section">
      <h2 class="section-title">详细统计</h2>
      <div class="detail-grid">
        <div class="detail-item"><span class="detail-label">错别字</span><span class="detail-value">${report.data.spellErrors}</span></div>
        <div class="detail-item"><span class="detail-label">语法错误</span><span class="detail-value">${report.data.grammarErrors}</span></div>
        <div class="detail-item"><span class="detail-label">语义错误</span><span class="detail-value">${report.data.semanticErrors}</span></div>
        <div class="detail-item"><span class="detail-label">参考文献错误</span><span class="detail-value">${report.data.referenceErrors}</span></div>
        <div class="detail-item"><span class="detail-label">图表错误</span><span class="detail-value">${report.data.imageErrors}</span></div>
        <div class="detail-item"><span class="detail-label">表格错误</span><span class="detail-value">${report.data.tableErrors}</span></div>
        <div class="detail-item"><span class="detail-label">错误密度</span><span class="detail-value">${report.data.errorDensity}/千字</span></div>
        <div class="detail-item"><span class="detail-label">已修正数</span><span class="detail-value">${report.data.correctedCount}</span></div>
      </div>
    </div>
    
    <div class="section">
      <h2 class="section-title">错误类型详情</h2>
      <table>
        <thead><tr><th>错误类型</th><th>数量</th><th>占比</th><th>常见问题</th></tr></thead>
        <tbody>
          ${report.typeDetails.map(item => `<tr><td><span class="type-badge ${item.type}">${item.label}</span></td><td>${item.count}</td><td>${item.percentage}%</td><td>${item.issues}</td></tr>`).join('')}
        </tbody>
      </table>
    </div>
    
    <div class="footer">智能文本检测与格式批注系统</div>
  </div>
</body>
</html>
      `;

      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${new Date().toISOString().slice(0, 10)}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }
};
</script>

<style scoped>
.report-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
  max-height: 600px;
  padding: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.report-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.report-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.report-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.icon {
  font-size: 0.85rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state p {
  margin: 0.5rem 0;
}

.empty-hint {
  font-size: 0.9rem;
  color: #bbb;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #fafafa;
  border-radius: 8px;
}

.card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  font-size: 1.5rem;
}

.card-icon.total { background-color: #e6f7ff; }
.card-icon.spell { background-color: #fff1f0; }
.card-icon.grammar { background-color: #f9f0ff; }
.card-icon.semantic { background-color: #fff2e8; }
.card-icon.reference { background-color: #f6ffed; }
.card-icon.image { background-color: #e6fffb; }
.card-icon.table { background-color: #fff0f6; }
.card-icon.corrected { background-color: #f6ffed; }

.card-content {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.card-label {
  font-size: 0.85rem;
  color: #666;
}

.chart-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.chart-card {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 1rem;
}

.chart-card h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.chart-container {
  width: 100%;
  height: 250px;
}

.detail-section {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 1rem;
}

.detail-section h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  background-color: #fff;
  border-radius: 4px;
}

.detail-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1890ff;
}

.type-detail-section {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 1rem;
}

.type-detail-section h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.type-detail-table table {
  width: 100%;
  border-collapse: collapse;
}

.type-detail-table th,
.type-detail-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.type-detail-table th {
  background-color: #fff;
  font-weight: 600;
  color: #333;
}

.type-detail-table tr:hover td {
  background-color: #fff;
}

.type-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.type-badge.spell {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.type-badge.grammar {
  background-color: #f9f0ff;
  color: #722ed1;
}

.type-badge.semantic {
  background-color: #fff2e8;
  color: #cf1322;
}

.type-badge.reference {
  background-color: #f6ffed;
  color: #52c41a;
}

.type-badge.image {
  background-color: #e6fffb;
  color: #13c2c2;
}

.type-badge.table {
  background-color: #fff0f6;
  color: #eb2f96;
}

@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-section {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .type-detail-table {
    overflow-x: auto;
  }
}
</style>