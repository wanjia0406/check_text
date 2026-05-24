# -*- coding: utf-8 -*-
"""
高级图片处理与OCR模块（使用PaddleOCR）
"""

import os
import io
import numpy as np
from PIL import Image
import base64

# 从 image_ocr 导入 PaddleOCR
try:
    from .image_ocr import extract_text_from_image as paddleocr_extract
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False


# =========================
# 图片质量分析
# =========================

def analyze_image_quality(image_input):
    """分析图片质量指标"""
    try:
        # 解析输入
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return {}
            image = Image.open(image_input)
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            return {}
        
        # 转换为灰度图
        if image.mode != "L":
            gray_image = image.convert("L")
        else:
            gray_image = image
        
        img_np = np.array(gray_image)
        
        # 计算质量指标
        brightness = np.mean(img_np)
        contrast = img_np.std()
        
        # 模糊度（拉普拉斯方差）
        from scipy.ndimage import laplace
        laplacian_img = laplace(img_np)
        blur_score = np.var(laplacian_img)
        
        return {
            "brightness": brightness,
            "contrast": contrast,
            "blur_score": blur_score,
            "width": image.width,
            "height": image.height
        }
    except Exception as e:
        print(f"❌ 图片质量分析失败: {e}")
        return {}


# =========================
# 主OCR识别函数（使用PaddleOCR）
# =========================

def extract_text_from_image(image_input, use_multiple_strategies=True, verbose=False):
    """
    从图片中提取文本（使用PaddleOCR）
    :param image_input: 图片文件路径、字节数据、PIL Image或numpy数组
    :param use_multiple_strategies: 保留兼容性，不再使用
    :param verbose: 是否输出详细日志
    :return: 识别出的文本
    """
    try:
        # 检查PaddleOCR是否可用
        if not HAS_PADDLEOCR:
            print("[WARNING] PaddleOCR不可用")
            return ""
        
        # 处理输入
        if isinstance(image_input, np.ndarray):
            # 如果是numpy数组，转换为bytes
            pil_img = Image.fromarray(image_input)
            buf = io.BytesIO()
            pil_img.save(buf, format='PNG')
            input_data = buf.getvalue()
        elif isinstance(image_input, Image.Image):
            # 如果是PIL Image，转换为bytes
            buf = io.BytesIO()
            image_input.save(buf, format='PNG')
            input_data = buf.getvalue()
        else:
            input_data = image_input
        
        # 使用PaddleOCR识别
        text = paddleocr_extract(input_data)
        
        if verbose:
            print(f"✅ PaddleOCR识别完成，识别到 {len(text.splitlines())} 行文本")
        
        return text
        
    except Exception as e:
        print(f"❌ PaddleOCR识别失败: {e}")
        return ""
