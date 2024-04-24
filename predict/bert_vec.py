import pickle
import torch
from transformers import BertTokenizer, BertModel, BertConfig

# 加载预训练的BERT模型和分词器
def load_pretrained_bert_model(device="cuda"):
    model_weights_path = r"E:\obsidian\Master\fund_stream_project\codes\bert\bert_ft_checkpoint-84500\pytorch_model.bin"
    model_config_path = r"E:\obsidian\Master\fund_stream_project\codes\bert\bert_ft_checkpoint-84500\config.json"
    vocab_file_path = r"E:\obsidian\Master\fund_stream_project\codes\bert\model\vocab.txt"

    tokenizer = BertTokenizer.from_pretrained(vocab_file_path)
    config = BertConfig.from_pretrained(model_config_path)

    # 加载BERT模型并将其移动到指定设备（GPU 或 CPU）
    model = BertModel.from_pretrained(model_weights_path, config=config).to(device)
    return tokenizer, model

# 加载预训练的BERT模型
tokenizer, model = load_pretrained_bert_model()

# 对句子进行编码
def encode_sentence(sentence, tokenizer, model, device="cuda"):
    inputs = tokenizer(sentence, return_tensors="pt", max_length=512, truncation=True)
    inputs = {key: tensor.to(device) for key, tensor in inputs.items()}  # 将输入数据移动到GPU上
    with torch.no_grad():
        outputs = model(**inputs)
    
    sentence_embedding = torch.mean(outputs.last_hidden_state, dim=1)
    return sentence_embedding[0].tolist()

with open(r'E:\obsidian\Master\fund_stream_project\codes\predict\code_opinions_dict.pickle','rb') as f:
    wanted_sen=pickle.load(f)
wanted_sen_vec = {}

def process_line(line, max_length=450):
    if len(line) <= max_length:
        return [line]
    else:
        index = max_length
        while (index >= 0) and (line[index] not in "。?!？！，,"):  # 优化检索句号或逗号的方式
            index -= 1
        
        if index == -1:
            return [line[:max_length]] + process_line(line[max_length:], max_length)
        else:
            return [line[:index + 1]] + process_line(line[index + 1:], max_length)

count = 0
device = "cuda" if torch.cuda.is_available() else "cpu"  # 检查是否可用CUDA
for key in wanted_sen.keys():
    wanted_sen_vec[key] = []
    for sentence in wanted_sen[key]:
        if len(sentence) >= 450:
            sen_split = process_line(sentence)
            for sen in sen_split:
                wanted_sen_vec[key].append(encode_sentence(sen, tokenizer, model, device))
        else:
            wanted_sen_vec[key].append(encode_sentence(sentence, tokenizer, model, device))
    count += 1
    print(count)

with open(r'E:\obsidian\Master\fund_stream_project\codes\predict\code_opinions_vec_dict_bert_fted.pickle','wb') as f:
    pickle.dump(wanted_sen_vec, f)
