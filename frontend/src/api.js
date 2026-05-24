import axios from "axios";

const API = "http://127.0.0.1:8000";


// 创建axios实例
const axiosInstance = axios.create({
  baseURL: API,
  timeout: 900000 , // 5分钟超时（处理大文件需要更长时间）
  headers: {
    'Content-Type': 'application/json'
  },
  retry: 2, // 重试次数
  retryDelay: 1000 // 重试间隔（毫秒）
});

// 请求拦截器
axiosInstance.interceptors.request.use(
  config => {
    console.log(`[API请求] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('[API请求配置错误]', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  response => {
    console.log(`[API响应] ${response.status} ${response.config.url}`);
    return response;
  },
  error => {
    console.error('[API请求错误]:', error);
    
    // 重试机制
    const config = error.config;
    if (config && config.retry > 0) {
      config.retry--;
      console.log(`[重试] 剩余重试次数: ${config.retry}`);
      
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(axiosInstance(config));
        }, config.retryDelay || 1000);
      });
    }
    
    // 统一错误处理
    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 404:
          alert('请求的资源不存在');
          break;
        case 400:
          alert(`请求参数错误: ${error.response.data.detail || '请检查输入'}`);
          break;
        case 500:
          alert('服务器内部错误，请稍后重试');
          break;
        default:
          alert(`请求失败 [${error.response.status}]: ${error.response.data.detail || error.response.data.error || '未知错误'}`);
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应（网络错误）
      alert('网络错误，请检查网络连接或稍后重试');
    } else {
      // 请求配置出错
      alert(`请求配置错误: ${error.message}`);
    }
    return Promise.reject(error);
  }
);

/**
 * 上传文件到服务器
 * @param {File} file - 要上传的文件
 * @param {Function} onProgress - 上传进度回调函数
 * @returns {Promise} axios请求Promise
 */
export const uploadFile = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(`/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      // 处理上传进度
      if (progressEvent.total > 0) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`上传进度: ${percentCompleted}%`);
        if (onProgress) {
          onProgress({
            stage: 'uploading',
            progress: percentCompleted,
            message: `正在上传文件... ${percentCompleted}%`
          });
        }
      }
    }
  });
};

/**
 * 轮询检查处理状态（用于显示处理进度）
 * @param {string} fileId - 文件ID
 * @param {Function} onStatusUpdate - 状态更新回调函数
 * @returns {Promise} 处理完成Promise
 */
export const checkProcessStatus = (fileId, onStatusUpdate) => {
  // 模拟进度更新（实际项目中需要后端支持）
  return new Promise((resolve) => {
    let progress = 0;
    const stages = [
      { progress: 20, message: '正在初始化...' },
      { progress: 35, message: '正在读取文件...' },
      { progress: 50, message: '正在进行文本分析...' },
      { progress: 70, message: '正在检测参考文献...' },
      { progress: 85, message: '正在生成报告...' },
      { progress: 100, message: '处理完成!' }
    ];
    
    let stageIndex = 0;
    const interval = setInterval(() => {
      if (stageIndex < stages.length) {
        const stage = stages[stageIndex];
        progress = stage.progress;
        
        if (onStatusUpdate) {
          onStatusUpdate({
            stage: 'processing',
            progress: progress,
            message: stage.message
          });
        }
        
        stageIndex++;
      } else {
        clearInterval(interval);
        resolve();
      }
    }, 800);
  });
};

/**
 * 下载文件
 * @param {string} filename - 文件名
 */
export const downloadFile = (filename) => {
  // 直接打开下载链接
  window.open(`${API}/download/${filename}`, '_blank');
};

/**
 * 下载修复文档（包含图片和表格）
 * @param {string} fileId - 文件ID
 * @param {string} originalFilename - 原始文件名
 * @param {Array} images - 图片修正数据
 * @param {Array} tables - 表格修正数据
 * @returns {Promise} 下载Promise
 */
export const downloadCorrectedFile = async (fileId, originalFilename, images = [], tables = []) => {
  try {
    const params = new URLSearchParams();
    if (images && images.length > 0) {
      params.append('images', JSON.stringify(images));
    }
    if (tables && tables.length > 0) {
      params.append('tables', JSON.stringify(tables));
    }
    
    const url = `/download/corrected/${fileId}/${originalFilename}?${params.toString()}`;
    const response = await axiosInstance.get(url, {
      responseType: 'blob',
      timeout: 60000,
    });
    const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = blobUrl;
    const nameWithoutExt = originalFilename.replace(/\.[^/.]+$/, '') || '文档';
    const filename = `${nameWithoutExt}_修复版.docx`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    }, 1000);
  } catch (error) {
    console.error('下载失败:', error);
    throw error;
  }
};

/**
 * 删除服务器上的临时文件
 * @param {string} fileId - 文件ID
 * @returns {Promise} axios请求Promise
 */
export const cleanupFile = (fileId) => {
  return axiosInstance.delete(`/cleanup/${fileId}`);
};

/**
 * 健康检查（检查服务器是否正常运行）
 * @returns {Promise} axios请求Promise
 */
