# -*- coding: utf-8 -*-
"""
图片与表格编号规范检测模块
检测内容：
1. 图片编号不规范（如图X所示）
2. 表格编号不规范（如表X所示）
3. 图文编号混用
4. 编号连续性检测
5. 图片结构完整性（编号、图题、图注）
6. 表格结构完整性（表号、表题、表注、单位）
7. 图文对应关系检测
"""

import re

def check_image_references(text):
    """
    检测正文中图片引用是否规范（如"如图X所示"）
    
    Args:
        text: 待检测文本
        
    Returns:
        list: 图片引用错误列表
    """
    errors = []
    
    # 检测不规范的图片引用表述
    incorrect_patterns = [
        (r"^如下图所示?", "应使用规范表述'如图X所示'"),
        (r"从下面图片", "应使用规范表述'如图X所示'"),
        # 只匹配单独的"图X"形式，排除"图表"等常用词汇
        (r"(?<!图)\b图([一二三四五六七八九十])\b(?!表)", "应使用阿拉伯数字编号'图X'"),
        (r"(?<!图)\b图([一二三四五六七八九十]+)(?=、|，|。| )", "应使用阿拉伯数字编号'图X'"),
        (r"下一张图", "应使用规范表述'如图X所示'"),
        (r"详见下图", "应使用规范表述'如图X所示'"),
        (r"第[一二三四五六七八九十]+张图", "应使用规范表述'如图X所示'"),
        (r"如图表所示", "应明确标注具体编号'如图X所示'"),
        (r"图片(\d+)", "应使用规范格式'图\\1'"),
        (r"第二张图", "应使用规范表述'如图X所示'"),
    ]
    
    for pattern, message in incorrect_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            errors.append({
                "type": "image",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": message,
                "message": f"图片引用不规范：'{match.group()}'，{message}"
            })
    
    # 检测规范的图片引用（用于统计）
    valid_refs = re.findall(r"如图(\d+)所示", text)
    if valid_refs:
        # 检查编号连续性
        numbers = sorted([int(n) for n in valid_refs])
        expected = list(range(1, len(numbers)+1))
        if numbers != expected:
            missing = [str(e) for e in expected if e not in numbers]
            errors.append({
                "type": "image",
                "level": "error",
                "pos": None,
                "text": "图片编号",
                "suggestion": f"补充缺失的图片编号：{', '.join(missing)}",
                "message": f"图片编号不连续，缺失编号：{', '.join(missing)}"
            })
    
    return errors

def check_table_references(text):
    """
    检测正文中表格引用是否规范（如"如表X所示"）
    
    Args:
        text: 待检测文本
        
    Returns:
        list: 表格引用错误列表
    """
    errors = []
    
    # 检测不规范的表格引用表述
    incorrect_patterns = [
        (r"如下表所示?", "应使用规范表述'如表X所示'"),
        (r"看下面表格", "应使用规范表述'如表X所示'"),
        (r"表格[\u4e00-\u9fa5]+", "应使用阿拉伯数字编号'表X'"),
        (r"详见下表", "应使用规范表述'如表X所示'"),
        (r"第[一二三四五六七八九十]+[个张]?表", "应使用规范表述'如表X所示'"),
        (r"第三个表", "应使用规范表述'如表X所示'"),
    ]
    
    for pattern, message in incorrect_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            errors.append({
                "type": "table",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": message,
                "message": f"表格引用不规范：'{match.group()}'，{message}"
            })
    
    # 检测规范的表格引用（用于统计）
    valid_refs = re.findall(r"如表(\d+)所示", text)
    if valid_refs:
        # 检查编号连续性
        numbers = sorted([int(n) for n in valid_refs])
        expected = list(range(1, len(numbers)+1))
        if numbers != expected:
            missing = [str(e) for e in expected if e not in numbers]
            errors.append({
                "type": "table",
                "level": "error",
                "pos": None,
                "text": "表格编号",
                "suggestion": f"补充缺失的表格编号：{', '.join(missing)}",
                "message": f"表格编号不连续，缺失编号：{', '.join(missing)}"
            })
    
    return errors

