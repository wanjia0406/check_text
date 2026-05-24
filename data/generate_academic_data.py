import json
import os
import random

# ==================== 人工智能领域错误模式 ====================
AI_ERRORS = {
    # 常见错别字
    "未莱": "未来", "将进": "将近", "一不": "一步", "优话": "优化",
    "模形": "模型", "错识": "错误", "语发": "语法", "识边": "识别",
    "能尼": "能力", "智恩": "智能", "完山": "完善", "系通": "系统",
    "算发": "算法", "特正": "特征", "训炼": "训练", "测式": "测试",
    "验正": "验证", "分折": "分析", "建摸": "建模", "数剧": "数据",
    "挖崛": "挖掘", "机戒": "机械", "学系": "学习", "神径": "神经",
    "网洛": "网络", "深渡": "深度", "加树": "加速", "并形": "并行",
    "串形": "串行", "存诸": "存储", "处里": "处理", "输λ": "输入",
    "输岀": "输出", "接囗": "接口", "协义": "协议", "标谁": "标准",
    "格试": "格式", "编玛": "编码", "译玛": "译码", "加蜜": "加密",
    "解蜜": "解密", "压宿": "压缩", "搜素": "搜索", "排徐": "排序",
    "插如": "插入", "删出": "删除", "修该": "修改", "查旬": "查询",
    "更行": "更新", "卷及": "卷积", "神精": "神经", "全连": "全连接",
    "反传": "反向传播", "损实": "损失", "优画": "优化", "梯读": "梯度",
    "下将": "下降", "随极": "随机", "森令": "森林", "向量": "向量",
    "举证": "矩阵", "张是": "张量", "偏导": "偏导", "求导": "求导",
    "积份": "积分", "似然": "似然", "概律": "概率", "拟和": "拟合",
    "预则": "预测", "模似": "模拟", "仿直": "仿真", "评佑": "评估",
    
    # 机器学习特定错误
    "机戒学习": "机器学习", "机学": "机器学习", "机习": "机器学习",
    "深度学系": "深度学习", "深渡学习": "深度学习", "深学": "深度学习",
    "人工知能": "人工智能", "人工智": "人工智能", "人智": "人工智能",
    "自然语言处里": "自然语言处理", "自然语处理": "自然语言处理",
    "计祘机视觉": "计算机视觉", "计算机视": "计算机视觉",
    "强化学习": "强化学习", "强化学系": "强化学习", "强化学": "强化学习",
    "迁移学习": "迁移学习", "迁秊学习": "迁移学习", "迁移学": "迁移学习",
    "联邦学习": "联邦学习", "联帮学习": "联邦学习", "联邦学": "联邦学习",
    "半监督学习": "半监督学习", "半监都学习": "半监督学习",
    "无监督学习": "无监督学习", "无监都学习": "无监督学习",
    
    # 神经网络架构错误
    "卷及神经": "卷积神经", "卷及网络": "卷积网络", "卷机": "卷积",
    "循还神经": "循环神经", "循还网络": "循环网络",
    "长短记亿": "长短期记忆", "长短期记": "长短期记忆",
    "门空循环": "门控循环", "门空单元": "门控单元",
    
    # 优化算法错误
    "梯度下将": "梯度下降", "梯读下降": "梯度下降",
    "随极梯度": "随机梯度", "动粮法": "动量法",
    "adam优化": "Adam优化", "学系率": "学习率",
    
    # 评估指标错误
    "准确卒": "准确率", "召会率": "召回率", "精que率": "精确率",
    "损实函数": "损失函数", "过拟和": "过拟合", "欠拟和": "欠拟合",
    "正侧化": "正则化", "交差验证": "交叉验证", "数剧增强": "数据增强",
    
    # 模型组件错误
    "嵌如层": "嵌入层", "注义力机制": "注意力机制", "多头注义力": "多头注意力",
    "编玛器": "编码器", "解玛器": "解码器",
    
    # 应用场景错误
    "文本分類": "文本分类", "情感分折": "情感分析", "机戒翻译": "机器翻译",
    "图象识别": "图像识别", "语因合成": "语音合成", "问达系统": "问答系统",
    "推鉴系统": "推荐系统", "知识圗谱": "知识图谱",
}

