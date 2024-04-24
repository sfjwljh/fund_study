import os
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
# 文件夹路径
folder_path = r"C:\Users\LJH\Desktop\txt存放\飞书"

# 获取文件夹内所有txt文件的路径
txt_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]

def read_stopwords_from_file(file_path):
    stopwords = set()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            word = line.strip()
            stopwords.add(word)
    return stopwords

stopwords_file_path = r'E:\obsidian\Master\fund_stream_project\codes\analyse\停用词.txt'  # 指定停用词列表的文件路径
stopwords = read_stopwords_from_file(stopwords_file_path)



# 读取所有txt文件内容
corpus = []
for file_path in txt_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        corpus.append(text)

# 使用jieba进行分词
tokenized_corpus = []
for text in corpus:
    tokens = jieba.cut(text)
    filtered_tokens = [token for token in tokens if token not in stopwords]
    tokenized_text = " ".join(filtered_tokens)
    tokenized_corpus.append(tokenized_text)

# 计算TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(tokenized_corpus)

# 获取词汇表和对应的TF-IDF值
features = vectorizer.get_feature_names_out()

# 找到TF-IDF值排前100000的词
n = 30  # 可以根据需求调整显示的词汇数量
# for i, text in enumerate(corpus):
#     print(f"Top {n} words in file {txt_files[i]}:")
#     file_vector = X[i]
#     sorted_indices = file_vector.toarray().argsort()[0, ::-1][:n]
#     for idx in sorted_indices:
#         print(features[idx], file_vector[0, idx])

pickle_result=[corpus,txt_files,X,features]


# 打开文件以写入模式
with open('tfidf_result.pickle', 'wb') as f:
    # 使用 pickle.dump() 将对象写入文件
    pickle.dump(pickle_result, f)