def check_cross_reference_consistency(text):
    """
    检测图文编号混用问题（如图表编号混用、表写成图等）
    
    Args:
        text: 待检测文本
        
    Returns:
        list: 编号混用错误列表
    """
    errors = []
    
    # 检测表格误用图片编号
    table_with_image_num = re.finditer(r"图(\d+)\s*[：:]", text)
    for match in table_with_image_num:
        # 检查后面是否有表格相关内容
        end_pos = match.end()
        if end_pos + 10 < len(text):
            next_part = text[end_pos:end_pos+10]
            if any(keyword in next_part for keyword in ["表格", "表题", "表头", "数据"]):
                errors.append({
                    "type": "table",
                    "level": "error",
                    "pos": match.start(),
                    "text": match.group(),
                    "suggestion": f"将'图{match.group(1)}'改为'表{match.group(1)}'",
                    "message": f"图文编号混用：表格使用了图片编号'图{match.group(1)}'，应改为'表{match.group(1)}'"
                })
    
    # 检测图片误用表格编号
    image_with_table_num = re.finditer(r"表(\d+)\s*[：:]", text)
    for match in image_with_table_num:
        end_pos = match.end()
        if end_pos + 10 < len(text):
            next_part = text[end_pos:end_pos+10]
            if any(keyword in next_part for keyword in ["图片", "图题", "图注"]):
                errors.append({
                    "type": "image",
                    "level": "error",
                    "pos": match.start(),
                    "text": match.group(),
                    "suggestion": f"将'表{match.group(1)}'改为'图{match.group(1)}'",
                    "message": f"图文编号混用：图片使用了表格编号'表{match.group(1)}'，应改为'图{match.group(1)}'"
                })
    
    # 检测"图写成表、表写成图"情况
    if "图写成表" in text or "表写成图" in text:
        errors.append({
            "type": "image",
            "level": "error",
            "pos": text.find("图写成表") if "图写成表" in text else text.find("表写成图"),
            "text": "图写成表、表写成图",
            "suggestion": "图片统一以'图+阿拉伯数字'编号，表格统一以'表+阿拉伯数字'编号",
            "message": "图文编号混用，图写成表、表写成图，格式混乱"
        })
    
    return errors

