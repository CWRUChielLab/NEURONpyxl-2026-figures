"""
This script is a time benchmark for NEURONpyxl simulations.
It uses the CPG network from Momohara, et al. (2022), corresponding
to the excel file in ../sheets/fig10.xlsx. This file saves the times from
10 independent simulations of the network under noisy and noiseless conditions
to a CSV file located in ../data/benchmark/benchmark_neuron.csv.
"""

from neuronpyxl import Network
from pathlib import Path
import numpy as np
import pandas as pd

excelpath = "./sheets/fig10.xlsx"
Path(f"./data/benchmark").mkdir(parents=True, exist_ok=True)

noise_params = (50,1e-5,25) # frequency (Hz), synaptic weight (uS), time constant (ms)
simdur = 40000 # ms
n = 10 # number of samples
noiseless_times = np.zeros(n) # Set up array
noisy_times = np.zeros(n)

def main():
    # Initialize Network object without noise
    nw_noiseless = Network(
                params_file=excelpath,
                sim_name="BMP",noise=None,dt=-1,integrator=2,atol=1e-5,
                eq_time=10000,simdur=simdur,seed=False
            )
    
    for i in range(n):
        nw_noiseless.run(record_none=True)
        noiseless_times[i] = nw_noiseless.simtime

    # Save memory by not storing the entire simulation
    # data for the noisy case
    del nw_noiseless

    # Initialize Network object with noise
    nw_noisy = Network(
                params_file=excelpath,
                sim_name="BMP",noise=noise_params,dt=-1,integrator=2,atol=1e-5,
                eq_time=10000,simdur=simdur,seed=False
            )
    
    for j in range(n):
        nw_noisy.run(record_none=True)
        noisy_times[j] = nw_noisy.simtime

    del nw_noisy

    # Save the data to a file in the ./data folder
    pd.DataFrame({
        "noisy": noisy_times,
        "noiseless": noiseless_times
        }).to_csv("./data/benchmark/benchmark_neuron.csv")

if __name__ == "__main__":
    main()
