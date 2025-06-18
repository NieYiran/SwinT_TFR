import os
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import spectrogram
import matplotlib.pyplot as plt

# 核心函数：处理CSV -> 多张图 -> 打包成zip
def process_csv_to_spectrograms(csv_path, output_img_dir, sampling_rate=100, prefix="spectrogram"):
    data = np.genfromtxt(csv_path, delimiter=',')
    if data.ndim == 1:
        data = np.expand_dims(data, axis=0)

    total_time = data.shape[1] / sampling_rate
    time = np.linspace(0, total_time, data.shape[1], endpoint=False)

    # FFT 滤波
    fft_values = fft(data)
    frequencies = fftfreq(data.shape[1], d=time[1] - time[0])
    mask = (frequencies >= 10) & (frequencies <= 20)
    filtered_fft = fft_values * mask[:, np.newaxis].T
    filtered_signal = np.fft.ifft(filtered_fft).real

    for i in range(filtered_signal.shape[0]):
        f, t, Sxx = spectrogram(filtered_signal[i], fs=sampling_rate, nperseg=60, noverlap=30)
        t_extended = np.linspace(0, 2.5, len(t) + 2)
        Sxx_extended = np.pad(Sxx, ((0, 0), (1, 1)), mode='edge')
        Sxx_normalized = Sxx_extended / np.sum(Sxx_extended, axis=0, keepdims=True)

        plt.figure()
        plt.pcolormesh(t_extended, f, Sxx_normalized, shading='gouraud', cmap='jet', vmin=0, vmax=1)
        plt.axis('off')
        plt.gca().set_position([0, 0, 1, 1])

        # 使用 prefix 和序号命名图像
        filename = f"{prefix}_{i+1}.png"
        plt.savefig(os.path.join(output_img_dir, filename), bbox_inches='tight', pad_inches=0)
        plt.close()