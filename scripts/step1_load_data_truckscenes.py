
import os

from truckscenes import TruckScenes

VERSION = "v1.0-mini"
DATASET_DIR = "../data/man-truckscenes"

ts = TruckScenes(VERSION, DATASET_DIR, verbose=True)

print("\n📋 场景信息：")
ts.list_scenes()

print(f"\n✅ 成功载入 {len(ts.scene)} 个场景！")

print("\n🔍 前5个场景示例：")
for i, s in enumerate(ts.scene[:5]):
    print(f"{i+1}. 名称: {s['name']} | 描述: {s['description']}")


