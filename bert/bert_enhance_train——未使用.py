import os
import torch
from transformers import BertTokenizer, LineByLineTextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments
from torch.utils.data import ConcatDataset
from transformers import BertTokenizer, BertModel
from transformers import BertModel, BertConfig
import torch

# 下载并加载预训练的中文BERT模型和分词器
def load_pretrained_bert_model():
    # tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    # model = BertModel.from_pretrained("bert-base-chinese")


    # 指定模型权重文件路径和配置文件路径
    model_weights_path = r"E:\obsidian\Master\fund_stream_project\codes\bert\model\pytorch_model.bin"
    model_config_path = r"E:\obsidian\Master\fund_stream_project\codes\bert\model\config.json"
        # 指定词汇表文件路径
    vocab_file_path = r"E:\obsidian\Master\fund_stream_project\codes\bert\model\vocab.txt"

    # 使用词汇表文件路径加载分词器
    tokenizer = BertTokenizer.from_pretrained(vocab_file_path)

    # 加载BERT配置
    config = BertConfig.from_pretrained(model_config_path)

    # 使用本地路径加载BERT模型
    model = BertModel.from_pretrained(model_weights_path, config=config)
    return tokenizer, model

# 加载预训练的BERT模型
tokenizer, model = load_pretrained_bert_model()
# 设置GPU
device = torch.device("cuda")
model.to(device)  # 将模型转移到GPU上


tokenizer, model = load_pretrained_bert_model()

# 设置微调参数
output_dir = "./fine_tuned_bert_model"
batch_size = 8
num_train_epochs = 3

# 准备用于微调的数据集
data_dir = r"C:\Users\LJH\Desktop\txt存放\飞书"  # 你的数据目录

# 创建一个包含所有训练数据集的列表
train_datasets = []

# 遍历所有txt文件，并为每个文件创建一个LineByLineTextDataset
for filename in os.listdir(data_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(data_dir, filename)
        train_datasets.append(LineByLineTextDataset(
            tokenizer=tokenizer,
            file_path=file_path,
            block_size=4,  # 将 block_size 设置为 256，确保每个样本的长度不超过512个token
        ))

# 将所有数据集合并成一个
merged_train_dataset = ConcatDataset(train_datasets)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

# 设置微调参数
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    num_train_epochs=num_train_epochs,
    per_device_train_batch_size=batch_size,
    save_steps=10_000,
    save_total_limit=2,
    prediction_loss_only=True,
    logging_dir='./logs',  # 设置日志文件存储目录
    logging_steps=1,  # 每500个训练步骤记录一次日志
    logging_first_step=True,  # 在第一次训练步骤时记录日志

)

# 使用Trainer进行微调
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=merged_train_dataset,
)

# 开始微调BERT模型
trainer.train()

# 保存微调后的BERT模型
model.save_pretrained(output_dir)
