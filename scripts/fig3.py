# To compile the mod files, run neuronpyxl -f gen_mods --file sheets/fig3.xlsx

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
from utility import remove_axes,plot_vertical_scalebar
from neuronpyxl import Network
from neuron import h

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--snnap_data",
    required=True,
    type=Path,
    help="Path to SNNAP data.",
)

excelpath = "./sheets"
figpath = "./figs"
excelfile = "fig3.xlsx"
    

if __name__ == "__main__":
    args = parser.parse_args()
    snnap_path = os.path.join(args.snnap_data,"fig3")

    nw = Network(params_file=os.path.join(excelpath, excelfile), sim_name="excitability",\
                noise=None,dt=-1,integrator=2,atol=1e-5,eq_time=1000,simdur=9000,seed=False)
    
    # Extra recordings for special plotting
    # Record BR from kcas mechanism
    br_rec = h.Vector().record(nw.cells["B4"].section(0.5)._ref_BR_neuronpyxl_kcas)
    # Record the total time, not the relative time reported by neuronpyxl
    total_time = h.Vector().record(h._ref_t)
    nw.run()

    # Organize data
    br = br_rec.as_numpy()
    t_tot = total_time.as_numpy()
    tvec = np.arange(0,9000,step=0.05)
    data = pd.DataFrame(nw.get_interpolated_cell_data("B4",tvec))
    br = np.interp(tvec,t_tot-1000,br_rec)
    t = tvec

    # Get SNNAP data
    snnapdata = pd.read_csv(os.path.join(snnap_path,"excitability.smu.out"),\
                            sep="\t").dropna(axis=1).dropna(axis=0)
    snnapdata.columns = ["t","V","I_leak","I_na","I_k","I_kcas","I_kcaf","cai","I_app"]
    snnapdata = snnapdata[snnapdata["t"]>=10]
    snnapdata["t"] -= 10
    t = data["t"] / 1000
    tsnnap = np.array(snnapdata["t"])

    # Plot styling
    snnapcolor = "dodgerblue"
    nrncolor = "orangered"
    lw = 5
    fs=30

    # Plot everything
    fig = plt.figure(figsize=(14, 10), constrained_layout=True)
    sfigs = fig.subfigures(1, 2, width_ratios=[2, 1.2])

    ax1 = sfigs[0].subplots(3, 1)   # left subfigure: 3 rows × 1 col
    ax2 = sfigs[1].subplots(1, 1)   # right subfigure: 1 plot

    ax1[0].plot(t,data["V"],color=nrncolor,linewidth=lw,label="NEURON")
    ax1[0].plot(tsnnap,snnapdata["V"],\
                color=snnapcolor,linestyle="dashed",linewidth=lw,label="SNNAP")
    ax1[0].set_ylabel("Voltage (mV)",fontsize=fs)
    
    ax1[1].plot(t,data["I_kcas"],color=nrncolor,linewidth=lw)
    ax1[1].plot(tsnnap,snnapdata["I_kcas"],\
                color=snnapcolor,linestyle="dashed",linewidth=lw)
    ax1[1].set_ylabel(r"$I_{K_{Ca,s}}$ (nA)",fontsize=fs)

    ax1[2].plot(t,data["cai"]*1e6,color=nrncolor,linewidth=lw)
    ax1[2].plot(tsnnap,snnapdata["cai"],\
                color=snnapcolor,linestyle="dashed",linewidth=lw)
    ax1[2].set_ylabel(r"$[Ca]_i$ (nM)",fontsize=fs)
    ax1[2].set_xlabel("Time (s)",fontsize=fs)
    
    # Plot fBR on a twin axis
    ax1_twinx = plt.twinx(ax1[2])
    ax1_twinx.plot(t,br,color='black', linestyle='dashdot', linewidth=3)
    ax1_twinx.set_ylabel("f[BR]",fontsize=30)
    ax1_twinx.set_yticks([0.0,0.015,0.03])
    ax1_twinx.tick_params(axis="y", labelsize=30)

    # Remove axes for asthetics
    for ax in ax1:
        ax.tick_params(axis="both", labelsize=30)
        remove_axes(ax1[1])
    remove_axes(ax1[2],remove_x=False,remove_y=False)
    remove_axes(ax1_twinx,remove_x=False,remove_y=False)

    # Plot just one spike
    start = 97600
    end = 99200
    ax2.plot(t[start:end]-t[start],data["V"][start:end],\
             label="NEURON",color=nrncolor,linewidth=lw)
    ax2.plot(tsnnap[start:end]-tsnnap[start],snnapdata["V"][start:end],\
             label="SNNAP",color=snnapcolor,linestyle="dashed",linewidth=lw)
    # Add legend element for fBR
    ax2.plot([],[],color='black', linestyle='dashdot', linewidth=4,label="f[BR]")

    ax2.legend(frameon=False,fontsize=30)
    ax2.set_xlabel("Time (s)",fontsize=fs)
    ax2.tick_params(axis="x", labelsize=30)

    remove_axes(ax2,remove_x=False,remove_y=True)
    plot_vertical_scalebar(ax2,bar_width=0.0005,offset=0,yoffset=2)
    
    # Save fig
    fig.align_ylabels()
    fig.savefig(os.path.join(figpath,f"fig3.jpg"),bbox_inches="tight",dpi=300)
