import os
import numpy as np
import open3d as o3d
from truckscenes import TruckScenes
from tqdm import tqdm

def load_radar_pcd(filepath):
    try:
        pcd = o3d.io.read_point_cloud(filepath)
        return np.asarray(pcd.points)
    except Exception as e:
        print(f"❌ Failed to read radar .pcd: {filepath}\n{e}")
        return None


def get_radar_points(ts, sample_token):
    radar_points = []
    for sd in ts.sample_data:
        if sd['sample_token'] == sample_token and sd['sensor_modality'] == 'radar':
            file_path = os.path.join(ts.dataroot, sd['filename'])
            points = load_radar_pcd(file_path)

            if points is not None:
                radar_points.append(points)
    if radar_points:
        return np.concatenate(radar_points, axis=0)
    else:
        return np.empty((0, 3))

def visualize_radar_points(points, save_path=None):
    if points.shape[0] == 0:
        print("⚠️ No radar points to visualize.")
        return
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.paint_uniform_color([0.2, 0.8, 1.0])  # 蓝绿色调
    o3d.visualization.draw_geometries([pcd])
    if save_path:
        o3d.io.write_point_cloud(save_path, pcd)
        print(f"✅ Saved radar pointcloud to {save_path}")

if __name__ == "__main__":
    ts = TruckScenes(dataroot="../data/man-truckscenes", version="v1.0-mini")
    sample_token = "32d2bcf46e734dffb14fe2e0a823d059"  # 替换为你想看的
    radar_points = get_radar_points(ts, sample_token)
    visualize_radar_points(radar_points, save_path=f"../output/visualizations/{sample_token}/radar_cloud.ply")
