# -*- coding: utf-8 -*-
import re

VALID_TYPES = {
    'J': {'name': '期刊文章', 'required': ['authors', 'title', 'type', 'journal'], 'optional': ['year', 'volume', 'issue', 'pages']},
    'M': {'name': '专著', 'required': ['authors', 'title', 'type', 'publisher'], 'optional': ['year', 'place']},
    'C': {'name': '会议论文集', 'required': ['authors', 'title', 'type', 'conference'], 'optional': ['year', 'place', 'publisher']},
    'D': {'name': '学位论文', 'required': ['authors', 'title', 'type', 'school'], 'optional': ['year', 'place']},
    'R': {'name': '报告', 'required': ['authors', 'title', 'type'], 'optional': ['year']},
    'N': {'name': '报纸文章', 'required': ['title', 'type', 'newspaper'], 'optional': ['authors', 'year', 'page']},
}

AUTHOR_SEPARATORS = ['，', ',', '、', '和', '与', '及']

PLACE_KEYWORDS = ['北京', '上海', '广州', '济南', '南京', '杭州', '西安', '成都', '武汉', '天津', '重庆', '深圳', '青岛', '苏州']

SCHOOL_TO_PLACE = {
    '山东大学': '济南',
    '清华大学': '北京',
    '北京大学': '北京',
    '复旦大学': '上海',
    '上海交通大学': '上海',
    '浙江大学': '杭州',
    '南京大学': '南京',
}

PUBLISHER_KEYWORDS = ['出版社', '出版集团', '出版公司', '书局']
JOURNAL_KEYWORDS = ['学报', '杂志', '期刊', '研究', '科学', '大学学报', '学院学报', '工程', '应用', '技术', '导刊', '现代化', '知识']
CONFERENCE_KEYWORDS = ['会议', '年会', '研讨会', '论坛']
NEWSPAPER_KEYWORDS = ['日报', '晚报', '报']
REPORT_KEYWORDS = ['白皮书', '报告', '调查报告', '指南', '统计数据']
SCHOOL_KEYWORDS = ['大学', '学院', '研究院']

KNOWN_JOURNALS = {
    '计算机工程与应用', '计算机科学', '信息技术', '软件导刊', '数字技术与应用', 
    '电脑知识与技术', '教育现代化'
}

KNOWN_PUBLISHERS = {
    '机械工业出版社', '清华大学出版社', '科学出版社', '教育出版社'
}


def find_reference_section(paragraphs):
    """
    在段落列表中查找参考文献章节的起始位置
    
    Args:
        paragraphs: 段落列表
        
    Returns:
        int: 参考文献章节起始索引，未找到返回-1
    """
    reference_keywords = ["参考文献", "References", "REFERENCES", "参考资料", "引用文献"]
    for i, p in enumerate(paragraphs):
        if any(keyword in p for keyword in reference_keywords):
            return i
    return -1


