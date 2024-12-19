import pymysql
def connect_db():
    db = pymysql.connect(host='39.98.191.184',
                        user='work',
                        password='Wswsn1520790880!',
                        database='test1',
                        charset='utf8mb4',
                        port=3306,)
    return db,db.cursor()
