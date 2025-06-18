import time
from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, uuid, zipfile
from routers import users  # 导入路由模块
from functions.detect import load_model, predict_image
from functions.spectrogram import process_csv_to_spectrograms
from typing import List
import sqlite3
from datetime import datetime
import base64

# ------------------- FastAPI 初始化与跨域设置 -------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)
# 目录配置
BASE_DIR = "static"
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_PATH = 'Users/history.db'
UPLOAD_DIR = os.path.abspath("static/uploads")
OUTPUT_DIR = os.path.abspath("static/downloads")

# ------------------- /detect 接口：图像检测 -------------------
@app.post("/detect")
async def detect(
    A: UploadFile = File(None),
    B: UploadFile = File(None),
    C: UploadFile = File(None)
):
    response = {
        "timestamp": time.time(),
        "documents": []
    }

    for zone, file in zip(["A", "B", "C"], [A, B, C]):
        if file is not None:
            image_bytes = await file.read()
            weight_path = f'./weights/best_model/{zone}.pth'
            assert os.path.exists(weight_path), f"模型文件 {zone}.pth 不存在！"

            model = load_model(weight_path)
            result = predict_image(image_bytes, model)

            response["documents"].append({
                "filename": file.filename,
                "location": zone,
                "result": result["probabilities"],
                "prediction": result["prediction"]
            })

    return response

# ------------------- /upload-csv 接口：上传 CSV 并返回图像压缩包 -------------------

@app.post("/upload-csv")
async def upload_csv(files: List[UploadFile] = File(...)):
    try:
        unique_id = str(uuid.uuid4())
        file_dir = os.path.join(UPLOAD_DIR, unique_id)
        print("保存路径:", file_dir)
        os.makedirs(file_dir, exist_ok=True)

        # 创建图像保存目录
        img_output_dir = os.path.join(file_dir, "images")
        os.makedirs(img_output_dir, exist_ok=True)

        for file in files:
            csv_path = os.path.join(file_dir, file.filename)
            with open(csv_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            base_filename = os.path.splitext(file.filename)[0]
            process_csv_to_spectrograms(csv_path, img_output_dir, prefix=base_filename)

        # 打包图像
        zip_filename = f"spectrograms_{unique_id}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, zip_files in os.walk(img_output_dir):
                for name in zip_files:
                    filepath = os.path.join(root, name)
                    arcname = os.path.relpath(filepath, img_output_dir)
                    zipf.write(filepath, arcname)

        download_url = f"/static/downloads/{zip_filename}"
        return JSONResponse(content={"download_url": download_url})

    except Exception as e:
        print("异常：", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

# 上传记录接口
@app.post("/upload-record")
async def upload_record(
    user_id: str = Form(...),
    operation: str = Form(...),
    records: UploadFile = File(...)
):
    try:
        file_data = await records.read()
        # 提取文件 MIME 类型 和 原始文件名
        mime_type = records.content_type or 'application/octet-stream'
        filename = records.filename or 'unknown_file'
        # 获取当前时间戳，格式为 YYYYMMDDHHMMSS
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # 写入数据库（含新字段）
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO operations (user_id, timestamp, operation, records, mime_type, filename)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, timestamp, operation, file_data, mime_type, filename))
        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "操作记录已成功保存"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/query-records")
async def query_records(user_id: str = Query(...), role: int = Query(...)):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if role == 1:
            cursor.execute('''
                SELECT user_id, timestamp, operation, records, mime_type, filename FROM operations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC
            ''', (user_id,))
        elif role == 0:
            cursor.execute('''
                SELECT user_id, timestamp, operation, records, mime_type, filename FROM operations 
                ORDER BY timestamp DESC
            ''')
        else:
            return JSONResponse(status_code=400, content={"error": "无效的角色值，应为0或1"})
        rows = cursor.fetchall()
        conn.close()
        # 构建结果列表
        result = []
        for row in rows:
            record_base64 = base64.b64encode(row[3]).decode("utf-8") if row[3] else None
            result.append({
                "user_id": row[0],
                "timestamp": row[1],
                "operation": row[2],
                "records_base64": record_base64,
                "mime_type": row[4],
                "filename": row[5]
            })
        return JSONResponse(content={"records": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/delete-record")
async def delete_record(user_id: str = Form(...), timestamp: str = Form(...)):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 执行删除操作
        cursor.execute("""
            DELETE FROM operations
            WHERE user_id = ? AND timestamp = ?
        """, (user_id, timestamp))
        conn.commit()
        # 判断是否成功删除记录
        if cursor.rowcount == 0:
            return JSONResponse(content={"message": "未找到对应记录，删除失败"}, status_code=404)
        return {"message": "记录删除成功"}
    except Exception as e:
        return JSONResponse(content={"message": f"数据库操作失败: {str(e)}"}, status_code=500)
    finally:
        conn.close()

# 启动服务器时的命令： uvicorn main:app --reload