def is_likely_reference(text):
    """
    判断文本是否可能是参考文献
    
    Args:
        text: 待判断文本
        
    Returns:
        bool: 是否可能是参考文献
    """
    text = text.strip()
    
    # 1. 必须有编号格式 [数字] 或 数字. 或 数字、
    has_number = re.match(r"^\[\d+\]", text) or re.match(r"^\d+[.\uff0e、]", text)
    if not has_number:
        return False
    
    # 2. 长度至少15个字符
    if len(text) < 15:
        return False
    
    # 3. 检查是否包含年份（19xx或20xx）
    has_year = re.search(r"(19|20)\d{2}", text)
    
    # 4. 检查是否包含文献类型标识 [A-Z] 或 【A-Z】
    has_type = re.search(r"\[[A-Z]\]", text) or re.search(r"【[A-Z]】", text)
    
    # 5. 检查是否包含作者名模式（姓名字符后跟分隔符）
    author_pattern = re.search(r"[\u4e00-\u9fff]{2,4}[，,．。]", text)
    
    # 6. 检查是否包含期刊、出版社等关键词
    has_source_keyword = any(keyword in text for keyword in JOURNAL_KEYWORDS + PUBLISHER_KEYWORDS + SCHOOL_KEYWORDS + CONFERENCE_KEYWORDS + NEWSPAPER_KEYWORDS + REPORT_KEYWORDS)
    
    # 7. 排除明显不是参考文献的普通句子
    # 排除以提问句号结尾的普通句子（句号前3字不是期刊/出版社等）
    if text.endswith("。") or text.endswith("？") or text.endswith("！"):
        if not has_type and not has_source_keyword:
            return False
    
    # 至少满足以下条件中的2个
    score = 0
    if has_year: score += 1
    if has_type: score += 1
    if author_pattern: score += 1
    if has_source_keyword: score += 1
    
    # 如果有类型标识，基本可以确定是参考文献
    if has_type:
        return True
    
    # 如果有年份+作者，也可以确定是参考文献
    if has_year and author_pattern:
        return True
    
    # 如果有年份或作者 + 来源关键词，也可以确定
    if (has_year or author_pattern) and has_source_keyword:
        return True
    
    # 否则需要至少3个条件满足
    return score >= 3


def extract_references(paragraphs):
    """
    从段落列表中提取参考文献
    
    Args:
        paragraphs: 段落列表
        
    Returns:
        list: 参考文献列表
    """
    start = find_reference_section(paragraphs)
    
    refs = []
    
    if start != -1:
        # 如果找到"参考文献"章节标题，提取章节后的内容
        for p in paragraphs[start+1:]:
            p = p.strip()
            if not p:
                continue
            if re.match(r"^\[\d+\]", p) or re.match(r"^\d+[.\uff0e、]", p):
                if is_likely_reference(p):
                    refs.append(p)
    else:
        # 如果没有找到章节标题，只在段落数较少且很可能都是参考文献时提取
        # 限制：至少需要 [J]/[M]/[D] 等类型标识或是明显文献格式
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            # 必须有 [数字] 开头
            if not (re.match(r"^\[\d+\]", p) or re.match(r"^\d+[.\uff0e、]", p)):
                continue
            # 必须有文献类型标识 [J]/[M]/[D]/[C]/[N]/[R] 或 年份+作者+来源关键词
            has_type = re.search(r"\[[A-Z]\]", p) or re.search(r"【[A-Z]】", p)
            has_year = re.search(r"(19|20)\d{2}", p)
            has_author = re.search(r"[\u4e00-\u9fff]{2,4}[，,]", p)
            has_source = any(k in p for k in JOURNAL_KEYWORDS + PUBLISHER_KEYWORDS + SCHOOL_KEYWORDS + CONFERENCE_KEYWORDS + NEWSPAPER_KEYWORDS + REPORT_KEYWORDS)
            if has_type or (has_year and has_author and has_source):
                refs.append(p)
    
    return refs


def check_index_sequence(refs):
    """
    检查参考文献编号序列是否连续
    
    Args:
        refs: 参考文献列表
        
    Returns:
        list: 编号错误列表
    """
    errors = []
    indexes = []
    for ref in refs:
        match = re.match(r"\[(\d+)\]", ref)
        if match:
            indexes.append(int(match.group(1)))

    if indexes:
        sorted_indexes = sorted(indexes)
        expected = list(range(1, len(sorted_indexes)+1))
        if sorted_indexes != expected:
            missing = [e for e in expected if e not in sorted_indexes]
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": "编号序列",
                "suggestion": f"补充编号 {missing}",
                "message": f"编号不连续，缺失编号: {missing}"
            })
        
        seen = set()
        duplicates = []
        for idx in indexes:
            if idx in seen:
                duplicates.append(idx)
            seen.add(idx)
        if duplicates:
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": "编号序列",
                "suggestion": f"删除重复编号",
                "message": f"存在重复编号: {duplicates}"
            })
    return errors


