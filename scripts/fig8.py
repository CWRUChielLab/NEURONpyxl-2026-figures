import numpy as np
import os
import scienceplots
import matplotlib.pyplot as plt
import pandas as pd
plt.style.use(['no-latex','notebook'])

excelpath = "./Excel_files"
excelfile = "fig5-fig9.xlsx"

data_folder = "/media/uri/uri-external-drive/SNNAP_data/fig9"

snnap_data = pd.read_csv(os.path.join(data_folder,"snnap.smu.out"), sep="\t",header=None)
snnap_data.columns = ["t","V","I1","I2","I3","I4","I5","I6","I7","I8"]
snnap_data = snnap_data[snnap_data["t"] > 10]
data = pd.HDFStore(os.path.join(data_folder,"nrn.h5"))["membrane"]
t = data["t"].to_numpy() / 1000
v = data["V_B4"].to_numpy()
vsnnap = snnap_data["V"].to_numpy()

from neuronpyxl import network

freq = 50
weight = 1e-5
tau = 25
"""
nw = network.Network(
        params_file=os.path.join(excelpath,excelfile),
        sim_name="nostim",
        noise=None,
        dt=-1,
        integrator=2,
        atol=1e-5,
        seed=True,
        eq_time=5000,
        simdur=10000
        )

nw.run()
"""
data_clean = pd.HDFStore("./Dickman_etal_2025_Figures/Data/fig9/clean_B4/nostim_data.h5")["membrane"]["V_B4"]
#rest_potential = nw.get_cell_data("B4")["V"][-1]
rest_potential=data_clean.to_numpy()[-1]
print(f"Rest potential: {rest_potential} mV")
"""
nw_noisy = network.Network(
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
nw_noisy.run()
"""

from scipy.optimize import curve_fit
fs = 30
def gauss(x, A, mu, sigma):
    return 1/np.sqrt(2*np.pi)/A * np.exp(-(x - mu)**2 / (2 * sigma**2))

def gaussian_fit(counts,bins,data):    
    bin_centers = 0.5*(bins[1:] + bins[:-1])
    p0 = [1., np.mean(data), np.std(data)]
    popt, _ = curve_fit(gauss, bin_centers, counts, p0=p0)
    x_fit = np.linspace(min(bins), max(bins), 100)
    return x_fit, *popt
nbins = 50
fig, axs = plt.subplots(1, 1, figsize=(14, 10), constrained_layout=True)
nvcounts, nvbins, _ = axs.hist(v-rest_potential, bins=nbins, color='red', edgecolor='none',
                                   alpha=0.4,orientation="vertical", density=True,label="NEURON")
svcounts, svbins, _ = axs.hist(vsnnap-rest_potential, bins=nbins, color='dodgerblue', edgecolor='none',
                                   alpha=0.4,orientation="vertical", density=True,label="SNNAP")
nrnfit = gaussian_fit(nvcounts, nvbins, v-rest_potential)
snnapfit = gaussian_fit(svcounts, svbins, vsnnap-rest_potential)
ls = "dashed"
axs.set_xlabel(r"$V-Vr$ (mV)",fontsize=fs)
lw = 4
axs.plot(nrnfit[0],gauss(*nrnfit), color='red', label=None,linewidth=lw,linestyle=ls)
axs.plot(snnapfit[0], gauss(*snnapfit), color='dodgerblue', label=None,linewidth=lw,linestyle=ls)
axs.legend(frameon=False,loc="upper right",fontsize=30)
# for ax in axs.flatten():
axs.spines["top"].set_visible(False)
axs.spines["right"].set_visible(False)
axs.spines["left"].set_visible(False)
axs.set_yticks([])
# axs.set_ylim(axs[0].get_ylim())
axs.tick_params(labelsize=fs)
plt.show()

fig.savefig("figs/Dickman_etal_Results_noise2.jpg", bbox_inches="tight", dpi=300)

voltage_bias = np.mean(v) - rest_potential 
print(f"Number of samples: {len(t)}")
print(f"Voltage bias = {voltage_bias} mV")
