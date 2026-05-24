import torch
import os
from transformers import BertTokenizer, BertForMaskedLM

# 配置pycorrector缓存目录
os.environ["PYCORRECTOR_CACHE_DIR"] = r"D:\Users\86182\.pycorrector"

try:
    from pycorrector import Corrector
    PYCORRECTOR_AVAILABLE = True
except ImportError:
    PYCORRECTOR_AVAILABLE = False
    print("[WARNING] pycorrector 未安装")

# 导入参考文献校验模块（直接引用 reference_checker）
try:
    from .reference_checker import (
        extract_references,
        check_index_sequence,
        check_reference,
        suggest_reference_fix,
        is_likely_reference
    )
    REFERENCE_CHECKER_AVAILABLE = True
except ImportError:
    REFERENCE_CHECKER_AVAILABLE = False
    print("[WARNING] 参考文献校验模块未找到")

class SingleModelCorrector:
    """单模型纠错器 - 基于BERT的中文文本纠错模型"""
    
    def __init__(self, model_path, device, threshold=0.99):
        """
        初始化单模型纠错器
        
        Args:
            model_path: 预训练模型路径
            device: 运行设备 (CPU/GPU)
            threshold: 置信度阈值，低于此值的修正建议将被忽略
        """
        self.device = device
        self.threshold = threshold
        
        # 常见错误映射表（扩展版）
        self.error_map = {
            # AI领域特定错误
            '推鉴': '推荐', '过虑': '过滤', '机戒': '机器', '网洛': '网络',
            '希疏': '稀疏', '拟和': '拟合', '领彧': '领域', '机术': '技术',
            '按排': '安排', '安照': '按照', '建义': '建议', '根椐': '根据',
            '问提': '问题', '管里': '管理', '过拟和': '过拟合', '扩涨': '扩展',
            '结裹': '结果', '重偠': '重要', '符和': '符合', '有校': '有效',
            '因该': '应该', '让坐': '让座', '领遇': '领域', '分知': '分支',
            '跳无': '跳舞', '七习': '学习', '校术': '技术', '结里': '结果',
            '算发': '算法', '结国': '结果', '研救': '研究', '参攷': '参考',
            '校果': '效果', '分悉': '分析', '研揪': '研究', '质亮': '质量',
            '时剑': '时间', '训炼': '训练', '模形': '模型', '体念': '体验',
            '卒': '率', '较妤': '较好', '出理': '处理','侧试':'测试',
            
            # 新增：常见错别字
            '未莱': '未来', '优话': '优化', '错识': '错误', '识边': '识别',
            '能尼': '能力', '智恩': '智能', '完山': '完善', '进一不': '进一步',
            '语发': '语法', '边能': '能力', '智惠': '智慧', '完缮': '完善',
            '模形': '模型',
            '图象': '图像', '图相': '图像',
            '习学': '学习', '学系': '学习',
            '数居': '数据',
            '奖赏': '奖励',
            '关细': '关系',
            '生诚': '生成',
            '词嵌如': '词嵌入',
            '卷基': '卷积',
            '过虑': '过滤',
            '圗谱': '图谱',
            '参造': '参考',
            '个性花': '个性化',
            
            # 新增：教育/学术领域常见错误
            '深度学西': '深度学习', '学术论问': '学术论文',
            '课程报高': '课程报告', '辩别': '辨别',
            '在次': '再次', '必需': '必须',
            
            # 新增：更多常见错误词（形近字错误）
            '混烂': '混乱', '走像': '走向', '互联往': '互联网',
            '资原': '资源', '积磊': '积累', '融和': '融合',
            '技述': '技术', '报高': '报告', '分西': '分析',
            '策列': '策略', '网洛': '网络', '过虑': '过滤',
            '希疏': '稀疏', '重偠': '重要', '因该': '应该',
            '完缮': '完善', '个信化': '个性化', '算发': '算法',
            '出理': '处理', '时剑': '时间', '训炼': '训练',
            '体念': '体验', '奖赏': '奖励', '关细': '关系',
            '生诚': '生成', '词嵌如': '词嵌入', '卷基': '卷积',
            '圗谱': '图谱', '参造': '参考', '质良': '质量',
            
            # 新增：学术论文常见错误
            '趋式': '趋势', '逻缉': '逻辑', '步奏': '步骤',
            '方发': '方法', '数剧': '数据', '对笔': '对比',
            '基楚': '基础', '实险': '实验', '工做': '工作',
            '规法': '规范', '耗废': '耗费', '分折': '分析',
            
            # 新增：同音字错误
            '论问': '论文', '指道': '指导', '帮组': '帮助',
            '期见': '期间', '衷新': '更新', '专叶': '专业',
        }
        
        # 专业术语保护列表
        self.protected_terms = {
            '深度学习', '神经网络', '机器学习', '人工智能', '自然语言处理',
            '算法', '模型', '数据', '训练', '测试', '验证',
            '特征', '分类', '回归', '聚类', '推荐', '推荐系统',
            '卷积', '递归', '梯度', '损失', '优化', '精准性',
            'Transformer', 'BERT', 'GPT', 'CNN', 'RNN', 'NCF', 'DIN',
            'TensorFlow', 'PyTorch', 'CUDA', 'GPU', 'CPU',
            '摘要', '引言', '结论', '参考文献', '实验', '关键词',
            '结果', '分析', '讨论', '方法', '研究', '展望',
            '函数', '矩阵', '向量', '概率', '统计', '特征融合',
            '定理', '证明', '公式', '参数', '变量', '泛化能力',
            '如图', '如表', '所示', '其中', '因此', '应用',
            '基于', '通过', '利用', '采用', '提出', '提升',
            '准度', '精度', '准确度', '精准度', '个性化',
            '协同过滤', '数据稀疏', '冷启动', '信息过载',
            '用户体验', '可解释性', '轻量化', '多模态',
            '当前', '早期', '未来', '随着', '在', '从',
            '应用', '研究', '分析', '探讨', '解决', '发展',
            '掩码', '编码', '解码', '嵌入', '词嵌入', '注意力', '注意力机制',
            '程度', '参考', '个性化',
            # 新增：用户提到的词汇保护
            '形近字', '形近', '字形', '表题', '标题', '问题', '理解', '推理', '原理', '处理', '整体', '文献', '图表', '处错误','发展',
            '发展', '成本', '研发', '提供', '发挥', '发行', '发作', '发言', '发扬', '发动', '提起', '提示', '提问', '提议', '提成', '提取', '提前', '推广', '推荐', '提升',
            
            # 语言学术语保护
            '语病', '逻辑不通', '语法错误', '语义错误', '用词不当',
            '搭配不当', '成分残缺', '语序不当', '句式杂糅',
            '前后矛盾', '歧义', '重复累赘', '逻辑混乱',
            '表达不清', '语句不通', '通顺', '流畅', '连贯',
            
            # 新增：测试样例相关词汇（避免误改）
            '样例', '学院', '大学', '研究院', '研究所', '出版社',
            '学报', '杂志', '期刊', '报纸', '会议', '报告',
            '论文', '指南', '白皮书', '调查报告', '统计数据',
            '规范', '标准', '格式', '页码', '卷号', '期号',
            '年份', '标题', '作者', '参考文献', '摘要', '关键词',
            '摘要', '引言', '结论', '附录', '致谢', '目录',
            
            # 新增：常见机构名称词汇
            '部门', '教务处', '研究院', '科学院', '工程院',
            '教育部', '科技部', '工信部', '高校', '校园',
            
            # 新增：地名保护
            '北京', '上海', '济南', 'XX',
            
            # 新增：测试文档中的人名（避免误改）
            '张三', '李四', '王五', '赵六', '钱七', '孙八', '周九',
            
            # 新增：正确术语保护（避免被误改）
            '卷期', '分隔', '所在地', '目的地'
        }
        
        # 单字保护
        self.protected_single_chars = {
            '的', '了', '是', '在', '和', '有', '我', '他', '她', '它',
            '这', '那', '此', '其', '某', '各', '每', '该', '本',
            '于', '以', '为', '因', '由', '从', '向', '对', '把',
            '用', '被', '给', '与', '及', '而', '并', '或', '即',
            '形', '型', '题', '达',  # 形近字保护
            '.', '。', ',', '，', '!', '！', '?', '？', ':', '：',
            ';', '；', "'", '"', '(', ')', '（', '）', '[', ']', '【', '】',
            '-', '_', '/', '\\', '@', '#', '$', '%', '^', '&', '*',
            '+', '=', '<', '>', '~', '`', '|', ' ','”'
        }
        
        # emoji保护列表（包含常见emoji，确保不被修改）
        self.protected_emojis = {
            # 常用表情符号
            '✅', '❌', '⚠️', '💡', '🔥', '💯', '⭐', '🌟', '✨', '💪',
            '❤️', '💔', '😊', '😂', '🤣', '😭', '😢', '😤', '😱', '😎',
            '🤔', '🙂', '🙃', '😇', '🤓', '😋', '😌', '😍', '🤗', '🤩',
            '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🥵', '🥶', '🥴', '😵',
            '🤯', '🤠', '🥳', '🥸', '😎', '🤓', '🧐', '😕', '😟', '🙁',
            '☹️', '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰',
            '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫',
            '🥱', '😴', '😪', '🤤', '😴',
            # 常见图标
            '📌', '📍', '🎯', '🏷️', '📎', '📏', '📐', '✏️', '✒️', '🖊️', '🖋️',
            '📝', '📄', '📃', '📑', '📊', '📈', '📉', '📈', '📉', '📊',
            '📋', '📁', '📂','🗂️', '📎','🏷️', '🖇️', '📎', '🏷️',
            # 符号
            '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '⚫', '⚪', '🔘',
            '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '⚫', '⚪', '🔘',
            '✅', '❌', '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️',
            '➡️', '⬅️', '⬆️', '⬇️', '↗️', '↘️', '↙️', '↖️', '➡️', '⬅️',
            '🔄', '🔁', '🔂', '➰', '➿', '🔀', '🔁', '🔂', '🔀', '🔁',
            # 其他常用
            '🎯', '🔔', '🔕', '🔊', '🔇', '🔉', '🔈', '🎧', '🎼', '🎵', '🎶',
            '📱', '📲', '💻', '🖥️', '⌨️', '🖱️', '🖲️', '💽', '💾', '💿',
            '📀', '📼', '📷', '📸', '📹', '🎥', '📺', '📻', '🎙️', '🎚️',
            '🎛️', '⏰', '⏳', '⌛', '📅', '📆', '🗓️', '📡', '🚀', '🛸',
            # 更多emoji
            '🎯', 
            '✨', '🌟', '💫', '⭐', '🌟', '✨', '💫', '⭐', '🌟', '✨',
            '🔥', '💧', '🌊', '🌈', '☀️', '⭐', '🌙', '⭐', '🌙', '⭐',
            '🍎', '🍊', '🍋', '🍇', '🍓', '🍒', '🥝', '🍑', '🍌', '🍉',
            '🥭', '🍍', '🥥', '🍈', '🍇', '🍓', '🍒', '🥝', '🍑', '🍌',
            # 旗帜和标志
            '🚩', '🏳️', '🏴', '🏁', '🚩', '🏳️', '🏴', '🏁', '🚩', '🏳️',
            # 数字符号
            '🔢', '🔣', '🔤', '🔡', '🔠', '🔢', '🔣', '🔤', '🔡', '🔠',
        }
        
        # emoji正则表达式（作为辅助检测）- 扩展范围覆盖更多emoji
        import re
        self.emoji_pattern = re.compile(
            r'[\u2600-\u26FF\u2700-\u27BF\u1F000-\u1FAFF\uE000-\uF8FF'
            r'\u200D\uFE0F]',
            re.UNICODE
        )

        # 加载模型
        try:
            self.tokenizer = BertTokenizer.from_pretrained(
                model_path,
                use_fast=True,
                local_files_only=True
            )

            self.model = BertForMaskedLM.from_pretrained(model_path, local_files_only=True)
            self.model.to(device)
            self.model.eval()
            print(f"[OK] 模型加载成功: {os.path.basename(model_path)}")
        except Exception as e:
            print(f"[ERROR] 模型加载失败: {e}")
            raise
    
    def apply_error_map(self, text):
        """
        应用错误映射表进行文本修正
        
        Args:
            text: 待修正的文本
            
        Returns:
            修正后的文本
        """
        result = text
        for error, correct in self.error_map.items():
            # 检查错误词是否包含 emoji，如果包含则跳过
            contains_emoji = self._contains_emoji(error)
            if not contains_emoji:
                result = result.replace(error, correct)
        return result
    
    def _is_emoji(self, char):
        """
        检查单个字符是否为 emoji
        
        Args:
            char: 待检查的字符
            
        Returns:
            bool: 是否为 emoji
        """
        # 首先检查保护列表
        if char in self.protected_emojis:
            return True
        # 然后使用正则表达式检查
        return bool(self.emoji_pattern.match(char))
    
    def _contains_emoji(self, text):
        """
        检查文本是否包含 emoji
        
        Args:
            text: 待检查的文本
            
        Returns:
            bool: 是否包含 emoji
        """
        # 首先检查保护列表中的emoji
        for emoji in self.protected_emojis:
            if emoji in text:
                return True
        # 然后使用正则表达式检查
        return bool(self.emoji_pattern.search(text))
    
    def _is_in_protected_term(self, sentence, pos, char):
        """
        检查字符是否在受保护的术语中（避免被误改）
        
        Args:
            sentence: 完整句子
            pos: 字符位置
            char: 待检查字符
            
        Returns:
            bool: 是否在保护术语中
        """
        if char in self.protected_single_chars:
            return True
        
        # 检查是否为 emoji 图标（保护 emoji 不被修改）
        if self._is_emoji(char):
            return True
        
        # 优化：只检查以当前位置为中心的可能匹配范围
        max_term_len = max(len(t) for t in self.protected_terms) if self.protected_terms else 1
        
        # 检查从当前位置开始或结束的保护术语
        for term in self.protected_terms:
            term_len = len(term)
            if term_len > len(sentence):
                continue
            
            # 检查当前位置是否在这个术语的范围内
            # 计算可能的起始位置
            start_pos = max(0, pos - term_len + 1)
            end_pos = min(len(sentence) - term_len, pos)
            
            for start_offset in range(start_pos, end_pos + 1):
                end_offset = start_offset + term_len
                if sentence[start_offset:end_offset] == term:
                    if start_offset <= pos < end_offset:
                        return True
        return False
    
    def _find_protected_positions(self, text):
        """
        一次性找出文本中所有保护术语的位置（高效版本）
        
        Args:
            text: 待检测文本
            
        Returns:
            set: 所有保护术语覆盖的位置集合
        """
        protected_positions = set()
        text_len = len(text)
        
        # 遍历所有保护术语，找出它们在文本中的所有出现位置
        for term in self.protected_terms:
            term_len = len(term)
            if term_len > text_len:
                continue
            
            # 使用 find 循环找出所有出现位置（比逐位置比较快得多）
            start = 0
            while True:
                pos = text.find(term, start)
                if pos == -1:
                    break
                # 将这个术语覆盖的所有位置加入集合
                for i in range(pos, pos + term_len):
                    protected_positions.add(i)
                start = pos + 1
        
        # 添加单个保护字符
        for i, char in enumerate(text):
            if char in self.protected_single_chars:
                protected_positions.add(i)
            # 检查是否为 emoji
            if self._is_emoji(char):
                protected_positions.add(i)
        
        return protected_positions
    
    def correct(self, sentence):
        """
        使用单模型进行文本纠错
        
        Args:
            sentence: 待纠错的句子
            
        Returns:
            tuple: (修正后的文本, 错误列表)
        """
        if not sentence or not sentence.strip():
            return sentence, []
        
        # 直接使用原始文本，不替换emoji
        # 在处理过程中跳过emoji字符即可
        corrected_chars = list(sentence)
        errors_from_map = []
        
        # 记录从错误映射表中修正的错误（按位置排序，避免位置偏移）
        map_corrections = []
        for error, correct in self.error_map.items():
            # 检查错误词是否包含emoji，如果包含则跳过
            if self._contains_emoji(error):
                continue
            
            if len(error) > 1 and error in sentence:
                # 找到所有出现的位置（修复：之前只找第一个）
                start = 0
                while True:
                    try:
                        pos = sentence.index(error, start)
                        map_corrections.append({
                            "pos": pos,
                            "error": error,
                            "correct": correct
                        })
                        start = pos + len(error)
                    except ValueError:
                        break
        
        # 按位置排序，从后往前应用修正，避免位置偏移
        map_corrections.sort(key=lambda x: x["pos"], reverse=True)
        
        # 创建已修正位置集合（基于原始文本位置）
        map_corrected_positions = set()
        for correction in map_corrections:
            pos = correction["pos"]
            error = correction["error"]
            correct = correction["correct"]
            
            # 应用修正
            corrected_chars = corrected_chars[:pos] + list(correct) + corrected_chars[pos + len(error):]
            
            # 记录被修正的位置范围
            for i in range(pos, pos + len(error)):
                map_corrected_positions.add(i)
            
            errors_from_map.append({
                "type": "spell",
                "level": "error",
                "pos": pos,
                "text": error,
                "suggestion": correct,
                "message": "常见错误词替换"
            })
        
        # 对原始文本进行模型检测（与错误映射表并行执行）
        try:
            inputs = self.tokenizer(
                sentence,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                return_offsets_mapping=True
            )

            offset_mapping = inputs.pop("offset_mapping")[0]
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1)
            pred_ids = torch.argmax(probs, dim=-1)
            confidence = probs.max(dim=-1).values
            pred_tokens = self.tokenizer.convert_ids_to_tokens(pred_ids)

            errors = []

            # ============= 模型检测前，先一次性找出所有保护术语位置 =============
            protected_positions = self._find_protected_positions(sentence)
            
            # ============= 模型检测（仅在非保护位置进行） =============
            for i, (start, end) in enumerate(offset_mapping):
                if start == end or i >= len(pred_tokens):
                    continue

                pred_token = pred_tokens[i]
                conf = confidence[i].item()

                if start < len(sentence) and sentence[start].isascii() and sentence[start].isalpha():
                    continue
                if start < len(sentence) and sentence[start].isdigit():
                    continue
                if start < len(sentence) and sentence[start] in '，。！？、；：""''（）【】《》<>(){}[]':
                    continue
                if pred_token.startswith("##") or end - start != 1:
                    continue
                if start >= len(sentence) or end > len(sentence):
                    continue

                ori_char = sentence[start:end]
                pred_char = pred_token

                if pred_char in ["[UNK]", "[PAD]", "[CLS]", "[SEP]"]:
                    continue
                if ori_char.lower() == pred_char.lower():
                    continue
                if ori_char in self.protected_single_chars:  # 直接检查原始字符是否在保护列表
                    continue
                if start in protected_positions:  # 检查是否在保护位置
                    continue
                
                # ============= 额外检查：如果原始字符是emoji，跳过 =============
                if self._is_emoji(ori_char):
                    continue

                # ============= 额外检查：当前位置周围是否有保护术语 =============
                is_near_protected = False
                for term in self.protected_terms:
                    term_len = len(term)
                    for start_offset in range(max(0, start - term_len + 1), min(start + 1, len(sentence) - term_len + 1)):
                        end_offset = start_offset + term_len
                        if end_offset <= len(sentence) and sentence[start_offset:end_offset] == term:
                            if start_offset <= start < end_offset:
                                is_near_protected = True
                                break
                    if is_near_protected:
                        break
                if is_near_protected:
                    continue
                
                # ============= 额外检查：预测字符是否会导致保护术语被破坏 =============
                if pred_char in self.protected_single_chars:
                    continue

                if ori_char != pred_char and conf > self.threshold:
                    is_single_cjk = ('\u4e00' <= ori_char <= '\u9fff' or '\u3400' <= ori_char <= '\u4dbf')
                    if is_single_cjk and len(pred_char) == 1 and ('\u4e00' <= pred_char <= '\u9fff' or '\u3400' <= pred_char <= '\u4dbf'):
                        if conf < 0.9995:
                            continue
                    if start < len(corrected_chars) and start not in map_corrected_positions:
                        corrected_chars[start] = pred_char
                        errors.append({
                            "type": "spell",
                            "level": "error",
                            "pos": start,
                            "text": ori_char,
                            "suggestion": pred_char,
                            "message": f"置信度 {round(conf, 3)}"
                        })

            # 合并错误映射表的错误和模型检测的错误（按位置排序）
            all_errors = errors_from_map + errors
            all_errors.sort(key=lambda x: x.get('pos', 0))
            
            return ''.join(corrected_chars), all_errors
        except Exception as e:
            print(f"[ERROR] 纠错失败: {e}")
            # 直接返回原始文本（emoji已经被保护）
            return ''.join(corrected_chars), errors_from_map

