import requests
import json
from math import ceil
import os
access_token="121.e9a71493deeec8a3ed50a86b74dd243a.Yaiys4d9C0vmYVhEo7xus_onRcL5pWIdaLNjbVe.SqVxbQ"
"""
说明：
根据baidu_disk提供的基础API，自定义了一些函数，方便使用
"""
def get_files(show_path):
  """
  返回百度网盘单级目录下的所有项目信息，包括目录和文件
  返回的是一个字典的列表，每个文件/目录是一个字典
  返回参数：
  fs_id	uint64	文件在云端的唯一标识ID
  path	string	文件的绝对路径
  server_filename	string	文件名称
  size	uint	文件大小，单位B
  isdir	uint	是否为目录，0 文件、1 目录
  """
  file_list=[]
  add_num=-1
  start=1  #这个编号的是不包含的

  while add_num!=0:
    limit=1000  #一次最多1000个
    start+=add_num
    url="https://pan.baidu.com/rest/2.0/xpan/file?method=list&dir="+show_path+"&limit="+str(limit)+"&start="+str(start)+"&access_token="+access_token
    payload = {}
    files = {}
    headers = {
      'User-Agent': 'pan.baidu.com'
    }

    response = requests.request("GET", url, headers=headers, data = payload, files = files)
    response_dict = json.loads(response.text)
    if response_dict['errno']==-6:
      raise ValueError("access_token过期，请刷新")
    elif response_dict['errno']!=0:

      raise ValueError("路径"+show_path+"不存在,注意开头要有/")
      

    add_num=len(response_dict['list'])
    file_list.extend(response_dict['list'])
  return file_list

def get_names(folder_path,file_or_folder_or_both):
  """
  folder_path: 要查看的目录在网盘上的绝对路径
  file_or_folder： 三值，file_only表示只要文件的名字，folder_only表示只要文件夹的名字，both表示不区分都要
  返回一个一维列表
  """
  all_list=get_files(folder_path)
  result=[]
  for content in all_list:
    if file_or_folder_or_both=='both':
      # result.append(content['server_filename'])
      result=[i['server_filename'] for i in all_list]
    if file_or_folder_or_both=='file_only':
      result = [i['server_filename'] for i in all_list if i['isdir'] == 0]
    if file_or_folder_or_both=='folder_only':
      result = [i['server_filename'] for i in all_list if i['isdir'] == 1]
  return result



def file_exist(check_file):
  """
  传入一个绝对路径，检查该路径的文件是否存在
  如：/api_test/435.mp3
  """
  if check_file[-1]=='/':
    raise(check_file+"不是文件或目录名")

  pre_path='/'.join(check_file.split('/')[:-1])
  file_names=get_names(pre_path,'both')
  if check_file.split('/')[-1] in file_names:
    return True
  else:
    return False
  
def get_fsid(file_path):
  """
  传入绝对路径，返回文件的fs_id
  """
  if file_path[-1]=='/':
    raise(file_path+"不是文件或目录名")

  pre_path='/'.join(file_path.split('/')[:-1])
  file_names=get_files(pre_path)
  for content in file_names:
    if content['server_filename']==file_path.split('/')[-1]:
      return content['fs_id']
  raise ValueError(file_path+'不存在')

def get_dlink_size_prename_suffix(fs_id):
  """
  传入一个fsid，查询文件信息，获得dlink和文件size
  """
  # fs_id=490696277775986
  # 传多个fs_id时，url编码中 [是%5B  ,是%2C  ]是%5D
  url = "http://pan.baidu.com/rest/2.0/xpan/multimedia?method=filemetas&access_token="+access_token+"&fsids=%5B"+str(fs_id)+"%5D&dlink=1"

  payload = {}
  files = {}
  headers = {
    'User-Agent': 'pan.baidu.com'
  }

  response = requests.request("GET", url, headers=headers, data = payload, files = files)
  info=json.loads(response.text.encode('utf8'))['list'][0]
  # print(info)
  name=info['filename']
  # print(names)
  if '.' in name:
      prename=name.split('.')[0]
      suffix="."+name.split('.')[-1]
  else :
      prename=name
      suffix=""
  return (info['dlink'],info['size'],prename,suffix)

# print(get_fsid('/api_test/4380398_02.mp3'))
# dlink,size=get_dlink_and_size(490696277775986)
# print(size)

def download(dlink,size,prename,suffix):
  
  block_size=5242880
  task_num=ceil(size/block_size)
  filename=prename
  for i in range(0,task_num):
    if os.path.exists(filename+'_'+str(i)):
      continue
    url=dlink+"&access_token="+access_token
    payload = {}
    files = {}
    headers = {
      'User-Agent': 'pan.baidu.com',
      "Range":"bytes="+str(i*block_size)+"-"+str(min(size,(i+1)*block_size-1))
    }
    # print(url)
    response = requests.request("GET", url, headers=headers, data = payload, files = files)

    fp = open(filename+'_'+str(i), "wb")
    fp.write(response.content)      # 将下载文件保存到 filename 里
    fp.close()
  merge(filename,suffix,task_num,block_size)

