import json

def get_sample_environment(ts, sample_token):
    """
    Given a sample_token, returns environment info from the corresponding scene.
    Output: dict with keys: scene_token, scene_name, weather, timeofday, location
    """
    sample = ts.get('sample', sample_token)
    scene_token = sample['scene_token']
    scene = ts.get('scene', scene_token)

    desc = scene.get("description", "")
    weather = "unknown"
    timeofday = "unknown"
    location = "unknown"

    parts = desc.split(';')
    for p in parts:
        if p.startswith("weather."):
            weather = p.split('.')[1]
        elif p.startswith("daytime."):
            timeofday = p.split('.')[1]
        elif p.startswith("area."):
            location = p.split('.')[1]

    env_info = {
        'scene_token': scene_token,
        'scene_name': scene.get('name', 'unknown'),
        'weather': weather,
        'timeofday': timeofday,
        'location': location,
        'description': desc
    }

    return env_info


def analyze_sample(ts, sample_token, output_dir):
    import os
    import json

    sample = ts.get('sample', sample_token)
    sample_data_tokens = [
        sd['token'] for sd in ts.sample_data
        if sd['sample_token'] == sample_token
    ]

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

    if __name__ == "__main__":
        from truckscenes import TruckScenes

        # 设置 TruckScenes 数据路径和版本
        ts = TruckScenes(dataroot="../data/man-truckscenes", version="v1.0-mini")

        # 指定 sample_token（可以从你的 sample_summary.csv 里拿一个）
        sample_token = "32d2bcf46e734dffb14fe2e0a823d059"

        # 设置输出目录
        output_dir = "../output/visualizations"

        # 分析这个 sample
        analyze_sample(ts, sample_token, output_dir)