class DualModelCorrector:
    """双模型纠错器（macbert4mdcspell_v3 + macbert4csc-base）- 投票融合两个模型的结果
    Note: 此类目前未被使用，当前系统使用的是 TextCorrector 类（macbert_finetuned + pycorrector）
    """
    
    def __init__(self, model1_path, model2_path, device, threshold=0.9):
        """
        初始化双模型纠错器
        
        Args:
            model1_path: macbert4mdcspell_v3 模型路径（主模型）
            model2_path: macbert4csc-base 模型路径（辅助模型）
            device: 运行设备 (CPU/GPU)
            threshold: 置信度阈值
        """
        self.device = device
        self.threshold = threshold
        
        # 加载两个模型
        print("🔄 加载模型1: macbert4mdcspell_v3...")
        self.model1 = SingleModelCorrector(model1_path, device, threshold)
        
        print("🔄 加载模型2: macbert4csc-base...")
        self.model2 = SingleModelCorrector(model2_path, device, threshold)
        
        print("[OK] 双模型加载完成")
    
    def correct_text(self, text):
        """
        使用双模型进行文本纠错（投票融合策略）
        
        Args:
            text: 待纠错的文本
            
        Returns:
            tuple: (修正后的文本, 错误列表)
        """
        if not text or not text.strip():
            return text, []
        
        # 1. 两个模型分别纠错
        result1, errors1 = self.model1.correct(text)
        result2, errors2 = self.model2.correct(text)
        
        # 2. 投票融合：以result1为基础（已包含错误映射表修正）
        final_result = list(result1)
        all_errors = []
        
        # 获取模型1错误映射表修正的位置范围
        map_corrected_positions = set()
        for e in errors1:
            if e.get('message') == '常见错误词替换':
                pos = e['pos']
                length = len(e['text'])
                for i in range(pos, pos + length):
                    map_corrected_positions.add(i)
        
        # 获取两个模型的错误集合
        errors1_set = {(e['pos'], e['text']) for e in errors1}
        errors2_set = {(e['pos'], e['text']) for e in errors2}
        
        # 合并错误列表（去重）
        for e in errors1:
            all_errors.append(e)
        for e in errors2:
            if (e['pos'], e['text']) not in errors1_set:
                all_errors.append(e)
        
        # 融合修正结果：跳过已被错误映射表修正的位置
        for i in range(len(text)):
            # 跳过已被错误映射表修正的位置
            if i in map_corrected_positions:
                continue
            
            char1 = result1[i] if i < len(result1) else text[i]
            char2 = result2[i] if i < len(result2) else text[i]
            
            # 投票规则：优先采用两个模型一致的结果
            if char1 == char2 and char1 != text[i]:
                final_result[i] = char1
            elif char1 != text[i] and char2 == text[i]:
                # 优先采用模型1（macbert4mdcspell_v3）
                final_result[i] = char1
            elif char2 != text[i] and char1 == text[i]:
                final_result[i] = char2
        
        return ''.join(final_result), all_errors