# ==================== 扩展错误模式（新增）====================
EXTENDED_ERRORS = {
    # 数据科学术语
    "数居": "数据", "分折师": "分析师", "挖倔": "挖掘", "可视画": "可视化",
    "模形化": "模型化", "特征工呈": "特征工程", "数据清洗": "数据清洗",
    "数据标住": "数据标注", "数据集": "数据集", "样例": "样本",
    "数据探勘": "数据挖掘", "数据分折": "数据分析", "数据整里": "数据整理",
    "数据变显": "数据变现", "数据驱东": "数据驱动", "大数居": "大数据",
    
    # 深度学习术语
    "神经网洛": "神经网络", "卷积神精": "卷积神经", "全连接层": "全连接层",
    "池化层": "池化层", "激活函數": "激活函数", "前馈网络": "前馈网络",
    "反传波": "反向传播", "梯度消失": "梯度消失", "梯度瀑炸": "梯度爆炸",
    "卷积核": "卷积核", "卷基层": "卷积层", "归一话": "归一化",
    "批归一化": "批归一化", "残差网洛": "残差网络", "注意力层": "注意力层",
    
    # NLP特定错误
    "词嵌如": "词嵌入", "语义分折": "语义分析", "句法分折": "句法分析",
    "命名实体": "命名实体", "实体识别": "实体识别", "关系抽取": "关系抽取",
    "文本生诚": "文本生成", "机器翻泽": "机器翻译", "问答系通": "问答系统",
    "情感分惜": "情感分析", "文本向量化": "文本向量化", "词法分折": "词法分析",
    "指代消解": "指代消解", "文本摘药": "文本摘要", "关键此提取": "关键词提取",
    
    # CV特定错误
    "图相识别": "图像识别", "目标检测": "目标检测", "语议分割": "语义分割",
    "实例分割": "实例分割", "姿杰估计": "姿态估计", "人脸识辩": "人脸识别",
    "物体跟综": "物体跟踪", "图像生诚": "图像生成", "超分辨律": "超分辨率",
    "图像分折": "图像分析", "图像检索": "图像检索", "特征提娶": "特征提取",
    "图像配准": "图像配准", "图像融合": "图像融合", "三维重建": "三维重建",
    
    # 强化学习错误
    "奖赏函数": "奖励函数", "策略梯度": "策略梯度", "值函數": "值函数",
    "Q学习": "Q学习", "深度Q网络": "深度Q网络", "策略优化": "策略优化",
    "演员评论家": "演员评论家", "马尔可夫": "马尔可夫", "贝尔曼": "贝尔曼",
    "状态空间": "状态空间", "动作空间": "动作空间", "回报函数": "回报函数",
    "策略网络": "策略网络", "值网络": "值网络", "探索利用": "探索利用",
    
    # 知识图谱错误
    "实体关细": "实体关系", "知识表答": "知识表达", "知识推理": "知识推理",
    "本体论": "本体论", "语义网": "语义网", "RDF": "RDF", "OWL": "OWL",
    "三元组": "三元组", "知识存诸": "知识存储", "知识融合": "知识融合",
    "知识图谱构建": "知识图谱构建", "实体链结": "实体链接", "关系图谱": "关系图谱",
    
    # 推荐系统错误
    "协同过虑": "协同过滤", "内容推荐": "内容推荐", "混合推荐": "混合推荐",
    "矩阵分结": "矩阵分解", "因子分解": "因子分解", "隐式反馈": "隐式反馈",
    "个性化推荐": "个性化推荐", "推荐算法": "推荐算法", "冷启动": "冷启动",
    "召回策略": "召回策略", "排序模型": "排序模型", "多目标优化": "多目标优化",
    
    # 新增：AI框架与工具
    "TensorFlow": "TensorFlow", "Pytorch": "PyTorch", "PyTorch": "PyTorch",
    "MXNet": "MXNet", "Keras": "Keras", "Scikit-learn": "scikit-learn",
    "OpenCV": "OpenCV", "NLTK": "NLTK", "SpaCy": "spaCy",
    
    # 新增：AI伦理与安全
    "AI伦里": "AI伦理", "数据隐私": "数据隐私", "算法偏见": "算法偏见",
    "可解释AI": "可解释AI", "AI安全": "AI安全", "对抗攻击": "对抗攻击",
    "模型鲁棒性": "模型鲁棒性", "数据漂逸": "数据漂移", "模型退化": "模型退化",
    
    # 新增：AI应用场景
    "智能客服": "智能客服", "智能音箱": "智能音箱", "智能手表": "智能手表",
    "自动驾驶": "自动驾驶", "智能力学": "智能制造", "智能农业": "智能农业",
    "智慧医疗": "智慧医疗", "智慧教育": "智慧教育", "智慧城市": "智慧城市",
    
    # 新增：数学与统计术语
    "概率分布": "概率分布", "统计推段": "统计推断", "假没检验": "假设检验",
    "置信区间": "置信区间", "回归分折": "回归分析", "相关分折": "相关分析",
    "主成分分折": "主成分分析", "因子分折": "因子分析", "聚类分折": "聚类分析",
    
    # 新增：编程与工程术语
    "编呈": "编程", "算法设汁": "算法设计", "代码优话": "代码优化",
    "并行计祘": "并行计算", "分布试": "分布式", "云计祘": "云计算",
    "边端计祘": "边缘计算", "数据中芯": "数据中心", "服务器": "服务器",
}