def parse_reference(ref):
    """
    解析参考文献格式，提取各字段信息
    
    Args:
        ref: 参考文献文本
        
    Returns:
        dict: 包含各字段信息的字典
    """
    parts = {
        'number': None,
        'authors': [],
        'title': None,
        'type': None,
        'journal': None,
        'publisher': None,
        'school': None,
        'conference': None,
        'newspaper': None,
        'year': None,
        'volume': None,
        'issue': None,
        'pages': None,
        'place': None,
        'has_dot_after_author': False,
        'has_type_bracket': False,
        'format_error': False,
        'field_errors': [],
        'has_fullwidth_comma': False,
        '_raw_ref': ref,
        'date_format_error': False,
    }
    
    num_match = re.match(r"\[(\d+)\]", ref)
    if num_match:
        parts['number'] = num_match.group(1)
    else:
        num_match2 = re.match(r"^(\d+)[.\uff0e、]", ref)
        if num_match2:
            parts['number'] = num_match2.group(1)
    
    remaining = re.sub(r"^\[\d+\]\s*|^\d+[.\uff0e、]\s*", "", ref).strip()
    if '，' in remaining:
        parts['has_fullwidth_comma'] = True
    
    type_patterns = [r"\[([A-Z]/[A-Z]+)\]", r"\[([A-Z]+)\]", r"【[A-Z]+】"]
    for pattern in type_patterns:
        type_match = re.search(pattern, remaining)
        if type_match:
            parts['type'] = type_match.group(1)
            parts['has_type_bracket'] = True
            remaining = re.sub(pattern, "", remaining).strip()
            break
    
    if not parts['type']:
        parts['type'] = _infer_ref_type(ref)
    
    parts = _parse_authors_and_title(remaining, parts)
    
    year_match = re.search(r"(19|20)\d{2}", ref)
    if year_match:
        parts['year'] = year_match.group(0)
    
    date_pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日"
    date_match = re.search(date_pattern, ref)
    if date_match:
        parts['date_format_error'] = True
    
    parts = _parse_volume_issue_pages(ref, parts)
    parts = _parse_source_info(ref, parts)
    parts = _parse_place(ref, parts)
    
    return parts


def _parse_authors_and_title(remaining, parts):
    ref_type = parts.get('type')
    
    if ref_type == 'N':
        comma_pos = remaining.find('，')
        if comma_pos > 0:
            parts['title'] = remaining[:comma_pos].strip()
            parts['format_error'] = True
        else:
            parts['title'] = remaining.strip()
        return parts
    
    dot_pos = remaining.find('。')
    dot2_pos = remaining.find('．')
    eng_dot_pos = remaining.find('.')
    
    author_end = -1
    if dot_pos > 0:
        author_end = dot_pos
        parts['has_dot_after_author'] = True
    elif dot2_pos > 0:
        author_end = dot2_pos
        parts['has_dot_after_author'] = True
    elif eng_dot_pos > 0 and eng_dot_pos < 10:
        author_end = eng_dot_pos
        parts['has_dot_after_author'] = True
    
    if author_end == -1:
        comma_parts = re.split(r"[,，]", remaining)
        if len(comma_parts) >= 2:
            first_part = comma_parts[0].strip()
            second_part = comma_parts[1].strip()
            
            if len(first_part) > 4 and len(second_part) <= 4:
                parts['format_error'] = True
                parts['authors'] = [second_part]
                parts['title'] = first_part
                return parts
            
            if len(second_part) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in second_part):
                parts['format_error'] = True
                parts['authors'] = [second_part]
                parts['title'] = first_part
                return parts
            
            if len(first_part) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in first_part):
                parts['authors'] = [first_part]
                remaining_after = remaining[len(first_part)+1:].strip()
                next_comma = remaining_after.find('，')
                if next_comma > 0:
                    parts['title'] = remaining_after[:next_comma].strip()
                else:
                    parts['title'] = remaining_after.strip()
                return parts
    
    if author_end > 0:
        author_str = remaining[:author_end].strip()
        authors = []
        current = ""
        for char in author_str:
            if char in AUTHOR_SEPARATORS:
                if current.strip():
                    authors.append(current.strip())
                    current = ""
            else:
                current += char
        if current.strip():
            authors.append(current.strip())
        parts['authors'] = authors
        
        title_part = remaining[author_end+1:].strip()
        title_part = re.sub(r"\[[A-Z]+\]|【[A-Z]+】", "", title_part).strip()
        parts['title'] = title_part
    else:
        comma_pos = remaining.find('，')
        if comma_pos > 0:
            first_part = remaining[:comma_pos].strip()
            if len(first_part) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in first_part):
                parts['authors'] = [first_part]
                remaining_after = remaining[comma_pos+1:].strip()
                next_comma = remaining_after.find('，')
                if next_comma > 0:
                    parts['title'] = remaining_after[:next_comma].strip()
                else:
                    parts['title'] = remaining_after.strip()
            else:
                parts['title'] = first_part
                parts['format_error'] = True
    
    return parts


