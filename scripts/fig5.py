# To compile the mod files, neuronpyxl -f gen_mods --file Excel_files/fig7.xlsx

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utility import remove_axes,plot_vertical_scalebar,add_snnap_path_arg
from neuronpyxl import Network

parser = add_snnap_path_arg()

excelpath = "./sheets"
figpath = "./figs"
excelfile = "fig5.xlsx"

if __name__ == "__main__":
    args = parser.parse_args()
    snnapdatapath = os.path.join(args.snnap_data,"fig5")

    fs = 14
    lw = 3

    snnap_data = pd.read_csv(os.path.join(snnapdatapath,"synapse.smu.out"), sep="\t").dropna(axis=1)
    snnap_data.columns = ["t", "V_A", "nai_A", "V_B", "nai_B", "V_C", "nai_C"]
    tsnnap = np.asarray(snnap_data["t"])

    nw = Network(params_file=os.path.join(excelpath, excelfile), sim_name="synapse",
                                noise=None,dt=-1,integrator=2,atol=1e-5,eq_time=5000,simdur=13000,seed=False)

    nw.run(voltage_only=True)

    A = nw.get_cell_data("A")
    B = nw.get_cell_data("B")
    C = nw.get_cell_data("C")
    t = np.array(A["t"]) / 1000

    colors = ["red", "teal", "orchid"]
    snnapcolor = "dodgerblue"
    nrncolor = "orangered"
    fig, ax = plt.subplots(3, 1, figsize=(14,10),constrained_layout=True)
    ax[0].plot(t, A["V"], color=nrncolor,label="NEURON",linewidth=lw)
    ax[0].plot(tsnnap, snnap_data["V_A"], label="SNNAP", color=snnapcolor,linestyle="--",linewidth=lw)
    ax[0].set_ylabel("Neuron A",rotation=0,fontsize=20)
    ax[0].legend(frameon=False,fontsize=20)

    ax[1].plot(t, B["V"],color=nrncolor,linewidth=lw)
    ax[1].plot(tsnnap, snnap_data["V_B"], color=snnapcolor,linestyle="--",linewidth=lw)
    ax[1].set_ylabel("Neuron B",rotation=0,fontsize=20)

    ax[2].plot(t, C["V"],color=nrncolor,linewidth=lw)
    ax[2].plot(tsnnap, snnap_data["V_C"], color=snnapcolor,linestyle="--",linewidth=lw)
    ax[2].set_ylabel("Neuron C",rotation=0,fontsize=20)

    ax[2].set_xlabel("Time (s)",fontsize=fs)
    ax[2].set_xticks(np.arange(0,14,step=0.5))

    for a in ax:
        a.set_xlim((0,13))

    remove_axes(ax[0],remove_x=True,remove_y=True)
    remove_axes(ax[1],remove_x=True,remove_y=True)
    remove_axes(ax[2],remove_x=False,remove_y=True)

    plot_vertical_scalebar(ax[2],scalebar_length=50,bar_width=0.025,xoffset=0.1,yoffset=20)
    plt.show()
    fig.savefig(os.path.join(figpath,f"fig5.jpg"), bbox_inches="tight",dpi=300)