# 合并所有错误模式
ALL_ERRORS = {**AI_ERRORS, **EXTENDED_ERRORS}

# ==================== AI领域句子模板 ====================
AI_TEMPLATES = [
    # 基础模板
    "{error}是{field}领域的核心{concept}，在{application}中得到广泛应用。",
    "本文提出了一种基于{error}的{method}，有效提升了{metric}性能。",
    "{error}算法通过{mechanism}机制，实现了{task}任务的{result}效果。",
    "在{field}中，{error}技术被广泛用于解决{problem}问题。",
    
    # 深度学习架构
    "{error}模型采用{architecture}架构，能够有效捕捉{aspect}特征。",
    "基于{error}的{framework}在{dataset}数据集上取得了{state_of_art}结果。",
    "{error}的{component}设计使其在{scenario}场景下表现出色。",
    
    # 训练与优化
    "通过{error}方法，可以有效{action}模型的{metric}指标。",
    "{error}策略能够有效缓解{issue}问题，提升模型的{robustness}。",
    "采用{error}优化器可以加速{training}过程，提高{efficiency}。",
    
    # 应用与评估
    "{error}技术在{industry}领域的{application}中展现出良好的{performance}。",
    "实验结果表明，{error}方法在{metric}指标上优于{baseline}方法。",
    "{error}系统通过{evaluation}评估，达到了{target}要求。",
    
    # 研究方向
    "未来的{research}将{error}，进一步{goal}模型的{capability}。",
    "{error}为{field}领域的{challenge}提供了新的{solution}。",
    "基于{error}的{innovation}有望推动{field}的{development}。",
    
    # 更具体的模板
    "{error}是{field}中的{concept}，它能够{action}{metric}。",
    "近年来，{error}在{application}领域取得了显著{result}。",
    "我们提出了一种新的{error}方法，适用于{scenario}场景。",
    "{error}与{mechanism}相结合，可以有效解决{problem}。",
    "在{dataset}数据集上的{result}表明，{error}具有良好的{aspect}。",
    "{error}的{component}设计是{field}领域的研究热点之一。",
    "通过{error}技术，我们成功{action}了{metric}性能指标。",
    "{error}算法的{mechanism}机制使其在{scenario}中表现优异。",
    
    # 新增：研究方法类模板
    "本研究采用{error}方法对{dataset}数据集进行{result}，结果表明{aspect}得到显著提升。",
    "基于{error}的{framework}被应用于{application}任务，取得了{state_of_art}的{metric}。",
    "我们设计了一种基于{error}的{method}，在{task}任务上验证了其{effectiveness}。",
    "{error}技术与{mechanism}相结合，为{field}领域提供了新的{perspective}。",
    
    # 新增：技术对比类模板
    "与{baseline}相比，{error}方法在{metric}上提升了{percentage}，表现更优。",
    "{error}算法在{scenario}场景下的{aspect}性能优于传统的{baseline}方法。",
    "实验结果显示，{error}在{dataset}上的{result}效果显著，验证了其{value}价值。",
    
    # 新增：应用场景类模板
    "{error}在{industry}领域的{application}中展现出良好的{performance}，具有广阔的{potential}。",
    "基于{error}的{system}已成功应用于{scenario}，为{field}带来了{benefit}。",
    "{error}技术在{application}中的{implementation}取得了{successful}的{outcome}。",
    
    # 新增：问题解决类模板
    "针对{issue}问题，{error}提供了一种有效的{solution}，能够{action}{metric}。",
    "{error}方法成功解决了{field}领域中的{challenge}，推动了{development}。",
    "通过{error}策略，我们有效{action}了{metric}，缓解了{issue}问题。",
    
    # 新增：理论分析类模板
    "{error}的{mechanism}机制可以通过{theory}理论进行解释，具有明确的{foundation}。",
    "从{perspective}角度分析，{error}的{design}设计符合{principle}原则。",
    "{error}的{component}结构具有良好的{property}特性，适用于{scenario}场景。",
    
    # 新增：未来展望类模板
    "{error}为{field}领域的{future}发展提供了新的{direction}，值得进一步{research}。",
    "未来的{work}将聚焦于{error}的{improvement}，以{goal}更高的{target}。",
    "基于{error}的{innovation}有望在{industry}领域实现{breakthrough}突破。",
]