def _parse_volume_issue_pages(ref, parts):
    volume_issue_pattern = r"(?:,|，)\s*(\d+)\s*\((\d+)\)"
    match = re.search(volume_issue_pattern, ref)
    if match:
        parts['volume'] = match.group(1)
        parts['issue'] = match.group(2)
    else:
        volume_match = re.search(r"(?:,|，)\s*(\d+)\s*卷", ref)
        if volume_match:
            parts['volume'] = volume_match.group(1)
        else:
            comma_parts = re.split(r"[,，]", ref)
            year = parts.get('year')
            for part in comma_parts:
                part = part.strip()
                if part.isdigit() and len(part) in [2, 3]:
                    if year and part != year[-2:] and part != year[-3:]:
                        parts['volume'] = part
                        break
    
    if not parts['issue']:
        issue_match = re.search(r"\((\d+)\)", ref)
        if issue_match:
            parts['issue'] = issue_match.group(1)
    
    page_patterns = [r":\s*(\d+-\d+)", r"，\s*(\d+-\d+)", r",\s*(\d+)-(\d+)", r"：\s*(\d+)-(\d+)"]
    for pattern in page_patterns:
        page_match = re.search(pattern, ref)
        if page_match:
            if page_match.group(1):
                parts['pages'] = page_match.group(1)
            elif len(page_match.groups()) >= 2 and page_match.group(2):
                parts['pages'] = f"{page_match.group(1)}-{page_match.group(2)}"
            break
    
    return parts


def _parse_source_info(ref, parts):
    for keyword in PUBLISHER_KEYWORDS:
        match = re.search(r"([\u4e00-\u9fff]+?)" + keyword, ref)
        if match:
            parts['publisher'] = match.group(0)
            break
    
    if not parts['school']:
        school_patterns = [r"([\u4e00-\u9fff]+大学)", r"([\u4e00-\u9fff]+学院)", r"([\u4e00-\u9fff]+研究院)"]
        for pattern in school_patterns:
            match = re.search(pattern, ref)
            if match:
                parts['school'] = match.group(1)
                break
    
    if not parts['conference']:
        conference_patterns = [r"([\u4e00-\u9fff]+会议)", r"([\u4e00-\u9fff]+年会)", r"([\u4e00-\u9fff]+研讨会)", r"([\u4e00-\u9fff]+论坛)"]
        for pattern in conference_patterns:
            match = re.search(pattern, ref)
            if match:
                parts['conference'] = match.group(1)
                break
    
    if not parts['newspaper']:
        newspaper_patterns = [r"([\u4e00-\u9fff]+日报)", r"([\u4e00-\u9fff]+晚报)", r"([\u4e00-\u9fff]+报)"]
        for pattern in newspaper_patterns:
            match = re.search(pattern, ref)
            if match:
                parts['newspaper'] = match.group(1)
                break
    
    if not parts['journal']:
        parts['journal'] = _extract_journal_name(ref)
    
    return parts


