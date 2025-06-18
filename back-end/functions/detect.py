from model import swin_tiny_patch4_window7_224 as create_model  # ✅你自己的模型定义
import torch, json
from PIL import Image
from io import BytesIO
from torchvision import transforms
from typing import Dict

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
img_size = 224
transform = transforms.Compose([
    transforms.Resize(int(img_size * 1.14)),
    transforms.CenterCrop(img_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
# 加载类别映射
with open('./class_indices.json', 'r') as f:
    class_indict = json.load(f)
idx_to_label = {int(k): v for k, v in class_indict.items()}

def load_model(weight_path: str):
    model = create_model(num_classes=len(class_indict)).to(device)
    model.load_state_dict(torch.load(weight_path, map_location=device))
    model.eval()
    return model

def predict_image(image_bytes: bytes, model) -> Dict:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output = torch.squeeze(model(img_tensor)).cpu()
        predict = torch.softmax(output, dim=0)

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