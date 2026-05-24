# load_model.py - 本地模型加载测试脚本
import os
from transformers import AutoTokenizer, AutoModelForMaskedLM

# 本地模型路径（和你下载的路径完全一致，不用改）
MODEL_PATH = "D:\py-90-day\Smart_text_checker\models\macbert4csc-base"
# 检查模型是否存在（提前预判错误）
if not os.path.exists(MODEL_PATH):
    print("❌ 模型目录不存在，请确认模型下载完成！")
else:
    try:
        # 加载分词器和模型
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForMaskedLM.from_pretrained(MODEL_PATH)
        print("✅ 本地模型加载成功！分词器+模型均可用")
        print(f"📌 分词器词汇表大小：{len(tokenizer.vocab)}")
        print(f"📌 模型设备：{model.device}")
    except Exception as e:
        print(f"❌ 模型加载失败，错误：{str(e)[:100]}")