# ==================== AI领域术语库 ====================
AI_TERMS = [
    "机器学习", "深度学习", "人工智能", "自然语言处理", "计算机视觉",
    "强化学习", "迁移学习", "联邦学习", "半监督学习", "无监督学习",
    "知识图谱", "推荐系统", "数据挖掘", "计算机图形学", "机器人学"
]

AI_CONCEPTS = [
    "技术", "方法", "模型", "算法", "框架", "理论", "范式", "体系",
    "原理", "机制", "策略", "方案"
]

AI_APPLICATIONS = [
    "文本分类", "情感分析", "机器翻译", "图像识别", "语音合成",
    "问答系统", "推荐系统", "知识图谱", "目标检测", "语义分割",
    "命名实体识别", "关系抽取", "文本生成", "图像生成", "语音识别"
]

AI_METHODS = [
    "方法", "算法", "框架", "模型", "系统", "方案", "策略", "技术",
    "途径", "手段", "流程", "步骤"
]

AI_PROBLEMS = [
    "分类", "回归", "聚类", "生成", "优化", "推理", "匹配", "排序",
    "检测", "识别", "抽取", "分割", "跟踪", "估计"
]

AI_ACTIONS = [
    "提升", "改善", "优化", "增强", "提高", "加速", "降低", "减少",
    "解决", "克服", "实现", "达到", "满足", "支持"
]

AI_METRICS = [
    "准确率", "召回率", "F1值", "精度", "效率", "鲁棒性", "泛化能力",
    "收敛速度", "训练效率", "推理速度", "内存占用"
]

AI_TASKS = [
    "文本纠错", "语义理解", "知识图谱", "推荐系统", "问答系统",
    "机器翻译", "图像生成", "语音识别", "目标跟踪", "异常检测",
    "文本摘要", "对话系统", "情感分析", "文档分类", "信息检索"
]

AI_RESULTS = [
    "实验", "验证", "测试", "评估", "对比", "分析", "论证", "检验",
    "证明", "验证", "确认", "展示", "表明", "揭示"
]

AI_BENEFITS = [
    "提高效率", "降低成本", "增强性能", "提升精度", "加速训练",
    "改善效果", "优化流程", "减少误差", "提高可靠性", "增强鲁棒性"
]

AI_VALUES = [
    "理论", "实践", "应用", "研究", "学术", "工业", "商业", "社会",
    "科学", "技术", "工程", "创新"
]

AI_DIRECTIONS = [
    "研究方向", "发展趋势", "技术路线", "优化策略", "改进方案",
    "未来展望", "发展方向", "研究前沿", "技术趋势"
]

AI_GOALS = [
    "提升", "优化", "改进", "增强", "完善", "突破", "创新", "超越",
    "实现", "达成", "满足", "实现"
]

