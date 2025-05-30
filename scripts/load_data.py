# load_data.py
from truckscenes.truckscenes import TruckScenes

def load_truckscenes_data(data_dir: str = '../data', version: str = 'v1.0-mini'):
    ts = TruckScenes(dataroot=data_dir, version=version)
    sample_tokens = [s['token'] for s in ts.sample]
    return ts, sample_tokens