from truckscenes import TruckScenes
import os

VERSION = 'v1.0-mini'
DATASET_DIR = os.path.abspath("../data/man-truckscenes")

def main():
    ts = TruckScenes(VERSION, DATASET_DIR, verbose=True)
    scene = ts.scene[0]
    sample_token = scene['first_sample_token']
    
    print(f"🔍 正在渲染 sample: {sample_token}")
    ts.render_sample(sample_token)

if __name__ == '__main__':
    main()