AI_TARGETS = [
    "核心", "关键", "主要", "重要", "基础", "核心竞争力", "关键技术",
    "核心问题", "重点方向", "首要任务"
]

AI_COMPONENTS = [
    "核心", "关键", "主要", "重要", "基础", "关键组件", "核心模块",
    "重要部分", "关键要素", "核心功能"
]

AI_ASPECTS = [
    "性能", "效率", "精度", "稳定性", "可靠性", "可扩展性",
    "鲁棒性", "泛化能力", "收敛性", "可解释性"
]

AI_OUTCOMES = [
    "最终", "预期", "实际", "理想", "最优", "令人满意", "良好",
    "优异", "出色", "卓越"
]

AI_FRAMEWORKS = [
    "架构", "框架", "平台", "系统", "工具", "基础设施",
    "开发框架", "计算平台", "训练框架", "部署系统"
]

AI_FIELDS = [
    "自然语言处理", "计算机视觉", "数据挖掘", "推荐系统", "知识图谱",
    "强化学习", "机器人", "自动驾驶", "医疗AI", "金融科技",
    "智能客服", "教育科技", "工业自动化", "智慧城市", "物联网"
]

AI_PERSPECTIVES = [
    "思路", "方法", "途径", "方向", "方案", "视角", "见解",
    "观点", "角度", "立场", "看法"
]

AI_ARCHITECTURES = [
    "Transformer", "CNN", "RNN", "LSTM", "GRU", "BERT", "GPT", "ViT",
    "ResNet", "VGG", "YOLO", "UNet", "T5", "XLNet", "ALBERT"
]

AI_MECHANISMS = [
    "注意力", "自注意力", "多头注意力", "残差连接", "归一化",
    "前馈网络", "编码器-解码器", "掩码机制", "门控机制", "记忆机制"
]

AI_DATASETS = [
    "ImageNet", "MSCOCO", "SQuAD", "GLUE", "IMDB",
    "MNIST", "CIFAR", "WikiText", "BookCorpus", "PubMed",
    "SNLI", "MultiNLI", "CoNLL", "PennTreebank", "Gutenberg"
]

AI_ISSUES = [
    "过拟合", "欠拟合", "梯度消失", "梯度爆炸", "数据稀疏",
    "计算复杂度", "内存限制", "训练不稳定", "泛化能力差", "可解释性"
]

AI_SCENARIOS = [
    "自然语言理解", "计算机视觉", "语音处理", "推荐系统", "智能对话",
    "图像生成", "文本生成", "强化学习", "知识推理", "数据挖掘"
]

AI_INDUSTRIES = [
    "医疗健康", "金融服务", "电子商务", "智能制造", "教育培训",
    "物流配送", "智能交通", "安防监控", "智能家居", "娱乐媒体"
]

AI_EVALUATIONS = [
    "定量分析", "定性评估", "消融实验", "对比实验", "用户研究",
    "交叉验证", "留一法", "自助法", "显著性检验", "误差分析"
]

AI_BASELINES = [
    "传统方法", "现有模型", "基准模型", "经典算法", "主流方案",
    "SOTA方法", "基线模型", "对比算法", "标准方法", "参考模型"
]

