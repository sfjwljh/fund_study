"""
此程序用于处理数据库和百度网盘数据交互
网盘清理，数据库清理，
"""
import my_disk_app as disk
import pymysql
db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
cursor = db.cursor()

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
update_download()