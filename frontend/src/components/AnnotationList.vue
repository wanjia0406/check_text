<template>
  <div class="annotation-container">
    <div class="annotation-header">
      <h2>📝 批注列表</h2>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="exportAnnotations">
          <i class="icon">📥</i> 导出批注
        </button>
        <button class="btn btn-primary" @click="refreshAnnotations">
          <i class="icon">🔄</i> 刷新列表
        </button>
      </div>
    </div>

    <div class="annotation-body">
      <div v-if="annotations.length === 0" class="empty-state">
        <i class="empty-icon">📋</i>
        <p>暂无批注记录</p>
        <p class="empty-hint">完成文档检测后，批注会自动生成</p>
      </div>

      <div v-else class="annotation-list">
        <div 
          v-for="(annotation, index) in annotations" 
          :key="index" 
          class="annotation-item"
          :class="{ active: selectedIndex === index }"
          @click="selectAnnotation(index)"
        >
        <div class="annotation-header-row">
          <div class="annotation-type" :class="annotation.type">
            {{ getTypeLabel(annotation.type) }}
          </div>
          <span class="annotation-date">{{ formatDate(annotation.createdAt) }}</span>
        </div>
        
        <div class="annotation-content">
          <p class="annotation-error">{{ annotation.error }}</p>
          <p v-if="annotation.correct" class="annotation-suggestion">
            <span class="suggestion-label">建议：</span>
            <span class="suggestion-text">{{ annotation.correct }}</span>
          </p>
        </div>
        
        <div class="annotation-meta">
          <span class="meta-item">位置：{{ annotation.position }}</span>
          <span class="meta-item">文件：{{ annotation.filename }}</span>
        </div>
        
        <div class="annotation-actions">
          <button class="action-btn edit-btn" @click.stop="editAnnotation(index)">
            <i class="icon">✏️</i> 编辑
          </button>
          <button class="action-btn delete-btn" @click.stop="deleteAnnotation(index)">
            <i class="icon">🗑️</i> 删除
          </button>
        </div>
      </div>
    </div>
  </div>

    <!-- 编辑批注弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑批注</h3>
          <button class="close-btn" @click="closeEditModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>错误内容</label>
            <input 
              type="text" 
              v-model="editingAnnotation.error" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>修正建议</label>
            <textarea 
              v-model="editingAnnotation.correct" 
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>错误类型</label>
            <select v-model="editingAnnotation.type" class="form-select">
              <option value="spell">错别字</option>
              <option value="grammar">语法错误</option>
              <option value="semantic">语义错误</option>
              <option value="reference">参考文献</option>
              <option value="image">图表错误</option>
              <option value="table">表格错误</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeEditModal">取消</button>
          <button class="btn btn-primary" @click="saveAnnotation">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    annotations: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedIndex: -1,
      showEditModal: false,
      editingAnnotation: {
        error: '',
        correct: '',
        type: 'spell',
        position: '',
        filename: '',
        createdAt: ''
      },
      editingIndex: -1
    };
  },
  methods: {
    getTypeLabel(type) {
      const labels = {
        spell: '错别字',
        grammar: '语法错误',
        semantic: '语义错误',
        reference: '参考文献',
        image: '图表错误',
        table: '表格错误',
        unknown: '其他错误'
      };
      return labels[type] || type;
    },

    formatDate(dateStr) {
      if (!dateStr) return '未知时间';
      const date = new Date(dateStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    selectAnnotation(index) {
      this.selectedIndex = index;
    },

    editAnnotation(index) {
      this.editingIndex = index;
      this.editingAnnotation = { ...this.annotations[index] };
      this.showEditModal = true;
    },

    closeEditModal() {
      this.showEditModal = false;
      this.editingIndex = -1;
      this.editingAnnotation = {
        error: '',
        correct: '',
        type: 'spell',
        position: '',
        filename: '',
        createdAt: ''
      };
    },

    saveAnnotation() {
      if (this.editingIndex >= 0) {
        this.$emit('update-annotation', {
          index: this.editingIndex,
          annotation: this.editingAnnotation
        });
      }
      this.closeEditModal();
    },

    deleteAnnotation(index) {
      if (confirm('确定要删除这条批注吗？')) {
        this.$emit('delete-annotation', index);
      }
    },

    exportAnnotations() {
      const data = JSON.stringify(this.annotations, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `annotations_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },

    refreshAnnotations() {
      this.$emit('refresh');
    }
  }
};
</script>

<style scoped>
.annotation-container {
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

.annotation-header {
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

.annotation-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.annotation-header h2 {
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

.annotation-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.annotation-item {
  padding: 1rem;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #fff;
}

.annotation-item:hover {
  border-color: #1890ff;
  background-color: #f8fafc;
}

.annotation-item.active {
  border-color: #1890ff;
  background-color: #e6f7ff;
}

.annotation-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.annotation-type {
  padding: 0.25rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.annotation-type.spell {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.annotation-type.grammar {
  background-color: #f9f0ff;
  color: #722ed1;
}

.annotation-type.semantic {
  background-color: #fff2e8;
  color: #cf1322;
}

.annotation-type.reference {
  background-color: #f6ffed;
  color: #52c41a;
}

.annotation-type.image {
  background-color: #e6fffb;
  color: #13c2c2;
}

.annotation-type.table {
  background-color: #fff0f6;
  color: #eb2f96;
}

.annotation-date {
  font-size: 0.8rem;
  color: #999;
}

.annotation-content {
  margin-bottom: 0.75rem;
}

.annotation-error {
  font-size: 0.95rem;
  color: #ff4d4f;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
  background-color: #fff1f0;
  padding: 0.5rem;
  border-radius: 4px;
}

.annotation-suggestion {
  font-size: 0.9rem;
  margin: 0;
}

.suggestion-label {
  color: #666;
  font-weight: 500;
}

.suggestion-text {
  color: #52c41a;
  font-weight: 500;
}

.annotation-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.annotation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
}

.edit-btn {
  background-color: #fff;
  color: #1890ff;
  border: 1px solid #1890ff;
}

.edit-btn:hover {
  background-color: #e6f7ff;
}

.delete-btn {
  background-color: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
}

.delete-btn:hover {
  background-color: #fff1f0;
}

.icon {
  font-size: 0.85rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 480px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #666;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.375rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
  background-color: #fafafa;
}
</style>