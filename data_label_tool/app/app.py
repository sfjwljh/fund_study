from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import json
import re
import sys
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 用户数据
USERS = {
    'admin': {
        'password': 'admin123',
        'is_admin': True
    },
    'ljh': {
        'password': 'ljh',
        'is_admin': True
    },
    'lyf': {
        'password': 'lyf',
        'is_admin': False
    },
    'prx': {
        'password': 'prx',
        'is_admin': False
    },
    'chp': {
        'password': 'chp',
        'is_admin': False
    },
    'xbx': {
        'password': 'xbx',
        'is_admin': False
    },

}

# 任务分配数据文件路径
ASSIGNMENTS_FILE = os.path.join(BASE_DIR, 'data', 'task_assignments.json')

# 加载任务分配数据
def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        try:
            with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
                assignments = json.load(f)
                # 初始化新用户
                for username in USERS:
                    if username not in assignments:
                        assignments[username] = {
                            "tasks": [],
                            "last_active": None
                        }
                return assignments
        except:
            return initialize_assignments()
    return initialize_assignments()

# 添加初始化任务分配数据的函数
def initialize_assignments():
    assignments = {
        username: {
            "tasks": [],
            "last_active": None
        } for username in USERS
    }
    save_assignments(assignments)
    return assignments

# 修改保存任务分配数据的函数
def save_assignments(assignments):
    # 需要确保原子性，防止多个管理员同时分配任务
    with open(ASSIGNMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(assignments, f, ensure_ascii=False, indent=2)

# 初始化任务分配数据
TASK_ASSIGNMENTS = load_assignments()

def calculate_progress(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_sentences = len(data)
        if total_sentences == 0:
            return 0
        
        completed = sum(1 for item in data if any(entity for entity in item.get('entities', [])
                                                if any(v for k, v in entity.items() if k != 'doubt_remark')))
        return (completed / total_sentences) * 100
    except:
        return 0

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['is_admin'] = USERS[username]['is_admin']
            return redirect(url_for('task_list'))
        flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 辅助函数
def get_task_id(filename):
    """从文件名中提取任务ID"""
    return int(filename.split('.')[0])

def get_task_filename(task_id):
    """从任务ID生成文件名"""
    return f"{task_id}.json"

# 修改任务列表路由
@app.route('/tasks')
def task_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 确保 data 目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        # 获取所有JSON文件
        all_tasks = []
        for f in os.listdir(DATA_DIR):
            if f.endswith('.json') and f != 'task_assignments.json':
                try:
                    task_id = get_task_id(f)
                    all_tasks.append(task_id)
                except:
                    continue
        
        if session['is_admin']:
            # 管理员可以看到所有任务和分配情况
            assigned_tasks = []
            unassigned_tasks = []
            
            # 找出已分配的任务
            assigned_ids = set()
            for username, data in TASK_ASSIGNMENTS.items():
                for task_id in data.get('tasks', []):
                    if task_id in all_tasks:  # 只处理存在的任务
                        assigned_ids.add(task_id)
                        filename = get_task_filename(task_id)
                        try:
                            progress = calculate_progress(os.path.join(DATA_DIR, filename))
                        except:
                            progress = 0
                        assigned_tasks.append({
                            'task_id': task_id,
                            'filename': filename,
                            'assigned_to': username,
                            'progress': progress
                        })
            
            # 找出未分配的任务
            for task_id in all_tasks:
                if task_id not in assigned_ids:
                    unassigned_tasks.append({
                        'task_id': task_id,
                        'filename': get_task_filename(task_id)
                    })
        else:
            # 普通用户只能看到分配给自己的任务
            username = session['username']
            assigned_tasks = []
            for task_id in TASK_ASSIGNMENTS.get(username, {}).get('tasks', []):
                if task_id in all_tasks:  # 只处理存在的任务
                    filename = get_task_filename(task_id)
                    try:
                        progress = calculate_progress(os.path.join(DATA_DIR, filename))
                    except:
                        progress = 0
                    assigned_tasks.append({
                        'task_id': task_id,
                        'filename': filename,
                        'progress': progress
                    })
            unassigned_tasks = []

        return render_template('tasks.html',
                            tasks=assigned_tasks,
                            unassigned_tasks=unassigned_tasks,
                            users=list(USERS.keys()) if session['is_admin'] else [],
                            is_admin=session['is_admin'])
    except Exception as e:
        print(f"Error in task_list: {str(e)}")  # 添加错误日志
        flash('加载任务列表时出错')
        return redirect(url_for('logout'))

# 修改分配任务的路由
@app.route('/assign_task/<int:task_id>/<username>')
def assign_task(task_id, username):
    if not session.get('is_admin'):
        flash('只有管理员可以分配任务')
        return redirect(url_for('task_list'))
    
    if username not in USERS:
        flash('用户不存在')
        return redirect(url_for('task_list'))
    
    # 从其他用户移除该任务
    for user, data in TASK_ASSIGNMENTS.items():
        if task_id in data['tasks']:
            data['tasks'].remove(task_id)
    
    # 分配给新用户
    if task_id not in TASK_ASSIGNMENTS[username]['tasks']:
        TASK_ASSIGNMENTS[username]['tasks'].append(task_id)
    TASK_ASSIGNMENTS[username]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    save_assignments(TASK_ASSIGNMENTS)
    flash(f'任务已分配给用户 {username}')
    return redirect(url_for('task_list'))

# 修改选择任务的路由
@app.route('/select_task/<int:task_id>')
def select_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    if not session['is_admin'] and task_id not in TASK_ASSIGNMENTS[username]['tasks']:
        flash('您没有权限访问此任务')
        return redirect(url_for('task_list'))
    
    # 更新最后活动时间
    TASK_ASSIGNMENTS[username]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_assignments(TASK_ASSIGNMENTS)
    
    session['current_task'] = get_task_filename(task_id)
    return redirect(url_for('index'))

# 中文句子分隔符正则
sentence_endings = r'[。！？]'


# 加载文本文件内容
def load_sentence(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        return file.read().strip()

# 将文本分割为句子
def split_text_into_sentences(text):
    sentences = re.split(sentence_endings, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]
def create_json(txt_path, json_path):
    content = load_sentence(txt_path)
    sentences = split_text_into_sentences(content)
    
    # 创建包含句子和空实体列表的字典，添加 industry 字段
    data = [{"sentence": sentence, "entities": []} for sentence in sentences]
    
    # 将数据写入JSON文件
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

# 修改主页路由
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'current_task' not in session:
        return redirect(url_for('task_list'))
        
    # 获取当前任务文件名
    filename = session['current_task']
    task_id = get_task_id(filename)
    username = session['username']
    
    # 检查权限
    if not session['is_admin'] and task_id not in TASK_ASSIGNMENTS[username]['tasks']:
        flash('您没有权限访问此任务')
        return redirect(url_for('task_list'))
        
    # 将文件路径存储在 session 中
    session['json_file'] = os.path.join(DATA_DIR, filename)
    
    return render_template('index.html')

# 修改加载 JSON 数据的函数
def load_json_data():
    if 'json_file' not in session:
        return []
    json_file = session['json_file']
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# 修改保存数据的函数
def save_json_data(data):
    if 'json_file' not in session:
        return False
    json_file = session['json_file']
    # 需要确保原子性，防止同一个文档被多人同时编辑
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

# 修改获取句子列表的路由
@app.route('/get_sentences')
def get_sentences():
    if 'current_task' not in session or 'json_file' not in session:
        return jsonify([])
    data_list = load_json_data()
    return jsonify(data_list)

# 修改获取实体数据的路由
@app.route('/get_entities/<int:sentence_id>', methods=['GET'])
def get_entities(sentence_id):
    if 'current_task' not in session or 'json_file' not in session:
        return jsonify([])
    data_list = load_json_data()
    if sentence_id < len(data_list):
        return jsonify(data_list[sentence_id]["entities"])
    return jsonify([])

# 修改保存实体数据的路由
@app.route('/save_entities', methods=['POST'])
def save_entities():
    if 'current_task' not in session or 'json_file' not in session:
        return jsonify({"message": "未选择任务"}), 400
    data = request.json
    sentence_id = data['sentence_id']
    entities = data['entities']
    
    data_list = load_json_data()
    if sentence_id < len(data_list):
        data_list[sentence_id]["entities"] = entities
        if save_json_data(data_list):
            return jsonify({"message": "数据已保存"})
        return jsonify({"message": "保存失败"}), 500
    return jsonify({"message": "错误：句子 ID 无效"}), 400

# 启动服务器
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=15208)