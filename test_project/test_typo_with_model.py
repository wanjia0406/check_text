#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
错别字检测模块测试脚本
使用 macbert_finetuned + pycorrector 双模型进行测试
测试数据：50000条
"""

import os
import sys
import json
import torch

# 添加core_codes路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_codes'))

from nlp_corrector import TextCorrector

# 模型路径
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'macbert_finetuned')

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "准确率": precision * 100,
        "召回率": recall * 100,
        "F1值": f1 * 100,
        "TP": tp,
        "FP": fp,
        "FN": fn
    }

def test_typo_detection(test_data, corrector):
    """测试错别字检测模块"""
    print(f"正在测试错别字检测模块（{len(test_data)}条）...")

    tp = 0
    fp = 0
    fn = 0

    for idx, item in enumerate(test_data):
        if (idx + 1) % 1000 == 0:
            print(f"  已处理: {idx + 1}/{len(test_data)}")

        source = item['source']
        has_error = item['has_error']

        corrected, errors = corrector.correct_text(source)
        detected_error = len(errors) > 0

        if detected_error and has_error:
            tp += 1
        elif detected_error and not has_error:
            fp += 1
        elif not detected_error and has_error:
            fn += 1

    return calculate_metrics(tp, fp, fn)

def main():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'val1.json')

    if not os.path.exists(data_path):
        print(f"错误：数据文件不存在: {data_path}")
        sys.exit(1)

    print(f"加载测试数据: {data_path}")
    test_data = load_data(data_path)
    print(f"测试样本数: {len(test_data)}")

    has_error_count = sum(1 for item in test_data if item['has_error'])
    no_error_count = len(test_data) - has_error_count
    print(f"  - 有错误样本: {has_error_count}")
    print(f"  - 无错误样本: {no_error_count}")

    print("\n" + "=" * 60)
    print("正在加载 macbert_finetuned + pycorrector 双模型...")
    print("=" * 60)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")

    try:
        corrector = TextCorrector(
            model_path=MODEL_PATH,
            device=device,
            threshold=0.8,
            use_pycorrector=True
        )
    except Exception as e:
        print(f"[ERROR] 模型加载失败: {e}")
        print(f"请确保模型路径存在: {MODEL_PATH}")
        sys.exit(1)

    # 测试所有数据
    metrics = test_typo_detection(test_data, corrector)

    print("\n" + "=" * 60)
    print("错别字检测模块测试报告")
    print("=" * 60)
    print(f"测试样本数: {len(test_data)}")
    print(f"有错误样本: {has_error_count}")
    print(f"无错误样本: {no_error_count}")
    print(f"准确率: {metrics['准确率']:.2f}%")
    print(f"召回率: {metrics['召回率']:.2f}%")
    print(f"F1值: {metrics['F1值']:.2f}%")
    print(f"TP: {metrics['TP']}, FP: {metrics['FP']}, FN: {metrics['FN']}")
    print("=" * 60)

    result = {
        "模块": "错别字检测",
        "模型": "macbert_finetuned + pycorrector",
        "样本数": len(test_data),
        "有错误样本": has_error_count,
        "无错误样本": no_error_count,
        **metrics
    }
    result_path = os.path.join(os.path.dirname(__file__), 'result_typo.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n测试结果已保存到: {result_path}")

if __name__ == "__main__":
    main()
