# test_pycorrector_class.py
import pycorrector

print("🧪 PyCorrector 类方式调用")

try:
    # 创建纠错器实例
    corrector = pycorrector.Corrector()
    
    # 进行纠错
    result = corrector.correct('少先队员因该为老人让坐')
    
    print(f"原文: 少先队员因该为老人让坐")
    print(f"纠错: {result[0]}")
    print(f"详情: {result[1]}")
    print("✅ 类方式调用成功！")
    
except Exception as e:
    print(f"❌ 类方式调用失败: {e}")