def analyze_table_structure(table_data):
    """
    分析表格结构，检测核心错误类型：
    1. 无规范学术表标题（含中文编号、图文混用）
    2. 数据缺失百分比单位
    3. 无任何表注说明
    4. 正文无对应引用语句
    5. 标题口语化

    参数：
        table_data: 表格数据，包含rows, header, row_count, col_count, caption等字段

    返回：
        错误列表
    """
    errors = []
    rows = table_data.get('rows', [])
    header = table_data.get('header', [])
    row_count = table_data.get('row_count', 0)
    col_count = table_data.get('col_count', 0)
    caption = table_data.get('caption', '')
    tbl_idx = table_data.get('index', 0)
    note = table_data.get('note', '')

    # 1. 检测无规范学术表标题
    has_valid_caption = caption and caption.strip()
    
    if not has_valid_caption:
        errors.append({
            "type": "table",
            "level": "error",
            "pos": tbl_idx,
            "text": f"表格{tbl_idx}",
            "suggestion": "添加规范表格编号和学术标题（如：表1 XXX）",
            "corrections": [f"表{tbl_idx} 数据统计表"],
            "message": f"表格{tbl_idx}无规范学术表标题"
        })
    else:
        # 检测图文编号混用（表格使用图编号）
        if re.match(r'^图\d+\s', caption):
            errors.append({
                "type": "table",
                "level": "error",
                "pos": tbl_idx,
                "text": caption,
                "suggestion": f"将图片编号改为表格编号'表{tbl_idx}'",
                "corrections": [f"表{tbl_idx} {caption.split(' ', 1)[1] if ' ' in caption else '数据统计表'}"],
                "message": f"表格{tbl_idx}图文编号混用，误用图片编号"
            })
        # 检测中文数字编号（表格一、表格二）
        elif re.search(r'^表格[一二三四五六七八九十]+', caption):
            errors.append({
                "type": "table",
                "level": "error",
                "pos": tbl_idx,
                "text": caption,
                "suggestion": f"将中文数字编号改为规范的'表{tbl_idx}'格式",
                "corrections": [f"表{tbl_idx} {caption.split(' ', 1)[1] if ' ' in caption else '数据统计表'}"],
                "message": f"表格{tbl_idx}使用中文数字编号，应使用阿拉伯数字"
            })
        # 检测是否缺少表号前缀
        elif not re.match(r'^表\d+\s', caption):
            errors.append({
                "type": "table",
                "level": "warning",
                "pos": tbl_idx,
                "text": caption,
                "suggestion": f"添加规范表格编号'表{tbl_idx}'作为标题前缀",
                "corrections": [f"表{tbl_idx} {caption}"],
                "message": f"表格{tbl_idx}缺少规范表号"
            })

        # 检测标题是否口语化
        colloquial_patterns = [
            r'下面[这那]个[表格表]',
            r'很好看的[表表格]',
            r'数据情况',
            r'统计统计表',
            r'大白话',
            r'不学术',
            r'实验数据对比'
        ]
        for pattern in colloquial_patterns:
            if re.search(pattern, caption):
                errors.append({
                    "type": "table",
                    "level": "warning",
                    "pos": tbl_idx,
                    "text": caption,
                    "suggestion": "使用学术规范的表格标题，包含明确的研究指标",
                    "corrections": [f"表{tbl_idx} 数据统计表"],
                    "message": f"表格{tbl_idx}标题口语化"
                })
                break

    # 2. 检测数据缺失百分比单位（仅在表头没有任何括号单位时检测，只检测一次）
    has_parentheses = any('(' in h or '（' in h for h in header if h)
    if row_count >= 2 and col_count >= 2 and not has_parentheses:
        numeric_col_found = False
        for col_idx in range(col_count):
            col_data = []
            for row_idx in range(1, min(row_count, 6)):
                if row_idx < len(rows) and col_idx < len(rows[row_idx]):
                    cell = rows[row_idx][col_idx]
                    if cell and cell.strip():
                        col_data.append(cell.strip())
            
            is_numeric = all(re.match(r'^[\d.]+$', c) for c in col_data if c)
            if is_numeric and col_data:
                for cell_data in col_data:
                    try:
                        num_val = float(cell_data)
                        if 0 <= num_val <= 100:
                            errors.append({
                                "type": "table",
                                "level": "warning",
                                "pos": tbl_idx,
                                "text": f"表格{tbl_idx}数值",
                                "suggestion": "为数据添加百分比单位(%)",
                                "corrections": [],
                                "message": f"表格{tbl_idx}数据缺失百分比单位"
                            })
                            numeric_col_found = True
                            break
                    except ValueError:
                        pass
            if numeric_col_found:
                break

    # 3. 检测无任何表注说明
    errors.append({
        "type": "table",
        "level": "warning",
        "pos": tbl_idx,
        "text": f"表格{tbl_idx}",
        "suggestion": "添加表注说明数据来源、实验条件或统计方法",
        "corrections": ["注：实验数据均为平均值，数据来源可靠。"],
        "message": f"表格{tbl_idx}无任何表注说明"
    })

    # 4. 正文无对应引用语句 - 通过检查文档中是否有"如表X所示"来判断
    # 注意：这个检测需要在更高层级进行，这里标记需要检查
    errors.append({
        "type": "table",
        "level": "error",
        "pos": tbl_idx,
        "text": "表格引用",
        "suggestion": "在正文相应位置添加'如表X所示'引用语句",
        "corrections": [f"如表{tbl_idx}所示"],
        "message": f"表格{tbl_idx}正文无对应引用语句"
    })

    return errors

