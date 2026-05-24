import torch
import os
from transformers import BertTokenizer, BertForMaskedLM

def load_model(model_path):
    """加载模型和tokenizer（本地文件）"""
    # 确保路径存在
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型路径不存在: {model_path}")
    
    # 获取绝对路径（使用正斜杠避免Windows路径问题）
    model_path = os.path.abspath(model_path).replace("\\", "/")
    print(f"加载本地模型: {model_path}")
    
    # 检查目录中是否有必要的文件
    required_files = ["vocab.txt", "config.json", "pytorch_model.bin"]
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            print(f"警告: 缺少文件 {file}")
    
    # 加载tokenizer和模型
    tokenizer = BertTokenizer.from_pretrained(
        model_path, 
        local_files_only=True,
        trust_remote_code=False
    )
    model = BertForMaskedLM.from_pretrained(
        model_path, 
        local_files_only=True,
        trust_remote_code=False
    )
    model.eval()
    return tokenizer, model

# AI领域专业术语保护列表（避免误纠正）
PROTECTED_TERMS = {
    "深度学习", "机器学习", "人工智能", "自然语言处理", "计算机视觉",
    "神经网络", "卷积神经网络", "循环神经网络", "Transformer", "BERT",
    "GPT", "PyTorch", "TensorFlow", "NLP", "CV", "GPU", "CPU",
    "特征工程", "数据挖掘", "知识图谱", "推荐系统", "强化学习",
    "迁移学习", "联邦学习", "半监督学习", "无监督学习", "监督学习",
    "词嵌入", "语义分析", "句法分析", "实体识别", "关系抽取",
    "文本生成", "机器翻译", "问答系统", "情感分析", "文本摘要",
    "图像识别", "目标检测", "语义分割", "实例分割", "姿态估计",
    "奖励函数", "策略梯度", "Q学习", "马尔可夫", "贝尔曼",
    "协同过滤", "矩阵分解", "冷启动", "召回策略", "排序模型",
    "Adam", "SGD", "梯度下降", "反向传播", "正则化",
    "过拟合", "欠拟合", "泛化能力", "鲁棒性", "准确率",
    "召回率", "F1分数", "损失函数", "优化器", "学习率",
    "batch", "epoch", "dropout", "attention", "embedding"
}

# 中文常用词汇词典（确保预测词是合理的中文词汇）
COMMON_CHINESE_WORDS = {
    "的", "是", "在", "有", "和", "了", "我", "你", "他", "她",
    "它", "这", "那", "上", "下", "前", "后", "左", "右", "中",
    "大", "小", "多", "少", "高", "低", "长", "短", "宽", "窄",
    "深", "浅", "远", "近", "好", "坏", "美", "丑", "真", "假",
    "正", "反", "东", "西", "南", "北", "里", "外", "内", "外",
    "来", "去", "出", "入", "进", "退", "开", "关", "走", "跑",
    "跳", "飞", "游", "爬", "吃", "喝", "睡", "坐", "站", "躺",
    "看", "听", "说", "读", "写", "想", "做", "学", "教", "会",
    "能", "会", "可以", "应该", "必须", "要", "不要", "不会", "不能",
    "任务", "检测", "识别", "分析", "处理", "实现", "设计", "应用", "发展",
    "技术", "算法", "模型", "系统", "方法", "理论", "研究", "工作", "学习",
    "重要", "关键", "核心", "广泛", "有效", "显著", "良好", "优秀", "成功",
    "通过", "基于", "使用", "采用", "提出", "解决", "提高", "提升", "优化",
    "图像", "文本", "数据", "知识", "特征", "结果", "性能", "指标", "效果",
    "领域", "应用", "场景", "任务", "问题", "挑战", "方案", "策略", "机制"
}

# 已知错别字对字典（只纠正这些明确的错误）
KNOWN_ERRORS = {
    # AI领域常见错别字
    "习学": "学习", "学系": "学习", "图象": "图像", "图相": "图像",
    "网洛": "网络", "神精": "神经", "卷基": "卷积", "全连": "全连接",
    "池化": "池化", "函數": "函数", "反传波": "反向传播", "瀑炸": "爆炸",
    "词嵌如": "词嵌入", "分折": "分析", "生诚": "生成", "翻泽": "翻译",
    "问达": "问答", "推鉴": "推荐", "圗谱": "图谱", "知只": "知识",
    "数居": "数据", "挖倔": "挖掘", "可视画": "可视化", "标住": "标注",
    "奖赏": "奖励", "值函數": "值函数", "策略": "策略", "马尔可夫": "马尔可夫",
    "贝尔曼": "贝尔曼", "关细": "关系", "表答": "表达", "推理": "推理",
    "协同过虑": "协同过滤", "矩阵分结": "矩阵分解", "隐式": "隐式",
    "伦里": "伦理", "漂逸": "漂移", "退化": "退化",
    "编呈": "编程", "设汁": "设计", "优话": "优化", "计祘": "计算",
    "分布试": "分布式", "云计祘": "云计算", "边端": "边缘", "中芯": "中心",
    # 单字错误
    "洛": "络", "积": "积", "虑": "滤", "诚": "成", "如": "入",
    "赏": "励", "细": "系", "居": "据", "象": "像", "相": "像",
    "里": "理", "折": "析", "形": "型", "加": "架", "泽": "译",
    "住": "注", "炼": "练", "呈": "程", "基": "积",
    # 常见错误词组
    "神经网洛": "神经网络", "卷基层": "卷积层", "词嵌如": "词嵌入",
    "协同过虑": "协同过滤", "知识圗谱": "知识图谱", "数居挖掘": "数据挖掘",
    "大数居": "大数据", "计算机视学": "计算机视觉", "自然语言处里": "自然语言处理",
    "BERT模形": "BERT模型", "深习": "深度学习", "习学": "学习"
}

