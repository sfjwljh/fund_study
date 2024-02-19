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
# 把MP3_raw目录里的文件在数据库上downloaded列都改为1
    names_list=disk.get_names(folder_path='/fund_stream_project/MP3_raw',file_or_folder_or_both='file_only')
    names_list=[name.split('.')[0] for name in names_list]

    for name in names_list:
        update_query = "UPDATE total SET downloaded =%s  WHERE CODE = %s"
        cursor.execute(update_query, (1, name))
        db.commit()