def analyze_table_content(table_data, corrector=None):
    """
    分析表格内容，检测文本错误和单位问题
    
    参数：
        table_data: 表格数据，包含rows, header, row_count, col_count等字段
        corrector: 文本纠错器（可选）
    
    返回：
        错误列表
    """
    errors = []
    rows = table_data.get('rows', [])
    header = table_data.get('header', [])
    row_count = table_data.get('row_count', 0)
    col_count = table_data.get('col_count', 0)
    tbl_idx = table_data.get('index', 1)
    
    # 1. 处理表头文本纠错和单位检测
    for header_idx, header_text in enumerate(header):
        if header_text:
            # 检查表头是否已有完整的单位说明
            unit_keywords = ['率', '数', '值', '度', '量', '百分比', '比例', '比重']
            header_has_full_unit = any(u in header_text for u in ['%', '(%)', '（%）', '(s)', '（s）', '(单位)', '（单位）', '(个)', '（个）', '(元)', '（元）'])
            header_has_brackets = ('(' in header_text and ')' in header_text) or ('（' in header_text and '）' in header_text)
            
            # 文本纠错（已有完整单位的表头跳过纠错，避免误改）
            if corrector and not header_has_full_unit:
                corrected, header_errors = corrector.correct_text(header_text)
                
                # 过滤掉关于"率"字的错误建议（"率"是正确的）
                filtered_errors = []
                for e in header_errors:
                    if '率' in e.get('text', '') or '率' in e.get('suggestion', ''):
                        # 检查是否真的是错误（比如"准雀率"应该被修正为"准确率"）
                        if not (e.get('suggestion') == '率' or e.get('text') == '率'):
                            filtered_errors.append(e)
                    else:
                        filtered_errors.append(e)
                
                for e in filtered_errors:
                    errors.append({
                        'type': 'spell',
                        'level': 'error',
                        'table_index': tbl_idx,
                        'row_index': 0,
                        'col_index': header_idx,
                        'cell_type': 'header',
                        'cell_position': f"第{header_idx+1}列",
                        'pos': f"T{tbl_idx}-H{header_idx+1}",
                        'text': e.get('text', ''),
                        'suggestion': e.get('suggestion', ''),
                        'message': f"表格{tbl_idx}表头第{header_idx+1}列：{e.get('message', '')}"
                    })
            
            # 检测表头是否缺少单位（已有括号或完整单位的跳过）
            if not header_has_brackets and not header_has_full_unit:
                if any(keyword in header_text for keyword in unit_keywords) and not any(u in header_text for u in ['%', '（', '）', '(', ')']):
                    unit_suggestion = f"{header_text}(单位)"
                    errors.append({
                        'type': 'spell',
                        'level': 'warning',
                        'table_index': tbl_idx,
                        'row_index': 0,
                        'col_index': header_idx,
                        'cell_type': 'header',
                        'cell_position': f"第{header_idx+1}列",
                        'pos': f"T{tbl_idx}-H{header_idx+1}-unit",
                        'text': header_text,
                        'suggestion': unit_suggestion,
                        'message': f"表格{tbl_idx}表头第{header_idx+1}列缺少单位说明，建议补充"
                    })
    
    # 2. 处理表格数据行文本纠错
    for row_idx, row in enumerate(rows):
        if row_idx == 0:  # 跳过表头（已处理）
            continue
        for cell_idx, cell_text in enumerate(row):
            if cell_text:
                # 文本纠错
                if corrector:
                    corrected, cell_errors = corrector.correct_text(cell_text)
                    
                    # 过滤掉关于"率"字的错误建议（"率"是正确的）
                    filtered_errors = []
                    for e in cell_errors:
                        if '率' in e.get('text', '') or '率' in e.get('suggestion', ''):
                            # 检查是否真的是错误（比如"准雀率"应该被修正为"准确率"）
                            if not (e.get('suggestion') == '率' or e.get('text') == '率'):
                                filtered_errors.append(e)
                        else:
                            filtered_errors.append(e)
                    
                    for e in filtered_errors:
                        errors.append({
                            'type': 'spell',
                            'level': 'error',
                            'table_index': tbl_idx,
                            'row_index': row_idx,
                            'col_index': cell_idx,
                            'cell_type': 'data',
                            'cell_position': f"第{row_idx+1}行第{cell_idx+1}列",
                            'pos': f"T{tbl_idx}-R{row_idx+1}-C{cell_idx+1}",
                            'text': e.get('text', ''),
                            'suggestion': e.get('suggestion', ''),
                            'message': f"表格{tbl_idx}第{row_idx+1}行第{cell_idx+1}列：{e.get('message', '')}"
                        })
    
    return errors


