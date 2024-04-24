
import os
import subprocess
import time
import sys
def find_mp3_files(path):
    mp3_files = []
    mp3_dir = os.path.join(path, 'MP3')
    # 遍历目录中的所有文件
    for file in os.listdir(mp3_dir):
        if file.endswith('.mp3'):
            mp3_files.append(file)
    return mp3_files

# 获取当前程序所在目录
current_dir = os.path.dirname(os.path.realpath(__file__))


while 1:
# 查找当前目录以及子目录中的所有MP3文件
    mp3_files = find_mp3_files(current_dir)
    # if len(mp3_files)<=2:
    #     print("sleeping")
    #     time.sleep(30)
    #     continue
    # 检查每个MP3文件是否有对应的同名目录
    for mp3_file in mp3_files:
        mp3_name = os.path.splitext(mp3_file)[0]
        output_dir = os.path.join(current_dir, 'output/', mp3_name)
        if not os.path.exists(output_dir):
            # 执行终端指令，例如创建同名目录
            mp3_path=current_dir+"/MP3/"+mp3_name+".mp3"
            command = "whisper --language Chinese --model medium "+current_dir+"/MP3/"+mp3_name+".mp3 --initial_prompt \"以下是普通话的句子。\" --device cuda --output_dir "+output_dir
            # print(command)
            subprocess.run(command, shell=True)

            # 判断平台，把文件删了，不同平台指令不一样
            if sys.platform[0]=="l":  #linux*   未测试，应该是这样
                subprocess.run('rm '+mp3_path, shell=True)   
            if sys.platform[0]=="w":  #win32
                subprocess.run('del '+mp3_path, shell=True)   
            
