# pipeline.py:
- 是完整的流程，包括：
1. 获取行业的情感标注数据（方面、方面、情感 三个维度）、并压缩到一维
2. 获取行业对应的指数基金价格数据、并计算技术特征
3. 以上二者合并
4. 空值处理
5. 特征筛选（可能不是所有特征都要使用）
6. 数据转lstm训练用的格式，并保存到本地（framework/data下）
7. 训练、预测、验证（调用了lstm_train_validate.py的函数）

提升效果需要修改的部分包括： 
1中特征压缩的方法：compress_opi_list
2中补充新的技术特征：price_calculate_technical_indicators
4的空值处理策略：empty_process
5特征筛选的策略，在main中实现
7训练的超参设置&LSTM模型  在lstm_train_validate.py中

# lstm_train_validate.py:
获取data下的pkl文件，然后训练lstm模型、输出评估。日志会记录在framework/logs下