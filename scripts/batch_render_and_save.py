import os
import matplotlib.pyplot as plt
from PIL import Image
from truckscenes import TruckScenes

VERSION = 'v1.0-mini'
DATASET_DIR = os.path.abspath('../data/man-truckscenes')
SAVE_DIR = os.path.abspath('./rendered_samples')
os.makedirs(SAVE_DIR, exist_ok=True)
NUM_SAMPLES = 10  # 你可以修改

def main():
    ts = TruckScenes(VERSION, DATASET_DIR, verbose=True)
    sample_tokens = [s['token'] for s in ts.sample[:10]]  # 前10个 sample

    print(f"🚀 开始批量渲染前 {len(sample_tokens)} 个样本...")

    for i, token in enumerate(sample_tokens):
        save_path = os.path.join(SAVE_DIR, f"sample_{i}_{token}.png")
        try:
            ts.render_sample(token, out_path=save_path)  # ✅ 直接保存图像
            print(f"✅ 已保存: {save_path}")
        except Exception as e:
            print(f"❌ 渲染失败: {token} | 原因: {e}")

if __name__ == "__main__":
    main()