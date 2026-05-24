<template>
  <div v-if="data">
    <h3>检测结果</h3>

    <p>错别字：{{ data.report["错别字"] }}</p>
    <p>参考文献错误：{{ data.report["参考文献错误"] }}</p>
    <p>总错误：{{ data.report["总错误"] }}</p>

    <button @click="download">下载修复Word</button>

    <h4>详细错误</h4>
    <ul>
      <li v-for="(d, i) in data.details" :key="i">
        {{ d }}
      </li>
    </ul>
  </div>
</template>

<script>
import { downloadFile } from "../api";

export default {
  props: ["data"],
  methods: {
    download() {
      // 从download_url中提取文件名
      if (this.data.download_url) {
        const urlParts = this.data.download_url.split('/');
        const filename = urlParts[urlParts.length - 1];
        downloadFile(filename);
      } else {
        alert("下载链接不存在");
      }
    },
  },
};
</script>