def _parse_place(ref, parts):
    if parts['school'] and parts['school'] in SCHOOL_TO_PLACE:
        parts['place'] = SCHOOL_TO_PLACE[parts['school']]
        return parts
    
    for place in PLACE_KEYWORDS:
        if place in ref:
            idx = ref.find(place)
            if idx > 0 and ref[idx-1] in ['，', ',', '。', '：', ':', '、']:
                parts['place'] = place
                break
            elif idx == 0:
                parts['place'] = place
                break
            elif place not in ['北京', '南京']:
                parts['place'] = place
                break
    return parts


def _extract_journal_name(ref):
    temp = ref
    temp = re.sub(r"\[\d+\]\s*", "", temp)
    temp = re.sub(r"^\d+[.\uff0e、]\s*", "", temp)
    temp = re.sub(r"\[[A-Z]+\]", "", temp)
    temp = re.sub(r"【[A-Z]+】", "", temp)
    
    comma_parts = re.split(r"[,，]", temp)
    
    for journal in KNOWN_JOURNALS:
        if journal in temp:
            return journal
    
    for part in comma_parts:
        part = part.strip()
        if any(keyword in part for keyword in JOURNAL_KEYWORDS) and len(part) > 2:
            return part
    
    for keyword in JOURNAL_KEYWORDS:
        match = re.search(r"(.+?)" + keyword, temp)
        if match:
            return match.group(0)
    
    if len(comma_parts) >= 3:
        candidate = comma_parts[2].strip()
        if not re.match(r"^\d+$", candidate) and not re.match(r".*出版社.*", candidate):
            return candidate
    
    return None


def check_reference(ref):
    """
    检查参考文献格式是否符合GB/T 7714规范
    
    Args:
        ref: 参考文献文本
        
    Returns:
        list: 格式错误列表
    """
    errors = []
    parts = parse_reference(ref)
    
    if not parts['number']:
        errors.append({
            "type": "reference",
            "level": "error",
            "pos": None,
            "text": ref,
            "suggestion": suggest_reference_fix(ref),
            "message": "缺少编号，应为 [n] 格式（如 [1]、[2]）"
        })
    
    if not parts['has_type_bracket']:
        errors.append({
            "type": "reference",
            "level": "error",
            "pos": None,
            "text": ref,
            "suggestion": suggest_reference_fix(ref),
            "message": "缺少文献类型标识（如[J]期刊、[M]专著、[D]学位论文、[R]报告、[N]报纸、[C]会议论文）"
        })
    
    if parts['format_error']:
        errors.append({
            "type": "reference",
            "level": "error",
            "pos": None,
            "text": ref,
            "suggestion": suggest_reference_fix(ref),
            "message": "作者与文献题名顺序颠倒，应改为：作者.标题[类型]"
        })
    
    if parts['authors'] and not parts['has_dot_after_author']:
        errors.append({
            "type": "reference",
            "level": "error",
            "pos": None,
            "text": ref,
            "suggestion": suggest_reference_fix(ref),
            "message": "作者后缺少句号分隔符（应为：作者.标题）"
        })
    
    if parts['date_format_error']:
        errors.append({
            "type": "reference",
            "level": "warning",
            "pos": None,
            "text": ref,
            "suggestion": suggest_reference_fix(ref),
            "message": "日期格式不规范，应为：年-月-日"
        })
    
    if parts['type']:
        type_errors = _check_by_type(parts, ref)
        errors.extend(type_errors)
    
    return errors


