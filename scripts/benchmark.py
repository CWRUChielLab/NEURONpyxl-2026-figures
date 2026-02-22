"""
This script is a time benchmark for NEURONpyxl simulations.
It uses the CPG network from Momohara, et al. (2022), corresponding
to the excel file in ../sheets/fig10.xlsx. This file saves the times from
10 independent simulations of the network under noisy and noiseless conditions
to a CSV file located in ../data/benchmark/benchmark_neuron.csv.
"""

from neuronpyxl import Network
import numpy as np
import pandas as pd
import time
from pathlib import Path
excelpath = "./sheets/fig10.xlsx"
Path(f"./data/benchmark").mkdir(parents=True, exist_ok=True)

noise_params = (50,1e-5,25) # frequency (Hz), synaptic weight (uS), time constant (ms)
simdur = 40000 # ms
n = 10 # number of samples
noiseless_times = np.zeros(n) # Set up array
noisy_times = np.zeros(n)

def main():
    nw_noiseless = Network(
                params_file=excelpath,
                sim_name="BMP",noise=None,dt=-1,integrator=2,atol=1e-5,
                eq_time=10000,simdur=simdur,seed=False
            )
    
    for i in range(n):
        t0 = time.time()
        nw_noiseless.run(record_none=True)
        noiseless_times[i] = time.time() - t0

    del nw_noiseless

    nw_noisy = Network(
                params_file=excelpath,
                sim_name="BMP",noise=noise_params,dt=-1,integrator=2,atol=1e-5,
                eq_time=10000,simdur=simdur,seed=False
            )
    
    for j in range(n):
        t0 = time.time()
        nw_noisy.run(record_none=True)
        noisy_times[j] = time.time() - t0

    del nw_noisy

    pd.DataFrame({
        "noisy": noisy_times,
        "noiseless": noiseless_times
        }).to_csv("./data/benchmark/benchmark_neuron.csv")

if __name__ == "_main__":
    main()
