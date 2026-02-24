import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from neuronpyxl import Network
from scipy.optimize import curve_fit
from utility import add_snnap_path_arg

parser = add_snnap_path_arg()

excelpath = "./sheets"
excelfile = "fig7.xlsx"
figpath = "./figs"

def gaussian(x, A, mu, sigma):
        return 1/np.sqrt(2*np.pi)/A * np.exp(-(x - mu)**2 / (2 * sigma**2))


def gaussian_fit(counts,bins,data):    
    bin_centers = 0.5*(bins[1:] + bins[:-1])
    p0 = [1., np.mean(data), np.std(data)]
    popt, _ = curve_fit(gaussian, bin_centers, counts, p0=p0)
    x_fit = np.linspace(min(bins), max(bins), 100)
    return x_fit, *popt


if __name__ == "__main__":
    args = parser.parse_args()
    data_folder = os.path.join(args.snnap_data,"fig7")

    snnap_data = pd.read_csv(os.path.join(data_folder,"snnap.smu.out"), sep="\t",header=None)
    snnap_data.columns = ["t","V","I1","I2","I3","I4","I5","I6","I7","I8"]
    snnap_data = snnap_data[snnap_data["t"] > 10]
    nrn_data = pd.HDFStore(os.path.join(data_folder,"nrn.h5"))["membrane"]
    t = nrn_data["t"].to_numpy() / 1000
    v = nrn_data["V_B4"].to_numpy()
    vsnnap = snnap_data["V"].to_numpy()

    freq = 50
    weight = 1e-5
    tau = 25
    
    nw = Network(
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
    
    rest_potential = nw.get_cell_data("B4")["V"][-1]
    print(f"Rest potential: {rest_potential} mV")

    fs = 30
    nbins = 50
    lw = 3

    fig, axs = plt.subplots(1, 2, figsize=(14, 10), constrained_layout=True,width_ratios=[1.5,1])
    nvcounts, nvbins, _ = axs[1].hist(v-rest_potential, bins=nbins, color='red', edgecolor='none',
                                    alpha=0.4,orientation="horizontal", density=True,label="NEURON")
    svcounts, svbins, _ = axs[1].hist(vsnnap-rest_potential, bins=nbins, color='dodgerblue', edgecolor='none',
                                    alpha=0.4,orientation="horizontal", density=True,label="SNNAP")
    nrnfit = gaussian_fit(nvcounts, nvbins, v-rest_potential)
    snnapfit = gaussian_fit(svcounts, svbins, vsnnap-rest_potential)
    ls = "dashed"
    axs[0].plot(t, v-rest_potential, color="red", linewidth=1,alpha=0.8)
    axs[0].set_ylabel("V-Vr (mV)",fontsize=fs)
    axs[0].set_xlabel("Time (s)",fontsize=fs)
    axs[0].hlines([0],0,500,linestyle="dashed",linewidth=lw,colors="black")
    axs[0].set_yticks([-0.004,-0.002,0,0.002,0.004])
    axs[1].set_xlabel("Density (a.u.)",fontsize=fs)
    
    axs[1].plot(gaussian(*nrnfit), nrnfit[0], color='red', label=None,linewidth=lw,linestyle=ls)
    axs[1].plot(gaussian(*snnapfit), snnapfit[0], color='dodgerblue', label=None,linewidth=lw,linestyle=ls)
    axs[1].legend(frameon=False,loc="upper right",fontsize=25)
    for ax in axs.flatten():
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axs[1].spines["left"].set_visible(False)
    axs[1].set_yticks([])
    axs[1].set_ylim(axs[0].get_ylim())
    axs[1].set_xticks([0,250,500])
    axs[1].tick_params(labelsize=22)
    axs[0].tick_params(labelsize=22)

    fig.savefig(os.path.join(figpath,"fig7.jpg"), bbox_inches="tight", dpi=300)

    voltage_bias = np.mean(v) - rest_potential 
    print(f"Number of samples: {len(t)}")
    print(f"Voltage bias = {voltage_bias} mV")
