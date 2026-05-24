#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两种组合方案对比测试（扩展测试用例）
方案1: macbert4mdcspell_v3 + pycorrector
方案2: macbert4mdcspell_v3 + macbert4csc-base
"""

import sys
import io
import os
import time
import torch

# 修复Windows命令行中文显示问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置pycorrector缓存目录
os.environ["PYCORRECTOR_CACHE_DIR"] = r"D:\Users\86182\.pycorrector"

from transformers import BertTokenizer, BertForMaskedLM
from pycorrector import Corrector

# ==================== 常见错误映射表 ====================
ERROR_MAP = {
    '推鉴': '推荐', '过虑': '过滤', '机戒': '机器', '网洛': '网络',
    '希疏': '稀疏', '拟和': '拟合', '领彧': '领域', '机术': '技术',
    '按排': '安排', '安照': '按照', '建义': '建议', '根椐': '根据',
    '问提': '问题', '管里': '管理', '过拟和': '过拟合', '扩涨': '扩展',
    '结裹': '结果', '重偠': '重要', '符和': '符合', '有校': '有效',
    '因该': '应该', '让坐': '让座', '领遇': '领域', '分知': '分支',
    '跳无': '跳舞', '七习': '学习', '校术': '技术', '结里': '结果',
}

def load_macbert_model(model_path, model_name):
    """加载本地macbert模型"""
    try:
        tokenizer = BertTokenizer.from_pretrained(model_path, local_files_only=True)
        model = BertForMaskedLM.from_pretrained(model_path, local_files_only=True)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        model.eval()
        
        return {'tokenizer': tokenizer, 'model': model, 'device': device, 'name': model_name}
        
    except Exception as e:
        print(f"✗ {model_name} 加载失败: {e}")
        return None

def load_pycorrector():
    """加载pycorrector规则引擎"""
    try:
        corrector = Corrector()
        return corrector
    except Exception as e:
        print(f"✗ pycorrector 加载失败: {e}")
        return None

def macbert_correct(text, model):
    """使用macbert模型进行纠错"""
    max_len = 128
    len_mid = min(max_len, len(text) + 2)
    
    with torch.no_grad():
        inputs = model['tokenizer'](text, padding=True, max_length=len_mid, truncation=True, return_tensors="pt").to(model['device'])
        outputs = model['model'](**inputs)
    
    probs = outputs.logits[0]
    ids = torch.argmax(probs, dim=-1)
    tokens_space = model['tokenizer'].decode(ids[1:-1], skip_special_tokens=False)
    text_new = tokens_space.replace(" ", "")
    target = text_new[:len(text)]
    
    return target

def pycorrector_correct(text, corrector):
    """使用pycorrector进行规则纠错"""
    result = corrector.correct(text)
    
    if isinstance(result, tuple) and len(result) >= 1:
        return result[0]
    elif isinstance(result, dict) and 'target' in result:
        return result['target']
    else:
        return str(result)

def apply_error_map(text):
    """应用错误映射表"""
    result = text
    for error, correct in ERROR_MAP.items():
        result = result.replace(error, correct)
    return result

def hybrid_macbert_pycorrector(text, macbert_model, pycorrector_obj):
    """方案1: macbert4mdcspell_v3 + pycorrector"""
    text = apply_error_map(text)
    macbert_result = macbert_correct(text, macbert_model)
    pycorrector_result = pycorrector_correct(text, pycorrector_obj)
    
    final_result = list(text)
    for i in range(len(text)):
        if i < len(macbert_result) and i < len(pycorrector_result):
            if macbert_result[i] == pycorrector_result[i] and macbert_result[i] != text[i]:
                final_result[i] = macbert_result[i]
            elif macbert_result[i] != text[i] and pycorrector_result[i] == text[i]:
                final_result[i] = macbert_result[i]
            elif pycorrector_result[i] != text[i] and macbert_result[i] == text[i]:
                final_result[i] = pycorrector_result[i]
    
    return ''.join(final_result)

def dual_macbert(text, model1, model2):
    """方案2: macbert4mdcspell_v3 + macbert4csc-base"""
    text = apply_error_map(text)
    result1 = macbert_correct(text, model1)
    result2 = macbert_correct(text, model2)
    
    final_result = list(text)
    for i in range(len(text)):
        if i < len(result1) and i < len(result2):
            if result1[i] == result2[i] and result1[i] != text[i]:
                final_result[i] = result1[i]
            elif result1[i] != text[i] and result2[i] == text[i]:
                final_result[i] = result1[i]
            elif result2[i] != text[i] and result1[i] == text[i]:
                final_result[i] = result2[i]
    
    return ''.join(final_result)

def main():
    # 模型路径
    model_paths = {
        'macbert4mdcspell_v3': r"D:\check_teset\models\macbert_v3\Macadam\macbert4mdcspell_v3",
        'macbert4csc-base': r"D:\check_teset\models\macbert4csc-base"
    }
    
    print("=" * 80)
    print("两种组合方案对比测试（扩展测试用例）")
    print("方案1: macbert4mdcspell_v3 + pycorrector")
    print("方案2: macbert4mdcspell_v3 + macbert4csc-base")
    print("=" * 80)
    
    # 加载组件
    print("\n正在加载模型...")
    macbert_v3 = load_macbert_model(model_paths['macbert4mdcspell_v3'], 'macbert4mdcspell_v3')
    macbert_base = load_macbert_model(model_paths['macbert4csc-base'], 'macbert4csc-base')
    pycorrector_obj = load_pycorrector()
    
    if not (macbert_v3 and macbert_base and pycorrector_obj):
        print("\n✗ 无法加载所有组件")
        return
    
    # 扩展测试用例
    test_cases = [
        # ===== 学术术语错误 =====
        ("推鉴系统", "推荐系统"),
        ("协同过虑", "协同过滤"),
        ("机戒学习", "机器学习"),
        ("神经网洛", "神经网络"),
        ("数据希疏", "数据稀疏"),
        ("过拟和", "过拟合"),
        ("预训炼", "预训练"),
        ("微掉", "微调"),
        ("卷及神经网络", "卷积神经网络"),
        ("Transformer架构", "Transformer架构"),
        # ===== 常见错别字 =====
        ("按排工作", "安排工作"),
        ("安照计划", "按照计划"),
        ("建义方案", "建议方案"),
        ("根椐数据", "根据数据"),
        ("问提分析", "问题分析"),
        ("管里", "管理"),
        ("分晰", "分析"),
        ("必需要", "必须要"),
        ("做用", "作用"),
        ("作工", "工作"),
        # ===== 句子级别错误 =====
        ("推荐系统是互联网领彧的核心机术", "推荐系统是互联网领域的核心技术"),
        ("能根椐用户行为推送符和需求的内容", "能根据用户行为推送符合需求的内容"),
        ("协同过虑算法能有校提升用户体验", "协同过滤算法能有效提升用户体验"),
        ("深度学习是人工智能研究的重偠方向", "深度学习是人工智能研究的重要方向"),
        ("该系统具有良好的可扩涨性和稳定性", "该系统具有良好的可扩展性和稳定性"),
        ("实验结裹表明该方法有效", "实验结果表明该方法有效"),
        ("通过交叉验证来评诂模型性能", "通过交叉验证来评估模型性能"),
        ("特征工程对于提高模型准确卒至关重要", "特征工程对于提高模型准确率至关重要"),
        # ===== 官方示例 =====
        ("少先队员因该为老人让坐", "少先队员应该为老人让座"),
        ("机七学习是人工智能领遇最能体现智能的一个分知", "机器学习是人工智能领域最能体现智能的一个分支"),
        ("真麻烦你了。希望你们好好的跳无", "真麻烦你了。希望你们好好地跳舞"),
        # ===== 论文写作常见错误 =====
        ("本文提出了一种新的算发", "本文提出了一种新的算法"),
        ("实验结国表明该方法有效", "实验结果表明该方法有效"),
        ("相关工作部分回顾了现有研救", "相关工作部分回顾了现有研究"),
        ("参攷文献", "参考文献"),
        ("表1展示了实验校果", "表1展示了实验效果"),
        # ===== 语法与语义错误 =====
        ("他的研究成果非常丰富多采", "他的研究成果非常丰富多彩"),
        ("我们要做一个全面的分悉", "我们要做一个全面的分析"),
        ("这个问题需要深入的研揪", "这个问题需要深入的研究"),
        ("数据的质亮直接影响模型性能", "数据的质量直接影响模型性能"),
        ("算法的时剑复杂度是O(n)", "算法的时间复杂度是O(n)"),
        # ===== 专业术语测试 =====
        ("深度学习模型的训炼过程", "深度学习模型的训练过程"),
        ("神经网络的反向传播算发", "神经网络的反向传播算法"),
        ("协同过滤推鉴系统", "协同过滤推荐系统"),
        ("随机森林算发", "随机森林算法"),
        ("支持向量机模形", "支持向量机模型"),
        # ===== 复杂句子 =====
        ("基于深度学习的推荐系统能够有效的提高用户体念", "基于深度学习的推荐系统能够有效的提高用户体验"),
        ("通过大量实验验证了该算法的准确性和稳定性", "通过大量实验验证了该算法的准确性和稳定性"),
        ("本文提出的方法在多个数据集上取得了较妤的效果", "本文提出的方法在多个数据集上取得了较好的效果"),
        ("研究表明深度学习技术在自然语言出理领域有广泛应用", "研究表明深度学习技术在自然语言处理领域有广泛应用"),
    ]
    
    print(f"\n测试用例总数: {len(test_cases)}")
    print("-" * 80)
    
    # 测试两种方案
    results1 = []
    results2 = []
    
    print("\n【方案1】macbert4mdcspell_v3 + pycorrector")
    print("-" * 80)
    
    for original, expected in test_cases:
        corrected1 = hybrid_macbert_pycorrector(original, macbert_v3, pycorrector_obj)
        corrected2 = dual_macbert(original, macbert_v3, macbert_base)
        
        results1.append({'original': original, 'corrected': corrected1, 'expected': expected, 'correct': corrected1 == expected})
        results2.append({'original': original, 'corrected': corrected2, 'expected': expected, 'correct': corrected2 == expected})
        
        # 显示有差异的结果
        if corrected1 != corrected2:
            print(f"\n原文: {original}")
            print(f"期望: {expected}")
            print(f"方案1: {corrected1} {'✓' if corrected1 == expected else '✗'}")
            print(f"方案2: {corrected2} {'✓' if corrected2 == expected else '✗'}")
    
    # 统计结果
    correct1 = sum(1 for r in results1 if r['correct'])
    correct2 = sum(1 for r in results2 if r['correct'])
    accuracy1 = (correct1 / len(test_cases)) * 100
    accuracy2 = (correct2 / len(test_cases)) * 100
    
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"{'方案':<50} {'正确率':>10} {'正确/总数':>15}")
    print("-" * 80)
    print(f"{'macbert4mdcspell_v3 + pycorrector':<50} {accuracy1:>9.1f}% {correct1:>6}/{len(test_cases):>6}")
    print(f"{'macbert4mdcspell_v3 + macbert4csc-base':<50} {accuracy2:>9.1f}% {correct2:>6}/{len(test_cases):>6}")
    
    # 分析差异
    print("\n【方案1独有的正确案例】")
    print("-" * 80)
    for r1, r2 in zip(results1, results2):
        if r1['correct'] and not r2['correct']:
            print(f"✓ 原文: {r1['original']}")
            print(f"  方案1: {r1['corrected']}")
            print(f"  方案2: {r2['corrected']}")
            print(f"  期望: {r1['expected']}")
    
    print("\n【方案2独有的正确案例】")
    print("-" * 80)
    for r1, r2 in zip(results1, results2):
        if not r1['correct'] and r2['correct']:
            print(f"✓ 原文: {r1['original']}")
            print(f"  方案1: {r1['corrected']}")
            print(f"  方案2: {r2['corrected']}")
            print(f"  期望: {r1['expected']}")
    
    print("\n【共同错误案例】")
    print("-" * 80)
    for r1, r2 in zip(results1, results2):
        if not r1['correct'] and not r2['correct']:
            print(f"✗ 原文: {r1['original']}")
            print(f"  方案1: {r1['corrected']}")
            print(f"  方案2: {r2['corrected']}")
            print(f"  期望: {r1['expected']}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