def merge(filename,suffix,task_num,block_size):
  # merge 合并多个文件块，并删除缓存
  write=open(filename+suffix, "wb")
  for i in range(0,task_num):
    read=open(filename+'_'+str(i), "rb")
    write.seek(i*block_size)
    write.write(read.read())
    read.close()
  write.close()
  for i in range(0,task_num):
    os.remove(filename+'_'+str(i))

# print(get_fsid('/api_test/123.ARW'))

# dlink,size,prename,suffix=get_dlink_size_prename_suffix(get_fsid('/fund_stream_project/MP3_raw/4356247.mp3'))
# download(dlink,size,prename,suffix)



def delete_file(path,check_exist):
  """
  注意，如果删除的路径不存在，删除不会报错，不会有任何提示
  删除前请务必一定确保文件路径正确，否则以为删了但实际上没删
  check_exist参数用于设置删除前是否检查路径文件是否存在，1为检查，0为不检查
  """
  if check_exist==1:
    if file_exist(path):
      pass
    else:
      raise ValueError(path+'文件不存在，无法删除')

  url = "https://pan.baidu.com/rest/2.0/xpan/file?method=filemanager&access_token="+access_token+"&opera=delete"

  payload = {'async': '1',
  'filelist': '[\"'+path+'\"]'
  }
  #
  confirm=input('确认删除'+path+'吗？\ny/n:')
  if confirm=='y':
    print('确认删除'+path)
  else:
    print('取消删除')
    return
  response = requests.request("POST", url, data = payload)
  response_dict = json.loads(response.text)
  if response_dict['errno']==0:
    # success
    pass
  elif response_dict['errno']==111:
    raise ValueError(path+'删除时，有其他异步任务正在执行')
  elif response_dict['errno']==-7:
    raise ValueError(path+'文件名非法')
  else:
    print(response.text.encode('utf8'))
  
def delete_abundant_files(folder_path):
  """
  删除多余的文件。百度网盘中重复的文件会自动加"(1)"保存
  输入的是需要清理的路径，无输出
  """
  names=[target_name for target_name in get_names(folder_path,'file_only') if '(1).' in target_name]
  file_names=get_names(folder_path,'file_only')
  for name in names:
    print(name)
    tmp_name="{}.{}".format(name.split('(1).')[0],name.split('(1).')[1])
    if tmp_name in file_names:
      delete_file(folder_path+'/'+name,check_exist=0)
      print('已删除')
    else:
      move_file(folder_path+'/'+name,folder_path+'/'+tmp_name)
      print('已经修改')

def delete_by_suffix(folder_path,suffix):
  """
  删除指定目录中同一后缀的文件
  """
  names=get_names(folder_path,'file_only')
  for name in names:
    if suffix == name.split('.')[-1]:
      delete_file(folder_path+'/'+name,check_exist=0)

def reserve_by_suffix(folder_path,suffix):
  """
  只保留指定后缀的文件
  """
  names=get_names(folder_path,'file_only')
  for name in names:
    if suffix != name.split('.')[-1]:
      delete_file(folder_path+'/'+name,check_exist=0)


def joint_delete_abundant_files(folder_path1,folder_path2):
  """
  比较两个目录，删除其中重复的文件。
  如果有重复，删除的是后一个目录里的
  """
  names1=get_names(folder_path1,'file_only')
  names2=get_names(folder_path2,'file_only')
  del_name=list(set(names1)&set(names2))
  for name in del_name:
    print(name)
    delete_file(folder_path2+'/'+name,check_exist=0)

def move_file(old_path,new_path):
  """
  移动，也可重命名
  """
  url = "https://pan.baidu.com/rest/2.0/xpan/file?method=filemanager&access_token="+access_token+"&opera=move"
  payload = {'async': '1',
  'filelist': '[{"path":"'+old_path+'","dest":"'+'/'.join(new_path.split('/')[:-1])+'","newname":"'+new_path.split('/')[-1]+'","ondup":"fail"}]'
  }

  response = requests.request("POST", url, data = payload)
  response_dict = json.loads(response.text)
  if response_dict['errno']==0:
    # success
    
    pass
  elif response_dict['errno']==111:
    raise ValueError(old_path+'移动时，有其他异步任务正在执行')
  elif response_dict['errno']==-7:
    raise ValueError(old_path+'移动时文件名非法')
  else:
    print(response.text.encode('utf8'))
# delete_abundant_files("/api_test")


def clear_files():
  """
  清理百度网盘文件流程
  """
  # 文件内去重
  folder_list=["/fund_stream_project/output","/fund_stream_project/MP3_raw","/fund_stream_project/MP3_translated"]
  for folder in folder_list:
    delete_abundant_files(folder)

  # 只保留MP3和txt文件
  folder_list=["/fund_stream_project/MP3_raw","/fund_stream_project/MP3_translated"]
  for folder in folder_list:
    reserve_by_suffix('mp3')
  folder_list=["/fund_stream_project/output"]
  for folder in folder_list:
    reserve_by_suffix('txt')

  # 多文件间去重
  joint_delete_abundant_files('MP3_translated','MP3_raw')


if __name__=='__main__':
  print('runing')
  # reserve_by_suffix("/api_test/folder1","mp3")