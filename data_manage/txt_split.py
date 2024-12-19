import re

def split_text_to_lines(file_path, output_path):
    # 读取文档内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用正则表达式分割内容，保留分割符
    sentences = re.split(r'([。！？\n])', content)

    # 合并句子和分隔符，并去掉多余的空格或空行
    result = []
    temp_sentence = ""
    for part in sentences:
        if part.strip():  # 去掉空行和无意义空格
            temp_sentence += part
            if part in "。！？\n":  # 如果遇到分隔符，表示一行结束
                result.append(temp_sentence.strip())
                temp_sentence = ""
    if temp_sentence:  # 添加最后一句
        result.append(temp_sentence.strip())

    # 将结果写入新的文档
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write("\n".join(result))

# 示例调用
input_file = "/Users/liujianhui02/Desktop/sync/obsidian/Master/fund_stream_project/codes/data_manage/4392063.txt"  # 输入文件路径
output_file = input_file.replace('.txt','_output.txt')  # 输出文件路径
split_text_to_lines(input_file, output_file)

print(f"分割完成！结果已保存到 {output_file}")
