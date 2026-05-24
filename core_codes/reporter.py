def generate_report(all_errors):
    """
    生成错误统计报告（按错误类型分类统计）
    
    Args:
        all_errors: 错误列表
        
    Returns:
        dict: 包含各类型错误计数的报告
    """
    report = {
        "错别字": 0,
        "语法错误": 0,
        "语义错误": 0,
        "参考文献错误": 0,
        "图表错误": 0,
        "表格错误": 0,
        "总错误": 0
    }

    if not all_errors:
        return report

    try:
        for e in all_errors:
            if isinstance(e, dict) and "type" in e:
                if e["type"] == "spell":
                    report["错别字"] += 1
                elif e["type"] == "grammar":
                    report["语法错误"] += 1
                elif e["type"] == "semantic":
                    report["语义错误"] += 1
                elif e["type"] == "reference":
                    report["参考文献错误"] += 1
                elif e["type"] == "image":
                    report["图表错误"] += 1
                elif e["type"] == "table":
                    report["表格错误"] += 1

        report["总错误"] = report["错别字"] + report["语法错误"] + report["语义错误"] + report["参考文献错误"] + report["图表错误"] + report["表格错误"]
    except Exception as ex:
        print(f"❌ 生成报告失败: {ex}")

    return report


def generate_detail_report(all_errors):
    """
    生成详细错误报告（包含每个错误的位置、内容和建议）
    
    Args:
        all_errors: 错误列表
        
    Returns:
        list: 详细错误描述列表
    """
    detail = []

    if not all_errors:
        return detail

    try:
        for e in all_errors:
            if isinstance(e, dict) and "type" in e:
                if e["type"] == "spell":
                    # 检查必要字段是否存在
                    pos = e.get('pos', '未知')
                    text = e.get('text', '')
                    suggestion = e.get('suggestion', '')
                    message = e.get('message', '')
                    detail.append(
                        f"位置{pos}：{text} → {suggestion}（{message}）"
                    )
                elif e["type"] == "reference":
                    # 检查必要字段是否存在
                    pos = e.get('pos', '未知')
                    text = e.get('text', '')
                    suggestion = e.get('suggestion', '')
                    message = e.get('message', '')
                    detail.append(
                        f"位置{pos}：{text} → {suggestion}（{message}）"
                    )
                elif e["type"] == "grammar":
                    # 语法错误
                    pos = e.get('pos', '未知')
                    text = e.get('text', '')
                    suggestion = e.get('suggestion', '')
                    message = e.get('message', '')
                    detail.append(
                        f"位置{pos}：{text} → {suggestion}（语法问题：{message}）"
                    )
                elif e["type"] == "semantic":
                    # 语义错误
                    pos = e.get('pos', '未知')
                    text = e.get('text', '')
                    suggestion = e.get('suggestion', '')
                    message = e.get('message', '')
                    detail.append(
                        f"位置{pos}：{text} → {suggestion}（语义问题：{message}）"
                    )
                elif e["type"] == "image":
                    # 图表错误
                    pos = e.get('pos', '未知')
                    text = e.get('text', '')
                    suggestion = e.get('suggestion', '')
                    message = e.get('message', '')
                    detail.append(
                        f"位置{pos}：{text} → {suggestion}（{message}）"
                    )
                elif e["type"] == "table":
                    # 表格错误
                    pos = e.get('pos', '未知')
                    text = e.get('text', '')
                    suggestion = e.get('suggestion', '')
                    message = e.get('message', '')
                    detail.append(
                        f"位置{pos}：{text} → {suggestion}（{message}）"
                    )
    except Exception as ex:
        print(f"❌ 生成详细报告失败: {ex}")

    return detail