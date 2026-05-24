<template>
  <div class="detail-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn btn-secondary" @click="goBack">
          <i class="icon">←</i> 返回
        </button>
        <span class="file-name">{{ fileName }}</span>
      </div>
      <div class="toolbar-right">
        <button 
          class="btn btn-primary" 
          @click="replaceAllErrors"
          :disabled="!hasReplaceableErrors"
        >
          <i class="icon">🔄</i> 一键替换全部错误
        </button>
        <button 
          class="btn btn-success" 
          @click="downloadDocument"
          :disabled="downloading || !result || !result.file_id || !result.original_filename"
        >
          <i class="icon">{{ downloading ? '⏳' : '📥' }}</i> {{ downloading ? '下载中...' : '下载修正文档' }}
        </button>
      </div>
    </div>

    <!-- 统计信息栏 -->
    <div class="stats-bar">
      <template v-if="checkType === 'image'">
        <div class="stat-item">
          <span class="stat-icon">🖼️</span>
          <span class="stat-label">图片总数</span>
          <span class="stat-value image">{{ result?.images?.length || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">📊</span>
          <span class="stat-label">表格总数</span>
          <span class="stat-value table">{{ result?.tables?.length || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">📝</span>
          <span class="stat-label">表格错别字</span>
          <span class="stat-value error">{{ typeStats.spell }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">⚠️</span>
          <span class="stat-label">图表错误</span>
          <span class="stat-value warning">{{ typeStats.image }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">⚠️</span>
          <span class="stat-label">表格错误</span>
          <span class="stat-value warning">{{ typeStats.table }}</span>
        </div>
      </template>
      <template v-else-if="checkType === 'reference'">
        <div class="stat-item">
          <span class="stat-icon">📚</span>
          <span class="stat-label">参考文献错误</span>
          <span class="stat-value warning">{{ typeStats.reference }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🔢</span>
          <span class="stat-label">总错误</span>
          <span class="stat-value total">{{ typeStats.total }}</span>
        </div>
      </template>
      <template v-else>
        <div class="stat-item">
          <span class="stat-icon">📝</span>
          <span class="stat-label">错别字</span>
          <span class="stat-value error">{{ typeStats.spell }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">📚</span>
          <span class="stat-label">参考文献错误</span>
          <span class="stat-value warning">{{ typeStats.reference }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">⚠️</span>
          <span class="stat-label">语义错误</span>
          <span class="stat-value danger">{{ typeStats.semantic }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">📖</span>
          <span class="stat-label">语法错误</span>
          <span class="stat-value grammar">{{ typeStats.grammar }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🖼️</span>
          <span class="stat-label">图表错误</span>
          <span class="stat-value image">{{ typeStats.image }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">📊</span>
          <span class="stat-label">表格错误</span>
          <span class="stat-value table">{{ typeStats.table }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🔢</span>
          <span class="stat-label">总错误</span>
          <span class="stat-value total">{{ typeStats.total }}</span>
        </div>
      </template>
      <div class="stat-item">
        <span class="stat-icon">✅</span>
        <span class="stat-label">已替换</span>
        <span class="stat-value success">{{ replacedCount }}</span>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧：文档预览区（文本模式） -->
      <div v-if="checkType !== 'image'" class="document-preview">
        <div class="preview-header">
          <span class="preview-icon">📄</span>
          <h3>文档内容预览</h3>
          <div class="preview-tips">
            <span class="tip-dot error-dot"></span>
            <span class="tip-text">红色高亮为错误内容</span>
          </div>
        </div>
        <div class="preview-body" ref="previewBody" @scroll="handlePreviewScroll">
          <!-- 显示文本内容（包含表格和图片） -->
          <div
            v-if="highlightedText"
            ref="textContent"
            class="text-content"
            v-html="highlightedText"
            @click="handleErrorClick"
            @mousemove="handleMouseMove"
            @mouseleave="handleMouseLeave"
          ></div>
          <div v-else class="empty-preview">
            <span class="empty-icon">📋</span>
            <p>暂无文档内容</p>
          </div>
        </div>
        
        <!-- 错误提示框 -->
        <div 
          v-if="showTooltip && tooltipData"
          class="error-tooltip"
          :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
        >
          <div class="tooltip-content">
            <div class="tooltip-row">
              <span class="tooltip-label">错误内容：</span>
              <span class="tooltip-value error">{{ tooltipData.error }}</span>
            </div>
            <div class="tooltip-row">
              <span class="tooltip-label">修正建议：</span>
              <span class="tooltip-value correct">{{ tooltipData.correct }}</span>
            </div>
            <div v-if="tooltipData.message" class="tooltip-row">
              <span class="tooltip-label">错误原因：</span>
              <span class="tooltip-value message">{{ tooltipData.message }}</span>
            </div>
          </div>
          <div class="tooltip-arrow"></div>
        </div>
      </div>

      <!-- 左侧：图片表格预览区 -->
      <div v-else class="document-preview">
        <div class="preview-header">
          <span class="preview-icon">📊</span>
          <h3>图片与表格预览</h3>
          <div class="preview-tips">
            <span class="tip-dot error-dot"></span>
            <span class="tip-text">鼠标悬停查看详情，点击红色文字纠错</span>
          </div>
        </div>
        <div class="preview-body" ref="previewBody" @scroll="handlePreviewScroll"
          @mousemove="handleMouseMove" @mouseleave="handleMouseLeave" @click="handleErrorClick">
          <!-- 图片列表 - 表格形式 -->
          <div v-if="result && result.images && result.images.length > 0" class="preview-section">
            <h4 class="section-title">📷 图片列表</h4>
            <table class="image-table">
              <thead>
                <tr>
                  <th>序号</th>
                  <th>图片预览</th>
                  <th>标题</th>
                  <th>位置</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="img in result.images" 
                  :key="'img-' + img.index" 
                  class="image-row"
                  :class="{ 'has-error': hasImageError(img.index) }"
                >
                  <td>{{ img.index }}</td>
                  <td class="img-preview-cell">
                    <img v-if="img.src" :src="img.src" :alt="img.caption" />
                    <div v-else class="img-placeholder">
                      <span>图片加载失败</span>
                    </div>
                  </td>
                  <td>{{ img.caption }}</td>
                  <td>{{ img.position }}</td>
                  <td>
                    <span v-if="hasImageError(img.index)" class="status-error">有问题</span>
                    <span v-else class="status-normal">正常</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 表格列表 - 仅显示错误模式 -->
          <div v-if="showOnlyErrors && spellErrorsForTable.length > 0" class="preview-section">
            <h4 class="section-title">📝 表格内容错误列表</h4>
            <div class="error-list-simple">
              <div
                v-for="(err, idx) in spellErrorsForTable"
                :key="'terr-' + idx"
                class="error-item-simple"
                :class="{ replaced: isTableErrorReplaced(err) }"
                @click="replaceSingleError(getOriginalIndex(err))"
              >
                <span class="error-pos">{{ err.pos }}</span>
                <span class="error-text-simple">{{ err.error }}</span>
                <span class="error-arrow">→</span>
                <span class="correct-text-simple">{{ (Array.isArray(err.corrections) ? err.corrections[0] : err.correct) || '无建议' }}</span>
              </div>
            </div>
          </div>

          <!-- 表格列表 - mini-table（正常模式） -->
          <div v-if="!showOnlyErrors && result && result.tables && result.tables.length > 0" class="preview-section">
            <h4 class="section-title">📊 表格列表</h4>
            <div class="tables-list">
              <div v-for="tbl in result.tables" :key="'tbl-' + tbl.index" class="table-wrapper">
                <table class="mini-table">
                  <thead>
                    <tr>
                      <th v-for="(header, hIdx) in tbl.header.slice(0, 6)" :key="hIdx">
                        <span v-html="highlightTableCell(tbl.index, 0, hIdx, header || `列${hIdx + 1}`)"></span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, rIdx) in tbl.rows.slice(1, 5)" :key="rIdx">
                      <td v-for="(cell, cIdx) in row.slice(0, 6)" :key="cIdx">
                        <span v-html="highlightTableCell(tbl.index, rIdx + 1, cIdx, cell || '-')"></span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-if="!result || (!result.images && !result.tables)" class="empty-preview">
            <span class="empty-icon">📋</span>
            <p>未在文档中发现图片或表格</p>
          </div>
        </div>

        <!-- 错误提示框 -->
        <div 
          v-if="showTooltip && tooltipData"
          class="error-tooltip"
          :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
        >
          <div class="tooltip-content">
            <div class="tooltip-row">
              <span class="tooltip-label">错误内容：</span>
              <span class="tooltip-value error">{{ tooltipData.error }}</span>
            </div>
            <div class="tooltip-row">
              <span class="tooltip-label">修正建议：</span>
              <span class="tooltip-value correct">{{ tooltipData.correct }}</span>
            </div>
            <div v-if="tooltipData.message" class="tooltip-row">
              <span class="tooltip-label">错误原因：</span>
              <span class="tooltip-value message">{{ tooltipData.message }}</span>
            </div>
          </div>
          <div class="tooltip-arrow"></div>
        </div>
      </div>

      <!-- 右侧：错误列表和修改建议 -->
      <div class="error-panel">
        <div class="panel-header">
          <span class="panel-icon">🔍</span>
          <h3>错误详情与修改建议</h3>
          <span class="error-count">{{ filteredErrors.length }} 个错误</span>
        </div>
        
        <!-- 错误类型筛选 -->
        <div class="filter-tabs">
          <button 
            v-for="tab in filterTabs" 
            :key="tab.value"
            class="filter-tab"
            :class="{ active: activeFilter === tab.value }"
            @click="activeFilter = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 错误列表 -->
        <div class="error-list">
          <div 
            v-for="(error, index) in filteredErrors" 
            :key="index"
            class="error-card"
            :class="{ 
              active: activeErrorIndex === index,
              replaced: replacedErrors.includes(getOriginalIndex(error))
            }"
            @mouseenter="activeErrorIndex = index"
            @mouseleave="activeErrorIndex = -1"
            @click="scrollToError(error, index)"
          >
            <div class="error-header">
              <span class="error-badge" :class="getErrorClass(error.type)">
                {{ getErrorLabel(error.type) }}
              </span>
              <span class="error-position">位置: {{ error.pos }}</span>
            </div>
            
            <div class="error-content">
              <div class="error-row">
                <span class="row-label">错误内容:</span>
                <span class="error-text">{{ error.message || error.error }}</span>
              </div>
              <div v-if="error.suggestion" class="error-row">
                <span class="row-label">修正建议:</span>
                <span class="correct-text">{{ error.suggestion }}</span>
              </div>
              <div v-if="error.corrections && error.corrections.length > 0" class="error-row">
                <span class="row-label">修正建议:</span>
                <span class="correct-text">{{ error.corrections.join('；') }}</span>
              </div>
              <div v-if="error.messages && error.messages.length > 0" class="error-row">
                <span class="row-label">错误原因:</span>
                <span class="message-text">{{ error.messages.join('；') }}</span>
              </div>
            </div>
            
            <div class="error-actions">
              <button 
                v-if="!replacedErrors.includes(getOriginalIndex(error))"
                class="action-btn replace-btn"
                @click="replaceSingleError(getOriginalIndex(error))"
              >
                <i class="btn-icon">✓</i> 替换
              </button>
              <span v-else-if="replacedErrors.includes(getOriginalIndex(error))" class="replaced-tag">
                <i class="tag-icon">✓</i> 已替换
              </span>
            </div>
          </div>
          
          <div v-if="filteredErrors.length === 0" class="empty-error-list">
            <span class="empty-icon">🎉</span>
            <p>暂无{{ activeFilter === 'all' ? '' : getFilterLabel(activeFilter) }}错误</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作栏 -->
    <div class="quick-actions">
      <button 
        class="quick-btn"
        :class="{ active: showOnlyErrors }"
        @click="showOnlyErrors = !showOnlyErrors"
      >
        <i class="quick-icon">👁️</i>
        {{ showOnlyErrors ? '显示全部' : '仅显示错误' }}
      </button>
      <button 
        class="quick-btn"
        @click="scrollToNextError"
        :disabled="!hasNextError"
      >
        <i class="quick-icon">⬇️</i>
        下一个错误
      </button>
    </div>
  </div>
</template>

<script>
import { downloadFixedFile, fixTable, editTable, fixAllErrors } from "../api";
import { parseDetails, mergeParsedErrors, filterMergedByCheckType } from "../utils/detailParsing";
import { escapeHtml as escHtml, collectNonOverlappingMatches } from "../utils/highlightUtils";

export default {
  props: {
    result: {
      type: Object,
      default: null
    },
    fileName: {
      type: String,
      default: '未命名文档'
    },
    checkType: {
      type: String,
      default: 'text'
    },
    originalFile: {
      type: [File, Object],
      default: null
    }
  },
  data() {
    return {
      replacedErrors: [],
      activeErrorIndex: -1,
      activeFilter: 'all',
      showOnlyErrors: false,
      nextErrorIndex: 0,
      // tooltip相关（文本模式 + 表格模式共用）
      showTooltip: false,
      tooltipData: null,
      tooltipPosition: { x: 0, y: 0 },
      // 下载相关
      downloading: false
    };
  },
  computed: {
    typeStats() {
      const list = this.filteredErrors;
      const count = (t) => list.filter((e) => e.type === t).length;
      return {
        spell: count("spell"),
        grammar: count("grammar"),
        semantic: count("semantic"),
        reference: count("reference"),
        image: count("image"),
        table: count("table"),
        total: list.length,
      };
    },
    filterTabs() {
      if (this.checkType === 'image') {
        return [
          { label: '全部', value: 'all' },
          { label: '图表', value: 'image' },
          { label: '表格', value: 'table' },
          { label: '错别字', value: 'spell' }
        ];
      }
      if (this.checkType === 'reference') {
        return [
          { label: '全部', value: 'all' },
          { label: '参考文献', value: 'reference' }
        ];
      }
      return [
        { label: '全部', value: 'all' },
        { label: '错别字', value: 'spell' },
        { label: '语法', value: 'grammar' },
        { label: '语义', value: 'semantic' },
        { label: '参考文献', value: 'reference' },
        { label: '图表', value: 'image' },
        { label: '表格', value: 'table' }
      ];
    },
    parsedErrors() {
      if (!this.result || !this.result.details) return [];
      return parseDetails(this.result.details);
    },

    mergedErrors() {
      return mergeParsedErrors(this.parsedErrors);
    },

    filteredErrors() {
      let errors = filterMergedByCheckType(this.mergedErrors, this.checkType);
      if (this.activeFilter === "all") return errors;
      return errors.filter((error) => error.type === this.activeFilter);
    },
    
    // 当前选中表格的错误列表
    
    // 表格模式：所有表格内容的 spell 错误（用于「仅显示错误」列表）
    spellErrorsForTable() {
      if (this.checkType !== 'image') return [];
      return this.filteredErrors.filter(e => e.type === 'spell');
    },
    
    hasReplaceableErrors() {
      return this.filteredErrors.some(error => error.corrections && error.corrections.length > 0);
    },
    
    replacedCount() {
      return this.replacedErrors.length;
    },
    
    hasNextError() {
      const unreplaced = this.filteredErrors.filter(error => 
        (error.corrections && error.corrections.length > 0) &&
        !(error.mergedOriginalIndices && error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx)))
      );
      return unreplaced.length > 0;
    },
    
    highlightedText() {
      // 如果只显示错误部分 - 统一只显示错误列表，按序号排序
      if (this.showOnlyErrors) {
        const validErrors = this.filteredErrors.filter(e => e.error || e.message);
        if (validErrors.length === 0) return '<p class="no-errors">未发现错误内容</p>';
        
        return validErrors.map((error, index) => {
          const isReplaced = error.mergedOriginalIndices && 
                            error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx));
          const errorText = error.error || error.message;
          
          return '<div class="text-error-list-item" style="' + (!isReplaced ? 'color: #d93026;' : 'color: #52c41a;') + '">' +
            '<span class="text-error-list-num">' + (index + 1) + '.</span>' +
            '<span class="text-error-list-content">' + 
              (isReplaced ? '(已替换) ' : '') + escHtml(errorText) + 
            '</span>' +
          '</div>';
        }).join('');
      }
      
      // 如果有带格式的HTML内容（包含图片和表格），优先使用
      if (this.result && this.result.original_html && this.result.original_html.trim()) {
        return this.highlightHtmlContent(this.result.original_html);
      }
      
      // 如果有原始文本，显示带高亮的文档内容
      if (this.result && this.result.original_text && this.result.original_text.trim()) {
        let text = this.result.original_text;
        
        const errorMap = {};
        this.filteredErrors.forEach((error, index) => {
          if (!error.error) return;
          const matchText = error.error;
          if (!errorMap[matchText]) errorMap[matchText] = [];
          errorMap[matchText].push({
            index,
            error,
            correct: Array.isArray(error.corrections) ? error.corrections[0] : error.correct,
            message: Array.isArray(error.messages) ? error.messages.join("；") : error.message,
            originalError: error.error,
          });
        });

        const uniqueErrors = Object.keys(errorMap);
        if (uniqueErrors.length === 0) {
          return escHtml(text).replace(/\n/g, "<br>");
        }

        const needleToInfo = {};
        uniqueErrors.forEach((k) => {
          needleToInfo[k] = errorMap[k][0];
        });

        const { merged: mergedMatches, unmatched: unmatchedErrors } = collectNonOverlappingMatches(text, needleToInfo);

        // 多个相同文字的表格错误：为每个匹配分配独立的 errorMap 条目
        const errUsage = {};
        mergedMatches.forEach((match) => {
          const arr = errorMap[match.text];
          if (arr && arr.length > 1) {
            const idx = (errUsage[match.text] || 0) % arr.length;
            match.info = { ...arr[idx], originalError: arr[idx].error };
            errUsage[match.text] = (errUsage[match.text] || 0) + 1;
          }
        });

        let result = "";
        let lastIndex = 0;

        mergedMatches.forEach((match) => {
          // 添加匹配前的文本
          result += escHtml(text.substring(lastIndex, match.start));

          // 获取错误信息
          const info = match.info;
          const isReplaced = info.error.mergedOriginalIndices && 
                            info.error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx));

          // 构建tooltip内容
          let tooltipContent = '';
          if (isReplaced) {
            tooltipContent = info.correct ? '已替换为: ' + info.correct : '已标记错误';
          } else {
            if (info.correct) {
              tooltipContent = '建议替换为: ' + info.correct;
            } else {
              tooltipContent = '错误内容';
            }
            if (info.message) {
              tooltipContent += '\n错误原因: ' + info.message;
            }
          }

          // 添加高亮标签
          const displayText = isReplaced ? (info.correct || info.error.error || match.text) : (info.error.error || match.text);
          result += '<span class="highlight-error ' + (info.correct && !isReplaced ? 'clickable' : '') + '" ' +
            'data-index="' + (info.error.originalIndex !== undefined ? info.error.originalIndex : info.index) + '" ' +
            'data-error="' + escHtml(info.error.error || match.text).replace(/"/g, '&quot;') + '" ' +
            'data-correct="' + escHtml(info.correct || '').replace(/"/g, '&quot;') + '" ' +
            'data-message="' + escHtml(info.message || '').replace(/"/g, '&quot;') + '" ' +
            (isReplaced ? 'style="background-color: #f6ffed; color: #52c41a; border-bottom: 2px solid #52c41a; cursor: default;"' : 'style="background-color: #fff2f0; color: #d93026; border-bottom: 2px solid #d93026; cursor: ' + (info.correct ? 'pointer' : 'default') + ';"') +
            '>' + escHtml(displayText) + '</span>';

          lastIndex = match.end;
        });
        
        // 添加剩余文本
        result += escHtml(text.substring(lastIndex));
        
        // 将换行转换为HTML换行
        result = result.replace(/\n/g, '<br>');
        
        // 如果有未匹配的错误，在末尾显示
        if (unmatchedErrors.length > 0) {
          result += '<div class="unmatched-errors">';
          result += '<h4 style="color: #d93026; margin-top: 20px; margin-bottom: 10px;">以下错误在文档正文中未找到对应内容：</h4>';
          unmatchedErrors.forEach((info, index) => {
            const isReplaced = info.error.mergedOriginalIndices && 
                              info.error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx));
            result += '<div style="padding: 10px; background-color: #fff2f0; border-radius: 4px; margin-bottom: 8px; border-left: 4px solid #d93026;">';
            result += '<div style="font-weight: bold; color: #d93026; margin-bottom: 4px;">错误' + (index + 1) + ':</div>';
            result += '<div><span style="color: #666;">原文:</span> <span style="color: #d93026;">' + escHtml(info.originalError || info.error.error) + '</span></div>';
            if (info.correct) {
              result += '<div><span style="color: #666;">建议:</span> <span style="color: #52c41a;">' + escHtml(info.correct) + '</span></div>';
            }
            if (info.message) {
              result += '<div><span style="color: #666;">原因:</span> <span style="color: #999;">' + escHtml(info.message) + '</span></div>';
            }
            result += '</div>';
          });
          result += '</div>';
        }
        
        return result;
      }
    }
  },
  methods: {
    getTextContentEl() {
      return this.$refs.textContent || (this.$el && this.$el.querySelector && this.$el.querySelector(".text-content"));
    },
    goBack() {
      this.$emit('back');
    },
    
    getOriginalIndex(error) {
      if (error.mergedOriginalIndices && error.mergedOriginalIndices.length > 0) {
        return error.mergedOriginalIndices[0];
      }
      return error.originalIndex;
    },
    
    getErrorClass(type) {
      const classes = {
        spell: 'spell-badge',
        grammar: 'grammar-badge',
        semantic: 'semantic-badge',
        reference: 'reference-badge',
        image: 'image-badge',
        table: 'table-badge',
        other: 'other-badge'
      };
      return classes[type] || 'other-badge';
    },

    getErrorLabel(type) {
      const labels = {
        spell: '错别字',
        grammar: '语法错误',
        semantic: '语义错误',
        reference: '参考文献',
        image: '图表错误',
        table: '表格错误',
        other: '其他错误'
      };
      return labels[type] || '其他错误';
    },

    getErrorTypeLabel(error) {
      if (error.type === 'spell') {
        if (error.message && error.message.includes('单位')) {
          return '单位缺失';
        }
        return '错别字';
      }
      if (error.type === 'table') {
        if (error.message) {
          if (error.message.includes('标题')) return '标题问题';
          if (error.message.includes('编号')) return '编号问题';
          if (error.message.includes('表注')) return '表注问题';
          if (error.message.includes('引用')) return '引用问题';
          if (error.message.includes('单位')) return '单位问题';
        }
        return '表格结构';
      }
      return this.getErrorLabel(error.type);
    },

    hasImageError(index) {
      return this.filteredErrors.some(e => e.type === 'image' && e.pos === index);
    },

    highlightTableCell(tableIndex, rowIndex, colIndex, text) {
      if (!text || text === '-') return escHtml(text);
      
      const errors = this.filteredErrors.filter(e => {
        if (e.type !== 'spell') return false;
        if (e.table_index !== tableIndex) return false;
        if (e.row_index !== undefined && e.row_index !== rowIndex) return false;
        if (e.col_index !== undefined && e.col_index !== colIndex) return false;
        return true;
      });
      
      if (errors.length === 0) return escHtml(text);
      
      const error = errors[0];
      const errorText = error.error || '';
      if (!errorText) return escHtml(text);
      
      const isReplaced = error.mergedOriginalIndices && 
                        error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx));
      const correct = Array.isArray(error.corrections) ? error.corrections[0] : error.correct;
      const message = Array.isArray(error.messages) ? error.messages[0] : error.message;
      const dataIndex = error.originalIndex !== undefined ? error.originalIndex : 0;
      
      // 在单元格文本中定位错误文字的准确位置，只高亮错误部分
      const errIdx = text.indexOf(errorText);
      if (errIdx === -1) return escHtml(text);
      
      const prefix = text.substring(0, errIdx);
      const suffix = text.substring(errIdx + errorText.length);
      const displayError = isReplaced ? (correct || errorText) : errorText;
      const style = isReplaced 
        ? 'background-color: #f6ffed; color: #52c41a; border-bottom: 2px solid #52c41a; cursor: default;'
        : 'background-color: #fff2f0; color: #d93026; border-bottom: 2px solid #d93026; cursor: pointer;';
      
      return escHtml(prefix) +
        '<span class="highlight-error' + (correct && !isReplaced ? ' clickable' : '') + '" ' +
        'data-index="' + dataIndex + '" ' +
        'data-error="' + escHtml(errorText).replace(/"/g, '&quot;') + '" ' +
        'data-correct="' + escHtml(correct || '').replace(/"/g, '&quot;') + '" ' +
        'data-message="' + escHtml(message || '').replace(/"/g, '&quot;') + '" ' +
        'style="' + style + '"' +
        '>' + escHtml(displayError) + '</span>' +
        escHtml(suffix);
    },
    
    // 处理包含图片和表格的HTML内容，添加错误高亮
    highlightHtmlContent(html) {
      if (!html) return '';
      
      // 创建临时元素来解析HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      
      // 获取所有文本节点
      const textNodes = [];
      const getTextNodes = (element) => {
        element.childNodes.forEach(child => {
          if (child.nodeType === Node.TEXT_NODE && child.textContent.trim()) {
            textNodes.push({ node: child, parent: element });
          } else if (child.nodeType === Node.ELEMENT_NODE) {
            // 只跳过img元素的子节点，表格元素需要处理内部文本以显示错误高亮
            if (child.tagName !== 'IMG') {
              getTextNodes(child);
            }
          }
        });
      };
      getTextNodes(tempDiv);
      
      // 创建错误映射（每个错误文字可能有多个独立条目，用数组收集）
      const errorMap = {};
      this.filteredErrors.forEach((error) => {
        if (error.error) {
          if (!errorMap[error.error]) errorMap[error.error] = [];
          errorMap[error.error].push({
            correct: Array.isArray(error.corrections) ? error.corrections[0] : error.correct,
            message: Array.isArray(error.messages) ? error.messages.join('；') : error.message,
            type: error.type,
            originalIndices: error.mergedOriginalIndices || [error.originalIndex],
            isReplaced: error.mergedOriginalIndices && error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx))
          });
        }
      });
      
      // 处理每个文本节点
      textNodes.forEach(({ node, parent }) => {
        let text = node.textContent;
        let result = '';
        let lastIndex = 0;
        const matches = [];
        
        // 查找所有错误匹配
        Object.keys(errorMap).forEach(errorText => {
          const escapedText = errorText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const regex = new RegExp(escapedText, 'g');
          let match;
          while ((match = regex.exec(text)) !== null) {
            matches.push({
              start: match.index,
              end: match.index + errorText.length,
              text: errorText,
              info: errorMap[errorText][0]
            });
          }
        });

        // 多条目相同文字：每个匹配分配独立的 errorMap 条目
        const errUsage2 = {};
        matches.forEach(m => {
          const arr = errorMap[m.text];
          if (arr && arr.length > 1) {
            const idx = (errUsage2[m.text] || 0) % arr.length;
            m.info = { ...arr[idx], originalIndices: arr[idx].originalIndices || [] };
            errUsage2[m.text] = (errUsage2[m.text] || 0) + 1;
          }
        });
        
        // 按位置排序并合并重叠
        matches.sort((a, b) => a.start - b.start);
        const mergedMatches = [];
        matches.forEach(match => {
          if (mergedMatches.length === 0) {
            mergedMatches.push(match);
          } else {
            const last = mergedMatches[mergedMatches.length - 1];
            if (match.start < last.end) {
              if (match.end > last.end) {
                last.end = match.end;
              }
            } else {
              mergedMatches.push(match);
            }
          }
        });
        
        // 如果没有匹配，跳过处理
        if (mergedMatches.length === 0) {
          return;
        }
        
        // 构建结果
        mergedMatches.forEach((match) => {
          result += escHtml(text.substring(lastIndex, match.start));
          
          const info = match.info;
          const isReplaced = info.isReplaced;
          const correctText = info.correct;
          
          const span = document.createElement('span');
          span.className = 'highlight-error' + (correctText && !isReplaced ? ' clickable' : '');
          span.dataset.error = match.text;
          span.dataset.correct = correctText || '';
          span.dataset.message = info.message || '';
          span.dataset.index = info.originalIndices[0];
          
          if (isReplaced) {
            span.style.backgroundColor = '#f6ffed';
            span.style.color = '#52c41a';
            span.style.borderBottom = '2px solid #52c41a';
            span.textContent = correctText || match.text;
          } else {
            span.style.backgroundColor = '#fff2f0';
            span.style.color = '#d93026';
            span.style.borderBottom = '2px solid #d93026';
            span.style.cursor = correctText ? 'pointer' : 'default';
            span.textContent = match.text;
          }
          
          result += span.outerHTML;
          lastIndex = match.end;
        });
        
        result += escHtml(text.substring(lastIndex));
        
        // 对于表格内的文本节点，使用 wrap 方式而不是 replaceChild
        // 避免破坏表格结构
        if (result !== escHtml(text)) {
          const parentTagName = parent.tagName ? parent.tagName.toLowerCase() : '';
          // 检查父节点是否是表格相关元素
          const isTableElement = ['td', 'th', 'tr', 'tbody', 'thead', 'tfoot', 'table'].includes(parentTagName);
          
          if (isTableElement) {
            // 对于表格元素，使用 documentFragment 来保持结构
            const fragment = document.createDocumentFragment();
            const tempSpan = document.createElement('span');
            tempSpan.innerHTML = result;
            while (tempSpan.firstChild) {
              fragment.appendChild(tempSpan.firstChild);
            }
            parent.replaceChild(fragment, node);
          } else {
            const newSpan = document.createElement('span');
            newSpan.innerHTML = result;
            parent.replaceChild(newSpan, node);
          }
        }
      });
      
      return tempDiv.innerHTML;
    },
    
    getFilterLabel(filter) {
      const labels = {
        all: '',
        spell: '错别字',
        grammar: '语法',
        semantic: '语义',
        reference: '参考文献',
        other: '其他'
      };
      return labels[filter] || '';
    },
    
    replaceSingleError(index) {
      if (!this.replacedErrors.includes(index)) {
        this.replacedErrors.push(index);
      }
    },
    
    // 处理文档预览中错误内容的点击替换
    handleErrorClick(event) {
      const target = event.target.closest('.highlight-error.clickable');
      if (target) {
        const errorText = target.dataset.error;
        const correctText = target.dataset.correct || '';
        const dataIdx = parseInt(target.dataset.index);
        
        // 按 data-index 精确定位 mergedError，避免同文字多条目时误匹配
        let mergedError = this.mergedErrors.find(e => e.originalIndex === dataIdx);
        if (!mergedError) {
          mergedError = this.mergedErrors.find(e => e.error === errorText);
        }
        if (mergedError && mergedError.mergedOriginalIndices) {
          mergedError.mergedOriginalIndices.forEach(originalIdx => {
            if (!this.replacedErrors.includes(originalIdx)) {
              this.replacedErrors.push(originalIdx);
            }
          });
        }
        
        // 更新DOM显示
        if (correctText) {
          target.innerHTML = escHtml(correctText);
        }
        target.style.backgroundColor = '#f6ffed';
        target.style.color = '#52c41a';
        target.style.borderColor = '#52c41a';
        target.style.cursor = 'default';
        target.classList.remove('clickable');
        target.dataset.tooltip = correctText ? '已替换为: ' + correctText : '已标记错误';
      }
    },
    
    async replaceAllErrors() {
      const replaceableErrors = this.filteredErrors.filter(error => 
        error.corrections && error.corrections.length > 0
      );

      if (replaceableErrors.length === 0) {
        this.$message({
          type: 'info',
          message: '没有可替换的错误'
        });
        return;
      }

      const errorIndices = [];
      const textContent = this.getTextContentEl();
      
      if (textContent) {
        const highlightElements = textContent.querySelectorAll('.highlight-error.clickable');
        
        highlightElements.forEach((el) => {
          const errorText = el.dataset.error;
          const correctText = el.dataset.correct;
          
          if (errorText && correctText) {
            el.innerHTML = escHtml(correctText);
            el.style.backgroundColor = '#f6ffed';
            el.style.color = '#52c41a';
            el.style.borderColor = '#52c41a';
            el.style.cursor = 'default';
            el.classList.remove('clickable');
            el.dataset.tooltip = '已替换为: ' + correctText;
          }
        });
      }

      replaceableErrors.forEach(error => {
        const indices = error.mergedOriginalIndices || [error.originalIndex];
        indices.forEach(idx => {
          if (!this.replacedErrors.includes(idx)) {
            this.replacedErrors.push(idx);
          }
        });
      });

      const originalText = this.result?.original_text || '';
      let correctedText = originalText;
      if (originalText && replaceableErrors.length > 0) {
        const sortedErrors = [...replaceableErrors].sort((a, b) => {
          const aPos = a.pos || 0;
          const bPos = b.pos || 0;
          return bPos - aPos;
        });
        const chars = [...originalText];
        sortedErrors.forEach(error => {
          const pos = error.pos || 0;
          const errText = error.error || '';
          const suggestion = Array.isArray(error.corrections) ? error.corrections[0] : (error.correct || '');
          if (errText && suggestion && pos < chars.length) {
            const errLen = errText.length;
            chars.splice(pos, errLen, ...suggestion);
          }
        });
        correctedText = chars.join('');
      }
      if (this.result) {
        this.result.corrected_text = correctedText;
      }

      this.$message({
        type: 'success',
        message: `已替换 ${this.replacedErrors.length} 个错误！`
      });

      if (this.originalFile) {
        try {
          const response = await fixAllErrors(this.originalFile, null);
          if (response?.data?.file_id) {
            this.$emit('file-fixed', {
              fileId: response.data.file_id,
              filename: response.data.filename || response.data.original_filename,
              originalFilename: this.fileName,
              correctedCount: this.replacedErrors.length
            });
            this.$message({
              type: 'success',
              message: '修正文档已生成，点击"下载修正文档"保存'
            });
          }
        } catch (err) {
          console.error('批量修正失败:', err);
        }
      } else {
        this.$message({
          type: 'info',
          message: '如需下载修正后的文档，请点击"下载修正文档"按钮'
        });
      }
    },
    
    // 处理鼠标移动
    handleMouseMove(event) {
      const target = event.target.closest('.highlight-error');
      if (target && target.dataset.index !== undefined) {
        const index = parseInt(target.dataset.index);
        if (!isNaN(index)) {
          // 直接从data属性获取数据
          this.tooltipData = {
            error: target.dataset.error || '',
            correct: target.dataset.correct || '',
            message: target.dataset.message || ''
          };
          
          // 计算tooltip位置（在鼠标上方）
          const rect = target.getBoundingClientRect();
          this.tooltipPosition = {
            x: rect.left + (rect.width / 2) - 120, // 居中偏移
            y: rect.top - 100 // 上方显示
          };
          this.showTooltip = true;
          return;
        }
      }
      this.showTooltip = false;
    },
    
    // 处理鼠标离开
    handleMouseLeave() {
      this.showTooltip = false;
    },
    
    // 判断表格错误是否已被替换
    isTableErrorReplaced(err) {
      if (!err || !err.mergedOriginalIndices) return false;
      return err.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx));
    },
    
    scrollToNextError() {
      const allErrors = this.filteredErrors;
      if (allErrors.length === 0) {
        this.$message({
          type: 'info',
          message: '没有错误'
        });
        return;
      }

      const startIndex = this.nextErrorIndex;
      let targetError = null;
      let foundIndex = -1;

      for (let i = 0; i < allErrors.length; i++) {
        const checkIndex = (startIndex + i) % allErrors.length;
        const error = allErrors[checkIndex];
        const hasCorrections = error.corrections && error.corrections.length > 0;
        const isReplaced = error.mergedOriginalIndices &&
                          error.mergedOriginalIndices.some(idx => this.replacedErrors.includes(idx));

        if (hasCorrections && !isReplaced) {
          targetError = error;
          foundIndex = checkIndex;
          break;
        }

        if ((startIndex + i) % allErrors.length === startIndex - 1) {
          break;
        }
      }

      if (!targetError) {
        this.$message({
          type: 'info',
          message: '没有更多未替换的错误'
        });
        return;
      }

      this.nextErrorIndex = (foundIndex + 1) % allErrors.length;

      const errorText = targetError.error;
      const previewBody = this.$refs.previewBody;
      if (!previewBody) return;

      // 清除旧标记
      previewBody.querySelectorAll('.highlight-error').forEach(el => el.classList.remove('scroll-to-target'));
      document.querySelectorAll('.target-marker').forEach(el => el.remove());
      document.querySelectorAll('.position-tip').forEach(el => el.remove());

      const highlightElements = previewBody.querySelectorAll('.highlight-error');
      let targetElement = null;

      highlightElements.forEach(el => {
        const elError = el.dataset.error;
        if (elError === errorText && !el.classList.contains('replaced')) {
          if (!targetElement) targetElement = el;
        }
      });

      if (!targetElement) {
        console.log('No matching highlight found for:', errorText);
        return;
      }

      targetElement.classList.add('scroll-to-target');
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

      const rect = targetElement.getBoundingClientRect();
      const containerRect = previewBody.getBoundingClientRect();
      const targetMarker = document.createElement('div');
      targetMarker.className = 'target-marker';
      targetMarker.innerHTML = '<div class="target-line"></div><div class="target-glow"></div>';
      targetMarker.style.top = (rect.top - containerRect.top) + 'px';
      targetMarker.style.height = rect.height + 'px';
      previewBody.appendChild(targetMarker);

      requestAnimationFrame(() => targetMarker.classList.add('marker-visible'));

      this.tooltipData = {
        error: targetError.error,
        correct: targetError.corrections[0] || '',
        message: targetError.messages[0] || ''
      };
      const highlightRect = targetElement.getBoundingClientRect();
      this.tooltipPosition = {
        x: highlightRect.left + (highlightRect.width / 2) - 120,
        y: highlightRect.top - 100
      };
      this.showTooltip = true;

      setTimeout(() => {
        targetElement.classList.remove('scroll-to-target');
        targetMarker.classList.remove('marker-visible');
        setTimeout(() => {
          targetMarker.remove();
          this.showTooltip = false;
        }, 300);
      }, 2500);
    },
    
    scrollToError(error, index) {
      if (!error || !error.error) {
        console.log('scrollToError: no error text', { error });
        return;
      }

      const textContent = this.getTextContentEl();
      if (!textContent) {
        console.log('scrollToError: textContent not found');
        return;
      }

      const errorText = error.error;
      console.log('Looking for error text:', errorText);
      console.log('Error type:', error.type);
      console.log('Error pos:', error.pos);

      const highlightElements = textContent.querySelectorAll('.highlight-error');
      console.log('Total highlights in DOM:', highlightElements.length);

      let targetElement = null;
      let matchCount = 0;

      highlightElements.forEach((el, idx) => {
        const elError = el.dataset.error;
        const elIndex = el.dataset.index;
        console.log(`Highlight ${idx}: error="${elError}", index="${elIndex}"`);
        if (elError === errorText) {
          matchCount++;
          if (!targetElement) {
            targetElement = el;
            console.log('Found match at idx', idx);
          }
        }
      });

      console.log('Total matches:', matchCount);

      if (targetElement) {
        textContent.querySelectorAll('.highlight-error').forEach(el => {
          el.classList.remove('scroll-to-target');
        });
        const existingMarkers = document.querySelectorAll('.target-marker');
        existingMarkers.forEach(el => el.remove());

        targetElement.classList.add('scroll-to-target');

        const rect = targetElement.getBoundingClientRect();
        const containerRect = targetElement.closest('.preview-body').getBoundingClientRect();
        const targetMarker = document.createElement('div');
        targetMarker.className = 'target-marker';
        targetMarker.innerHTML = '<div class="target-line"></div><div class="target-glow"></div>';
        targetMarker.style.top = (rect.top - containerRect.top) + 'px';
        targetMarker.style.height = rect.height + 'px';
        targetElement.closest('.preview-body').appendChild(targetMarker);

        requestAnimationFrame(() => {
          targetMarker.classList.add('marker-visible');
        });

        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setTimeout(() => {
          targetElement.classList.remove('scroll-to-target');
          targetMarker.classList.remove('marker-visible');
          setTimeout(() => targetMarker.remove(), 300);
        }, 3000);
      } else {
        console.log('No matching highlight found for:', errorText);
      }
    },
    
    showPositionTip(element, pos) {
      const existingTip = document.querySelector('.position-tip');
      if (existingTip) existingTip.remove();
      
      const tip = document.createElement('div');
      tip.className = 'position-tip';
      tip.innerHTML = '<span class="tip-number">' + (parseInt(pos) + 1) + '</span><span class="tip-label">号错误</span>';
      
      const rect = element.getBoundingClientRect();
      const containerRect = element.closest('.preview-body').getBoundingClientRect();
      
      tip.style.top = (rect.top - containerRect.top - 35) + 'px';
      tip.style.left = Math.max(10, rect.left - containerRect.left) + 'px';
      
      element.closest('.preview-body').appendChild(tip);
      
      requestAnimationFrame(() => {
        tip.classList.add('tip-visible');
      });
      
      setTimeout(() => {
        tip.classList.remove('tip-visible');
        setTimeout(() => tip.remove(), 300);
      }, 2500);
    },

    handlePreviewScroll() {
      if (!this.$refs.previewBody) return;

      const scrollTop = this.$refs.previewBody.scrollTop;
      const textContent = this.getTextContentEl();
      if (!textContent) return;

      const highlightElements = textContent.querySelectorAll('.highlight-error');
      let closestElement = null;
      let closestDistance = Infinity;

      highlightElements.forEach((el) => {
        const elTop = el.offsetTop;
        const distance = Math.abs(elTop - scrollTop);
        if (distance < closestDistance) {
          closestDistance = distance;
          closestElement = el;
        }
      });

      if (closestElement) {
        const errorIndex = parseInt(closestElement.dataset.index);
        const matchedError = this.mergedErrors.find(e => {
          const origIdx = this.getOriginalIndex(e);
          return origIdx === errorIndex;
        });

        if (matchedError) {
          const errorListIndex = this.filteredErrors.indexOf(matchedError);
          if (errorListIndex >= 0) {
            this.activeErrorIndex = errorListIndex;
          }
        }
      }
    },

    async downloadDocument() {
      if (!this.result?.file_id || !this.result?.original_filename) return;
      
      this.downloading = true;
      try {
        const images = this.result.images || [];
        const tables = this.result.tables || [];
        await downloadFixedFile(this.result.file_id, this.result.original_filename, images, tables);
        const stored = sessionStorage.getItem('reportStats');
        const stats = stored ? JSON.parse(stored) : { totalDetectedErrors: 0, totalCorrected: 0 };
        const currentReport = this.result?.report || {};
        const currentErrors = currentReport['总错误'] || currentReport['totalErrors'] || (this.result?.errors?.length || 0);
        stats.totalCorrected = (stats.totalCorrected || 0) + currentErrors;
        sessionStorage.setItem('reportStats', JSON.stringify(stats));
        const history = JSON.parse(sessionStorage.getItem('detectionHistory') || '[]');
        if (history.length > 0) {
          history[history.length - 1].correctedCount = (history[history.length - 1].correctedCount || 0) + currentErrors;
          sessionStorage.setItem('detectionHistory', JSON.stringify(history));
        }
        this.$message({
          type: 'success',
          message: '文件下载成功！'
        });
      } catch (error) {
        console.error('下载失败:', error);
        const errorMessage = error.response?.status === 404 
          ? '文件不存在或已过期' 
          : error.response?.status === 500
            ? '服务器内部错误，请稍后重试'
            : error.message?.includes('Network Error')
              ? '网络连接失败，请检查网络'
              : '下载失败，请重试';
        this.$message({
          type: 'error',
          message: errorMessage
        });
      } finally {
        this.downloading = false;
      }
    }
  }
};
</script>

<style scoped>
.detail-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Microsoft YaHei', 'SimSun', 'Times New Roman', sans-serif;
  background-color: #f5f7fa;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1.75rem;
  background: #1890ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.file-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
}

.toolbar-right {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5625rem 1.375rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.25s ease;
}

.btn-primary {
  background-color: rgba(255, 255, 255, 0.25);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.35);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background-color: rgba(255, 255, 255, 0.15);
  cursor: not-allowed;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.95);
  color: #333;
}

