import json
import os
import shutil
from datetime import datetime

# 定义路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'task_assignments.json')
TARGET_DIR = os.path.join(BASE_DIR, '已标注汇总')

def move_completed_files():
    # 确保目标目录存在
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    try:
        # 读取任务分配文件
        with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
            assignments = json.load(f)
        
        # 收集所有已完成的任务ID
        completed_tasks = set()
        for username, user_data in assignments.items():
            if 'done' in user_data:
                completed_tasks.update(user_data['done'])
        
        print(f"找到 {len(completed_tasks)} 个已完成的任务")
        
        # 移动文件
        moved_count = 0
        for task_id in completed_tasks:
            source_file = os.path.join(DATA_DIR, f"{task_id}.json")
            target_file = os.path.join(TARGET_DIR, f"{task_id}.json")
            
            if os.path.exists(source_file):
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"已复制: {task_id}.json")
                    moved_count += 1
                except Exception as e:
                    print(f"复制文件 {task_id}.json 时出错: {str(e)}")
            else:
                print(f"文件不存在: {task_id}.json")
        
        print(f"\n总结:")
        print(f"- 已完成任务数: {len(completed_tasks)}")
        print(f"- 成功复制文件数: {moved_count}")
        print(f"- 目标目录: {TARGET_DIR}")
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")

if __name__ == "__main__":
    move_completed_files()
