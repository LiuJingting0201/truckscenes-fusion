import os
import pandas as pd
from truckscenes.truckscenes import TruckScenes

# 初始化 TruckScenes 数据集
data_root = "../data/man-truckscenes"
ts = TruckScenes(version='v1.0-mini', dataroot=data_root, verbose=False)

# 构建结构化记录
records = []

for sample in ts.sample:
    sample_token = sample['token']
    scene_token = sample['scene_token']
    timestamp = sample['timestamp']
    num_annotations = len(sample['anns'])

    # 获取该 sample 的所有传感器通道
    sensor_channels = set()
    for sd in ts.sample_data:
        if sd['sample_token'] == sample_token:
            sensor_channels.add(sd['channel'])
    sensor_channels = sorted(sensor_channels)  # 排序方便查看/一致性


    # 目前 TruckScenes 无 log 表，默认填 unknown
    weather = "unknown"
    area = "unknown"

    records.append({
        "sample_token": sample_token,
        "scene_token": scene_token,
        "timestamp": timestamp,
        "num_annotations": num_annotations,
        "available_sensors": sensor_channels,
        "weather": weather,
        "area": area
    })

# 保存为 CSV
df = pd.DataFrame(records)
os.makedirs("../output", exist_ok=True)
df.to_csv("../output/sample_summary.csv", index=False)

print("✅ parse_sample.py 完成：输出文件为 output/sample_summary.csv")