.btn-secondary:hover {
  background-color: white;
  transform: translateY(-1px);
}

.btn-success {
  background-color: #52c41a;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #73d13d;
  transform: translateY(-1px);
}

.btn-success:disabled {
  background-color: #a0d911;
  cursor: not-allowed;
}

.icon {
  font-size: 1.0625rem;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  gap: 2.5rem;
  padding: 1.125rem 1.75rem;
  background-color: white;
  border-bottom: 1px solid #e8e8e8;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.stat-icon {
  font-size: 1.25rem;
}

.stat-label {
  font-size: 0.9375rem;
  color: #666;
}

.stat-value {
  font-size: 1.375rem;
  font-weight: 600;
  font-family: 'Arial', sans-serif;
}

.stat-value.error { color: #cf1322; }
.stat-value.warning { color: #d48806; }
.stat-value.danger { color: #cf1322; }
.stat-value.total { color: #333; }
.stat-value.success { color: #389e0d; }
.stat-value.grammar { color: #595959; }
.stat-value.image { color: #595959; }
.stat-value.table { color: #595959; }

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow: hidden;
}

/* 文档预览区 */
.document-preview {
  flex: 1.2;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1.125rem 1.375rem;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.preview-icon {
  font-size: 1.375rem;
}

.preview-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #333;
}

.preview-tips {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.tip-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.error-dot {
  background-color: #d93026;
}

.tip-text {
  font-size: 0.8125rem;
  color: #999;
}

.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* 图片列表表格样式 */
.image-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  font-size: 0.9rem;
}

.image-table th,
.image-table td {
  border: 1px solid #e8e8e8;
  padding: 0.75rem;
  text-align: left;
  vertical-align: middle;
}

.image-table th {
  background-color: #fafafa;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.tables-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.table-wrapper {
  position: relative;
}

.mini-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #666;
  cursor: pointer;
  transition: box-shadow 0.2s ease;
}

.mini-table:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mini-table th,
.mini-table td {
  border: 1px solid #999;
  padding: 0.5rem;
  text-align: left;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.mini-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}



.image-row:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

.image-row.has-error {
  background-color: #fff2f0;
  border-left: 3px solid #ff4d4f;
}

.img-preview-cell {
  width: 140px;
  padding: 0.5rem;
}

.img-preview-cell img {
  width: 120px;
  height: 90px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.tbl-preview-cell {
  width: 280px;
  padding: 0.5rem;
}

.tbl-preview-inner {
  width: 100%;
  overflow-x: auto;
}

.tbl-preview-inner table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  border: 1px solid #666;
}

.tbl-preview-inner th,
.tbl-preview-inner td {
  border: 1px solid #999;
  padding: 0.5rem;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

.tbl-preview-inner th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.status-error {
  color: #ff4d4f;
  font-weight: 600;
}

.status-normal {
  color: #52c41a;
}

.img-placeholder {
  width: 120px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 1px dashed #d9d9d9;
  margin: 0 auto;
}

.img-placeholder span {
  font-size: 0.8rem;
  color: #999;
}

.text-content {
  line-height: 1.9;
  font-size: 1.0625rem;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 文本预览区域中的表格样式 */
.text-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  border: 1px solid #ddd;
  font-size: 0.9rem;
}

.text-content table th,
.text-content table td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
  vertical-align: top;
}

.text-content table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.text-content table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.text-content table tr:hover {
  background-color: #f5f5f5;
}

/* 文本预览区域中的图片样式 */
.text-content img {
  max-width: 100%;
  height: auto;
  margin: 0.5rem 0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 文本预览区域中的列表样式 */
.text-content ul,
.text-content ol {
  margin: 0.5rem 0 0.5rem 1.5rem;
  padding-left: 0;
}

.text-content li {
  margin-bottom: 0.25rem;
}

.highlight-error {
  background-color: #fff2f0;
  border-bottom: 2px solid #d93026;
  padding: 0.125rem 0.375rem;
  margin: 0 0.125rem;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.highlight-error:hover {
  background-color: #ffccc7;
  transform: scale(1.02);
}

/* Tooltip 样式 */
.highlight-error::before {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #1f1f1f;
  color: #fff;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  white-space: pre-wrap;
  max-width: 320px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s ease;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  line-height: 1.6;
  text-align: left;
  margin-bottom: 8px;
}

.highlight-error::after {
  content: '';
  position: absolute;
  bottom: calc(100% - 2px);
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #1f1f1f;
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s ease;
  z-index: 1001;
}

.highlight-error:hover::before,
.highlight-error:hover::after {
  opacity: 1;
  visibility: visible;
}

.highlight-error.scroll-to-target {
  animation: scroll-highlight 2.5s ease-out forwards, target-pulse 0.6s ease-in-out infinite, error-flash 0.4s ease-in-out infinite;
  box-shadow: 0 0 0 6px rgba(255, 77, 79, 0.6), 0 0 20px rgba(255, 77, 79, 0.6), 0 0 40px rgba(255, 77, 79, 0.3);
  border-radius: 6px;
  background-color: #ffcccc !important;
  transform: scale(1.1) !important;
  z-index: 1000;
  border: 3px solid #ff4d4f;
  position: relative;
}

@keyframes scroll-highlight {
  0% {
    box-shadow: 0 0 0 12px rgba(255, 77, 79, 0.8), 0 0 30px rgba(255, 77, 79, 0.6);
    background-color: #ffcccc;
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 77, 79, 0.6), 0 0 25px rgba(255, 77, 79, 0.5);
    background-color: #ffcccc;
  }
  100% {
    box-shadow: 0 0 0 6px rgba(255, 77, 79, 0.4), 0 0 20px rgba(255, 77, 79, 0.3);
    background-color: #fff2f0;
  }
}

@keyframes target-pulse {
  0%, 100% {
    transform: scale(1.1);
  }
  50% {
    transform: scale(1.18);
  }
}

@keyframes error-flash {
  0%, 100% {
    background-color: #ffcccc;
  }
  50% {
    background-color: #ffe0de;
  }
}

.position-tip {
  position: absolute;
  background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
  z-index: 100;
  pointer-events: none;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.position-tip.tip-visible {
  opacity: 1;
  transform: translateY(0);
}

.position-tip .tip-number {
  background: white;
  color: #ff6b6b;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.position-tip .tip-label {
  font-weight: normal;
  font-size: 12px;
  opacity: 0.9;
}

.target-marker {
  position: absolute;
  left: 0;
  width: 4px;
  background: linear-gradient(180deg, #ff4d4f, #ff7875, #ff4d4f);
  border-radius: 2px;
  z-index: 999;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.target-marker.marker-visible {
  opacity: 1;
  animation: marker-glow 0.8s ease-in-out infinite;
}

.target-marker .target-line {
  position: absolute;
  top: 0;
  left: -3px;
  width: 10px;
  height: 100%;
  background: linear-gradient(90deg, rgba(255, 77, 79, 0.8), transparent);
  border-radius: 5px;
}

.target-marker .target-glow {
  position: absolute;
  top: -4px;
  left: -12px;
  width: 28px;
  height: calc(100% + 8px);
  background: radial-gradient(ellipse at left center, rgba(255, 77, 79, 0.5), transparent 70%);
  animation: glow-pulse 0.8s ease-in-out infinite;
}

@keyframes marker-glow {
  0%, 100% {
    box-shadow: 0 0 8px rgba(255, 77, 79, 0.8), 0 0 16px rgba(255, 77, 79, 0.4);
  }
  50% {
    box-shadow: 0 0 12px rgba(255, 77, 79, 1), 0 0 24px rgba(255, 77, 79, 0.6);
  }
}

@keyframes glow-pulse {
  0%, 100% {
    opacity: 0.6;
    transform: scaleX(1);
  }
  50% {
    opacity: 1;
    transform: scaleX(1.3);
  }
}

.highlight-error.clickable:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(217, 48, 38, 0.3);
}

.highlight-error .replace-hint {
  font-size: 0.75rem;
  color: #ff7875;
  font-weight: normal;
  margin-left: 0.25rem;
  opacity: 0.8;
}

.highlight-error.pulse {
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); background-color: #ff7875; }
}

/* 错误提示框样式 */
.error-tooltip {
  position: fixed;
  z-index: 10000;
  pointer-events: none;
}

.tooltip-content {
  background-color: #1f1f1f;
  color: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  min-width: 240px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  animation: tooltipFadeIn 0.2s ease;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tooltip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.tooltip-row:last-child {
  margin-bottom: 0;
}

.tooltip-label {
  color: #999;
  flex-shrink: 0;
}

.tooltip-value {
  font-weight: 500;
}

.tooltip-value.error {
  color: #ff7875;
}

.tooltip-value.correct {
  color: #52c41a;
}

.tooltip-value.message {
  color: #fff;
  opacity: 0.9;
}

.tooltip-arrow {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #1f1f1f;
}

/* 降级内容样式 */
.fallback-content {
  padding: 1rem;
  font-size: 0.9rem;
}

.fallback-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.fallback-note {
  color: #999;
  font-size: 0.8rem;
  margin-bottom: 1rem;
}

.fallback-divider {
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
}

.fallback-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #f0f0f0;
}

.fallback-num {
  font-weight: 600;
  color: #666;
  min-width: 2rem;
}

.fallback-error {
  font-weight: 500;
}

.fallback-arrow {
  color: #999;
  margin: 0 0.5rem;
}

.fallback-correct {
  color: #52c41a;
  font-weight: 500;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-errors {
  color: #52c41a;
  font-weight: 500;
  text-align: center;
}

/* 预览项样式 */
.preview-item {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 4px solid #333;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed #e8e8e8;
}

.preview-num {
  background-color: #333;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

.preview-type {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.preview-pos {
  font-size: 0.8rem;
  color: #999;
}

.preview-body {
  line-height: 1.7;
}

.preview-error,
.preview-correct,
.preview-message {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.preview-error:last-child,
.preview-correct:last-child,
.preview-message:last-child {
  margin-bottom: 0;
}

.preview-error .label,
.preview-correct .label,
.preview-message .label {
  font-size: 0.85rem;
  color: #999;
  font-weight: 500;
  min-width: 40px;
}

.preview-error .error-text {
  font-size: 0.9375rem;
  color: #d93026;
  font-weight: 500;
}

.preview-correct .correct-text {
  font-size: 0.9375rem;
  color: #52c41a;
  font-weight: 500;
}

.preview-message .message-text {
  font-size: 0.875rem;
  color: #666;
  font-style: italic;
}

.error-highlight {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #fff2f0;
  border-left: 4px solid #d93026;
  margin-bottom: 0.75rem;
  border-radius: 0 4px 4px 0;
}

.error-num {
  font-weight: 600;
  color: #d93026;
}

/* 文本错误列表项样式（仅显示错误模式） */
.text-error-list-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem 0;
  line-height: 1.8;
  font-size: 1.0625rem;
}

.text-error-list-num {
  font-weight: 600;
  min-width: 2rem;
}

.text-error-list-content {
  flex: 1;
}

/* 错误面板 */
.error-panel {
  flex: 0.8;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1.125rem 1.375rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  border-bottom: 1px solid #e8e8e8;
}

.panel-icon {
  font-size: 1.375rem;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #333;
}

.error-count {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  background-color: #333;
  color: white;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 20px;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  gap: 0.375rem;
  padding: 0.75rem 1.375rem;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.filter-tab {
  padding: 0.375rem 0.875rem;
  background-color: transparent;
  border: 1px solid #d9d9d9;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  border-color: #333;
  color: #333;
}

.filter-tab.active {
  background-color: #333;
  border-color: #333;
  color: white;
}

/* 错误列表 */
.error-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.error-card {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.875rem;
  border-left: 4px solid #d9d9d9;
  transition: all 0.25s ease;
}

.error-card:hover {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.error-card.active {
  background-color: #fff;
  border-left-color: #333;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
}

.error-card.replaced {
  background-color: #f6ffed;
  border-left-color: #52c41a;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.error-badge {
  padding: 0.1875rem 0.625rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.spell-badge {
  background-color: #fff2f0;
  color: #d93026;
}

.grammar-badge {
  background-color: #fff7e6;
  color: #fa8c16;
}

.semantic-badge {
  background-color: #f6ffed;
  color: #52c41a;
}

.reference-badge {
  background-color: #f5f5f5;
  color: #333;
}

.image-badge {
  background-color: #fff0f6;
  color: #eb2f96;
}

.table-badge {
  background-color: #f5f5f5;
  color: #595959;
}

.other-badge {
  background-color: #f5f5f5;
  color: #666;
}

.error-position {
  font-size: 0.8125rem;
  color: #999;
}

.error-content {
  margin-bottom: 0.875rem;
}

.error-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.error-row:last-child {
  margin-bottom: 0;
}

.row-label {
  font-size: 0.85rem;
  color: #999;
  font-weight: 500;
  min-width: 60px;
}

.error-text {
  font-size: 0.9375rem;
  color: #d93026;
  font-weight: 500;
}

.correct-text {
  font-size: 0.9375rem;
  color: #52c41a;
  font-weight: 500;
}

.message-text {
  font-size: 0.875rem;
  color: #666;
  font-style: italic;
}

.error-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 0.375rem 0.875rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: all 0.2s ease;
}

.replace-btn {
  background-color: #52c41a;
  color: white;
}

.replace-btn:hover {
  background-color: #73d13d;
}

.replaced-tag {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.875rem;
  background-color: #f6ffed;
  color: #52c41a;
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 4px;
}

.btn-icon, .tag-icon {
  font-size: 0.75rem;
}

.empty-error-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #999;
}

/* 快捷操作栏 */
.quick-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 0.875rem;
  background-color: white;
  border-top: 1px solid #e8e8e8;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4375rem 1rem;
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-btn:hover {
  background-color: #e8e8e8;
}

.quick-btn.active {
  background-color: #333;
  border-color: #333;
  color: white;
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-icon {
  font-size: 0.9375rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .document-preview {
    flex: none;
    max-height: 40vh;
  }
  
  .error-panel {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 1rem;
  }

  .stats-bar {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .filter-tabs {
    flex-wrap: wrap;
  }

  .quick-actions {
    flex-wrap: wrap;
  }
}

/* 文档内容样式 - 支持图片和表格 */
.doc-content {
  line-height: 1.8;
  font-size: 1rem;
  color: #333;
}

.doc-content p {
  margin-bottom: 1rem;
  text-align: justify;
}

.doc-content img {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: block;
}

.doc-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
  background-color: #fff;
}

.doc-content table th,
.doc-content table td {
  border: 1px solid #ddd;
  padding: 0.5rem 0.75rem;
  text-align: left;
  vertical-align: top;
}

.doc-content table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #333;
}

.doc-content table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.doc-content table tr:hover {
  background-color: #f5f5f5;
}

/* v-html 内容在 scoped 下需穿透，保证 Word 预览表格/图片边框一致 */
.document-preview :deep(.doc-content table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
  background-color: #fff;
  border: 1px solid #666;
}
.document-preview :deep(.doc-content th),
.document-preview :deep(.doc-content td) {
  border: 1px solid #999;
  padding: 8px;
  vertical-align: top;
}
.document-preview :deep(.doc-content th) {
  background-color: #f5f5f5;
  font-weight: 600;
}
.document-preview :deep(.doc-content img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0.75rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 「仅显示错误」模式下的错误列表 */
.error-list-simple {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0.5rem 0;
}
.error-item-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.error-item-simple:hover {
  background: #ffe7e5;
  box-shadow: 0 2px 6px rgba(255, 77, 79, 0.15);
}
.error-item-simple.replaced {
  background: #f6ffed;
  border-color: #b7eb8f;
  text-decoration: line-through;
  color: #52c41a;
}
.error-pos {
  font-size: 0.75rem;
  color: #999;
  font-family: monospace;
  min-width: 70px;
}
.error-text-simple {
  color: #d93026;
  font-weight: 600;
  flex: 1;
}
.error-arrow {
  color: #999;
  font-weight: bold;
}
.correct-text-simple {
  color: #52c41a;
  font-weight: 500;
  flex: 1;
}

/* 错误卡片滚动高亮 */
.error-card.scroll-to-target {
  animation: cardHighlight 2s ease;
}
@keyframes cardHighlight {
  0%, 100% { box-shadow: 0 0 0 0 rgba(24, 144, 255, 0); }
  50% { box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.4); }
}
</style>
<style>
.target-marker {
  position: absolute;
  left: -6px;
  width: 3px;
  background: linear-gradient(180deg, #fa8c16, #faad14, #fa8c16);
  border-radius: 3px;
  z-index: 999;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.5s ease, left 0.4s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: 0 0 10px rgba(250, 140, 22, 0.5);
}

.target-marker.marker-visible {
  opacity: 1;
  left: 0;
  animation: amber-glow 2s ease-in-out infinite;
}

@keyframes amber-glow {
  0%, 100% {
    box-shadow: 0 0 8px rgba(250, 140, 22, 0.4);
    opacity: 0.9;
  }
  50% {
    box-shadow: 0 0 16px rgba(250, 173, 20, 0.7);
    opacity: 1;
  }
}

.highlight-error.scroll-to-target {
  animation: elegant-spotlight 3s ease-out forwards !important;
  box-shadow: 0 0 0 3px rgba(250, 140, 22, 0.3), 0 8px 32px rgba(250, 140, 22, 0.2) !important;
  border-radius: 6px !important;
  background: rgba(250, 173, 20, 0.12) !important;
  transform: scale(1.03) !important;
  z-index: 1000;
  border: 2px solid rgba(250, 140, 22, 0.5) !important;
  position: relative;
}

@keyframes elegant-spotlight {
  0% {
    box-shadow: 0 0 0 8px rgba(250, 140, 22, 0.4), 0 12px 40px rgba(250, 140, 22, 0.3);
    background: rgba(250, 173, 20, 0.25) !important;
    transform: scale(1.08);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(250, 140, 22, 0.3), 0 8px 24px rgba(250, 140, 22, 0.2);
    background: rgba(250, 173, 20, 0.18) !important;
    transform: scale(1.05);
  }
  100% {
    box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.2), 0 4px 16px rgba(250, 140, 22, 0.15);
    background: rgba(250, 173, 20, 0.1) !important;
    transform: scale(1.02);
  }
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: #333;
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.modal-close:hover {
  opacity: 1;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(85vh - 140px);
}

.modal-section {
  margin-bottom: 1.5rem;
}

.modal-section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #333;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 0.5rem;
}

.table-preview-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
}

.table-preview-container .full-table {
  width: 100%;
  border-collapse: collapse;
}

.table-preview-container .full-table th,
.table-preview-container .full-table td {
  padding: 0.5rem;
  border: 1px solid #e8e8e8;
  text-align: left;
  font-size: 0.875rem;
}

.table-preview-container .full-table th {
  background-color: #fafafa;
  font-weight: 600;
}

.image-preview-container {
  max-height: 300px;
  overflow: hidden;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.image-preview-container img {
  width: 100%;
  height: auto;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  background-color: #f5f5f5;
  color: #999;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.8rem;
  color: #999;
}

.info-value {
  font-size: 0.9375rem;
  color: #333;
  font-weight: 500;
}

.errors-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.error-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.error-item.error {
  background-color: #fff2f0;
  border-left: 4px solid #ff4d4f;
}

.error-item.warning {
  background-color: #fffbe6;
  border-left: 4px solid #faad14;
}

.error-item.info {
  background-color: #f5f5f5;
  border-left: 4px solid #595959;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-bullet {
  font-weight: bold;
}

.error-type {
  font-size: 0.8rem;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.error-position {
  font-size: 0.8rem;
  color: #888;
  font-weight: 500;
}

.error-text {
  font-size: 0.85rem;
  color: #ff4d4f;
  font-weight: 500;
  font-style: italic;
}

.error-message {
  font-size: 0.9375rem;
  color: #333;
  font-weight: 500;
}

.error-suggestion {
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
}

.no-errors {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  background-color: #f6ffed;
  border-radius: 6px;
}

.success-icon {
  color: #52c41a;
  font-size: 1.25rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e8e8e8;
}

.modal-actions .btn {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-actions .btn-primary {
  background: #333;
  color: white;
}

.modal-actions .btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.modal-actions .btn-secondary {
  background-color: #f5f5f5;
  color: #666;
}

.modal-actions .btn-secondary:hover {
  background-color: #e8e8e8;
}

.position-tip {
  position: absolute;
  background: linear-gradient(135deg, #fa8c16, #faad14);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 14px rgba(250, 140, 22, 0.35), 0 2px 6px rgba(0, 0, 0, 0.1);
  z-index: 100;
  pointer-events: none;
  opacity: 0;
  transform: translateY(8px) scale(0.95);
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  gap: 6px;
}

.position-tip.tip-visible {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.position-tip .tip-number {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.position-tip .tip-label {
  font-weight: 400;
  font-size: 12px;
  opacity: 0.95;
}
/* ========== 修复：给所有表格添加边框线 ========== */


/* ========== 仅美化你能用的两段表格 ========== */

/* 弹窗里的完整大表格（美化版） */
.full-table {
  border-collapse: collapse !important;
  border: 2px solid #444 !important;
  background: #fff !important;
}
.full-table th {
  border: 1px solid #444 !important;
  background: #f5f7fa !important;
  font-weight: bold !important;
  padding: 10px !important;
}
.full-table td {
  border: 1px solid #bbb !important;
  padding: 10px !important;
}

/* 文档内容区表格（美化版） */
.doc-content table {
  border-collapse: collapse !important;
  border: 1px solid #666 !important;
  background: #fff !important;
}
.doc-content th {
  border: 1px solid #666 !important;
  background: #f5f5f5 !important;
  font-weight: bold !important;
  padding: 8px !important;
}
.doc-content td {
  border: 1px solid #999 !important;
  padding: 8px !important;
} 

</style>