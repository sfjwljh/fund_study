import pickle
import jieba

# 读取tfidf结果
with open(r'E:\obsidian\Master\fund_stream_project\codes\tfidf_result.pickle', 'rb') as f:

    pickle_result=pickle.load(f)
corpus=pickle_result[0]
txt_files=pickle_result[1]
X=pickle_result[2]
features=pickle_result[3]

# 从本地txt文件中读取停用词
stopwords_file = r'E:\obsidian\Master\fund_stream_project\codes\analyse\停用词.txt'
stopwords = set()
with open(stopwords_file, 'r', encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.strip())


# 从本地txt文件中读取筛选后的关键词
key_words_file = r'E:\obsidian\Master\fund_stream_project\codes\analyse\关键词.txt'
key_words = set()
with open(key_words_file, 'r', encoding='utf-8') as f:
    for line in f:
        key_words.add(line.strip())

        
wanted_sen=[]
for text_num in range(0,len(corpus)):
    text=corpus[text_num]
    text=text[text.find("文字记录:") + len("文字记录:"):].replace('\n','')

    file_vector = X[text_num]
    sorted_indices = file_vector.toarray().argsort()[0, ::-1][:30]
    # 拿到文档前30个关键词
    key_list_30=[]
    for idx in sorted_indices:
        if features[idx] in key_words:
            key_list_30.append(features[idx])


    # 将文档拆成句子
    sentences_list = []
    sentence = ''
    for word in text:
        if word in ['。', '！', '？']:
            sentence += word
            sentences_list.append(sentence)
            sentence = ''
        else:
            sentence += word

    # 去停用词
    sent_doc=[]
    for sentence in sentences_list:
        words = list(jieba.cut(sentence, cut_all=False))
        filtered_words = [word for word in words if word not in stopwords]
        if len(filtered_words)>0:
            sent_doc.append(filtered_words)
    
    

    for sentence in sent_doc:
        if set(sentence).intersection(set(key_list_30))!=set():
            # 交集非空，记录该句子
            wanted_sen.append(sentence)
with open('opinions.pickle','wb') as f:
    pickle.dump(wanted_sen,f)