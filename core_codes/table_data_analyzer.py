# -*- coding: utf-8 -*-
"""
表格数据错误分类分析工具
专门检测表格内部数据的四种核心错误：
1. 无规范学术表标题
2. 数据缺失百分比单位
3. 无任何表注说明
4. 正文无对应引用语句
"""

import re

def analyze_table_data_errors(table_content):
    """
    分析表格内容，检测四种核心错误类型
    
    参数：
        table_content: 表格内容文本
    
    返回：
        错误列表，包含错误类型、位置、建议和详细信息
    """
    errors = []
    
    # 1. 检测无规范学术表标题
    title_match = re.search(r'^(表\d+)\s+(.+)', table_content, re.MULTILINE)
    if not title_match:
        errors.append({
            "type": "table_title",
            "level": "error",
            "pos": 0,
            "text": table_content[:30] if len(table_content) > 30 else table_content,
            "suggestion": "添加规范表格编号和学术标题（如：表1 XXX）",
            "message": "无规范学术表标题"
        })
    else:
        # 检测标题是否口语化
        title_text = title_match.group(2)
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
            if re.search(pattern, title_text):
                errors.append({
                    "type": "table_title",
                    "level": "warning",
                    "pos": title_match.start(),
                    "text": title_match.group(),
                    "suggestion": "使用学术规范的表格标题，包含明确的研究指标",
                    "message": "表格标题口语化"
                })
                break
    
    # 2. 检测数据缺失百分比单位
    # 查找表格中的数值数据
    lines = table_content.split('\n')
    for line_num, line in enumerate(lines):
        # 检测数值后面是否缺少单位（针对百分比类数据）
        numeric_matches = re.finditer(r'(\d+\.?\d*)\s*(?=\t|$|\s)', line)
        for match in numeric_matches:
            num_value = match.group(1)
            # 判断是否可能是百分比数据（0-100之间的数值）
            try:
                num_float = float(num_value)
                if 0 <= num_float <= 100:
                    # 检查前后是否有单位
                    around_text = table_content[max(0, match.start()-15):match.end()+15]
                    if not re.search(r'[%％]|\(.*%\)|\(.*％\)|单位|s$|ms$|条$|人$', around_text):
                        # 检查是否在表头行（表头通常有单位说明）
                        if line_num > 0:  # 不是第一行（标题行）
                            errors.append({
                                "type": "data_unit",
                                "level": "warning",
                                "pos": match.start(),
                                "text": num_value,
                                "suggestion": f"为数值{num_value}添加百分比单位(%)",
                                "message": f"数据{num_value}缺失百分比单位"
                            })
            except ValueError:
                pass
    
    # 3. 检测无任何表注说明
    if not re.search(r'^注[:：]|^注释[:：]|^说明[:：]', table_content, re.MULTILINE):
        errors.append({
            "type": "table_note",
            "level": "warning",
            "pos": len(table_content) - 1,
            "text": "表注",
            "suggestion": "添加表注说明数据来源、实验条件或统计方法",
            "message": "无任何表注说明"
        })
    
    # 4. 检测正文无对应引用语句
    if not re.search(r'如表(\d+)所示', table_content):
        errors.append({
            "type": "text_reference",
            "level": "error",
            "pos": 0,
            "text": "表格引用",
            "suggestion": "在正文相应位置添加'如表X所示'引用语句",
            "message": "正文无对应引用语句"
        })
    
    return errors

def analyze_excel_error_file(file_path):
    """
    分析excel_error.txt文件中的表格错误
    
    参数：
        file_path: 文件路径
    
    返回：
        完整的错误分析报告
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按表格分割（匹配所有表格类型）
    pattern = r'([一二三四五六七八九十]+、(?:基础错误表格|跳号错误表格|口语化标题错误表格|无表头无含义错误表格|图文编号混用错误表格)\d+?)\s*([\s\S]*?)(?=\n✅|$|\n[一二三四五六七八九十]+、)'
    matches = re.finditer(pattern, content)
    
    report = []
    table_num = 0
    for match in matches:
        table_num += 1
        table_title = match.group(1)
        table_content = match.group(2)
        
        if table_content.strip():
            errors = analyze_table_data_errors(table_content)
            if errors:
                report.append({
                    "table_index": table_num,
                    "table_title": table_title,
                    "errors": errors
                })
    
    return report

def generate_error_report(report):
    """
    生成格式化的错误报告
    
    参数：
        report: 分析报告
    
    返回：
        格式化的报告文本
    """
    lines = []
    lines.append("="*60)
    lines.append("表格数据错误分类分析报告")
    lines.append("="*60)
    lines.append(f"分析表格数量: {len(report)}")
    lines.append("")
    
    for table in report:
        table_title = table.get('table_title', f"表格{table['table_index']}")
        lines.append(f"【{table_title}】")
        for error in table['errors']:
            level = "[错误]" if error['level'] == 'error' else "[警告]"
            lines.append(f"  {level} {error['message']}")
            lines.append(f"    原文片段: {error['text'][:30]}...")
            lines.append(f"    修正建议: {error['suggestion']}")
        lines.append("")
    
    # 统计各类错误数量
    error_counts = {
        "table_title": 0,
        "data_unit": 0,
        "table_note": 0,
        "text_reference": 0
    }
    
    for table in report:
        for error in table['errors']:
            error_counts[error['type']] += 1
    
    lines.append("="*60)
    lines.append("错误分类统计")
    lines.append("="*60)
    lines.append(f"1. 无规范学术表标题: {error_counts['table_title']} 个")
    lines.append(f"2. 数据缺失百分比单位: {error_counts['data_unit']} 个")
    lines.append(f"3. 无任何表注说明: {error_counts['table_note']} 个")
    lines.append(f"4. 正文无对应引用语句: {error_counts['text_reference']} 个")
    lines.append("="*60)
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 分析excel_error.txt文件
    file_path = r'd:\check_teset - 1\excel_error.txt'
    report = analyze_excel_error_file(file_path)
    print(generate_error_report(report))