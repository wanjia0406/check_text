/**
 * Parse backend ``details`` strings into normalized error rows (shared by App + ErrorDetail).
 */

export function parseDetailLine(detail, index) {
  let pos = -1;
  let error = "";
  let correct = "";
  let type = "spell";
  let message = "";
  let table_index, row_index, col_index;

  if (
    detail.startsWith("【图表错误】") ||
    detail.startsWith("【图表警告】") ||
    detail.startsWith("【图表提示】")
  ) {
    const content = detail.substring(6).trim();
    const posMatch = content.match(/图表(\d+)/);
    if (posMatch) pos = parseInt(posMatch[1], 10);
    type = "image";
    error = content;
    message = content;
  } else if (
    detail.startsWith("【表格错误】") ||
    detail.startsWith("【表格警告】") ||
    detail.startsWith("【表格提示】")
  ) {
    const content = detail.substring(6).trim();
    const posMatch = content.match(/表格(\d+)/);
    if (posMatch) pos = parseInt(posMatch[1], 10);
    type = "table";

    // 解析 "表格X错误内容→修正内容（建议）" 格式
    const arrowIdx = content.indexOf("→");
    if (arrowIdx !== -1) {
      const beforeArrow = content.substring(0, arrowIdx);
      const afterArrow = content.substring(arrowIdx + 1);

      // 提取error（原始错误内容）
      error = beforeArrow;

      // 解析修正内容和建议
      const leftParenIdx = afterArrow.indexOf("（");
      if (leftParenIdx !== -1) {
        correct = afterArrow.substring(0, leftParenIdx).trim();
        message = afterArrow.substring(leftParenIdx + 1, afterArrow.length - 1).trim();
      } else {
        correct = afterArrow.trim();
        message = afterArrow.trim();
      }
    } else {
      // 没有修正内容的情况，解析 "表格X错误内容（建议）" 格式
      error = content;
      const leftParenIdx = content.lastIndexOf("（");
      if (leftParenIdx !== -1) {
        message = content.substring(leftParenIdx + 1, content.length - 1).trim();
      } else {
        message = content;
      }
    }
  } else if (detail.startsWith("【表格内容错误】")) {
    const content = detail.substring(8).trim();
    const posMatch = content.match(/位置([^\s：:→]+)/);
    if (posMatch) pos = posMatch[1];

    // 从 pos 解析 table_index / row_index / col_index（如 T1-H2、T1-R3-C1）
    if (typeof pos === 'string') {
      const hMatch = pos.match(/^T(\d+)-H(\d+)/);
      if (hMatch) {
        table_index = parseInt(hMatch[1], 10);
        row_index = 0;
        col_index = parseInt(hMatch[2], 10) - 1;
      } else {
        const rcMatch = pos.match(/^T(\d+)-R(\d+)-C(\d+)/);
        if (rcMatch) {
          table_index = parseInt(rcMatch[1], 10);
          row_index = parseInt(rcMatch[2], 10) - 1;
          col_index = parseInt(rcMatch[3], 10) - 1;
        }
      }
    }

    const arrowIdx = content.indexOf("→");
    if (arrowIdx !== -1) {
      const beforeArrow = content.substring(0, arrowIdx);
      const afterArrow = content.substring(arrowIdx + 1);
      const colonIdx = beforeArrow.lastIndexOf("：");
      if (colonIdx !== -1) error = beforeArrow.substring(colonIdx + 1).trim();
      const leftParenIdx = afterArrow.indexOf("（");
      if (leftParenIdx !== -1) {
        correct = afterArrow.substring(0, leftParenIdx).trim();
        message = afterArrow.substring(leftParenIdx + 1, afterArrow.length - 1).trim();
      } else {
        message = afterArrow.trim();
      }
    } else {
      message = content;
    }
    type = "spell";
    if (!error) error = message;
  } else if (detail.startsWith("【参考文献错误】")) {
    const content = detail.substring(8).trim();
    const posMatch = content.match(/位置(\d+)/);
    if (posMatch) pos = parseInt(posMatch[1], 10);

    const arrowIdx = content.indexOf("→");
    if (arrowIdx !== -1) {
      const beforeArrow = content.substring(0, arrowIdx);
      const afterArrow = content.substring(arrowIdx + 1);
      const colonIdx = beforeArrow.lastIndexOf("：");
      if (colonIdx !== -1) error = beforeArrow.substring(colonIdx + 1).trim();
      const leftParenIdx = afterArrow.indexOf("（");
      if (leftParenIdx !== -1) {
        correct = afterArrow.substring(0, leftParenIdx).trim();
        message = afterArrow.substring(leftParenIdx + 1, afterArrow.length - 1).trim();
      } else {
        message = afterArrow.trim();
      }
    } else {
      message = content;
    }
    type = "reference";
    if (!error) error = message;
  } else {
    // 先尝试匹配表格单元格位置 (如 T1-H2, T1-R3-C1, T1-H2-unit)
    const tablePosMatch = detail.match(/位置(T\d+-[HR]\d+(-C\d+)?(-unit)?)[：:\s]/);
    if (tablePosMatch) {
      pos = tablePosMatch[1];
      if (typeof pos === 'string') {
        const hMatch = pos.match(/^T(\d+)-H(\d+)/);
        if (hMatch) {
          table_index = parseInt(hMatch[1], 10);
          row_index = 0;
          col_index = parseInt(hMatch[2], 10) - 1;
        } else {
          const rcMatch = pos.match(/^T(\d+)-R(\d+)-C(\d+)/);
          if (rcMatch) {
            table_index = parseInt(rcMatch[1], 10);
            row_index = parseInt(rcMatch[2], 10) - 1;
            col_index = parseInt(rcMatch[3], 10) - 1;
          }
        }
      }
      type = "spell";
    } else {
      const posMatch = detail.match(/位置(\d+)/);
      if (posMatch) pos = parseInt(posMatch[1], 10);
    }

    const parts = detail.split(" → ");
    if (parts.length === 2) {
      const beforeArrow = parts[0];
      const afterArrow = parts[1];
      const colonIdx = beforeArrow.indexOf("：");
      if (colonIdx !== -1) error = beforeArrow.substring(colonIdx + 1).trim();
      const leftParenIdx = afterArrow.indexOf("（");
      if (leftParenIdx !== -1) {
        correct = afterArrow.substring(0, leftParenIdx).trim();
        message = afterArrow.substring(leftParenIdx + 1, afterArrow.length - 1).trim();
      } else {
        correct = afterArrow.trim();
      }
    }

    // 根据 message 内容判断类型（语法 > 语义 > 图片 > 参考文献）
    if (table_index === undefined) {
      if (message.includes("语法问题") || message.includes("搭配")) {
        type = "grammar";
      } else if (message.includes("语义问题")) {
        type = "semantic";
      } else if (message.includes("图片") || message.includes("图表") || message.includes("图注") || message.includes("图题")) {
        type = "image";
      } else if (
        message.includes("参考文献") ||
        message.includes("学位论文") ||
        message.includes("会议论文") ||
        message.includes("期刊文章") ||
        message.includes("图书专著") ||
        message.includes("报纸文章") ||
        message.includes("网络报告") ||
        message.includes("报告文献") ||
        message.includes("GB/T 7714") ||
        message.includes("文献类型") ||
        message.includes("专著") ||
        message.includes("出版社") ||
        error.includes("[J]") ||
        error.includes("[M]") ||
        error.includes("[D]") ||
        error.includes("[R]") ||
        error.includes("[N]") ||
        error.includes("[C]")
      ) {
        type = "reference";
      }
      // 保留默认的 spell 类型
    }
  }

  return { pos, error, correct, type, message, originalIndex: index, table_index, row_index, col_index };
}

