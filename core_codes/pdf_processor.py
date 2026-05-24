import io
import os
import base64

# 延迟导入依赖，避免启动时加载
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("[WARNING] PyMuPDF模块未找到，将无法处理PDF文件")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[WARNING] PIL模块未找到，将无法处理图片")

try:
    from .image_ocr import extract_text_from_image_bytes
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False
    print("[WARNING] image_ocr模块未找到，将无法进行图片OCR识别")

# =========================
# PDF 论文级解析器（完整版）
# =========================

def extract_pdf_structure(pdf_path, password=None):
    """
    提取PDF文档的结构化内容
    
    Args:
        pdf_path: PDF文件路径
        password: PDF密码（可选）
        
    Returns:
        dict: 包含text、images、tables、metadata的结构化数据
    """
    doc = None
    try:
        # 尝试打开PDF，支持加密文档
        doc = fitz.open(pdf_path)
        
        # 如果PDF加密，尝试解密
        if doc.is_encrypted:
            if password:
                if not doc.authenticate(password):
                    print("❌ PDF密码错误")
                    return {"text": [], "images": [], "tables": [], "metadata": {}}
            else:
                print("❌ PDF已加密，请提供密码")
                return {"text": [], "images": [], "tables": [], "metadata": {}}

        texts = []
        images = []
        tables = []
        
        # 获取文档元数据
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", ""),
            "page_count": len(doc)
        }

        for page_index, page in enumerate(doc):

            # =====================
            # 1. 文本提取（保留结构）
            # =====================
            try:
                # 获取纯文本
                page_text = page.get_text("text")
                if page_text.strip():
                    texts.append({
                        "page": page_index + 1,
                        "type": "text",
                        "content": page_text
                    })
                
                # 获取带布局的文本（用于分析结构）
                blocks = page.get_text("blocks")
                for block in blocks:
                    if len(block) >= 4:
                        x0, y0, x1, y1, text, block_type, page_num = block[:7]
                        if block_type == 0 and text.strip():  # 文本块
                            texts.append({
                                "page": page_index + 1,
                                "type": "text_block",
                                "content": text.strip(),
                                "position": {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
                            })
            except Exception as e:
                print(f"❌ 提取页面文本失败 (第{page_index + 1}页): {e}")

            # =====================
            # 2. 图片提取（核心🔥）
            # =====================
            try:
                for img in page.get_images(full=True):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # 获取图片位置信息
                    img_rects = page.get_image_rects(xref)
                    position = None
                    if img_rects:
                        rect = img_rects[0]
                        position = {"x0": rect.x0, "y0": rect.y0, "x1": rect.x1, "y1": rect.y1}

                    images.append({
                        "page": page_index + 1,
                        "image": image_bytes,
                        "extension": image_ext,
                        "position": position,
                        "width": base_image.get("width", 0),
                        "height": base_image.get("height", 0)
                    })
            except Exception as e:
                print(f"❌ 提取页面图片失败 (第{page_index + 1}页): {e}")

            # =====================
            # 3. 表格提取
            # =====================
            try:
                tabs = page.find_tables()
                if tabs:
                    for tab in tabs:
                        table_data = []
                        # 获取表格边界框（可能是 Rect 对象或 tuple）
                        bbox = tab.bbox
                        if hasattr(bbox, 'x0'):
                            bx0, by0, bx1, by1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
                        else:
                            bx0, by0, bx1, by1 = bbox[0], bbox[1], bbox[2], bbox[3]
                        # 提取表格内容
                        for row in tab.extract():
                            row_data = []
                            for cell in row:
                                if cell:
                                    row_data.append(str(cell).strip())
                                else:
                                    row_data.append("")
                            table_data.append(row_data)
                        
                        tables.append({
                            "page": page_index + 1,
                            "content": table_data,
                            "bbox": {"x0": bx0, "y0": by0, "x1": bx1, "y1": by1},
                            "rows": len(table_data),
                            "cols": len(table_data[0]) if table_data else 0
                        })
            except Exception as e:
                print(f"❌ 提取页面表格失败 (第{page_index + 1}页): {e}")

            # =====================
            # 4. 页面尺寸信息
            # =====================
            try:
                page_rect = page.rect
                metadata[f"page_{page_index + 1}_size"] = {
                    "width": page_rect.width,
                    "height": page_rect.height
                }
            except Exception as e:
                pass

        return {
            "text": texts,
            "images": images,
            "tables": tables,
            "metadata": metadata
        }
    except Exception as e:
        print(f"❌ 解析PDF文件失败: {e}")
        return {
            "text": [],
            "images": [],
            "tables": [],
            "metadata": {}
        }
    finally:
        if doc:
            try:
                doc.close()
            except:
                pass


# =========================
# OCR（用于扫描PDF / 图片）
# =========================
def ocr_image(image_bytes, lang="chi_sim+eng"):
    """
    对图片字节进行OCR文字识别
    
    Args:
        image_bytes: 图片字节数据
        lang: 语言设置，默认中文+英文
        
    Returns:
        str: 识别出的文本
    """
    if not HAS_EASYOCR:
        print("⚠️  OCR功能不可用，image_ocr模块未加载")
        return ""
    
    try:
        # 使用image_ocr模块进行OCR识别
        text = extract_text_from_image_bytes(image_bytes)
        return text.strip()
    except Exception as e:
        print(f"❌ OCR识别失败: {e}")
        return ""


# =========================
# PDF转图片
# =========================
def pdf_to_images(pdf_path, output_dir=None, dpi=300, password=None):
    """
    将PDF每页转换为图片
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录，不指定则返回图片字节列表
        dpi: 图片分辨率，默认300
        password: PDF密码（可选）
        
    Returns:
        list: 如果指定output_dir返回文件路径列表，否则返回图片字节列表
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        
        # 如果PDF加密，尝试解密
        if doc.is_encrypted:
            if password:
                if not doc.authenticate(password):
                    print("❌ PDF密码错误")
                    return []
            else:
                print("❌ PDF已加密，请提供密码")
                return []
        
        results = []
        
        for page_index, page in enumerate(doc):
            # 设置渲染参数
            matrix = fitz.Matrix(dpi / 72, dpi / 72)  # 72是默认DPI
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            image_bytes = pix.tobytes("png")
            
            if output_dir:
                # 确保输出目录存在
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"page_{page_index + 1}.png")
                pix.save(output_path)
                results.append(output_path)
            else:
                results.append({
                    "page": page_index + 1,
                    "image": image_bytes,
                    "width": pix.width,
                    "height": pix.height
                })
        
        return results
    except Exception as e:
        print(f"❌ PDF转图片失败: {e}")
        return []
    finally:
        if doc:
            try:
                doc.close()
            except:
                pass


# =========================
# 构建表格单元格文本集合（用于去重）
# =========================
def _build_table_cell_set(tables_data):
    """
    构建表格单元格文本集合（用于去重）
    
    Args:
        tables_data: 表格数据列表
        
    Returns:
        set: 单元格文本集合
    """
    cell_set = set()
    for tb in tables_data:
        for row in tb.get("content", []):
            for cell in row:
                cell_text = str(cell).strip()
                if cell_text and len(cell_text) > 1:
                    cell_set.add(cell_text)
    return cell_set


def _filter_table_lines(text_content, table_cell_set):
    """
    从文本内容中过滤掉表格单元格内容
    
    Args:
        text_content: 文本内容
        table_cell_set: 表格单元格文本集合
        
    Returns:
        str: 过滤后的文本
    """
    if not table_cell_set:
        return text_content

    lines = text_content.split("\n")
    filtered_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("【PDF表格") or stripped.startswith("【图片OCR"):
            continue
        if stripped in table_cell_set:
            continue
        if len(stripped) < 3:
            filtered_lines.append(stripped)
            continue
        # 检查该行是否主要由表格单元格片段拼接而成
        # 如果该行中超过50%的非空白子串存在于table_cell_set中，则视为表格行
        fragments = [s.strip() for s in stripped.replace("\t", " ").split() if len(s.strip()) > 1]
        if not fragments:
            filtered_lines.append(stripped)
            continue
        match_count = sum(1 for f in fragments if f in table_cell_set)
        if len(fragments) >= 3 and match_count >= len(fragments) * 0.5:
            continue
        filtered_lines.append(stripped)

    return "\n".join(filtered_lines)


def _build_full_table_text_set(tables_data):
    """
    构建表格的完整文本行集合（用于精确去重）
    
    Args:
        tables_data: 表格数据列表
        
    Returns:
        set: 表格行文本集合
    """
    row_set = set()
    for tb in tables_data:
        for row in tb.get("content", []):
            row_text = " ".join([str(cell).strip() for cell in row if cell and str(cell).strip()])
            if row_text:
                row_set.add(row_text)
    return row_set


def _build_table_cell_set(tables_data):
    """
    构建表格的单元格文本集合（用于单元格级别去重）
    
    Args:
        tables_data: 表格数据列表
        
    Returns:
        set: 单元格文本集合
    """
    cell_set = set()
    for tb in tables_data:
        for row in tb.get("content", []):
            for cell in row:
                cell_text = str(cell).strip()
                if cell_text and len(cell_text) > 1:
                    cell_set.add(cell_text)
    return cell_set


def _is_mostly_table_content(text_line, table_cell_set):
    """
    判断一行文本是否主要由表格单元格内容组成
    
    Args:
        text_line: 待判断的文本行
        table_cell_set: 表格单元格文本集合
        
    Returns:
        bool: 是否主要为表格内容
    """
    if not table_cell_set:
        return False

    stripped = text_line.strip()
    if not stripped or len(stripped) < 3:
        return False

    fragments = [s.strip() for s in stripped.replace("\t", " ").split() if len(s.strip()) > 1]
    if not fragments:
        return False

    match_count = sum(1 for f in fragments if f in table_cell_set)
    return len(fragments) >= 3 and match_count >= len(fragments) * 0.5


def _remove_table_duplicates(text_content, tables_data):
    """
    从文本内容中删除与表格内重复的行
    
    Args:
        text_content: 文本内容
        tables_data: 表格数据列表
        
    Returns:
        str: 去重后的文本
    """
    if not tables_data:
        return text_content

    table_row_set = _build_full_table_text_set(tables_data)
    table_cell_set = _build_table_cell_set(tables_data)
    if not table_row_set and not table_cell_set:
        return text_content

    lines = text_content.split("\n")
    filtered_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("【PDF表格") or stripped.startswith("【图片OCR"):
            continue

        # 整行与表格行完全相同 -> 删除
        if stripped in table_row_set:
            continue

        # 整行与单个单元格内容完全相同 -> 删除
        if stripped in table_cell_set:
            continue

        # 检查是否主要由表格单元格内容组成（超过50%片段匹配）-> 删除
        if _is_mostly_table_content(stripped, table_cell_set):
            continue

        # 其他情况保留（正常正文段落）
        filtered_lines.append(stripped)

    return "\n".join(filtered_lines)


# =========================
# PDF文本提取（兼容旧接口）
# =========================
def extract_text_from_pdf(pdf_path, password=None):
    """
    提取PDF中的文本内容（兼容旧接口）
    
    Args:
        pdf_path: PDF文件路径
        password: PDF密码（可选）
        
    Returns:
        str: 提取的文本内容（包含图片OCR结果）
    """
    try:
        data = extract_pdf_structure(pdf_path, password)
        final_text = []

        # 按页分组，避免 text 和 text_block 重复
        pages_with_text = set()
        pages_with_blocks = set()

        for t in data["text"]:
            page = t.get("page", 1)
            ttype = t.get("type", "")
            if ttype == "text":
                pages_with_text.add(page)
            elif ttype == "text_block":
                pages_with_blocks.add(page)

        for t in data["text"]:
            if "content" not in t:
                continue
            content = t["content"].strip()
            if not content:
                continue
            if content.startswith("【PDF表格") or content.startswith("【图片OCR"):
                continue

            page = t.get("page", 1)
            ttype = t.get("type", "")

            if ttype == "text":
                if content.strip():
                    final_text.append(content)
            elif ttype == "text_block":
                if page in pages_with_text:
                    continue
                if content.strip():
                    final_text.append(content)

        # ===== OCR图片补充 =====
        for img in data["images"]:
            ocr_result = ocr_image(img["image"])
            if ocr_result:
                final_text.append(f"\n【图片OCR(第{img['page']}页)】\n{ocr_result}")

        return "\n\n".join(final_text)
    except Exception as e:
        print(f"❌ 提取PDF文本失败: {e}")
        return ""


# =========================
# 获取PDF页数
# =========================
def get_pdf_page_count(pdf_path, password=None):
    """
    获取PDF文档的页数
    
    Args:
        pdf_path: PDF文件路径
        password: PDF密码（可选）
        
    Returns:
        int: PDF页数
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        
        if doc.is_encrypted:
            if password:
                if not doc.authenticate(password):
                    return 0
            else:
                return 0
        
        return len(doc)
    except Exception as e:
        print(f"❌ 获取PDF页数失败: {e}")
        return 0
    finally:
        if doc:
            try:
                doc.close()
            except:
                pass


# =========================
# 检查PDF是否加密
# =========================
def is_pdf_encrypted(pdf_path):
    """
    检查PDF是否加密
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        bool: 是否加密
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        return doc.is_encrypted
    except Exception as e:
        print(f"❌ 检查PDF加密状态失败: {e}")
        return False
    finally:
        if doc:
            try:
                doc.close()
            except:
                pass


# =========================
# 提取PDF中的图片并保存
# =========================
def extract_pdf_images(pdf_path, output_dir, password=None):
    """
    提取PDF中的所有图片并保存到指定目录
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        password: PDF密码（可选）
        
    Returns:
        list: 保存的图片路径列表
    """
    try:
        data = extract_pdf_structure(pdf_path, password)
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        for i, img in enumerate(data["images"], 1):
            filename = f"image_{img['page']}_{i}.{img['extension']}"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(img["image"])
            saved_paths.append(filepath)
        
        return saved_paths
    except Exception as e:
        print(f"❌ 提取PDF图片失败: {e}")
        return []


# =========================
# 主入口（给API用）
# =========================
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python pdf_processor.py <pdf_path> [output_dir]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if output_dir:
        # 提取图片
        images = extract_pdf_images(pdf_path, output_dir)
        print(f"✅ 已提取 {len(images)} 张图片到 {output_dir}")
    else:
        # 提取文本
        text = extract_text_from_pdf(pdf_path)
        print("✅ 提取的文本内容（前2000字符）:")
        print(text[:2000])