export const checkHealth = () => {
  return axiosInstance.get('/health');
};

/**
 * 获取文件信息（如页数、大小等）
 * @param {File} file - 文件对象
 * @returns {Promise} axios请求Promise
 */
export const getFileInfo = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(`/file/info`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 检测文本错误（错别字、语法等）
 * @param {File} file - 文件对象
 * @param {Function} onProgress - 上传进度回调函数
 * @returns {Promise} axios请求Promise
 */
export const checkTextErrors = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(`/check/text`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total > 0) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (onProgress) {
          onProgress({
            stage: 'uploading',
            progress: percentCompleted,
            message: `正在上传文件... ${percentCompleted}%`
          });
        }
      }
    }
  });
};

/**
 * 校验参考文献格式
 * @param {File} file - 文件对象
 * @param {Function} onProgress - 上传进度回调函数
 * @returns {Promise} axios请求Promise
 */
export const checkReferences = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(`/check/reference`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total > 0) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (onProgress) {
          onProgress({
            stage: 'uploading',
            progress: percentCompleted,
            message: `正在上传文件... ${percentCompleted}%`
          });
        }
      }
    }
  });
};

/**
 * 检查图片格式和引用
 * @param {File} file - 文件对象
 * @param {Function} onProgress - 上传进度回调函数
 * @returns {Promise} axios请求Promise
 */
export const checkImages = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(`/check/image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total > 0) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (onProgress) {
          onProgress({
            stage: 'uploading',
            progress: percentCompleted,
            message: `正在上传文件... ${percentCompleted}%`
          });
        }
      }
    }
  });
};

/**
 * 检查表格格式
 * @param {File} file - 文件对象
 * @param {Function} onProgress - 上传进度回调函数
 * @returns {Promise} axios请求Promise
 */
export const checkTables = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return axiosInstance.post(`/check/table`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total > 0) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (onProgress) {
          onProgress({
            stage: 'uploading',
            progress: percentCompleted,
            message: `正在上传文件... ${percentCompleted}%`
          });
        }
      }
    }
  });
};

/**
 * 修正表格问题（添加标题、表头、单位等）
 * @param {File} file - 文件对象
 * @param {number} tableIndex - 表格索引
 * @param {Object} options - 修正选项
 * @returns {Promise} axios请求Promise
 */
export const fixTable = (file, tableIndex, options = {}) => {
  const formData = new FormData();
  formData.append("file", file);
  if (tableIndex !== undefined && tableIndex !== null) {
    formData.append("table_index", tableIndex.toString());
  }
  if (options.new_caption) {
    formData.append("new_caption", options.new_caption);
  }
  if (options.new_header) {
    formData.append("new_header", "true");
  }
  if (options.add_unit) {
    formData.append("add_unit", "true");
  }
  if (options.add_note) {
    formData.append("add_note", "true");
  }

  return axiosInstance.post(`/fix/table`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 编辑表格内容
 * @param {File} file - 文件对象
 * @param {number} tableIndex - 表格索引
 * @param {Array} headers - 表头数据
 * @param {Array} rows - 表格行数据
 * @returns {Promise} axios请求Promise
 */
export const editTable = (file, tableIndex, headers, rows) => {
  const formData = new FormData();
  formData.append("file", file);
  if (tableIndex !== undefined && tableIndex !== null) {
    formData.append("table_index", tableIndex.toString());
  }
  if (headers && headers.length > 0) {
    formData.append("headers", JSON.stringify(headers));
  }
  if (rows && rows.length > 0) {
    formData.append("rows", JSON.stringify(rows));
  }

  return axiosInstance.post(`/edit/table`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 下载修正后的文件（包含图片和表格修正）
 * @param {string} fileId - 文件ID
 * @param {string} originalFilename - 原始文件名
 * @param {Array} images - 图片修正数据
 * @param {Array} tables - 表格修正数据
 * @returns {Promise} 下载Promise
 */
export const downloadFixedFile = async (fileId, originalFilename, images = [], tables = []) => {
  try {
    const response = await axiosInstance.post(`/download/fixed`, {
      file_id: fileId,
      filename: originalFilename,
      images,
      tables
    }, {
      responseType: 'blob',
      timeout: 60000,
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const nameWithoutExt = originalFilename.replace(/\.[^/.]+$/, '') || '文档';
    const filename = `${nameWithoutExt}_修正版.docx`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      link.remove();
      window.URL.revokeObjectURL(url);
    }, 1000);
  } catch (error) {
    console.error('下载失败:', error);
    throw error;
  }
};

/**
 * 批量修正所有错误
 * @param {File} file - 文件对象
 * @param {Array} errorIndices - 要修正的错误索引列表（null表示全部修正）
 * @returns {Promise} axios请求Promise
 */
export const fixAllErrors = async (file, errorIndices = null) => {
  const formData = new FormData();
  formData.append("file", file);
  if (errorIndices && errorIndices.length > 0) {
    formData.append("error_indices", errorIndices.join(","));
  }

  return axiosInstance.post(`/fix/all`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 导出axios实例，方便其他地方使用
export default axiosInstance;
