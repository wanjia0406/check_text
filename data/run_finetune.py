import os
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForMaskedLM, get_linear_schedule_with_warmup
from torch.optim import AdamW
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CscDataset(Dataset):
    """中文拼写纠错数据集"""
    def __init__(self, data_path, tokenizer, max_length=128):
        self.data = self.load_data(data_path)
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def load_data(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        source = item["source"]
        target = item["target"]
        
        source_tokens = self.tokenizer(
            source,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        target_tokens = self.tokenizer(
            target,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            "input_ids": source_tokens["input_ids"].flatten(),
            "attention_mask": source_tokens["attention_mask"].flatten(),
            "labels": target_tokens["input_ids"].flatten()
        }

def train_epoch(model, dataloader, optimizer, scheduler, device):
    """训练一个epoch"""
    model.train()
    total_loss = 0.0
    
    for batch in tqdm(dataloader, desc="Training"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        total_loss += loss.item()
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
    
    return total_loss / len(dataloader)

def evaluate(model, dataloader, device):
    """评估模型"""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            total_loss += loss.item()
            
            # 计算准确率（只计算非padding位置）
            predictions = outputs.logits.argmax(dim=-1)
            mask = (labels != -100) & (labels != 0)  # 排除padding和cls
            correct += ((predictions == labels) & mask).sum().item()
            total += mask.sum().item()
    
    accuracy = correct / total if total > 0 else 0.0
    return total_loss / len(dataloader), accuracy

def main():
    # 配置参数
    config = {
        "model_name_or_path": r"D:\check_teset\models\macbert_v3\Macadam\macbert4mdcspell_v3",
        "train_data_path": os.path.join(os.path.dirname(__file__), "train.json"),
        "val_data_path": os.path.join(os.path.dirname(__file__), "val.json"),
        "output_dir": r"D:\check_teset\models\macbert_finetuned",
        "max_length": 128,
        "batch_size": 4,
        "learning_rate": 3e-5,
        "num_epochs": 5,
        "warmup_ratio": 0.1,
        "weight_decay": 0.01,
    }
    
    # 检查设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"使用设备: {device}")
    
    # 加载tokenizer和模型
    logger.info("加载tokenizer和模型...")
    tokenizer = BertTokenizer.from_pretrained(config["model_name_or_path"])
    model = BertForMaskedLM.from_pretrained(config["model_name_or_path"], local_files_only=True)
    model.to(device)
    
    # 加载数据集
    logger.info("加载数据集...")
    train_dataset = CscDataset(config["train_data_path"], tokenizer, config["max_length"])
    val_dataset = CscDataset(config["val_data_path"], tokenizer, config["max_length"])
    
    train_dataloader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=config["batch_size"], shuffle=False)
    
    # 配置优化器和学习率调度器
    logger.info("配置优化器...")
    optimizer = AdamW(
        model.parameters(),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"]
    )
    
    total_steps = len(train_dataloader) * config["num_epochs"]
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * config["warmup_ratio"]),
        num_training_steps=total_steps
    )
    
    # 创建输出目录
    os.makedirs(config["output_dir"], exist_ok=True)
    
    # 开始训练
    logger.info("开始训练...")
    best_val_accuracy = 0.0
    
    for epoch in range(config["num_epochs"]):
        logger.info(f"===== Epoch {epoch + 1}/{config['num_epochs']} =====")
        
        # 训练
        train_loss = train_epoch(model, train_dataloader, optimizer, scheduler, device)
        logger.info(f"训练损失: {train_loss:.4f}")
        
        # 评估
        val_loss, val_accuracy = evaluate(model, val_dataloader, device)
        logger.info(f"验证损失: {val_loss:.4f}, 验证准确率: {val_accuracy:.4f}")
        
        # 保存最佳模型
        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            logger.info(f"保存最佳模型 (准确率: {best_val_accuracy:.4f})")
            model.save_pretrained(config["output_dir"])
            tokenizer.save_pretrained(config["output_dir"])
    
    logger.info("训练完成！")
    logger.info(f"最佳验证准确率: {best_val_accuracy:.4f}")
    logger.info(f"模型已保存到: {config['output_dir']}")

if __name__ == "__main__":
    main()
