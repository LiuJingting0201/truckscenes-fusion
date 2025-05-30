import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import open3d as o3d
import numpy as np
from truckscenes.truckscenes import TruckScenes
import json
# 读取 .pcd 文件为 numpy 点云
def read_pcd_as_numpy(filepath):
    try:
        pcd = o3d.io.read_point_cloud(filepath)
        return np.asarray(pcd.points)
    except Exception as e:
        print(f"❌ Failed to read PCD file {filepath}: {e}")
        return None

def get_sample_environment(ts, sample_token):
    """
    Given a sample_token, returns environment info from the corresponding scene.
    Output: dict with keys: scene_token, scene_name, weather, timeofday, location
    """
    sample = ts.get('sample', sample_token)
    scene_token = sample['scene_token']
    scene = ts.get('scene', scene_token)

    env_info = {
        'scene_token': scene_token,
        'scene_name': scene.get('name', 'unknown'),
        'weather': scene.get('weather', 'unknown'),
        'timeofday': scene.get('timeofday', 'unknown'),
        'location': scene.get('location', 'unknown'),
        'description': scene.get('description', '')
    }

    return env_info


def analyze_sample(ts, sample_token, output_dir):
    import os
    import json

    sample = ts.get('sample', sample_token)
    sample_data_tokens = ts.get_sample_data_tokens(sample_token)
    sensor_counts = {}

    for token in sample_data_tokens:
        sd = ts.get('sample_data', token)
        modality = sd['sensor_modality']
        channel = sd['channel']
        sensor_counts[channel] = sensor_counts.get(channel, 0) + 1

    env_info = get_sample_environment(ts, sample_token)

    stats = {
        'sample_token': sample_token,
        'timestamp': sample['timestamp'],
        'num_annotations': len(sample['anns']),
        'sensor_counts': sensor_counts,
        'environment': env_info
    }

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{sample_token}_sensor_stats.json")
    with open(out_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Sensor stats saved to {out_path}")



# 合并多个 LiDAR 点云并使用 Open3D 可视化和保存为 .ply
def merge_and_display_lidar(lidar_list, sample_output_dir):
    all_points = []
    for ch, points in lidar_list:
        if points is not None:
            all_points.append(points)
    if not all_points:
        print("⚠️ 没有有效 LiDAR 点云数据")
        return

    merged = np.vstack(all_points)
    print(f"📦 合并点云共 {len(merged)} 个点，正在展示 3D 视图")

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(merged)

    # 可视化
    o3d.visualization.draw_geometries([pcd], window_name="Merged LiDAR")

    # 保存为 .ply
    ply_path = os.path.join(sample_output_dir, "merged_lidar.ply")
    o3d.io.write_point_cloud(ply_path, pcd)
    print(f"✅ 合并点云已保存为 {ply_path}")

# 使用官方方法渲染点云叠加图像并保存
def render_overlay(ts, sample_token, pointsensor_channel, camera_channel, output_path):
    try:
        ts.render_pointcloud_in_image(
            sample_token,
            pointsensor_channel=pointsensor_channel,
            camera_channel=camera_channel,
            render_intensity=True,
            out_path=output_path
        )
        print(f"✅ Overlay image saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to render overlay: {e}")

# 读取雷达通道的点数信息
def load_radar_points(ts, sample_token, dataroot):
    radar_points = {}
    for sd in ts.sample_data:
        if sd["sample_token"] != sample_token:
            continue
        channel = sd["channel"]
        if "RADAR" in channel:
            file_path = os.path.join(dataroot, sd["filename"])
            if os.path.exists(file_path):
                try:
                    pcd = o3d.io.read_point_cloud(file_path)
                    radar_points[channel] = len(np.asarray(pcd.points))
                except Exception as e:
                    radar_points[channel] = None
                    print(f"⚠️ Failed to read Radar: {file_path}, {e}")
            else:
                radar_points[channel] = None
    return radar_points

# CLI 参数解析
parser = argparse.ArgumentParser(description="Visualize TruckScenes sample")
parser.add_argument('--sample_token', type=str, help='Sample token to visualize')
parser.add_argument('--csv_path', type=str, help='CSV file with sample summary (for batch mode)')
parser.add_argument('--limit', type=int, default=1, help='Number of samples to visualize in batch')
args = parser.parse_args()

# 数据集初始化
data_root = "../data/man-truckscenes"
ts = TruckScenes(version='v1.0-mini', dataroot=data_root, verbose=False)

# 获取 sample_token 列表
sample_tokens = []
if args.sample_token:
    sample_tokens = [args.sample_token]
elif args.csv_path:
    df = pd.read_csv(args.csv_path)
    sample_tokens = df['sample_token'].tolist()[:args.limit]
else:
    raise ValueError("请提供 --sample_token 或 --csv_path 参数")

# 输出目录
base_output_dir = "../output/visualizations"
os.makedirs(base_output_dir, exist_ok=True)

# 遍历所有 sample_token
for sample_token in sample_tokens:
    print(f"\n🔍 Visualizing sample: {sample_token}")
    sample_output_dir = os.path.join(base_output_dir, sample_token)
    os.makedirs(sample_output_dir, exist_ok=True)

    image_data = []
    lidar_data = []

    for sd in ts.sample_data:
        if sd["sample_token"] != sample_token:
            continue

        channel = sd["channel"]
        file_path = os.path.join(data_root, sd["filename"])

        if "CAMERA" in channel and os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                image_data.append((channel, img))
            except Exception as e:
                print(f"❌ 图像读取失败: {file_path}, 错误: {e}")

        elif "LIDAR" in channel and os.path.exists(file_path):
            lidar = read_pcd_as_numpy(file_path)
            if lidar is not None:
                lidar_data.append((channel, lidar))

    # 相机图像拼接
    if image_data:
        image_data.sort(key=lambda x: x[0])
        n = len(image_data)
        fig, axs = plt.subplots(1, n, figsize=(4 * n, 4))
        if n == 1:
            axs = [axs]
        for ax, (ch, img) in zip(axs, image_data):
            ax.imshow(img)
            ax.set_title(ch, fontsize=8)
            ax.axis('off')
        plt.suptitle(f"Sample {sample_token} - Camera Views")
        plt.tight_layout()
        cam_path = os.path.join(sample_output_dir, "cam_views.png")
        plt.savefig(cam_path)
        plt.close()
        print(f"✅ Camera image saved to {cam_path}")
    else:
        print("⚠️ No camera data found.")

    # 合并 LiDAR 点云并显示
    valid_lidar = [(ch, ld) for ch, ld in lidar_data if ld is not None]
    merge_and_display_lidar(valid_lidar, sample_output_dir)

    # 渲染官方 overlay 图
    render_overlay(
        ts,
        sample_token,
        pointsensor_channel="LIDAR_TOP_LEFT",
        camera_channel="CAMERA_LEFT_FRONT",
        output_path=os.path.join(sample_output_dir, "overlay_lidar.png")
    )

    # 加载 Radar 点信息
    radar_info = load_radar_points(ts, sample_token, data_root)
    print(f"📡 Radar channel stats: {radar_info}")
