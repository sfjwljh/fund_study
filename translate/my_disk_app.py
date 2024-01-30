import requests
import json


access_token="121.92bcfc0ff065f427bd78fac550b89b27.YGvXR2tmXxEQSpCuqZFXtMwqyBLyDmHx4YqMYY-.KM1q8Q"

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
    add_num=len(response_dict['list'])
    file_list.extend(response_dict['list'])
  return file_list

def get_names(folder_path,file_or_folder_or_both):
  """
  folder_path: 要查看的目录在网盘上的绝对路径
  file_or_folder： 三值，file_only表示只要文件的名字，folder_only表示只要文件夹的名字，both表示不区分都要
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

print(get_names('/api_test/','file_only'))




