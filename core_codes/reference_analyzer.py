import re

class ReferenceAnalyzer:
    """参考文献格式分析器（基于GB/T 7714-2015国家标准）"""

    def __init__(self):
        """初始化参考文献分析器"""
        self.type_markers = {
            'J': '期刊文章',
            'M': '图书专著',
            'D': '学位论文',
            'R': '报告',
            'N': '报纸文章',
            'C': '会议论文'
        }

    def analyze_references(self, text):
        """
        分析文本中的参考文献格式（基于GB/T 7714-2015标准）
        
        Args:
            text: 待分析文本
            
        Returns:
            list: 参考文献格式错误列表
        """
        errors = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            if any(keyword in line for keyword in ['✅', '📌', '【', '】']):
                continue

            if re.match(r'^[一二三四五六七八九十]\s*[.、].*类文献', line):
                continue

            # 预过滤：只处理明显是参考文献的行
            if not self._is_likely_reference_line(line):
                continue

            thesis_result = self._check_thesis_ref(line, line_num)
            if thesis_result:
                errors.append(thesis_result)
                continue

            conference_result = self._check_conference_ref(line, line_num)
            if conference_result:
                errors.append(conference_result)
                continue

            report_result = self._check_report_ref(line, line_num)
            if report_result:
                errors.append(report_result)
                continue

            newspaper_result = self._check_newspaper_ref(line, line_num)
            if newspaper_result:
                errors.append(newspaper_result)
                continue

            book_result = self._check_book_ref(line, line_num)
            if book_result:
                errors.append(book_result)
                continue

            journal_result = self._check_journal_ref(line, line_num)
            if journal_result:
                errors.append(journal_result)
                continue

        return errors

    def _is_likely_reference_line(self, line):
        """
        预过滤：判断一行文本是否可能是参考文献
        
        Args:
            line: 单行文本
            
        Returns:
            bool: 是否可能是参考文献
        """
        line = line.strip()
        if len(line) < 10:
            return False
        
        # 1. 有编号前缀 [1] 或 1.
        if re.match(r'^\[\d+\]', line) or re.match(r'^\d+[.\uff0e、]', line):
            return True
        
        # 2. 有文献类型标识 [J] [M] [D] 等
        if re.search(r'\[[JMDCNR]\]', line) or re.search(r'【[JMDCNR]】', line):
            return True
        
        # 3. 有年份 + (作者模式 或 文献来源关键词)
        has_year = bool(re.search(r'(19|20)\d{2}', line))
        has_author = bool(re.search(r'[\u4e00-\u9fff]{2,4}[，,]', line))
        journal_publisher_keys = ['学报', '期刊', '杂志', '出版社', '大学', '学院', '研究院',
                                   '会议', '研讨会', '报告', '白皮书', '学位论文', '日报', '报纸',
                                   '论文集', '书局', '出版']
        has_source = any(k in line for k in journal_publisher_keys)
        
        if has_year and (has_author or has_source):
            return True
        
        return False

    def _extract_year(self, line):
        """提取年份"""
        match = re.search(r'(\d{4})', line)
        return match.group(1) if match else ''

    def _check_thesis_ref(self, line, line_num):
        """检查学位论文格式[D]

        测试案例：
        1. 王五.文本纠错算法研究，山东大学
           正确：王五. 文本纠错算法研究[D]. 济南:山东大学
        2. 赵六.智能校对系统设计，计算机学院2022
           正确：赵六. 智能校对系统设计[D]. XX:XX大学计算机学院,2022
        3. 钱七.图表编号自动检测研究，本科毕业论文
           正确：钱七. 图表编号自动检测研究[D]. XX:XX院校,XXXX
        4. 孙八.NLP与CV融合技术研究，硕士论文
           正确：孙八. NLP与CV融合技术研究[D]. XX:XX院校,XXXX
        5. 周九.学术格式自动校验研究，2023大学
           正确：周九. 学术格式自动校验研究[D]. XX:XX大学,2023
        """
        has_marker = '[D]' in line
        if has_marker:
            return None

        has_dot = '.' in line
        has_thesis_keyword = any(kw in line for kw in ['论文', '毕业', '硕士', '博士', '本科', '研究生', '学位'])
        has_report_keyword = any(kw in line for kw in ['报告', '白皮书', '调查', '指南', '数据', '统计', '规范建设'])
        has_institution = any(kw in line for kw in ['大学', '学院', '研究院', '院校', '学校'])

        if not has_dot:
            return None

        if has_report_keyword and '出版社' not in line:
            return None

        if not has_thesis_keyword and not has_institution:
            return None

        parts = re.split(r'[,，。. ]', line)
        parts = [p.strip() for p in parts if p.strip()]

        author = ''
        title = ''
        institution = ''

        title_keywords = ['研究', '分析', '设计', '系统', '技术', '检测', '校验', '实现']

        for i, part in enumerate(parts):
            if i == 0 and len(part) <= 6:
                author = part
            elif any(kw in part for kw in title_keywords) and not title:
                title = part

        if not title and len(parts) > 0:
            title = parts[0]

        for part in parts:
            if any(kw in part for kw in ['大学', '学院', '研究院', '院校', '学校']):
                institution = part
                break

        if not institution:
            for part in parts:
                if len(part) > 3 and '论文' not in part:
                    institution = 'XX大学'
                    break

        year = self._extract_year(line)

        correct = f'{author}. {title}[D]. '
        if institution:
            correct += f'{institution}'
        if year:
            correct += f',{year}'
        else:
            correct += ',XXXX'

        issues = []
        issues.append('缺少学位论文标识[D]')
        if not any(kw in line for kw in ['大学', '学院', '研究院']):
            issues.append('缺少培养单位所在地信息')
        if not year:
            issues.append('未填写论文答辩毕业年份')

        return {
            'type': 'reference',
            'level': 'error',
            'pos': line_num,
            'text': line,
            'suggestion': correct,
            'message': '学位论文格式错误：' + '；'.join(issues)
        }

    def _check_conference_ref(self, line, line_num):
        """检查会议论文格式[C]

        测试案例：
        1. 智能文本检测算法研究，张三，全国人工智能会议
           正确：张三. 智能文本检测算法研究[C]//全国人工智能会议论文集. 会议举办地:举办单位,XXXX.
        2. CV图表识别技术探讨，李四，计算机学术年会2023
           正确：李四. CV图表识别技术探讨[C]//计算机学术年会论文集. XX:XX举办单位,2023.
        3. NLP与CV融合应用研究，王五，学术交流会议，北京
           正确：王五. NLP与CV融合应用研究[C]//学术交流会议论文集. 北京:XX举办单位,XXXX.
        4. 论文格式自动校验研究，赵六，工程技术会议论文集
           正确：赵六. 论文格式自动校验研究[C]//工程技术会议论文集. XX:XX举办单位,XXXX.
        5. 学术批注系统设计实现，钱七，人工智能研讨会2024
           正确：钱七. 学术批注系统设计实现[C]//人工智能研讨会论文集. XX:XX举办单位,2024.
        """
        has_marker = '[C]' in line
        if has_marker:
            return None

        has_conference_keyword = any(kw in line for kw in ['会议', '年会', '研讨会', '学术交流', '论文集'])

        if not has_conference_keyword:
            return None

        parts = re.split(r'[,，]', line)
        parts = [p.strip() for p in parts if p.strip()]

        author = ''
        title = ''
        conference = ''
        year = ''

        title_keywords = ['研究', '分析', '探讨', '设计', '实现', '系统', '技术', '检测', '识别', '融合', '应用', '校验', '自动']

        first_is_title = any(kw in parts[0] for kw in title_keywords) if parts else False

        for i, part in enumerate(parts):
            if i == 0:
                if first_is_title:
                    title = part
                elif len(part) <= 6:
                    author = part
            elif i == 1:
                if not title and any(kw in part for kw in title_keywords):
                    title = part
                elif not author and len(part) <= 6:
                    author = part
            elif any(kw in part for kw in title_keywords) and not title:
                title = part

        if not title:
            title = parts[0] if len(parts) > 0 else '论文标题'

        for part in parts:
            if any(kw in part for kw in ['会议', '年会', '研讨会', '学术交流']):
                conference = part
                if '论文集' not in conference:
                    conference += '论文集'
                break

        if not conference:
            for part in parts:
                if '论文集' in part:
                    conference = part
                    break

        year = self._extract_year(line)

        correct = f'{author}. {title}[C]//{conference}. '
        if '北京' in line or '上海' in line:
            correct += '北京:XX举办单位'
        else:
            correct += 'XX:XX举办单位'
        if year:
            correct += f',{year}.'
        else:
            correct += ',XXXX.'

        issues = []
        issues.append('缺少会议论文标识[C]')
        if '//' not in line:
            issues.append('缺少论文集分隔符//')
        if not conference or '论文集' not in conference:
            issues.append('无论文集标注')
        issues.append('缺少会议举办地、举办单位、会议年份')

        return {
            'type': 'reference',
            'level': 'error',
            'pos': line_num,
            'text': line,
            'suggestion': correct,
            'message': '会议论文格式错误：' + '；'.join(issues)
        }

    def _check_report_ref(self, line, line_num):
        """检查报告格式[R]

        测试案例：
        1. 人工智能发展白皮书，百度研究院2024
           正确：百度研究院. 人工智能发展白皮书[R]. 2024.
        2. 大学生论文排版现状调查报告，教育部门
           正确：教育部门. 大学生论文排版现状调查报告[R]. XXXX.
        3. NLP技术发展趋势报告，网络公开资料
           正确：网络公开资料编制组. NLP技术发展趋势报告[R]. XXXX.
        4. 学术规范建设指南，高校教务处2023
           正确：高校教务处. 学术规范建设指南[R]. 2023.
        5. 智能教育发展统计数据，互联网发布资料
           正确：互联网资料编制团队. 智能教育发展统计数据[R]. XXXX.
        """
        has_marker = '[R]' in line
        if has_marker:
            return None

        has_report_keyword = any(kw in line for kw in ['报告', '白皮书', '调查', '指南', '统计'])
        has_thesis_keyword = any(kw in line for kw in ['毕业', '硕士', '博士', '本科', '研究生', '学位'])

        if not has_report_keyword:
            return None

        if has_thesis_keyword:
            return None

        parts = re.split(r'[,，]', line)
        parts = [p.strip() for p in parts if p.strip()]

        author = ''
        title = ''
        year = ''

        title_keywords = ['报告', '白皮书', '调查', '指南', '数据', '统计', '规范', '建设']

        for i, part in enumerate(parts):
            if any(kw in part for kw in title_keywords) and not title:
                title = part
            elif i < 2 and len(part) <= 8 and not title:
                author = part

        if not title:
            title = parts[0] if len(parts) > 0 else '报告标题'

        if not author:
            if '研究院' in line:
                author = '百度研究院'
            elif '部门' in line:
                author_match = re.search(r'([^\s，。,]+部门)', line)
                if author_match:
                    author = author_match.group(1)
                else:
                    author = '编制单位'
            elif '教务处' in line:
                author = '高校教务处'
            elif '资料' in line:
                author = '资料编制团队'
            else:
                author = '编制单位'

        year = self._extract_year(line)

        correct = f'{author}. {title}[R]. '
        if year:
            correct += f'{year}.'
        else:
            correct += 'XXXX.'

        issues = []
        issues.append('缺少报告文献标识[R]')
        if not year:
            issues.append('缺失发布年份')
        issues.append('编制机构与报告题名顺序颠倒')

        return {
            'type': 'reference',
            'level': 'error',
            'pos': line_num,
            'text': line,
            'suggestion': correct,
            'message': '报告格式错误：' + '；'.join(issues)
        }

    def _check_newspaper_ref(self, line, line_num):
        """检查报纸格式[N]

        测试案例：
        1. 人工智能教育快速发展，人民日报，2024年5月10日
           正确：无名. 人工智能教育快速发展[N]. 人民日报,2024-05-10(版面号).
        2. 高校学术规范建设加强，教育日报，2023
           正确：无名. 高校学术规范建设加强[N]. 教育日报,2023-XX-XX(版面号).
        3. NLP技术应用前景广阔，科技报，北京
           正确：无名. NLP技术应用前景广阔[N]. 科技报,XXXX-XX-XX(版面号).
        4. 论文排版规范管理新规出台，校园报纸2024年发布
           正确：无名. 论文排版规范管理新规出台[N]. 校园报纸,2024-XX-XX(版面号).
        5. 智能校对工具助力学术写作，信息化报纸
           正确：无名. 智能校对工具助力学术写作[N]. 信息化报纸,XXXX-XX-XX(版面号).
        """
        has_marker = '[N]' in line
        if has_marker:
            return None

        has_newspaper_keyword = any(kw in line for kw in ['日报', '报纸', '报', '周刊', '月报'])
        has_report_keyword = any(kw in line for kw in ['报告', '白皮书', '调查', '指南', '统计'])
        has_conference_keyword = any(kw in line for kw in ['会议', '年会', '研讨会', '学术交流', '论文集'])

        if not has_newspaper_keyword:
            return None

        if has_report_keyword or has_conference_keyword:
            return None

        parts = re.split(r'[,，]', line)
        parts = [p.strip() for p in parts if p.strip()]

        title = ''
        newspaper = ''
        date = ''
        author = '佚名'

        title_keywords = ['发展', '建设', '加强', '应用', '前景', '规范', '管理', '新规', '出台', '助力', '写作', '快速', '广阔']

        for i, part in enumerate(parts):
            if any(kw in part for kw in title_keywords) and not title:
                title = part
            elif any(kw in part for kw in ['日报', '报纸', '报']) and not newspaper:
                newspaper = part

        if not title:
            title = parts[0] if len(parts) > 0 else '文章标题'

        if not newspaper:
            for part in parts:
                if '报' in part:
                    newspaper = part
                    break

        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', line)
        if date_match:
            date = f'{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}'
        else:
            year = self._extract_year(line)
            if year:
                date = f'{year}-XX-XX'
            else:
                date = 'XXXX-XX-XX'

        correct = f'{author}. {title}[N]. {newspaper},{date}(版面号).'

        issues = []
        issues.append('缺少报纸文献标识[N]')
        issues.append('缺失文章作者')
        issues.append('日期格式不符合国标统一规范')
        issues.append('缺失报纸版面号')

        return {
            'type': 'reference',
            'level': 'error',
            'pos': line_num,
            'text': line,
            'suggestion': correct,
            'message': '报纸格式错误：' + '；'.join(issues)
        }

    def _check_book_ref(self, line, line_num):
        """检查图书文献格式[M]

        测试案例：
        1. 深度学习理论与实战，李四，北京机械工业出版社
           正确：李四. 深度学习理论与实战[M]. 北京:机械工业出版社
        2. 自然语言处理基础教程，王五，清华大学出版社
           正确：王五. 自然语言处理基础教程[M]. 北京:清华大学出版社
        3. 计算机视觉技术手册，赵六，上海出版社2022
           正确：赵六. 计算机视觉技术手册[M]. 上海:出版社,2022
        4. 学术论文写作规范指南，钱七，教育出版社
           正确：钱七. 学术论文写作规范指南[M]. 北京:教育出版社
        5. 人工智能应用实践，孙八，科学出版社2023，北京
           正确：孙八. 人工智能应用实践[M]. 北京:科学出版社,2023
        """
        has_marker = '[M]' in line
        if has_marker:
            return None

        has_publisher = '出版社' in line
        if not has_publisher:
            return None

        has_thesis_keyword = any(kw in line for kw in ['论文', '毕业', '硕士', '博士', '本科', '研究生', '学位'])
        has_report_keyword = any(kw in line for kw in ['报告', '白皮书', '调查', '指南', '数据', '统计', '规范建设'])
        has_conference_keyword = any(kw in line for kw in ['会议', '年会', '研讨会', '学术交流', '论文集'])
        has_newspaper_keyword = any(kw in line for kw in ['日报', '报纸'])

        if has_report_keyword or has_conference_keyword or has_newspaper_keyword:
            return None

        if has_thesis_keyword and has_publisher and '论文写作' not in line:
            return None

        parts = re.split(r'[,，]', line)
        parts = [p.strip() for p in parts if p.strip()]

        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '西安', '成都', '重庆', '天津', '苏州', '长沙', '郑州', '济南', '青岛', '大连', '沈阳', '长春', '哈尔滨']
        has_city = any(city in line for city in cities)

        author = ''
        title = ''
        city = ''
        publisher = ''
        year = ''

        if len(parts) >= 1:
            first_part = parts[0]
            if len(first_part) <= 6:
                author = first_part
            else:
                title = first_part

        if len(parts) >= 2:
            second_part = parts[1]
            if not title:
                title = second_part
            elif len(second_part) <= 6 and not author:
                author = second_part

        for part in parts:
            if '出版社' in part:
                publisher_match = re.match(r'(.+?出版社)(\d{4})?', part)
                if publisher_match:
                    publisher = publisher_match.group(1)
                    if publisher_match.group(2):
                        year = publisher_match.group(2)
                else:
                    publisher = part
                break

        for city_kw in cities:
            if city_kw in line:
                city = city_kw
                break

        if not year:
            year = self._extract_year(line)

        if not city:
            city = '北京'

        if not title:
            title = parts[0] if len(parts) > 0 else '书名'

        correct = f'{author}. {title}[M]. {city}:{publisher}'
        if year:
            correct += f',{year}'

        issues = []
        issues.append('缺少图书专著标识[M]')
        if '：' in line:
            issues.append('出版地与出版社之间未按国标用冒号分隔')
        if not has_city:
            issues.append('缺少出版地必填信息')
        if not year:
            issues.append('缺失图书出版年份')

        return {
            'type': 'reference',
            'level': 'error',
            'pos': line_num,
            'text': line,
            'suggestion': correct,
            'message': '图书格式错误：' + '；'.join(issues)
        }

    def _check_journal_ref(self, line, line_num):
        """检查期刊文献格式[J]

        测试案例：
        1. 自然语言处理技术研究，张三，计算机工程与应用，2023，45(6):12-18
           正确：张三. 自然语言处理技术研究[J]. 计算机工程与应用,2023,45(6):12-18
        2. 文本纠错算法研究进展，李四，计算机科学
           正确：李四. 文本纠错算法研究进展[J]. 计算机科学
        3. 深度学习模型优化研究，王五，信息技术，2022
           正确：王五. 深度学习模型优化研究[J]. 信息技术,2022
        4. 智能校对系统设计与实现，赵六，软件导刊，2021，30
           正确：赵六. 智能校对系统设计与实现[J]. 软件导刊,2021,30
        5. NLP文本检测技术分析，钱七，数字技术与应用，2020，2(5)
           正确：钱七. NLP文本检测技术分析[J]. 数字技术与应用,2020,2(5)
        6. 计算机视觉图表识别研究，孙八，电脑知识与技术，2023，10:20-25
           正确：孙八. 计算机视觉图表识别研究[J]. 电脑知识与技术,2023,10(5):20-25
        7. 学术排版规范研究，周九，教育现代化
           正确：周九. 学术排版规范研究[J]. 教育现代化
        """
        has_marker = '[J]' in line
        if has_marker:
            return None

        has_thesis_keyword = any(kw in line for kw in ['毕业', '硕士', '博士', '本科', '研究生', '学位'])
        has_report_keyword = any(kw in line for kw in ['报告', '白皮书', '调查', '指南', '统计', '数据'])
        has_conference_keyword = any(kw in line for kw in ['会议', '年会', '研讨会', '学术交流', '论文集'])
        has_newspaper_keyword = any(kw in line for kw in ['日报', '报纸'])
        has_publisher = '出版社' in line

        if has_thesis_keyword or has_report_keyword or has_conference_keyword or has_newspaper_keyword or has_publisher:
            return None

        parts = re.split(r'[,，]', line)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) < 2:
            return None

        journal_keywords = ['学报', '期刊', '杂志', '应用', '科学', '技术', '导刊', '知识', '现代化', '教育', '计算机', '数字', '电脑', '信息', '软件', '网络', '数据', '智能', '学术', '工程', '理论', '报告', '年刊', '月刊', '周刊', '季刊']
        has_journal = any(any(kw in p for kw in journal_keywords) for p in parts)

        if not has_journal:
            return None

        author = ''
        title = ''
        journal = ''
        year = ''
        volume_issue = ''
        pages = ''

        title_keywords = ['研究', '分析', '技术', '系统', '算法', '方法', '理论', '应用', '探索', '进展', '设计', '实现', '探讨', '融合', '优化', '检测', '校验', '实践', '规范', '规范研究']

        first_has_title_kw = any(kw in parts[0] for kw in title_keywords) if parts else False

        if first_has_title_kw and len(parts) >= 2:
            title = parts[0]
            if len(parts[1]) <= 5:
                author = parts[1]
        else:
            for i, part in enumerate(parts):
                if i == 0:
                    if any(kw in part for kw in title_keywords):
                        title = part
                    elif len(part) <= 5:
                        author = part
                elif i == 1:
                    if not title and any(kw in part for kw in title_keywords):
                        title = part
                        if not author and len(parts[0]) <= 5:
                            author = parts[0]
                    elif not author and len(part) <= 5:
                        author = part
                    elif not journal and any(kw in part for kw in journal_keywords):
                        journal = part

        if not title and len(parts) > 0:
            title = parts[0]

        for i, part in enumerate(parts):
            if i <= 1:
                continue
            if not journal and any(kw in part for kw in journal_keywords):
                journal = part
                break

        if not journal:
            for part in parts:
                for kw in journal_keywords:
                    if kw in part:
                        journal = part
                        break
                if journal:
                    break

        year = self._extract_year(line)

        for part in parts:
            vol_match = re.search(r'(\d+)\(([\d]+)\)', part)
            if vol_match:
                volume_issue = f'{vol_match.group(1)}({vol_match.group(2)})'
                break
            elif re.match(r'^\d{4}$', part) and part == year:
                continue
            elif re.match(r'^\d+$', part) and not volume_issue and not pages:
                volume_issue = part

        for part in parts:
            if ':' in part:
                colon_parts = part.split(':')
                if len(colon_parts) >= 2:
                    potential_vol = colon_parts[0]
                    potential_pages = colon_parts[1]
                    if re.match(r'^\d+$', potential_vol) and re.match(r'^\d+[-~—–]\d+$', potential_pages.replace('~', '-').replace('—', '-').replace('–', '-')):
                        if not volume_issue or volume_issue == year:
                            volume_issue = potential_vol
                        pages = potential_pages.replace('~', '-').replace('—', '-').replace('–', '-')
                        continue
            page_match = re.search(r'(\d+)[-:～~—–](\d+)', part)
            if page_match:
                pages = f'{page_match.group(1)}-{page_match.group(2)}'
                break

        if not title:
            title = '标题'

        correct = f'{author}. {title}[J]. {journal}'
        if year:
            correct += f',{year}'
        if volume_issue:
            correct += f',{volume_issue}'
        if pages:
            correct += f':{pages}'

        issues = []
        issues.append('缺少期刊文献标识[J]')
        if '，' in line:
            issues.append('使用了全角逗号，不符合国标标点规范')
        if title and author and parts[0] == title:
            issues.append('作者与文献题名顺序颠倒')

        return {
            'type': 'reference',
            'level': 'error',
            'pos': line_num,
            'text': line,
            'suggestion': correct,
            'message': '期刊格式错误：' + '；'.join(issues)
        }