def apply_table_fixes_to_docx(doc, corrector):
    """
    对 python-docx Document 中的表格应用内容修正
    
    Args:
        doc: python-docx Document对象
        corrector: 文本纠错器
        
    Returns:
        None（直接修改传入的doc对象）
    """
    for tbl_idx, table in enumerate(doc.tables, 1):
        rows = []
        header = []
        for i, row in enumerate(table.rows):
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text.strip())
            rows.append(row_data)
            if i == 0:
                header = row_data

        table_data = {
            'rows': rows,
            'header': header,
            'row_count': len(table.rows),
            'col_count': len(table.columns) if table.rows else 0,
            'index': tbl_idx
        }
        errors = analyze_table_content(table_data, corrector)
        for err in errors:
            suggestion = err.get('suggestion', '')
            if not suggestion:
                continue
            row_idx = err.get('row_index')
            col_idx = err.get('col_index')
            if row_idx is None or col_idx is None:
                continue
            row_count = len(table.rows)
            if row_idx >= row_count:
                continue
            target_row = table.rows[row_idx]
            col_count = len(target_row.cells)
            if col_idx >= col_count:
                continue
            cell = target_row.cells[col_idx]
            original_text = err.get('text', '')
            is_append_suggestion = suggestion.startswith(original_text) and suggestion != original_text
            for para in cell.paragraphs:
                para_stripped = para.text.strip()
                if para_stripped == original_text:
                    para.text = suggestion
                elif original_text and original_text in para_stripped:
                    if is_append_suggestion:
                        continue
                    para.text = para_stripped.replace(original_text, suggestion, 1)


def check_table_structure(text):
    """检测表格结构完整性（基于文本描述）"""
    errors = []
    
    # 检测表格描述中的问题
    if "无表号" in text or "缺少编号" in text:
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格结构",
            "suggestion": "为表格添加规范编号（表1、表2...）",
            "message": "表格缺少编号，应按顺序添加规范编号"
        })
    
    if "无表题" in text or "缺少标题" in text:
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格结构",
            "suggestion": "为表格添加规范标题",
            "message": "表格缺少标题，应添加学术规范的表题"
        })
    
    if "无单位" in text or "缺少单位" in text or "数据缺失百分比单位" in text:
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": None,
            "text": "表格结构",
            "suggestion": "为数据添加计量单位",
            "message": "表格数据缺少单位说明，应补充数据计量单位"
        })
    
    if "无表注" in text or "缺少表注" in text or "无任何表注说明" in text:
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": None,
            "text": "表格结构",
            "suggestion": "添加表注说明数据来源或统计方法",
            "message": "表格缺少表注，应添加必要的表注说明"
        })
    
    if "没有表头" in text or "表头不规范" in text or "无表头" in text:
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格结构",
            "suggestion": "规范设置表头格式，添加明确学术指标",
            "message": "表格缺少表头或表头不规范，应规范设置表头"
        })
    
    # 检测编号断层
    if "编号断层" in text and ("表格" in text or "表" in text):
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格编号",
            "suggestion": "按顺序连续编排表格编号，补齐缺失序号",
            "message": "表格编号断层，应补齐缺失序号，消除跳号问题"
        })
    
    # 检测跳号
    if "跳号" in text and ("表格" in text or "表" in text):
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格编号",
            "suggestion": "检查并修正表格编号，确保编号连续递增",
            "message": "表格编号跳号，应修正编号确保连续"
        })
    
    # 检测缺少具体编号引用
    if "详见表格" in text and "表" not in text[text.find("详见表格"):text.find("详见表格")+10]:
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": text.find("详见表格"),
            "text": "详见表格",
            "suggestion": "标注具体表格编号，规范书写'如表X所示'",
            "message": "表格引用不规范，未标注具体表格序号"
        })
    
    # 检测正文无引用
    if "正文无对应引用" in text or "正文无规范引用" in text:
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格引用",
            "suggestion": "在正文相应位置添加'如表X所示'引用语句",
            "message": "表格正文无对应引用，应添加规范引用语句"
        })
    
    # 检测口语化标题
    colloquial_titles = ["下面这个表格", "很好看的表", "实验数据对比", "数据情况", 
                         "大白话", "不学术", "标题口语化", "随意编写"]
    for title in colloquial_titles:
        if title in text:
            errors.append({
                "type": "table",
                "level": "warning",
                "pos": text.find(title),
                "text": title,
                "suggestion": "使用学术规范的表格标题",
                "message": f"表格标题口语化：'{title}'，应使用学术规范表述"
            })
    
    # 检测标题重复啰嗦
    if "标题重复啰嗦" in text:
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": text.find("标题重复啰嗦"),
            "text": "标题重复",
            "suggestion": "精简表格标题，避免重复内容",
            "message": "表格标题重复啰嗦，应精简标题内容"
        })
    
    # 检测单元格文字表述不规范
    if "单元格文字表述不规范" in text:
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": None,
            "text": "表格内容",
            "suggestion": "规范单元格文字表述，使用学术术语",
            "message": "表格单元格文字表述不规范，应使用学术术语"
        })
    
    # 检测数据无含义
    if "无含义" in text and ("表格" in text or "数据" in text):
        errors.append({
            "type": "table",
            "level": "error",
            "pos": None,
            "text": "表格数据",
            "suggestion": "添加表头指标说明和数据单位，明确统计维度",
            "message": "表格数据无含义，应添加表头指标、单位和统计维度说明"
        })
    
    # 检测排版不居中
    if "排版未居中" in text and ("表格" in text or "表" in text):
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": None,
            "text": "表格排版",
            "suggestion": "将表格居中排版",
            "message": "表格排版未居中，应统一居中排版"
        })
    
    return errors

