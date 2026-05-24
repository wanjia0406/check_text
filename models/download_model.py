import os
# 国内HF镜像，加速下载（关键）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from transformers import AutoTokenizer, AutoModelForMaskedLM

# 模型名称（固定）
model_name = "shibing624/macbert4csc-base-chinese"
# 保存到项目内models目录（相对路径，推荐）
save_path = "D:/py-90-day/Smart_text_checker/models/macbert4csc-base"

# 自动创建models目录（如果不存在），避免路径错误
if not os.path.exists(save_path):
    os.makedirs(save_path)
    print(f"✅ 已创建模型目录：{save_path}")

# 下载并保存模型/分词器
print("🚀 从国内镜像下载模型...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForMaskedLM.from_pretrained(model_name)

# 保存到本地
tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print(f"🎉 模型下载完成！已保存到：{os.path.abspath(save_path)}")