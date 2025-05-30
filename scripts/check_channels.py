from truckscenes import TruckScenes

ts = TruckScenes(dataroot="../data/man-truckscenes", version="v1.0-mini")
sample_token = "32d2bcf46e734dffb14fe2e0a823d059"

sample = ts.get('sample', sample_token)
data = sample["data"]

channels = []
for token in data.values():
    sd = ts.get('sample_data', token)
    channels.append(sd['channel'])

print("✅ 当前 sample 拥有的 channel：")
for ch in channels:
    print("-", ch)