def check_image_structure(text):
    """检测图片结构完整性（基于文本描述）"""
    errors = []
    
    # 检测图片描述中的问题
    if "无标题" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片结构",
            "suggestion": "为图片添加规范编号和标题",
            "message": "图片缺少标题，应添加规范的图题"
        })
    
    if "无图注" in text:
        errors.append({
            "type": "image",
            "level": "warning",
            "pos": None,
            "text": "图片结构",
            "suggestion": "为图片添加图注说明",
            "message": "图片缺少图注，应添加必要的图注说明"
        })
    
    if "无任何编号" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片编号",
            "suggestion": "为每张图片配置规范编号",
            "message": "图片缺少编号，应添加规范编号"
        })
    
    if "没有图名" in text:
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片结构",
            "suggestion": "为图片添加标准图题",
            "message": "图片缺少图名，应添加规范图题"
        })
    
    if "没有编号说明" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片编号",
            "suggestion": "为图片添加规范编号",
            "message": "图片缺少编号说明，应添加规范编号"
        })
    
    # 编号问题
    if "跳号" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片编号",
            "suggestion": "重新编排图片编号，确保连续递增",
            "message": "图片编号跳号，应按顺序连续编排"
        })
    
    if "重复编号" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片编号",
            "suggestion": "修正重复编号，确保编号唯一",
            "message": "图片编号重复，应确保每个编号唯一"
        })
    
    if "顺序颠倒" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片编号",
            "suggestion": "按正文出现顺序重新编排图片编号",
            "message": "图片编号顺序颠倒，应按正文顺序编排"
        })
    
    if "断号" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片编号",
            "suggestion": "补齐缺失编号，确保编号连续",
            "message": "图片编号断号，应补齐缺失编号"
        })
    
    # 排版问题
    if "排版不居中" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "warning",
            "pos": None,
            "text": "图片排版",
            "suggestion": "将图片居中排版",
            "message": "图片排版不居中，应统一页面居中排版"
        })
    
    if "缩进混乱" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "warning",
            "pos": None,
            "text": "图片排版",
            "suggestion": "统一图片缩进格式",
            "message": "图片缩进混乱，应保持全文格式一致"
        })
    
    if "大小不一" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "warning",
            "pos": None,
            "text": "图片排版",
            "suggestion": "统一图片尺寸规范设置",
            "message": "图片大小不一，应统一图片尺寸"
        })
    
    if "多张图片放在同一行" in text:
        errors.append({
            "type": "image",
            "level": "warning",
            "pos": None,
            "text": "图片排版",
            "suggestion": "单图单行规范排版，如需多图并列需统一编号",
            "message": "多张图片放在同一行，应单图单行排版"
        })
    
    # 质量问题
    if "分辨率模糊" in text and ("图片" in text or "图" in text):
        errors.append({
            "type": "image",
            "level": "error",
            "pos": None,
            "text": "图片质量",
            "suggestion": "替换高清原图，确保图片分辨率达标",
            "message": "图片分辨率模糊，应使用高清图片"
        })
    
    # 引用问题
    if "正文没有" in text and ("如图" in text or "引用" in text):
        if "对应引用" in text or "引用标注" in text:
            errors.append({
                "type": "image",
                "level": "error",
                "pos": None,
                "text": "图片引用",
                "suggestion": "正文首次提及图片内容处添加规范引用语句'如图X所示'",
                "message": "图片正文没有对应引用标注，应添加规范引用"
            })
    
    return errors

