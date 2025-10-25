# Author: Mian Qin
# Date Created: 10/24/25
import sqlite3


def main():
    ...
    conn = sqlite3.connect('users.db')  # 替换为你的数据库文件
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = ? WHERE username = ?", (1, "mianqin"))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
