from model import *
from tqdm import tqdm

init = 0
patient_data = []

with open("../../data/ckd_positive.csv", "r") as f:
    for line in tqdm(f.readlines()):
        if init == 0:
            init = 1
            continue
        patient_data.append(Patient(line.strip()))