def correct_text(text, tokenizer, model, device="cpu", confidence_threshold=0.995, max_iterations=5):
    """使用模型进行文本纠错（迭代式，带置信度阈值过滤和术语保护）"""
    model.to(device)
    current_text = text
    all_corrections = []  # 记录所有纠正
    
    for iteration in range(max_iterations):
        tokens = tokenizer.tokenize(current_text)
        if not tokens:
            break
        
        input_ids = tokenizer.encode(current_text, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            max_probs, predictions = torch.max(probs, dim=-1)
        
        # 找到置信度最高且超过阈值的错误
        best_correction = None
        best_confidence = 0.0
        
        for i, (token_id, prob) in enumerate(zip(predictions[0][1:-1], max_probs[0][1:-1])):
            original_token = tokens[i]
            predicted_token = tokenizer.decode(token_id)
            confidence = prob.item()
            
            # 跳过专业术语（保护AI领域术语不被误改）
            if original_token in PROTECTED_TERMS:
                continue
            
            # 检查预测词是否是合理的中文词汇
            # 如果预测词不在常用词词典中且不是单字，跳过此预测
            if len(predicted_token) > 1 and predicted_token not in COMMON_CHINESE_WORDS:
                continue
            
            # 【关键优化】只纠正已知的错别字对
            # 如果原词不是常见错误词，跳过（减少误纠正）
            if original_token not in KNOWN_ERRORS:
                continue
            
            # 如果预测词不是对应的正确词，跳过
            if KNOWN_ERRORS.get(original_token) != predicted_token:
                continue
            
            if predicted_token != original_token and confidence >= confidence_threshold and confidence > best_confidence:
                best_correction = (i, original_token, predicted_token, confidence)
                best_confidence = confidence
        
        if best_correction:
            i, original_token, predicted_token, confidence = best_correction
            # 构建新文本
            new_tokens = tokens[:i] + [predicted_token] + tokens[i+1:]
            current_text = tokenizer.convert_tokens_to_string(new_tokens)
            all_corrections.append(best_correction)
        else:
            # 没有高置信度的错误，结束迭代
            break
    
    return current_text, all_corrections

def test_models():
    """测试并对比微调前后的模型（带置信度阈值过滤）"""
    # 获取脚本所在目录的父目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 模型路径（使用相对路径避免空格问题）
    original_model_path = os.path.join(base_dir, 'models', 'macbert_v3', 'Macadam', 'macbert4mdcspell_v3')
    finetuned_model_path = os.path.join(base_dir, 'models', 'macbert_finetuned')
    
    # 置信度阈值（可调整，越高越保守，减少过度纠正）
    confidence_threshold = 0.99
    
    # 测试样本（AI领域常见错误）
    test_cases = [
        "深度习学模型在图象识别任务中表现出色。",
        "神经网洛通过卷基层提取特征。",
        "协同过虑算法用于推荐系统。",
        "文本生诚技术基于词嵌如实现。",
        "强化学习中的奖赏函数设计至关重要。",
        "知识圗谱构建需要实体关细抽取。",
        "数居挖掘技术在大数居分析中应用广泛。",
        "计算机视学中的目标检测算法不断发展。",
        "自然语言处里中的语义分折是关键技术。",
        "BERT模形在NLP任务中取得了state-of-the-art结果。",
        "基于PyTorch的深度学习框加支持自动微分。",
        "图相识别技术在自动驾驶领域具有广阔应用前景。",
        "机器翻泽系统的性能评估需要多维度指标。",
        "数据标住质量直接影响模型训炼效果。",
        "特征工呈是机器学习流水线的重要环节。"
    ]
    
    print("=" * 80)
    print("AI领域文本纠错模型对比测试（置信度阈值：%.2f）" % confidence_threshold)
    print("=" * 80)
    
    # 加载原始模型
    print("\n加载原始模型...")
    orig_tokenizer, orig_model = load_model(original_model_path)
    
    # 加载微调后模型
    print("加载微调后模型...")
    ft_tokenizer, ft_model = load_model(finetuned_model_path)
    
    print("\n" + "=" * 80)
    print(f"{'原文':<40} {'原始模型':<40} {'微调后模型':<40}")
    print("=" * 120)
    
    for text in test_cases:
        orig_result, orig_corrections = correct_text(text, orig_tokenizer, orig_model, confidence_threshold=confidence_threshold)
        ft_result, ft_corrections = correct_text(text, ft_tokenizer, ft_model, confidence_threshold=confidence_threshold)
        
        print(f"{text:<40} {orig_result:<40} {ft_result:<40}")
        
        # 打印详细纠正信息
        if ft_corrections:
            print(" " * 40 + f"  微调模型纠正: {ft_corrections}")
    
    print("\n" + "=" * 80)
    print("测试完成！")

if __name__ == "__main__":
    test_models()
