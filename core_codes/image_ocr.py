import os
import io
import numpy as np
from PIL import Image
import base64

# ===================== 云GPU 固定配置 =====================
USE_GPU = True

# =================================================================

from paddleocr import PaddleOCR
HAS_PADDLEOCR = True

ocr = None

def get_ocr():
    global ocr
    if ocr is None:
        try:
            # 🔥 只留 lang，其他全部删除！
            ocr = PaddleOCR(lang="ch")
            print("✅ PaddleOCR初始化成功")
        except Exception as e:
            print(f"❌ PaddleOCR初始化失败: {e}")
            return None
    return ocr


def extract_text_from_image(image_path, use_preprocess=True, lang=['ch_sim', 'en']):
    try:
        if isinstance(image_path, str):
            if not os.path.exists(image_path):
                print("❌ 图片路径不存在")
                return ""
            input_img = image_path
        elif isinstance(image_path, bytes):
            input_img = image_path
        else:
            print("❌ 无效的图片输入")
            return ""

        ocr_engine = get_ocr()
        if ocr_engine is None:
            return ""

        results = ocr_engine.ocr(input_img)

        texts = []
        if results:
            for line in results:
                for word in line:
                    texts.append(word[1][0])

        return "\n".join(texts)

    except Exception as e:
        print(f"❌ PaddleOCR识别失败: {e}")
        return ""


def extract_text_from_image_bytes(image_bytes, use_preprocess=True, lang=['ch_sim', 'en']):
    return extract_text_from_image(image_bytes, use_preprocess, lang)


def image_to_base64(image_path):
    try:
        if isinstance(image_path, str):
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
        else:
            encoded = base64.b64encode(image_path).decode("utf-8")
        return encoded
    except Exception as e:
        print(f"❌ 图片转Base64失败: {e}")
        return ""


def base64_to_image(base64_str, output_path):
    try:
        image_data = base64.b64decode(base64_str)
        with open(output_path, "wb") as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"❌ Base64转图片失败: {e}")
        return False


def get_image_info(image_path):
    try:
        if isinstance(image_path, str):
            image = Image.open(image_path)
            file_size = os.path.getsize(image_path)
        else:
            image = Image.open(io.BytesIO(image_path))
            file_size = len(image_path)
        
        info = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "channels": len(image.getbands()),
            "file_size": file_size
        }
        return info
    except Exception as e:
        print(f"❌ 获取图片信息失败: {e}")
        return {}


def resize_image(image_path, max_width=1920, max_height=1080, output_path=None):
    try:
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = Image.open(io.BytesIO(image_path))
        
        width, height = image.size
        scale = min(max_width / width, max_height / height)
        
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        if output_path:
            image.save(output_path)
            return output_path
        else:
            return image
    except Exception as e:
        print(f"❌ 调整图片大小失败: {e}")
        return None


def convert_image_format(image_path, output_path, format="PNG"):
    try:
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = Image.open(io.BytesIO(image_path))
            
        image.save(output_path, format=format)
        return True
    except Exception as e:
        print(f"❌ 转换图片格式失败: {e}")
        return False


def extract_images_from_pdf(pdf_path, output_dir):
    try:
        from pdf_processor import extract_pdf_images
        return extract_pdf_images(pdf_path, output_dir)
    except Exception as e:
        print(f"❌ 从PDF提取图片失败: {e}")
        return []


def close_ocr():
    global ocr
    ocr = None
    print("✅ PaddleOCR资源已释放")


# =========================
# 主入口
# =========================
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python image_ocr.py <image_path> [output_text_path]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    text = extract_text_from_image(image_path)
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ 识别结果已保存到 {output_path}")
    else:
        print("✅ 识别结果:")
        print(text)