class TextCorrector:
    """统一接口的文本纠错器（兼容单模型和多模型融合）"""
    
    def __init__(self, model_path, device, threshold=0.9, use_pycorrector=True):
        """
        初始化文本纠错器
        
        Args:
            model_path: 模型路径（单模型模式）
            device: 运行设备 (CPU/GPU)
            threshold: 置信度阈值
            use_pycorrector: 是否使用pycorrector辅助纠错
        """
        self.device = device
        self.threshold = threshold
        self.use_pycorrector = use_pycorrector and PYCORRECTOR_AVAILABLE
        
        # 使用单模型 + pycorrector 组合
        self.single_corrector = SingleModelCorrector(model_path, device, threshold)
        
        # 加载pycorrector
        if self.use_pycorrector:
            try:
                self.pycorrector = Corrector()
                print("[OK] pycorrector 加载成功")
            except Exception as e:
                print("[ERROR] pycorrector加载失败: {e}")
                self.use_pycorrector = False
        
        # 参考文献校验模块已通过直接导入方式加载
        if REFERENCE_CHECKER_AVAILABLE:
            print("[OK] 参考文献校验模块加载成功")
    
    def correct_text(self, text):
        """
        组合纠错：macbert + pycorrector + 语法检测 + 参考文献分析
        
        Args:
            text: 待纠错的文本
            
        Returns:
            tuple: (修正后的文本, 错误列表)
        """
        if not text or not text.strip():
            return text, []

        # 1. macbert纠错（包含错误映射表修正）
        macbert_result, macbert_errors = self.single_corrector.correct(text)

        # 2. pycorrector纠错
        if self.use_pycorrector:
            pycorrector_result, pycorrector_errors = self._pycorrector_correct(text)
        else:
            pycorrector_result = text
            pycorrector_errors = []

        # 3. 投票融合：以macbert结果为基础（已包含错误映射表修正）
        # 因为错误映射表可能改变文本长度，所以从macbert_result开始
        final_result = list(macbert_result)
        all_errors = []

        # 获取macbert错误映射表修正的位置范围
        map_corrected_positions = set()
        for e in macbert_errors:
            if e.get('message') == '常见错误词替换':
                pos = e['pos']
                length = len(e['text'])
                for i in range(pos, pos + length):
                    map_corrected_positions.add(i)

        # 合并错误列表（去重）
        macbert_error_set = {(e['pos'], e['text']) for e in macbert_errors}

        for e in macbert_errors:
            all_errors.append(e)
        for e in pycorrector_errors:
            if (e['pos'], e['text']) not in macbert_error_set:
                # 检查是否在保护词汇中
                is_protected = False
                for term in self.single_corrector.protected_terms:
                    term_len = len(term)
                    pos = e['pos']
                    if pos + len(e['text']) <= len(text):
                        for start_offset in range(max(0, pos - term_len + 1), min(pos + 1, len(text) - term_len + 1)):
                            end_offset = start_offset + term_len
                            if end_offset <= len(text) and text[start_offset:end_offset] == term:
                                if start_offset <= pos < end_offset:
                                    is_protected = True
                                    break
                    if is_protected:
                        break
                if not is_protected:
                    all_errors.append(e)

        # 投票融合前，先一次性找出所有保护术语位置
        protected_positions = self.single_corrector._find_protected_positions(text)

        # 投票融合：只处理原始文本范围内的字符，且不覆盖错误映射表已修正的位置
        for i in range(len(text)):
            # 跳过已被错误映射表修正的位置（保留错误映射表的修正结果）
            if i in map_corrected_positions:
                continue

            # 检查当前位置是否在保护词汇中（O(1) 查找）
            if i in protected_positions:
                final_result[i] = text[i]  # 保持原字符不变
                continue

            macbert_char = macbert_result[i] if i < len(macbert_result) else text[i]
            pycorrector_char = pycorrector_result[i] if i < len(pycorrector_result) else text[i]
            original_char = text[i]

            is_single_cjk = ('\u4e00' <= original_char <= '\u9fff' or '\u3400' <= original_char <= '\u4dbf')
            if is_single_cjk:
                if len(macbert_char) == 1 or len(pycorrector_char) == 1:
                    final_result[i] = original_char
                    continue

            # 投票规则：只在macbert和pycorrector都确认需要修改时才修改
            # 避免单模型的误判覆盖正确的修正
            if macbert_char == pycorrector_char and macbert_char != original_char:
                final_result[i] = macbert_char
            elif macbert_char != original_char and pycorrector_char == original_char:
                # 只有macbert建议修改，pycorrector认为正确，保持macbert的结果（已在final_result中）
                pass
            elif pycorrector_char != original_char and macbert_char == original_char:
                # 只有pycorrector建议修改，macbert认为正确，采用pycorrector的建议
                final_result[i] = pycorrector_char
            # else: 两者都认为正确，或者意见不一致，保持macbert_result的结果

        # 4. 添加语法和语义错误检测
        grammar_errors = self._detect_grammar_errors(text)
        all_errors.extend(grammar_errors)

        # 5. 添加参考文献格式分析（直接使用 reference_checker）
        if REFERENCE_CHECKER_AVAILABLE:
            # 将文本按行分割为段落
            paragraphs = [line.strip() for line in text.split('\n') if line.strip()]
            # 提取参考文献列表
            refs = extract_references(paragraphs)
            # 检查编号序列
            index_errors = check_index_sequence(refs)
            all_errors.extend(index_errors)
            # 对每个参考文献进行格式检查
            for ref in refs:
                # 使用 check_reference 检查格式
                check_result = check_reference(ref)
                if check_result:
                    # 使用 suggest_reference_fix 生成修正建议
                    suggestion = suggest_reference_fix(ref)
                    all_errors.append({
                        'type': 'reference',
                        'level': 'error',
                        'pos': None,
                        'text': ref,
                        'suggestion': suggestion,
                        'message': check_result
                    })

        # 按位置排序
        all_errors.sort(key=lambda x: x.get('pos', 0))

        filtered_errors = []
        for e in all_errors:
            if e.get('type') == 'spell' and e.get('level') == 'error':
                err_text = e.get('text', '')
                suggestion = e.get('suggestion', '')
                if len(err_text) == 1 and ('\u4e00' <= err_text <= '\u9fff' or '\u3400' <= err_text <= '\u4dbf'):
                    if len(suggestion) == 1 and ('\u4e00' <= suggestion <= '\u9fff' or '\u3400' <= suggestion <= '\u4dbf'):
                        if e.get('message', '') != '常见错误词替换':
                            continue
            filtered_errors.append(e)

        return ''.join(final_result), filtered_errors
    
    def _detect_grammar_errors(self, text):
        """
        检测语法和语义错误（基于规则匹配），并对文本进行实际修正
        
        Args:
            text: 待检测文本
            
        Returns:
            tuple: (修正后的文本, 语法和语义错误列表)
        """
        errors = []
        corrected_text = text
        import re
        
        # ============= 成分残缺类错误检测 =============
        
        # 1. "通过...使..."结构（缺主语）
        match = re.search(r'通过[\u4e00-\u9fa5，。、；：]+使', text)
        if match:
            suggestion = match.group().replace('使', '让')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "成分残缺：\"通过...使...\"结构导致主语缺失，建议改为\"通过...让...\"或删除\"通过\""
            })
        
        # 2. "经过...让..."结构（缺主语）
        match = re.search(r'经过[\u4e00-\u9fa5，。、；：]+让', text)
        if match:
            suggestion = match.group().replace('让', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "成分残缺：\"经过...让...\"结构导致主语缺失，建议删除\"让\""
            })
        
        # 3. "在...中，让..."结构（缺主语）
        match = re.search(r'在[\u4e00-\u9fa5，。、；：]+中[\u4e00-\u9fa5，。、；：]*让', text)
        if match:
            suggestion = match.group().replace('让', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "成分残缺：\"在...中，让...\"结构导致主语缺失，建议删除\"让\""
            })
        
        # 4. "根据...显示"结构（缺主语）
        match = re.search(r'根据[\u4e00-\u9fa5，。、；：]+显示', text)
        if match:
            suggestion = match.group().replace('根据', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "成分残缺：\"根据...显示\"结构冗余，建议删除\"根据\""
            })
        
        # 5. "随着...让..."结构（缺主语）
        match = re.search(r'随着[\u4e00-\u9fa5，。、；：]+让', text)
        if match:
            suggestion = match.group().replace('让', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "成分残缺：\"随着...让...\"结构导致主语缺失，建议删除\"让\""
            })
        
        # ============= 句式杂糅类错误检测 =============
        
        # 6. "目的是为了..."杂糅
        match = re.search(r'目的是为了', text)
        if match:
            suggestion = "目的是"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "句式杂糅：\"目的是为了\"重复，建议改为\"目的是\"或\"为了\""
            })
        
        # 7. "初衷是为了..."杂糅
        match = re.search(r'初衷是为了|初衷主要是以', text)
        if match:
            suggestion = "初衷是"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "句式杂糅：\"初衷是为了\"重复，建议改为\"初衷是\""
            })
        
        # 8. "之所以...其原因是因为..."杂糅
        match = re.search(r'之所以.*原因是因为|之所以.*是因为', text)
        if match:
            suggestion = "原因是"
            corrected_text = re.sub(r'之所以.*(原因是因为|是因为)', suggestion, corrected_text)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group()[:15] + "...",
                "suggestion": suggestion,
                "message": "句式杂糅：\"之所以...是因为\"重复，建议改为\"原因是\"或\"由于\""
            })
        
        # 9. "围绕...作为核心"杂糅
        match = re.search(r'围绕.*作为核心|围绕.*为核心', text)
        if match:
            suggestion = "围绕"
            corrected_text = re.sub(r'围绕(.*)(作为核心|为核心)', suggestion + r'\1', corrected_text)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "句式杂糅：\"围绕...作为核心\"重复，建议改为\"围绕\"或\"以...为核心\""
            })
        
        # 10. "具有...作用"杂糅
        match = re.search(r'实现.*功能作用|具有.*作用', text)
        if match:
            suggestion = match.group().replace('作用', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "句式杂糅：\"功能作用\"或\"具有...作用\"冗余，建议删除\"作用\""
            })
        
        # ============= 语义重复啰嗦类错误检测 =============
        
        # 11. 程度副词重复
        match = re.search(r'十分显著明显|非常重大的重要|普遍十分|十分非常', text)
        if match:
            suggestion = re.sub(r'(十分|非常|显著|明显|重大的|重要)', '', match.group())[:4]
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：程度副词重复使用，建议简化表达"
            })
        
        # 12. 数量词重复
        match = re.search(r'大量很多|许多很多|众多大量', text)
        if match:
            suggestion = match.group()[:2]
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：数量词重复使用，建议使用单个词"
            })
        
        # 13. 动词重复
        match = re.search(r'反复多次不断|多次反复|不断反复', text)
        if match:
            suggestion = "多次"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：动词重复使用，建议简化为\"多次\""
            })
        
        # 14. 结果重复
        match = re.search(r'最终结论结果|最终结果|结论结果', text)
        if match:
            suggestion = "结论"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：\"结论\"与\"结果\"重复，建议使用\"结论\""
            })
        
        # 15. 副词重复
        match = re.search(r'快速迅速|迅速高效|高效精准', text)
        if match:
            suggestion = match.group()[:2]
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：副词重复使用，建议使用单个词"
            })
        
        # 16. 形容词重复
        match = re.search(r'规范统一整齐|统一整齐|规范整齐', text)
        if match:
            suggestion = "规范统一"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：形容词重复使用，建议简化为\"规范统一\""
            })
        
        # 17. 整体重复
        match = re.search(r'整体整体|总体上大体|预期想要', text)
        if match:
            suggestion = match.group()[:2]
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：词语重复使用，建议删除重复部分"
            })
        
        # ============= 关联词错误类检测 =============
        
        # 18. "只要...才能..."搭配错误
        match = re.search(r'只要.*才能', text)
        if match:
            suggestion = match.group().replace('只要', '只有')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "关联词搭配错误：\"只要\"应与\"就\"搭配，\"只有\"才与\"才能\"搭配"
            })
        
        # 19. "不但...而且..."位置错误
        match = re.search(r'不但[\u4e00-\u9fa5]{2,4}，而且', text)
        if match and match.group().count('，') >= 1:
            suggestion = match.group()[:2] + match.group()[2:].replace('，', '') + "，"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "关联词位置错误：\"不但\"应放在主语之后"
            })
        
        # 20. "虽然...但是..."搭配错误
        match = re.search(r'虽然.*但是.*不仅', text)
        if match:
            suggestion = re.sub(r'虽然|但是', '', match.group())[:10]
            corrected_text = re.sub(r'虽然(.*)但是(.*)不仅', r'\1\2不仅', corrected_text)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group()[:15] + "...",
                "suggestion": suggestion,
                "message": "关联词使用不当：\"虽然...但是...\"与\"不仅\"混用，建议简化句式"
            })
        
        # 21. "即使...但是..."搭配错误
        match = re.search(r'即使.*但是', text)
        if match:
            suggestion = match.group().replace('即使', '虽然')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "关联词搭配错误：\"即使\"应与\"也\"搭配，\"虽然\"才与\"但是\"搭配"
            })
        
        # 22. "要么...要么..."搭配错误
        match = re.search(r'要么.*要么.*才能', text)
        if match:
            suggestion = "只有" + match.group()[2:].replace('要么', '').replace('才能', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "关联词搭配错误：\"要么...要么...\"是选择关系，不能与\"才能\"搭配"
            })
        
        # ============= 逻辑连接词错误检测 =============
        
        # 23. "所以因此"重复
        match = re.search(r'所以因此|因此所以|故而所以', text)
        if match:
            suggestion = "因此"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "逻辑连接词重复：建议使用单个连接词"
            })
        
        # 24. "必须一定"重复
        match = re.search(r'必须一定|一定要必须', text)
        if match:
            suggestion = "必须"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：\"必须\"与\"一定\"重复，建议使用\"必须\""
            })
        
        # 25. "完全彻底"重复
        match = re.search(r'完全彻底|彻底完全', text)
        if match:
            suggestion = "完全"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：\"完全\"与\"彻底\"重复，建议使用\"完全\""
            })
        
        # 26. "所有全部"重复
        match = re.search(r'所有全部|全部所有', text)
        if match:
            suggestion = "所有"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：\"所有\"与\"全部\"重复，建议使用\"所有\""
            })
        
        # 27. "同时也要并且"重复
        match = re.search(r'同时也要并且|既要.*也要并且', text)
        if match:
            suggestion = "同时也要"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义重复：连接词重复使用，建议简化"
            })
        
        # ============= 逻辑搭配不当类检测 =============
        
        # 28. "改善...习惯"搭配不当
        match = re.search(r'改善.*习惯', text)
        if match:
            suggestion = "纠正" + match.group()[2:]
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "搭配不当：\"改善\"与\"习惯\"搭配不当，建议使用\"纠正\"或\"养成\""
            })
        
        # 29. "影响...不好"搭配不当
        match = re.search(r'影响.*不好|影响.*变差', text)
        if match:
            suggestion = match.group().replace('不好', '').replace('变差', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "搭配不当：\"影响\"已包含负面含义，无需再加\"不好\"或\"变差\""
            })
        
        # 30. "降低...变差"搭配不当
        match = re.search(r'降低.*变差|降低.*不好', text)
        if match:
            suggestion = match.group().replace('变差', '').replace('不好', '')
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "搭配不当：\"降低\"已包含负面含义，无需再加\"变差\"或\"不好\""
            })
        
        # 31. "速度就越快很多"搭配不当
        match = re.search(r'速度就越快很多|时间速度', text)
        if match:
            suggestion = "速度就越快"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "搭配不当：\"越快\"与\"很多\"重复，建议简化"
            })
        
        # ============= 摘要语病专项检测 =============
        
        # 32. "研究探讨和分析了"冗余
        match = re.search(r'研究探讨和分析|研究分析探讨', text)
        if match:
            suggestion = "研究"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "摘要语病：动词冗余，建议简化为\"研究\""
            })
        
        # 33. "为了能够"冗余
        match = re.search(r'为了能够|为了可以', text)
        if match:
            suggestion = "为"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "摘要语病：\"为了\"已包含\"能够\"的含义，建议简化为\"为\""
            })
        
        # 34. "一系列相关问题现状"冗余
        match = re.search(r'一系列相关问题|一系列.*问题现状', text)
        if match:
            suggestion = "问题"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "摘要语病：\"一系列\"、\"相关\"、\"现状\"冗余，建议简化为\"问题\""
            })
        
        # 35. "具备较好良好的实用应用价值"冗余
        match = re.search(r'具备较好良好|实用应用价值', text)
        if match:
            suggestion = "具备良好的应用价值"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "摘要语病：形容词和名词重复，建议简化"
            })
        
        # 36. "不仅...而且同时也"冗余
        match = re.search(r'不仅.*而且同时也|不仅.*同时也', text)
        if match:
            suggestion = "不仅...还"
            corrected_text = re.sub(r'不仅(.*)而且同时也', r'不仅\1还', corrected_text)
            corrected_text = re.sub(r'不仅(.*)同时也', r'不仅\1还', corrected_text)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "摘要语病：连接词冗余，建议简化为\"不仅...还\""
            })
        
        # ============= 其他常见语法错误 =============
        
        # 37. 重复词检测
        match = re.search(r'(\b[\u4e00-\u9fa5]{1,4}\b)\s+\1', text)
        if match:
            suggestion = match.group(1)
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "warning",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "重复使用词语，请检查是否需要删除"
            })
        
        # 38. "的"字错误使用（如"很的好"）
        match = re.search(r'([很非常特别十分格外相当])\s*的\s*([\u4e00-\u9fa5]{2,})', text)
        if match and match.group(2) not in ['情况', '程度', '多', '少', '大', '小', '方面']:
            suggestion = match.group(1) + match.group(2)
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "可能存在\"的\"字多余，建议改为\"" + suggestion + "\""
            })
        
        # 39. 连续多个"的"
        match = re.search(r'的{2,}', text)
        if match:
            suggestion = "的"
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "grammar",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "连续使用多个\"的\"，建议改为单个\"的\""
            })
        
        # 40. 语义矛盾 - 否定词与肯定词冲突
        match = re.search(r'没[有]*[是能会可以应该能够]', text)
        if match:
            suggestion = match.group()[1:] if match.group().startswith('没') else match.group()
            corrected_text = corrected_text.replace(match.group(), suggestion)
            errors.append({
                "type": "semantic",
                "level": "error",
                "pos": match.start(),
                "text": match.group(),
                "suggestion": suggestion,
                "message": "语义矛盾：否定词与肯定词冲突"
            })
        
        # 41. 句子缺少主语（以动词开头）
        sentences = re.split(r'[。！？]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 8:
                verbs = ['研究', '分析', '探讨', '提出', '认为', '指出', '表明', '显示', '发现', '得到', '开展', '进行']
                for verb in verbs:
                    if sentence.startswith(verb) and not re.match(r'^[我你他她它我们你们他们这那此该本某][\u4e00-\u9fa5]', sentence):
                        suggestion = "本文" + sentence[:5]
                        corrected_text = corrected_text.replace(sentence, suggestion + sentence[5:])
                        errors.append({
                            "type": "grammar",
                            "level": "warning",
                            "pos": text.find(sentence),
                            "text": sentence[:10] + "...",
                            "suggestion": suggestion,
                            "message": "句子可能缺少主语，建议补充主语如\"本文\"、\"作者\"等"
                        })
                        break
        
        return corrected_text, errors
    
    def correct_text(self, text):
        """组合纠错：macbert + pycorrector + 语法检测 + 参考文献分析"""
        if not text or not text.strip():
            return text, []
        
        # 调用原有的组合纠错方法
        final_result, all_errors = self._original_correct_text(text)
        
        # 添加语法和语义错误检测
        grammar_corrected_text, grammar_errors = self._detect_grammar_errors(final_result)
        all_errors.extend(grammar_errors)
        # 应用语法纠错到最终结果
        final_result = grammar_corrected_text
        
        # 按位置排序
        all_errors.sort(key=lambda x: x.get('pos', 0))
        
        # 过滤空白字符错误（空格、制表符、换行等不应该被当作错误）
        all_errors = [
            err for err in all_errors 
            if 'text' in err and err['text'] and err['text'].strip()
        ]
        
        return final_result, all_errors
    
    def _original_correct_text(self, text):
        """原有的组合纠错方法（用于内部调用）"""
        if not text or not text.strip():
            return text, []
        
        # 1. macbert纠错（包含错误映射表修正）
        macbert_result, macbert_errors = self.single_corrector.correct(text)
        
        # 2. pycorrector纠错
        if self.use_pycorrector:
            pycorrector_result, pycorrector_errors = self._pycorrector_correct(text)
        else:
            pycorrector_result = text
            pycorrector_errors = []
        
        # 3. 投票融合：以macbert结果为基础（已包含错误映射表修正）
        final_result = list(macbert_result)
        all_errors = []
        
        # 获取macbert错误映射表修正的位置范围
        map_corrected_positions = set()
        for e in macbert_errors:
            if e.get('message') == '常见错误词替换':
                pos = e['pos']
                length = len(e['text'])
                for i in range(pos, pos + length):
                    map_corrected_positions.add(i)
        
        # 合并错误列表（去重）
        macbert_error_set = {(e['pos'], e['text']) for e in macbert_errors}
        
        for e in macbert_errors:
            all_errors.append(e)
        for e in pycorrector_errors:
            if (e['pos'], e['text']) not in macbert_error_set:
                # 检查是否在保护词汇中
                is_protected = False
                for term in self.single_corrector.protected_terms:
                    term_len = len(term)
                    pos = e['pos']
                    if pos + len(e['text']) <= len(text):
                        for start_offset in range(max(0, pos - term_len + 1), min(pos + 1, len(text) - term_len + 1)):
                            end_offset = start_offset + term_len
                            if end_offset <= len(text) and text[start_offset:end_offset] == term:
                                if start_offset <= pos < end_offset:
                                    is_protected = True
                                    break
                    if is_protected:
                        break
                if not is_protected:
                    all_errors.append(e)
        
        # 投票融合：只处理原始文本范围内的字符，且不覆盖错误映射表已修正的位置
        for i in range(len(text)):
            if i in map_corrected_positions:
                continue
            
            is_protected = self.single_corrector._is_in_protected_term(text, i, text[i])
            if is_protected:
                final_result[i] = text[i]
                continue
            
            macbert_char = macbert_result[i] if i < len(macbert_result) else text[i]
            pycorrector_char = pycorrector_result[i] if i < len(pycorrector_result) else text[i]
            original_char = text[i]

            is_single_cjk = ('\u4e00' <= original_char <= '\u9fff' or '\u3400' <= original_char <= '\u4dbf')
            if is_single_cjk:
                if len(macbert_char) == 1 or len(pycorrector_char) == 1:
                    final_result[i] = original_char
                    continue

            if macbert_char == pycorrector_char and macbert_char != original_char:
                final_result[i] = macbert_char
            elif macbert_char != original_char and pycorrector_char == original_char:
                pass
            elif pycorrector_char != original_char and macbert_char == original_char:
                final_result[i] = pycorrector_char
        
        return ''.join(final_result), all_errors
    
    def _pycorrector_correct(self, text):
        """使用pycorrector进行规则纠错（emoji由后续投票融合阶段保护）"""
        try:
            # 直接对原始文本进行纠错
            # emoji会在后续的投票融合阶段被保护（_is_in_protected_term会检查emoji）
            result = self.pycorrector.correct(text)
            
            if isinstance(result, tuple) and len(result) >= 1:
                corrected = result[0]
            elif isinstance(result, dict) and 'target' in result:
                corrected = result['target']
            else:
                corrected = str(result)
            
            # 处理错误列表
            errors = []
            if isinstance(result, tuple) and len(result) >= 2 and isinstance(result[1], list):
                for item in result[1]:
                    if isinstance(item, tuple) and len(item) >= 3:
                        # 检查是否涉及emoji
                        is_emoji_error = self.single_corrector._contains_emoji(item[0]) or \
                                        self.single_corrector._contains_emoji(str(item[2]))
                        if not is_emoji_error:
                            errors.append({
                                "type": "spell",
                                "level": "error",
                                "pos": item[1],
                                "text": item[0],
                                "suggestion": item[2],
                                "message": "pycorrector修正"
                            })
            
            return corrected, errors
        except Exception as e:
            print(f"[ERROR] pycorrector纠错失败: {e}")
            return text, []
