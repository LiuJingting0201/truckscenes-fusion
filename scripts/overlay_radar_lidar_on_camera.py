import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from truckscenes import TruckScenes
from utils.render_pointcloud_in_image import render_pointcloud_in_image


def overlay_radar_lidar_on_camera(ts, sample_token, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    sample = ts.get('sample', sample_token)

    # 使用官方函数：投影Radar到前向Camera
    try:
        fig_radar = render_pointcloud_in_image(ts, sample_token, dot_size=4, pc_type='RADAR', verbose=False)
        radar_path = os.path.join(out_dir, f"{sample_token}_overlay_radar.png")
        fig_radar.savefig(radar_path, dpi=200)
        plt.close(fig_radar)
        print(f"📡 Radar overlay saved to {radar_path}")
    except Exception as e:
        print(f"⚠️ Failed to render radar overlay: {e}")

    # 使用官方函数：投影LiDAR到前向Camera
    try:
        fig_lidar = render_pointcloud_in_image(ts, sample_token, dot_size=1, pc_type='LIDAR', verbose=False)
        lidar_path = os.path.join(out_dir, f"{sample_token}_overlay_lidar.png")
        fig_lidar.savefig(lidar_path, dpi=200)
        plt.close(fig_lidar)
        print(f"🛰️ LiDAR overlay saved to {lidar_path}")
    except Exception as e:
        print(f"⚠️ Failed to render lidar overlay: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample_token", type=str, required=True, help="Sample token to visualize")
    parser.add_argument("--output_dir", type=str, default="../output/visualizations", help="Output directory")
    parser.add_argument("--version", type=str, default="v1.0-mini", help="Dataset version")

    args = parser.parse_args()
    ts = TruckScenes(dataroot="../data/man-truckscenes", version=args.version)
    overlay_radar_lidar_on_camera(ts, args.sample_token, args.output_dir)
