import os
import pandas as pd
from neuronpyxl import Network

excelpath = "./sheets"
excelfile = "fig7.xlsx"
savepath = "./data"

freq = 50
weight = 1e-5
tau = 25

if __name__ == "__main__":
    nw = Network(
            params_file=os.path.join(excelpath,excelfile),
            sim_name="nostim",
            noise=(freq,weight,tau),
            dt=-1,
            integrator=2,
            atol=1e-5,
            seed=True,
            eq_time=1000,
            simdur=500000
            )
    nw.run()

    data = nw.get_cell_data("B4")
    pd.DataFrame(data).to_hdf(os.path.join(savepath,"fig7_noisy_B4_data.h5"))