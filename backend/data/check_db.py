# Author: Mian Qin
# Date Created: 10/24/25
import sqlite3

# 连接SQLite示例
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# 执行查询
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()

# 在PyCharm调试器中可以查看results变量的值
for row in results:
    print(row)

cursor.close()
conn.close()
