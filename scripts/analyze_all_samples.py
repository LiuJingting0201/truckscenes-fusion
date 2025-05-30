import os
from truckscenes import TruckScenes
from analyze_sensor_stats import analyze_sample  # 导入你刚才定义的函数

# 设置路径
visualization_root = "../output/visualizations"
ts = TruckScenes(dataroot="../data/man-truckscenes", version="v1.0-mini")

# 获取所有已生成的 sample_token 文件夹名
sample_tokens = [
    name for name in os.listdir(visualization_root)
    if os.path.isdir(os.path.join(visualization_root, name))
]

# 批量分析每一个 sample
for token in sample_tokens:
    print(f"🔍 Processing {token} ...")
    analyze_sample(ts, token, output_dir=visualization_root)
