from transformers import AutoTokenizer, AutoModelForMaskedLM

# 你的模型路径
MODEL_PATH = r"D:\py-90-day\Smart_text_checker\models\macbert4csc-base"

# 加载模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForMaskedLM.from_pretrained(MODEL_PATH)

# ==================== 干净、无空格、真正可用的纠错函数 ====================
def correct_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    logits = outputs.logits

    pred_ids = logits.argmax(dim=-1)
    corrected = tokenizer.decode(pred_ids[0], skip_special_tokens=True).replace(" ", "")
    return corrected

# ==================== 测试 ====================
test_sentences = [
    "这里有很多错别子。",
    "我按装了一个新软件。",
    "天空是兰色的。",
    "他开心的跑了起来。",
    "我吃了一碗书，这句话不通顺。",
    "今天的天气很好，我想去公圆。"
]

print("="*50)
print("✅ 最终干净纠错结果（无空格、可直接使用）\n")

for s in test_sentences:
    fixed = correct_text(s)
    print(f"原句：{s}")
    print(f"修正：{fixed}")
    print("-"*30)