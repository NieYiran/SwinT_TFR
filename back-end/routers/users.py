from fastapi import APIRouter, Form, HTTPException
import sqlite3

router = APIRouter()

DB_PATH = 'Users/users.db'  # 数据库路径

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_admin(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row and row["role"] == 0

@router.post("/admin/regist")
async def register(
    user_id: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, password, role) VALUES (?, ?, ?)",
            (user_id, password, 1)  # 默认role为1，普通用户
        )
        conn.commit()
        return 1
    except sqlite3.IntegrityError:
        return 0
    finally:
        conn.close()

@router.post("/admin/login")
async def login(
    user_id: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE user_id = ? AND password = ?",
        (user_id, password)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "username": result["user_id"],
            "role": result["role"]
        }
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.get("/admin/users")
def get_all_users(current_user: str = 'admin'):
    if not check_admin(current_user):
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

@router.post("/admin/users")
def add_user(
    user_id: str = Form(...),
    password: str = Form(...),
    role: int = Form(1),
    current_user: str = 'admin'
):
    if not check_admin(current_user):
        raise HTTPException(status_code=403, detail="仅管理员可操作")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id, password, role) VALUES (?, ?, ?)", (user_id, password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="用户已存在")
    finally:
        conn.close()
    return {"message": "用户添加成功"}

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: str, current_user: str = 'admin'):
    if not check_admin(current_user):
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    if user_id == 'admin':
        raise HTTPException(status_code=403, detail="不允许删除管理员账号")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "用户已删除"}
