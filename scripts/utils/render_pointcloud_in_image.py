import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import open3d as o3d

def find_sample_data(ts, sample_token, channel_name):
    sample = ts.get('sample', sample_token)
    for token in sample['data'].values():
        sd = ts.get('sample_data', token)
        if sd['channel'] == channel_name:
            return sd
    return None

def get_preferred_channel(channels, sensor_type):
    preferred_keywords = ["TOP_FRONT", "RIGHT_FRONT", "FRONT", "TOP"]
    for keyword in preferred_keywords:
        for ch in channels:
            if sensor_type in ch and keyword in ch:
                return ch
    return None

def render_pointcloud_in_image(ts, sample_token, dot_size=3, pc_type="RADAR", verbose=False):
    sample = ts.get("sample", sample_token)
    sd_tokens = sample["data"]
    available_channels = [ts.get("sample_data", token)["channel"] for token in sd_tokens.values()]

    cam_channel = get_preferred_channel(available_channels, "CAMERA")
    pc_channel = get_preferred_channel(available_channels, pc_type)

    if cam_channel is None or pc_channel is None:
        raise RuntimeError(f"Missing data for {cam_channel} or {pc_channel}")

    cam_sd = find_sample_data(ts, sample_token, cam_channel)
    pc_sd = find_sample_data(ts, sample_token, pc_channel)

    if cam_sd is None or pc_sd is None:
        raise RuntimeError(f"Missing data for {cam_channel} or {pc_channel}")

    cam_path = os.path.join(ts.dataroot, cam_sd["filename"])
    pc_path = os.path.join(ts.dataroot, pc_sd["filename"])

    if not os.path.exists(cam_path):
        raise FileNotFoundError(f"Image not found: {cam_path}")
    if not os.path.exists(pc_path):
        raise FileNotFoundError(f"Pointcloud not found: {pc_path}")

    img = Image.open(cam_path)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(img)

    # Load point cloud
    ext = os.path.splitext(pc_path)[1].lower()
    try:
        if ext == ".pcd":
            pcd = o3d.io.read_point_cloud(pc_path)
            pc = np.asarray(pcd.points)
        elif ext == ".bin":
            pc_raw = np.fromfile(pc_path, dtype=np.float32)
            if pc_type == "LIDAR":
                if len(pc_raw) % 4 == 0:
                    pc = pc_raw.reshape(-1, 4)
                elif len(pc_raw) % 3 == 0:
                    pc = pc_raw.reshape(-1, 3)
                else:
                    raise ValueError(f"Unexpected LIDAR format: cannot reshape array of size {len(pc_raw)}")
            else:
                pc = pc_raw.reshape(-1, 3)
        else:
            raise ValueError(f"Unsupported point cloud file extension: {ext}")
    except Exception as e:
        raise RuntimeError(f"Failed to parse pointcloud from {pc_path}: {e}")

    if pc.shape[1] < 3:
        raise ValueError(f"{pc_type} format unknown: {pc.shape}")

    xs = img.width // 2 + (pc[:, 0] * 10)
    ys = img.height // 2 - (pc[:, 1] * 10)

    ax.scatter(xs, ys, s=dot_size, c=pc[:, 0], cmap='jet', alpha=0.7)
    ax.set_title(f"{pc_type} overlay on {cam_channel}")
    ax.axis("off")

    return fig
