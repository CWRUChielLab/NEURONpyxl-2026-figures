# To compile the mod files, run neuronpyxl -f gen_mods --file Excel_files/fig6.xlsx

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from utility import remove_axes, plot_vertical_scalebar,add_snnap_path_arg
from neuronpyxl import Network

parser = add_snnap_path_arg()

excelpath = "./sheets"
figpath = "./figs"
excelfile = "fig6.xlsx"

if __name__ == "__main__":
    args = parser.parse_args()
    snnapdatapath = os.path.join(args.snnap_data,"fig6")

    fs = 30
    lw = 2.5

    snnap_data = pd.read_csv(os.path.join(snnapdatapath,"synapse.smu.out"), sep="\t").dropna(axis=1)
    snnap_data.columns = ["t", "VA", "VB"]
    nw = Network(params_file=os.path.join(excelpath, excelfile), sim_name="main",
                                noise=None,dt=0.01,integrator=2,atol=1e-5,eq_time=0,simdur=6000,seed=False)

    nw.run(voltage_only=True)

    tvec = np.array(snnap_data["t"])*1000
    A = nw.get_interpolated_cell_data("A",tvec)
    B = nw.get_interpolated_cell_data("B",tvec)
    t = np.array(A["t"]) / 1000

    # I'm sorry but I had to manually find the indices of the times when
    # the voltage deflection occurs
    times = np.array([(850, 1000), (1350, 1500), (1850, 2000), (2350, 2500), \
                      (2850, 3000), (3350, 3500), (3850, 4000), (4350, 4500), (4850, 5000)])
    dt = 0.005
    indices = (times / dt).astype(int)

    from matplotlib import colormaps
    cmap = colormaps['coolwarm']
    colors = [cmap(i/9) for i in range(9)]  # 10 colors from the colormap

    amps_snnap = []
    Vs_snnap = []

    fig, (ax1,ax2) = plt.subplots(1, 2, figsize=(14, 7),width_ratios=[1.4,1])

    amps_nrn = []
    Vs_nrn = []

    for i,(start, end) in enumerate(indices):
        x = np.asarray(B["t"][start:end] - B["t"][start])
        y = np.asarray(B["V"][start:end] - B["V"][start])
        Vs_nrn.append(B["V"][start])
        amps_nrn.append(max(y))
        ax1.plot(x,y, label=f'{math.floor(B["V"][end])}',color=colors[i],linewidth=lw,zorder=1)
    

    ax2.plot(Vs_nrn, amps_nrn,color="black",linewidth=lw,linestyle="dashed",zorder=0)
    ax2.scatter(Vs_nrn, amps_nrn,color=colors,marker="o",s=100,zorder=1,edgecolors="black")
    ax2.set_xlabel("Holding potential (mV)",fontsize=fs)
    ax2.set_xticks([-90,-70,-50,-30,-10])
    ax1.set_xlabel("Time (ms)",fontsize=fs)
    ax1.set_xticks([0,30,60,90,120,150])

    remove_axes(ax1,remove_x=False,remove_y=False)
    remove_axes(ax2,remove_x=False,remove_y=True)

    ax1.set_ylabel(r"$V_i(t)-V_i(0)$ (mV)",fontsize=fs)
    ax1.set_yticks([0,0.1,0.2,0.3,0.4])
    ax2.set_ylim(ax1.get_ylim())
    ax1.tick_params(axis="y", labelsize=22)
    ax1.tick_params(axis='x', labelsize=22)
    ax2.tick_params(axis='x', labelsize=22)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(
        handles[::-1], labels[::-1],
        title="Holding potential",
        title_fontsize='xx-large',
        fontsize=22,
        loc="center left",
        bbox_to_anchor=(1, 0.7),
        frameon=False,
        borderaxespad=0,
        ncol=1,
        bbox_transform=fig.transFigure
    )

    plot_vertical_scalebar(ax2,scalebar_length=0.1,bar_width=0.4,yoffset=0.05,textoffset=1.0)
    fig.tight_layout(pad=3.0)
    fig.align_ylabels()
    fig.savefig(os.path.join(figpath,f"fig6.jpg"), dpi=300, bbox_inches='tight')
