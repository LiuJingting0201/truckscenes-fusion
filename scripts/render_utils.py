# render_utils.py
import os
from truckscenes.utils.data_classes import LidarPointCloud

from truckscenes import TruckScenes
import matplotlib.pyplot as plt

import os
import matplotlib.pyplot as plt

def render_and_save(ts, sample_token, save_dir, sensors=None):
    """
    渲染并保存某个 sample 的多个 sensor 图像。
    """
    if sensors is None:
        # 默认选择一些典型传感器
        sensors = ["CAMERA_FRONT", "LIDAR_TOP_LEFT", "RADAR_FRONT"]

    os.makedirs(save_dir, exist_ok=True)

    for sensor in sensors:
        try:
            ts.render_sample_data(sample_token, sensor)
            print(f"✅ 渲染完成: {sample_token} - {sensor}")
        except Exception as e:
            print(f"❌ 渲染失败: {sample_token} - {sensor} | 原因: {e}")

    # Camera
    try:
        show_camera(ts, sample_token, save_path=os.path.join(out_dir, 'camera.png'))
    except Exception as e:
        print(f"[!] Failed to render camera for {sample_token}: {e}")

    # LiDAR
    try:
        show_lidar(ts, sample_token, save_path=os.path.join(out_dir, 'lidar.png'))
    except Exception as e:
        print(f"[!] Failed to render LiDAR for {sample_token}: {e}")

    # Radar
    try:
        show_radar(ts, sample_token, save_path=os.path.join(out_dir, 'radar.png'))
    except Exception as e:
        print(f"[!] Failed to render radar for {sample_token}: {e}")