export function parseDetails(details) {
  if (!details || !details.length) return [];
  return details.map((d, i) => {
    try {
      return parseDetailLine(d, i);
    } catch {
      return { pos: -1, error: String(d), correct: "", type: "other", message: String(d), originalIndex: i };
    }
  });
}

export function mergeParsedErrors(parsedErrors) {
  const errorMap = {};

  parsedErrors.forEach((error, loopIndex) => {
    if (error.type === "other") return;

    const srcIndex = typeof error.originalIndex === "number" ? error.originalIndex : loopIndex;
    // 表格内 spell 错误按位置区分，避免不同单元格的相同错误文字被合并
    const key = (error.type === 'spell' && error.table_index !== undefined)
      ? `table_${error.table_index}_${error.row_index}_${error.col_index}_${error.error || error.message}`
      : (error.error || error.message || `error_${srcIndex}`);
    if (!key || key.startsWith("error_")) {
      if (!error.message) return;
    }

    if (!errorMap[key]) {
      errorMap[key] = {
        error: error.error || error.message || "",
        corrections: [error.correct].filter(Boolean),
        messages: [error.message].filter(Boolean),
        type: error.type,
        originalIndices: [srcIndex],
        pos: error.pos,
        table_index: error.table_index,
        row_index: error.row_index,
        col_index: error.col_index,
      };
    } else {
      if (error.correct && !errorMap[key].corrections.includes(error.correct)) {
        errorMap[key].corrections.push(error.correct);
      }
      if (error.message && !errorMap[key].messages.includes(error.message)) {
        errorMap[key].messages.push(error.message);
      }
      if (!errorMap[key].originalIndices.includes(srcIndex)) {
        errorMap[key].originalIndices.push(srcIndex);
      }
    }
  });

  return Object.values(errorMap).map((error, index) => ({
    ...error,
    originalIndex: index,
    mergedOriginalIndices: error.originalIndices,
  }));
}

export function filterMergedByCheckType(mergedErrors, checkType) {
  if (checkType === "image") return mergedErrors.filter((e) => e.type === "image" || e.type === "table" || e.type === "spell");
  if (checkType === "reference") return mergedErrors.filter((e) => e.type === "reference");
  return mergedErrors;
}
