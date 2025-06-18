import os
import json
import torch
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from torchvision import transforms
from model import swin_tiny_patch4_window7_224 as create_model
import time

# 初始化 FastAPI 应用
app = FastAPI()

# 允许跨域（适配 Nuxt3 前端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设备配置
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
img_size = 224

# 图像预处理
transform = transforms.Compose([
    transforms.Resize(int(img_size * 1.14)),
    transforms.CenterCrop(img_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 加载类别索引（例如 {"0级": 0, "1级": 1, "2级": 2, "3级": 3}）
with open('./class_indices.json', 'r') as f:
    class_indict = json.load(f)

# 反转索引：从数字索引 → 标签
idx_to_label = {int(k): v for k, v in class_indict.items()}

# 创建模型并加载权重
def load_model(weight_path: str):
    model = create_model(num_classes=len(class_indict)).to(device)
    model.load_state_dict(torch.load(weight_path, map_location=device))
    model.eval()
    return model

# 图像预测函数
def predict_image(image_bytes: bytes, model) -> Dict:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output = torch.squeeze(model(img_tensor)).cpu()
        predict = torch.softmax(output, dim=0)

    # 输出标签: 概率字典 + 初步判断
    probabilities = {
        idx_to_label[i]: round(float(predict[i]), 4)
        for i in range(len(predict))
    }

    max_index = torch.argmax(predict).item()
    predicted_label = idx_to_label[max_index]

    return {
        "probabilities": probabilities,
        "prediction": predicted_label
    }

# 检测接口
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

    # 依次处理 A/B/C 三个区段图像
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
                "result": result["probabilities"],       # 各级别概率
                "prediction": result["prediction"]       # 概率最大对应级别
            })

    return response