def _check_by_type(parts, ref):
    errors = []
    ref_type = parts['type']
    
    if ref_type == 'J':
        if not parts['journal']:
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "期刊文章缺少期刊名信息"
            })
        if parts['volume'] and not parts['issue']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "期刊文章有卷号无期号，建议补充期号（格式：卷号(期号)）"
            })
        if parts['issue'] and not parts['volume']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "期刊文章有期号无卷号，格式不规范（应为：卷号(期号)）"
            })
        if parts['pages'] and not parts['issue'] and parts['volume']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "页码前缺少期号，建议补充期号"
            })
        if not parts['year']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "期刊文章缺少出版年份信息"
            })
    
    elif ref_type == 'M':
        if not parts['publisher']:
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "专著缺少出版社信息（格式：出版地:出版社）"
            })
        if not parts['place'] and parts['publisher']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "专著缺少出版地信息"
            })
        if not parts['year']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "专著缺少出版年份信息"
            })
    
    elif ref_type == 'D':
        if not parts['school']:
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "学位论文缺少培养单位（如XX大学、XX研究院）"
            })
        if not parts['place'] and parts['school']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "学位论文缺少培养单位所在地信息"
            })
        if not parts['year']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "学位论文缺少论文答辩毕业年份"
            })
    
    elif ref_type == 'N':
        if not parts['newspaper']:
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "报纸文章缺少报纸名称"
            })
        if not parts['authors'] or len(parts['authors']) == 0:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "报纸文章缺少作者信息，默认使用佚名"
            })
        if not parts['year']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "报纸文章缺少发布日期，格式应为：年-月-日"
            })
    
    elif ref_type == 'C':
        if not parts['conference']:
            errors.append({
                "type": "reference",
                "level": "error",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "会议论文缺少会议名称"
            })
        if not parts['year']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "会议论文缺少会议年份信息"
            })
        if not parts['place']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "会议论文缺少会议举办地信息"
            })
    
    elif ref_type == 'R':
        if not parts['year']:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "报告缺少发布年份信息"
            })
        if not parts['authors'] or len(parts['authors']) == 0:
            errors.append({
                "type": "reference",
                "level": "warning",
                "pos": None,
                "text": ref,
                "suggestion": suggest_reference_fix(ref),
                "message": "报告缺少编制机构信息"
            })
    
    return errors


def suggest_reference_fix(ref):
    """
    根据GB/T 7714规范生成参考文献格式修正建议
    
    Args:
        ref: 参考文献文本
        
    Returns:
        str: 修正后的参考文献格式
    """
    parts = parse_reference(ref)
    
    if not parts['number'] and not parts['authors'] and not parts['title']:
        return ref
    
    ref_type = parts['type'] or _infer_ref_type(ref)
    
    result = f"[{parts['number'] or '1'}] "
    
    if parts['authors']:
        result += "".join(parts['authors']) + "."
    else:
        inferred_authors = _infer_authors_from_ref(ref, ref_type)
        if inferred_authors:
            result += inferred_authors + "."
        else:
            if ref_type == 'N':
                result += "佚名."
            else:
                result += "佚名."
    
    if parts['title']:
        result += f"{parts['title']}"
    else:
        result += "无标题"
    
    # 会议论文格式特殊处理：[C]后面不加句号，直接接//
    if ref_type == 'C':
        result += f"[{ref_type}]"
    else:
        result += f"[{ref_type}]."
    
    if ref_type == 'J':
        result = _build_journal_format(result, parts)
    elif ref_type == 'M':
        result = _build_book_format(result, parts)
    elif ref_type == 'D':
        result = _build_thesis_format(result, parts)
    elif ref_type == 'R':
        result = _build_report_format(result, parts)
    elif ref_type == 'N':
        result = _build_newspaper_format(result, parts)
    elif ref_type == 'C':
        result = _build_conference_format(result, parts)
    else:
        result = _build_journal_format(result, parts)
    
    if not result.endswith(('。', '．', '.')):
        result += "."
    
    return result


