import pandas as pd
import matplotlib.pyplot as plt
import os


def csv_to_image(csv_path: str, save_root_path: str):
    """
    从 CSV 文件生成时频图，并将每一行的数据绘制为图像保存到指定目录。

    Args:
        csv_path (str): 输入 CSV 文件路径
        save_root_path (str): 保存生成图像的目录路径
    """
    # 确保保存路径存在
    os.makedirs(save_root_path, exist_ok=True)

    # 读取 CSV 文件
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"读取 CSV 文件失败: {str(e)}")

    # 遍历每一行数据，假设每一行是一个信号
    for idx, row in df.iterrows():
        # 假设每一行数据是一个信号（可根据实际格式调整）
        signal = row.values

        # 生成时频图
        plt.figure(figsize=(10, 6))
        plt.plot(signal)
        plt.title(f"Spectrogram {idx}")
        plt.xlabel('Frequency')
        plt.ylabel('Amplitude')

        # 保存图像为 PNG
        filename = f"spec_{idx}.png"
        file_path = os.path.join(save_root_path, filename)
        plt.savefig(file_path)
        plt.close()  # 关闭图像，释放内存

    print(f"图像已保存到 {save_root_path}")

