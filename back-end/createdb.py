import sqlite3
import os

# 数据库文件路径
DB_FILENAME = r"C:\Users\nyr\Documents\GitHub\SwinT_TFR\Users\history.db"

# 如果数据库不存在就创建
if not os.path.exists(DB_FILENAME):
    # 连接数据库（会自动创建文件）
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    # 创建表，新增 mime_type 和 filename 字段
    cursor.execute('''
        CREATE TABLE operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            records BLOB,
            mime_type TEXT,
            filename TEXT
        )
    ''')

    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    print(f"数据库 {DB_FILENAME} 已成功创建并初始化。")
else:
    print(f"数据库 {DB_FILENAME} 已存在。")