def _infer_ref_type(ref):
    THESIS_KEYWORDS = ['本科毕业', '硕士论文', '博士论文', '毕业论文']
    
    for keyword in PUBLISHER_KEYWORDS:
        if keyword in ref:
            return 'M'
    
    for keyword in REPORT_KEYWORDS:
        if keyword in ref:
            return 'R'
    
    for keyword in CONFERENCE_KEYWORDS:
        if keyword in ref:
            return 'C'
    
    for keyword in NEWSPAPER_KEYWORDS:
        if keyword in ref:
            if '日报' in ref or '晚报' in ref or '报,' in ref or '报，' in ref:
                return 'N'
            elif keyword == '报' and ('技术报' in ref or '校园报' in ref or '信息化报' in ref):
                return 'N'
    
    if any(keyword in ref for keyword in THESIS_KEYWORDS):
        return 'D'
    
    if any(keyword in ref for keyword in SCHOOL_KEYWORDS):
        if '研究院' in ref:
            if '百度' in ref or '公司' in ref or '集团' in ref:
                return 'R'
        return 'D'
    
    return 'J'


def _infer_authors_from_ref(ref, ref_type):
    if ref_type == 'R':
        comma_pos = ref.find('，')
        if comma_pos > 0:
            after_comma = ref[comma_pos+1:].strip()
            if len(after_comma) > 2:
                year_match = re.search(r"(19|20)\d{2}", after_comma)
                if year_match:
                    after_comma = after_comma[:year_match.start()].strip()
                return after_comma
        return None
    
    if ref_type == 'N':
        return None
    
    comma_parts = re.split(r"[,，]", ref)
    for part in comma_parts:
        part = part.strip()
        if 2 <= len(part) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in part):
            if not any(keyword in part for keyword in PUBLISHER_KEYWORDS + JOURNAL_KEYWORDS + CONFERENCE_KEYWORDS + NEWSPAPER_KEYWORDS + SCHOOL_KEYWORDS):
                return part
    return None


def _build_journal_format(result, parts):
    journal = parts['journal'] or _extract_journal_name(parts['_raw_ref']) or '期刊名'
    result += f"{journal}"
    
    year = parts['year']
    volume = parts['volume']
    issue = parts['issue']
    pages = parts['pages']
    
    if year:
        result += f",{year}"
    if volume:
        result += f",{volume}"
        if issue:
            result += f"({issue})"
    if pages:
        result += f":{pages}"
    
    return result


def _build_book_format(result, parts):
    place = parts['place'] or 'XX'
    
    publisher = parts['publisher']
    if not publisher:
        for pub in KNOWN_PUBLISHERS:
            if pub in parts['_raw_ref']:
                publisher = pub
                break
    if not publisher:
        publisher = '出版社'
    
    result += f"{place}:{publisher}"
    if parts['year']:
        result += f",{parts['year']}"
    return result


def _build_thesis_format(result, parts):
    place = parts['place']
    
    school_patterns = [r"([\u4e00-\u9fff]+大学)", r"([\u4e00-\u9fff]+学院)", r"([\u4e00-\u9fff]+研究院)"]
    school = parts['school']
    if not school:
        for pattern in school_patterns:
            match = re.search(pattern, parts['_raw_ref'])
            if match:
                school = match.group(1)
                break
    if not school:
        school = 'XX大学'
    
    if school in SCHOOL_TO_PLACE and not place:
        place = SCHOOL_TO_PLACE[school]
    
    if not place:
        place = 'XX'
    
    result += f"{place}:{school}"
    if parts['year']:
        result += f",{parts['year']}"
    return result


def _build_report_format(result, parts):
    if parts['year']:
        result += f"{parts['year']}"
    return result


def _build_newspaper_format(result, parts):
    newspaper = parts['newspaper'] or '报纸名称'
    result += f"{newspaper}"
    
    year = parts['year']
    if year:
        result += f",{year}-XX-XX(版面号)"
    else:
        result += ",XXXX-XX-XX(版面号)"
    
    return result


def _build_conference_format(result, parts):
    conference = parts['conference'] or '会议名称'
    
    if '论文集' not in conference:
        result += f"//{conference}论文集"
    else:
        result += f"//{conference}"
    
    place = parts['place'] or 'XX'
    result += f".{place}:XX举办单位"
    
    if parts['year']:
        result += f",{parts['year']}"
    
    return result