def generate_error_sentence():
    """生成包含AI领域错误的学术句子"""
    template = random.choice(AI_TEMPLATES)
    error_word = random.choice(list(ALL_ERRORS.keys()))
    correct_word = ALL_ERRORS[error_word]
    
    params = {
        "error": error_word,
        "term": random.choice(AI_TERMS),
        "concept": random.choice(AI_CONCEPTS),
        "application": random.choice(AI_APPLICATIONS),
        "method": random.choice(AI_METHODS),
        "problem": random.choice(AI_PROBLEMS),
        "action": random.choice(AI_ACTIONS),
        "metric": random.choice(AI_METRICS),
        "task": random.choice(AI_TASKS),
        "result": random.choice(AI_RESULTS),
        "benefit": random.choice(AI_BENEFITS),
        "value": random.choice(AI_VALUES),
        "direction": random.choice(AI_DIRECTIONS),
        "goal": random.choice(AI_GOALS),
        "target": random.choice(AI_TARGETS),
        "component": random.choice(AI_COMPONENTS),
        "aspect": random.choice(AI_ASPECTS),
        "outcome": random.choice(AI_OUTCOMES),
        "framework": random.choice(AI_FRAMEWORKS),
        "field": random.choice(AI_FIELDS),
        "perspective": random.choice(AI_PERSPECTIVES),
        "architecture": random.choice(AI_ARCHITECTURES),
        "mechanism": random.choice(AI_MECHANISMS),
        "dataset": random.choice(AI_DATASETS),
        "state_of_art": "state-of-the-art",
        "scenario": random.choice(AI_SCENARIOS),
        "issue": random.choice(AI_ISSUES),
        "robustness": "鲁棒性",
        "training": "训练",
        "efficiency": "效率",
        "industry": random.choice(AI_INDUSTRIES),
        "performance": "性能",
        "baseline": random.choice(AI_BASELINES),
        "evaluation": random.choice(AI_EVALUATIONS),
        "research": "研究",
        "challenge": "挑战",
        "solution": "解决方案",
        "innovation": "创新",
        "development": "发展",
        "capability": "能力",
        
        # 新增参数
        "property": random.choice(["稳定性", "可靠性", "可扩展性", "灵活性", "高效性"]),
        "percentage": random.choice(["10%", "15%", "20%", "25%", "30%"]),
        "value": random.choice(["实用", "理论", "应用", "研究", "商业"]),
        "potential": "应用潜力",
        "system": "系统",
        "benefit": random.choice(["显著效益", "实际价值", "积极影响", "重要贡献"]),
        "implementation": "实现",
        "successful": "成功",
        "theory": random.choice(["信息论", "概率论", "统计学", "机器学习理论"]),
        "foundation": "理论基础",
        "design": "设计",
        "principle": random.choice(["最优性", "收敛性", "稳定性", "泛化性"]),
        "future": "未来",
        "direction": random.choice(["研究方向", "发展方向", "应用方向"]),
        "work": "工作",
        "improvement": random.choice(["改进", "优化", "提升", "完善"]),
        "breakthrough": "突破性",
        "effectiveness": "有效性"
    }
    
    source = template.format(**params)
    target = source.replace(error_word, correct_word)
    
    return {"source": source, "target": target}

def generate_typo_pair():
    """生成简单的AI领域错别字对"""
    error_word = random.choice(list(ALL_ERRORS.keys()))
    correct_word = ALL_ERRORS[error_word]
    
    field = random.choice(AI_FIELDS)
    concept = random.choice(AI_CONCEPTS)
    method = random.choice(AI_METHODS)
    result = random.choice(AI_RESULTS)
    application = random.choice(AI_APPLICATIONS)
    problem = random.choice(AI_PROBLEMS)
    metric = random.choice(AI_METRICS)
    aspect = random.choice(AI_ASPECTS)
    perspective = random.choice(AI_PERSPECTIVES)
    
    sentences = [
        f"{error_word}是{field}领域的核心{concept}。",
        f"基于{error_word}的{method}取得了良好的{result}效果。",
        f"{error_word}技术在{application}中应用广泛。",
        f"我们提出了一种新的{error_word}方法。",
        f"{error_word}能够有效解决{problem}问题。",
        f"{error_word}模型的{metric}性能得到显著提升。",
        f"{error_word}算法具有良好的{aspect}特性。",
        f"{error_word}框架为{field}提供了新的{perspective}。",
        f"研究{error_word}对于{field}具有重要意义。",
        f"{error_word}在{application}任务中表现出色。",
        f"{error_word}是解决{problem}的有效途径。",
        f"近年来{error_word}得到了广泛研究和应用。",
    ]
    
    source = random.choice(sentences)
    target = source.replace(error_word, correct_word)
    
    return {"source": source, "target": target}

