<template>
  <div ref="chart" style="width: 400px;height:300px;"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: ["report"],
  data() {
    return {
      chartInstance: null
    };
  },
  mounted() {
    this.draw();
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    // 清理事件监听器
    window.removeEventListener('resize', this.handleResize);
    // 销毁图表实例
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
  watch: {
    // 监听report属性变化，重新绘制图表
    report: {
      handler() {
        this.draw();
      },
      deep: true
    }
  },
  methods: {
    draw() {
      if (!this.report) return;
      
      try {
        // 初始化或获取图表实例
        if (!this.chartInstance && this.$refs.chart) {
          this.chartInstance = echarts.init(this.$refs.chart);
        }
        
        if (this.chartInstance) {
          this.chartInstance.setOption({
            title: { text: "错误统计" },
            series: [
              {
                type: "pie",
                data: [
                  { name: "错别字", value: this.report["错别字"] || 0 },
                  { name: "参考文献", value: this.report["参考文献错误"] || 0 },
                  { name: "语法错误", value: this.report["语法错误"] || 0 },
                  { name: "语义错误", value: this.report["语义错误"] || 0 },
                  { name: "图表错误", value: this.report["图表错误"] || 0 },
                  { name: "表格错误", value: this.report["表格错误"] || 0 },
                ],
              },
            ],
          });
        }
      } catch (error) {
        console.error('图表绘制失败:', error);
      }
    },
    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    }
  },
};
</script>