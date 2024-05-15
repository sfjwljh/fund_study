"""
此程序用于处理数据库和百度网盘数据交互
网盘清理，数据库清理，
"""
import my_disk_app as disk
import pymysql
import pdb
import sys
db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
cursor = db.cursor()

def update_db_by_disk():
    """
    根据网盘内的文件，更新数据库
    """

    # 更新MP3
    MP3_foleders=['/fund_stream_project/MP3_raw','/fund_stream_project/MP3_translated']
    mp3_names_list=[]
    for folder in MP3_foleders:
        mp3_names_list.extend(disk.get_names(folder,file_or_folder_or_both='file_only'))
    mp3_names_list=[int(i.split('.')[0]) for i in mp3_names_list]
    print("--------------------开始更新mp3记录------------------")
    
    count_all=0
    count_act=0
    task_num=len(mp3_names_list)
    for name in mp3_names_list:

        select_query = "select downloaded from total where code=%s"
        cursor.execute(select_query,(name))
        try:
            db_code_exist=cursor.fetchone()[0]
        except:
            print(str(name)+"有下载的mp3但是不在数据库中")
            continue
        if 1==db_code_exist:
            # print(str(name)+"downloaded已经是1")
            count_all+=1
            print(f"进度：{count_all}/{task_num}，已更新{count_act}", end='\r')
            # sys.stdout.flush()
            continue
        # pdb.set_trace()

        # update_query = "UPDATE total SET stt =%s  WHERE CODE = %s"
        update_query = "UPDATE total SET downloaded =%s  WHERE CODE = %s"
        cursor.execute(update_query, (1, name))
        db.commit()
        count_all+=1
        count_act+=1
        print(f"进度：{count_all}/{task_num}，已更新{count_act}", end='\r')
        sys.stdout.flush()

    print("\n--------------------mp3记录更新完毕------------------")
    print('\n\n')
    # 更新txt

    txt_foleders=['/fund_stream_project/output']
    txt_names_list=[]
    for folder in txt_foleders:
        txt_names_list.extend(disk.get_names(folder,file_or_folder_or_both='file_only'))
    txt_names_list=[int(i.split('.')[0]) for i in txt_names_list]
    print("--------------------开始更新txt记录------------------")
    
    count_all=0
    count_act=0
    task_num=len(txt_names_list)
    for name in txt_names_list:

        select_query = "select stt from total where code=%s"
        cursor.execute(select_query,(name))
        try:
            db_code_exist=cursor.fetchone()[0]
        except:
            print(str(name)+"有下载的txt但是不在数据库中")
            continue

        if 1==db_code_exist:
            # print(str(name)+"stt已经是1")
            count_all+=1
            print(f"进度：{count_all}/{task_num}，已更新{count_act}", end='\r')
            sys.stdout.flush()
            continue
        # pdb.set_trace()

        update_query = "UPDATE total SET stt =%s  WHERE CODE = %s"
        # update_query = "UPDATE total SET downloaded =%s  WHERE CODE = %s"
        cursor.execute(update_query, (1, name))
        db.commit()
        count_all+=1
        count_act+=1
        print(f"进度：{count_all}/{task_num}，已更新{count_act}", end='\r')
        sys.stdout.flush()


    print("\n--------------------txt记录更新完毕------------------")
    print('\n\n')
    print("--------------------开始删除多余的MP3记录------------------")
    select_query = "select code from total where downloaded=1"
    cursor.execute(select_query,)
    db_down_list=cursor.fetchall()
    db_down_list=[i[0] for i in db_down_list]
    remove_list=[i for i in db_down_list if i not in mp3_names_list]
    print("发现{}条记录在db中，但不在网盘中".format(len(remove_list)))

    count_all=0
    task_num=len(remove_list)
    for name in remove_list:
        delete_query = "DELETE FROM total WHERE CODE = %s"
        cursor.execute(delete_query, (name))
        db.commit()
        count_all+=1
        print(f"删除进度：{count_all}/{task_num}", end='\r')
    print("\n--------------------多余的MP3记录删除完毕------------------")
    print('\n\n')
    print("--------------------开始删除多余的txt记录------------------")
    select_query = "select code from total where stt=1"
    cursor.execute(select_query,)
    db_down_list=cursor.fetchall()
    db_down_list=[i[0] for i in db_down_list]
    remove_list=[i for i in db_down_list if i not in txt_names_list]
    print("发现{}条记录在db中，但不在网盘中".format(len(remove_list)))
    count_all=0
    task_num=len(remove_list)
    for name in remove_list:
        delete_query = "DELETE FROM total WHERE CODE = %s"
        cursor.execute(delete_query, (name))
        db.commit()
        count_all+=1
        print(f"删除进度：{count_all}/{task_num}", end='\r')
    print("\n--------------------多余的txt记录删除完毕------------------")
    print('\n\n')


def update_download():
    count=0
# 把MP3_raw/translated目录里的文件在数据库上downloaded列都改为1
# 把translated目录里的文件在数据库上stt列都改为1
    names_list=disk.get_names(folder_path='/fund_stream_project/MP3_translated',file_or_folder_or_both='file_only')
    # names_list=disk.get_names(folder_path='/fund_stream_project/MP3_translated',file_or_folder_or_both='file_only')
    names_list=[int(name.split('.')[0]) for name in names_list]

    # print(len(db_code_list))

    for name in names_list:
        # 检查是否存在
        # select_query = "select code from total where code=%s"
        # cursor.execute(select_query,(name))
        # db_code_exist=cursor.fetchone()
        # if db_code_exist:
        #     update_query = "UPDATE total SET downloaded =%s  WHERE CODE = %s"
        #     cursor.execute(update_query, (1, name))
        #     db.commit()
        # else:
        #     print(str(name)+"不存在于db")

        # 不检查是否存在
        update_query = "UPDATE total SET stt =%s  WHERE CODE = %s"
        # update_query = "UPDATE total SET downloaded =%s  WHERE CODE = %s"
        cursor.execute(update_query, (1, name))
        db.commit()
        count+=1
        print(count)
update_db_by_disk()