def generate_complex_sentence():
    """生成复杂的AI领域句子（包含多个错误）"""
    sentence_templates = [
        "本文提出了一种基于{error1}和{error2}的{method}，用于{application}任务，实验结果表明该方法在{metric}上提升了{percentage}。",
        "{error1}是{field}领域的重要{concept}，与{error2}相结合可以有效{action}模型性能，特别是在{scenario}场景下。",
        "通过{error1}机制和{error2}策略，我们设计了一个高效的{framework}，能够处理{challenge}问题。",
        "{error1}模型在{dataset}数据集上进行{error2}，取得了{state_of_art}的{result}效果。",
        "针对{problem}问题，我们采用{error1}方法和{error2}优化策略，显著{action}了{metric}指标。",
        "{error1}技术与{error2}算法相结合，在{application}任务上取得了{result}突破。",
        "基于{error1}的{framework}集成了{error2}机制，提升了{metric}性能。",
        "{error1}和{error2}是{field}领域的两个核心{concept}，它们共同推动了{development}。",
    ]
    
    template = random.choice(sentence_templates)
    error1 = random.choice(list(ALL_ERRORS.keys()))
    error2 = random.choice(list(ALL_ERRORS.keys()))
    while error2 == error1:
        error2 = random.choice(list(ALL_ERRORS.keys()))
    
    params = {
        "error1": error1,
        "error2": error2,
        "method": random.choice(AI_METHODS),
        "application": random.choice(AI_APPLICATIONS),
        "metric": random.choice(AI_METRICS),
        "percentage": str(random.randint(5, 30)) + "%",
        "field": random.choice(AI_FIELDS),
        "concept": random.choice(AI_CONCEPTS),
        "action": random.choice(AI_ACTIONS),
        "scenario": random.choice(AI_SCENARIOS),
        "framework": random.choice(AI_FRAMEWORKS),
        "challenge": random.choice(AI_ISSUES),
        "dataset": random.choice(AI_DATASETS),
        "state_of_art": "state-of-the-art",
        "result": random.choice(AI_RESULTS),
        "problem": random.choice(AI_PROBLEMS),
        "development": "发展"
    }
    
    source = template.format(**params)
    target = source.replace(error1, ALL_ERRORS[error1]).replace(error2, ALL_ERRORS[error2])
    
    return {"source": source, "target": target}

def generate_dataset(num_samples=20000, train_ratio=0.9):
    """生成AI领域训练数据集（确保不重复）"""
    data = []
    seen_sources = set()  # 用于记录已生成的源句子，避免重复
    
    max_attempts = num_samples * 5  # 最大尝试次数
    
    # 生成简单错别字样本 (40%)
    target_simple = int(num_samples * 0.4)
    attempts = 0
    while len([d for d in data if 'simple' in d.get('type', '')]) < target_simple and attempts < max_attempts:
        item = generate_typo_pair()
        if item["source"] not in seen_sources:
            item['type'] = 'simple'
            data.append(item)
            seen_sources.add(item["source"])
        attempts += 1
    
    # 生成学术句子样本 (40%)
    target_sentence = int(num_samples * 0.4)
    attempts = 0
    while len([d for d in data if d.get('type') == 'sentence']) < target_sentence and attempts < max_attempts:
        item = generate_error_sentence()
        if item["source"] not in seen_sources:
            item['type'] = 'sentence'
            data.append(item)
            seen_sources.add(item["source"])
        attempts += 1
    
    # 生成复杂句子样本 (20%)
    target_complex = int(num_samples * 0.2)
    attempts = 0
    while len([d for d in data if d.get('type') == 'complex']) < target_complex and attempts < max_attempts:
        item = generate_complex_sentence()
        if item["source"] not in seen_sources:
            item['type'] = 'complex'
            data.append(item)
            seen_sources.add(item["source"])
        attempts += 1
    
    # 打乱顺序
    random.shuffle(data)
    
    # 移除type字段（不需要保存到JSON）
    for item in data:
        item.pop('type', None)
    
    # 分割训练集和验证集
    split_idx = int(len(data) * train_ratio)
    return data[:split_idx], data[split_idx:]

def save_dataset(train_data, val_data, output_dir):
    """保存数据集到指定目录"""
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "val.json"), "w", encoding="utf-8") as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    
    print(f"训练集已保存: {len(train_data)}条")
    print(f"验证集已保存: {len(val_data)}条")
    print(f"总样本数: {len(train_data) + len(val_data)}条")

if __name__ == "__main__":
    output_dir = os.path.dirname(__file__)
    train_data, val_data = generate_dataset(num_samples=20000, train_ratio=0.9)
    save_dataset(train_data, val_data, output_dir)
    print("AI领域数据集生成完成！")