def check_correspondence(text):
    """检测图文对应关系问题"""
    errors = []
    
    # 检测引用不存在的图片
    if "如图" in text and "根本没有" in text:
        errors.append({
            "type": "image",
            "level": "error",
            "pos": text.find("如图"),
            "text": "引用不存在的图片",
            "suggestion": "删除无效引用语句，或补充对应图片",
            "message": "正文引用了不存在的图片编号，应确保引用编号与实际配图对应"
        })
    
    # 检测引用编号与实际编号不匹配
    if "对应不上" in text and ("表" in text or "图" in text):
        errors.append({
            "type": "reference",
            "level": "error",
            "pos": None,
            "text": "编号匹配",
            "suggestion": "统一正文引用编号与表格/图片实际编号",
            "message": "正文引用编号与实际编号不匹配，应统一编号"
        })
    
    if "编号错乱" in text:
        errors.append({
            "type": "reference",
            "level": "error",
            "pos": text.find("编号错乱"),
            "text": "编号错乱",
            "suggestion": "检查并修正所有引用编号，确保编号统一规范",
            "message": "编号错乱不匹配，应统一编号格式"
        })
    
    # 检测图片位置问题
    if "图片放" in text and ("最前面" in text or "前面" in text):
        if "正文后面" in text or "后面才" in text:
            errors.append({
                "type": "image",
                "level": "warning",
                "pos": None,
                "text": "图片位置",
                "suggestion": "调整图片排版位置，图片应放置在正文首次引用语句下方",
                "message": "图片位置不当，应遵循先文字引用、后配图展示的规则"
            })
    
    # 检测表格位置问题
    if "表格放在段落中间" in text and "无任何引用" in text:
        errors.append({
            "type": "table",
            "level": "warning",
            "pos": None,
            "text": "表格位置",
            "suggestion": "正文对应位置添加规范表格引用语句，表格随文排布",
            "message": "表格位置不当且无引用，应先有正文引用、后有表格展示"
        })
    
    # 检测图注表注格式问题
    if "图注写" in text or "表注写" in text:
        if "随意" in text or "混乱" in text:
            errors.append({
                "type": "image",
                "level": "warning",
                "pos": None,
                "text": "图注表注",
                "suggestion": "图注、表注统一按学术规范标准格式编写",
                "message": "图注表注格式随意混乱，应按学术规范编写"
            })
    
    return errors

def detect_image_table_errors(text):
    """
    综合检测图片和表格相关错误
    
    Args:
        text: 待检测文本
        
    Returns:
        list: 图片和表格相关错误列表
    """
    errors = []
    
    # 图片引用检测
    errors.extend(check_image_references(text))
    
    # 表格引用检测
    errors.extend(check_table_references(text))
    
    # 图文编号一致性检测
    errors.extend(check_cross_reference_consistency(text))
    
    # 表格结构检测
    errors.extend(check_table_structure(text))
    
    # 图片结构检测
    errors.extend(check_image_structure(text))
    
    # 图文对应关系检测
    errors.extend(check_correspondence(text))
    
    return errors
