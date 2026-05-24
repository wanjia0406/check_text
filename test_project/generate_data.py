#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大规模测试数据生成脚本
- 错别字检测：50000条
- 语法检测：20000条
- 语义检测：20000条
- 参考文献校验：20000条
"""

import os
import json
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

TYPO_COUNT = 50000
GRAMMAR_COUNT = 20000
SEMANTIC_COUNT = 20000
REFERENCE_COUNT = 20000

TYPO_PAIRS = [
    ("习学", "学习"), ("图象", "图像"), ("题问", "问题"), ("建义", "建议"),
    ("分折", "分析"), ("部置", "布置"), ("按排", "安排"), ("规化", "规划"),
    ("辩认", "辨认"), ("容合", "融合"), ("连系", "联系"), ("反醒", "反省"),
    ("急燥", "急躁"), ("烦燥", "烦躁"), ("松驰", "松弛"), ("密诀", "秘诀"),
    ("精采", "精彩"), ("端祥", "端详"), ("陪偿", "赔偿"), ("安祥", "安详"),
    ("挺而走险", "铤而走险"), ("谈笑风声", "谈笑风生"), ("走头无路", "走投无路"),
    ("一愁莫展", "一筹莫展"), ("世外桃园", "世外桃源"),
    ("姿式", "姿势"), ("尊守", "遵守"), ("即然", "既然"), ("在坐", "在座"),
    ("座客", "做客"), ("装祯", "装帧"), ("编缉", "编辑"), ("不记其数", "不计其数"),
    ("大慨", "大概"), ("必竟", "毕竟"), ("决对", "绝对"), ("坚苦", "艰苦"),
    ("克苦", "刻苦"), ("刻服", "克服"), ("权利", "权力"),
    ("度难关", "渡难关"), ("分辩", "分辨"), ("严励", "严厉"), ("历害", "厉害"),
    ("利马", "立马"), ("立既", "立即"), ("竟争", "竞争"), ("座标", "坐标"),
    ("坐阵", "坐镇"), ("车箱", "车厢"), ("风彩", "风采"), ("神彩", "神采"),
    ("光采", "光彩"), ("喝采", "喝彩"), ("报负", "抱负"), ("抱复", "报复"),
    ("复盖", "覆盖"), ("担误", "耽误"), ("耽心", "担心"), ("安照", "按照"),
    ("按装", "安装"), ("班配", "般配"), ("包函", "包含"), ("包览", "包揽"),
    ("保贵", "宝贵"), ("报怨", "抱怨"), ("暴燥", "暴躁"), ("毕竞", "毕竟"),
    ("变象", "变相"), ("查觉", "察觉"), ("长备", "常备"), ("城实", "诚实"),
    ("呈述", "陈述"), ("冲激", "冲击"), ("充份", "充分"), ("冲满", "充满"),
    ("纯结", "纯洁"), ("从新", "重新"), ("重伸", "重申"), ("重迭", "重叠"),
    ("出板", "出版"), ("初忠", "初衷"), ("处份", "处分"), ("触机", "契机"),
    ("串连", "串联"), ("传布", "传播"), ("喘嘘", "喘息"),
    ("次递", "次第"), ("摧促", "催促"), ("催残", "摧残"), ("搭挡", "搭档"),
    ("答辨", "答辩"), ("带替", "代替"), ("待慢", "怠慢"), ("怠漫", "怠慢"),
    ("担搁", "耽搁"), ("耽阁", "耽搁"), ("单簿", "单薄"), ("挡案", "档案"),
    ("低毁", "诋毁"), ("抵毁", "诋毁"), ("弟一", "第一"), ("颠复", "颠覆"),
    ("凋凌", "凋零"), ("调落", "凋落"), ("调零", "凋零"), ("跌荡", "跌宕"),
    ("顶极", "顶级"), ("定婚", "订婚"), ("定货", "订货"), ("定购", "订购"),
    ("洞查", "洞察"), ("洞澈", "洞彻"), ("渡假", "度假"), ("渡过", "度过"),
    ("兑变", "蜕变"), ("蛾眉", "峨眉"), ("恩慧", "恩惠"), ("发楞", "发愣"),
    ("烦脑", "烦恼"), ("繁脑", "烦恼"), ("反工", "返工"), ("反回", "返回"),
    ("反覆", "反复"), ("范筹", "范畴"), ("防碍", "妨碍"), ("妨隘", "妨碍"),
    ("飞弛", "飞驰"), ("费话", "废话"),
]

TYPO_TEMPLATES = [
    "通过{correct}技术，我们实现了很好的{result}。",
    "这个{correct}能够提高{metric}，效果显著。",
    "研究表明，{correct}对{target}有重要影响。",
    "该{correct}方法可以{action}，提高效率。",
    "{subject}的{correct}性能优秀，值得应用。",
    "实验结果显示，{correct}表明了{conclusion}。",
    "基于{correct}的{model}可以解决实际问题。",
    "{correct}与{object}之间存在密切关系。",
]

CORRECT_WORDS = [
    "学习", "分析", "提高", "改善", "实现", "优化", "增强", "提升",
    "准确率", "效率", "性能", "效果", "质量", "精度", "速度",
    "算法", "模型", "系统", "方法", "技术", "框架",
    "机器学习", "深度学习", "神经网络", "数据挖掘", "计算机视觉", "自然语言处理",
    "结果", "输出", "响应", "表现", "功能", "作用",
    "假设", "理论", "结论", "问题", "数据",
]

SUBJECTS = ["算法", "模型", "系统", "方法", "技术", "框架"]
OBJECTS = ["数据", "信息", "知识", "结果", "性能"]
MODELS = ["模型", "框架", "系统", "算法"]
CONCLUSIONS = ["证明了假设", "验证了理论", "支持了结论", "说明了问题"]

def generate_typo_data(count):
    """生成错别字测试数据"""
    data = []
    for i in range(count):
        has_error = random.choice([True, False])

        if has_error:
            typo, correct = random.choice(TYPO_PAIRS)
            template = random.choice(TYPO_TEMPLATES)
            sentence = template.format(
                correct=correct,
                result=random.choice(["效率", "准确率", "性能", "效果"]),
                metric=random.choice(["效率", "准确率", "召回率", "F1值"]),
                target=random.choice(["结果", "性能", "输出"]),
                action=random.choice(["提高", "改善", "解决"]),
                subject=random.choice(SUBJECTS),
                conclusion=random.choice(CONCLUSIONS),
                model=random.choice(MODELS),
                object=random.choice(OBJECTS)
            )
            if correct in sentence:
                source = sentence.replace(correct, typo, 1)
                target = sentence
            else:
                source = sentence
                target = sentence
                has_error = False
        else:
            template = random.choice([
                "通过机器学习技术，我们实现了很好的效果。",
                "这个深度学习方法可以提高准确率，效果显著。",
                "研究表明，神经网络对结果有重要影响。",
                "该数据挖掘方法可以改善性能，提高效率。",
                "算法的性能优秀，值得应用。",
                "实验结果显示，机器学习证明了假设。",
                "基于深度学习的模型可以解决实际问题。",
                "数据与信息之间存在密切关系。",
            ])
            source = template
            target = template

        data.append({
            "id": i + 1,
            "source": source,
            "target": target,
            "has_error": has_error
        })

    return data


def generate_grammar_data(count):
    """生成语法检测数据 - has_error=true时source是错误句子，target是正确句子"""
    data = []

    GRAMMAR_ERROR_CORRECT_PAIRS = [
        ("通过使用机器学习，使效率提高。", "通过机器学习，效率得到提高。"),
        ("由于使用深度学习，使性能下降。", "由于深度学习，性能得到改善。"),
        ("在通过优化算法，使效果显著。", "通过优化算法，效果得到提升。"),
        ("该研究以提高效率为目的。", "该研究以提高效率为目标。"),
        ("该方法以改善性能为目的。", "该方法以改善性能为目标。"),
        ("这是由于数据不足的原因造成的。", "这是由于数据不足造成的。"),
        ("这是因为参数设置的原因造成的。", "这是因为参数设置造成的。"),
        ("在实验环境下，使准确率。", "在实验环境下，准确率得到提升。"),
        ("通过机器学习方法，使质量提高。", "通过机器学习方法，质量得到提高。"),
        ("由于环境因素影响，使效率下降。", "由于环境因素影响，效率得到改善。"),
    ]

    CORRECT_ONLY_SENTENCES = [
        "通过机器学习技术，我们实现了很好的效果。",
        "该深度学习方法可以提高准确率，效果显著。",
        "研究表明，神经网络对结果有重要影响。",
        "该数据挖掘方法可以改善性能，提高效率。",
        "算法的性能优秀，值得应用。",
        "实验结果显示，机器学习证明了假设。",
        "基于深度学习的模型可以解决实际问题。",
        "数据与信息之间存在密切关系。",
        "在不同实验环境下，性能得到优化。",
        "由于数据充足，结果得到改善。",
    ]

    for i in range(count):
        has_error = random.choice([True, False])

        if has_error:
            source, target = random.choice(GRAMMAR_ERROR_CORRECT_PAIRS)
        else:
            source = random.choice(CORRECT_ONLY_SENTENCES)
            target = source

        data.append({
            "id": i + 1,
            "source": source,
            "target": target,
            "has_error": has_error
        })

    return data


def generate_semantic_data(count):
    """生成语义检测数据 - has_error=true时source是错误句子，target是正确句子"""
    data = []

    SEMANTIC_ERROR_CORRECT_PAIRS = [
        ("苹果在天上飞。", "苹果在地上。"),
        ("香蕉在水里跑。", "香蕉在地上。"),
        ("米饭在天上飞。", "米饭在碗里。"),
        ("鱼在水里跑。", "鱼在水里游。"),
        ("猫在天上飞。", "猫在地上走。"),
        ("狗在水里飞。", "狗在地上跑。"),
        ("鸟在水里跑。", "鸟在天上飞。"),
        ("太阳从西边升起。", "太阳从东边升起。"),
        ("冬天很热。", "冬天很冷。"),
        ("夏天很冷。", "夏天很热。"),
    ]

    CORRECT_ONLY_SENTENCES = [
        "人需要喝水才能生存。",
        "电脑可以帮助人们工作。",
        "苹果是一种水果。",
        "香蕉是一种水果。",
        "米饭是食物。",
        "鱼生活在水中。",
        "猫是陆生动物。",
        "狗是陆生动物。",
        "鸟在空中飞行。",
        "太阳从东方升起。",
        "冬天温度低。",
        "夏天温度高。",
        "水在零度会结冰。",
        "火会发光发热。",
    ]

    for i in range(count):
        has_error = random.choice([True, False])

        if has_error:
            source, target = random.choice(SEMANTIC_ERROR_CORRECT_PAIRS)
        else:
            source = random.choice(CORRECT_ONLY_SENTENCES)
            target = source

        data.append({
            "id": i + 1,
            "source": source,
            "target": target,
            "has_error": has_error
        })

    return data


def generate_reference_data(count):
    """生成参考文献校验数据 - has_error=true时source是错误格式，target是正确格式"""
    data = []

    REFERENCE_ERROR_CORRECT_PAIRS = [
        ("张三 机器学习综述", "[1] 张三. 机器学习综述[J]. 计算机学报, 2020, 43(1): 1-20."),
        ("李四, 王五 深度学习应用研究", "[2] 李四, 王五. 深度学习应用研究[M]. 北京: 清华大学出版社, 2019."),
        ("赵六 数据挖掘算法", "[3] 赵六. 数据挖掘算法[D]. 北京大学, 2018."),
        ("陈七 神经网络优化方法", "[4] 陈七. 神经网络优化方法[J]. 软件学报, 2021, 32(2): 45-60."),
        ("刘八 Python编程实践", "[5] 刘八. Python编程实践[M]. 北京: 人民邮电出版社, 2022."),
        ("王九 Java编程指南", "[6] 王九. Java编程指南[M]. 北京: 电子工业出版社, 2020."),
        ("孙十 Web开发实战", "[7] 孙十. Web开发实战[J]. 计算机技术, 2019, 45(3): 12-25."),
    ]

    CORRECT_ONLY_REFERENCES = [
        "[1] 张三. 机器学习综述[J]. 计算机学报, 2020, 43(1): 1-20.",
        "[2] 李四, 王五. 深度学习应用研究[M]. 北京: 清华大学出版社, 2019.",
        "[3] 赵六. 数据挖掘算法[D]. 北京大学, 2018.",
        "[4] 陈七. 神经网络优化方法[J]. 软件学报, 2021, 32(2): 45-60.",
        "[5] 刘八. Python编程实践[M]. 北京: 人民邮电出版社, 2022.",
    ]

    for i in range(count):
        has_error = random.choice([True, False])

        if has_error:
            source, target = random.choice(REFERENCE_ERROR_CORRECT_PAIRS)
        else:
            source = random.choice(CORRECT_ONLY_REFERENCES)
            target = source

        data.append({
            "id": i + 1,
            "source": source,
            "target": target,
            "has_error": has_error
        })

    return data


def main():
    """主函数"""
    print("=" * 80)
    print("大规模测试数据生成脚本")
    print("=" * 80)

    print(f"\n正在生成错别字检测数据 ({TYPO_COUNT}条)...")
    typo_data = generate_typo_data(TYPO_COUNT)
    typo_path = os.path.join(OUTPUT_DIR, 'typo_data.json')
    with open(typo_path, 'w', encoding='utf-8') as f:
        json.dump(typo_data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {len(typo_data)}条")

    print(f"\n正在生成语法检测数据 ({GRAMMAR_COUNT}条)...")
    grammar_data = generate_grammar_data(GRAMMAR_COUNT)
    grammar_path = os.path.join(OUTPUT_DIR, 'grammar_data.json')
    with open(grammar_path, 'w', encoding='utf-8') as f:
        json.dump(grammar_data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {len(grammar_data)}条")

    print(f"\n正在生成语义检测数据 ({SEMANTIC_COUNT}条)...")
    semantic_data = generate_semantic_data(SEMANTIC_COUNT)
    semantic_path = os.path.join(OUTPUT_DIR, 'semantic_data.json')
    with open(semantic_path, 'w', encoding='utf-8') as f:
        json.dump(semantic_data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {len(semantic_data)}条")

    print(f"\n正在生成参考文献校验数据 ({REFERENCE_COUNT}条)...")
    reference_data = generate_reference_data(REFERENCE_COUNT)
    reference_path = os.path.join(OUTPUT_DIR, 'reference_data.json')
    with open(reference_path, 'w', encoding='utf-8') as f:
        json.dump(reference_data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {len(reference_data)}条")

    print("\n" + "=" * 80)
    print("所有测试数据生成完成！")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
