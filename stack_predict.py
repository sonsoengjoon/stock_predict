import pymysql

connection = pymysql.connect(host='localhost', port=13306, db='investar', user='root', passwd='qwaszx2689!', autocommit=True)

cursor = connection.cursor()
cursor.execute("SELECT VERSION();")
result = cursor.fetchone()

print("MariaDB version : {}".format(result))

connection.close()
