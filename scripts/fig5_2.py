# To compile the mod files, run neuronpyxl -f gen_mods --file Excel_files/fig5-fig9.xlsx

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from neuronpyxl import Network
from neuron import h

# snnapdatapath = "/media/uri/uri-external-drive/SNNAP_data/fig5"
excelpath = "./sheets"
figpath = "./figs"
fig_prefix = "Dickman_etal_Results"
excelfile = "fig3.xlsx"

def remove_axes(ax,remove_x=True,remove_y=False):
    # For aesthetics
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if remove_x:
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
    if remove_y:
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        
def plot_vertical_scalebar(ax,scalebar_length=10,bar_width=0.25,offset=0,yoffset=10,xoffset=0,textoffset=0.001):
    from matplotlib.patches import Rectangle
    # Get axis limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Coordinates for bottom-right corner
    x_start = xlim[1] - offset - bar_width + xoffset
    y_start = ylim[0] + offset + yoffset

    scalebar = Rectangle((x_start, y_start), width=bar_width, height=scalebar_length,
                        color='black', linewidth=0, zorder=10)

    ax.add_patch(scalebar)

    # Optional: Add text label
    ax.text(x_start-textoffset, y_start + scalebar_length / 2, f'{scalebar_length} mV',
            va='center', ha='right', color='black', fontsize=14)
    

if __name__ == "__main__":
    nw = Network(params_file=os.path.join(excelpath, excelfile), sim_name="excitability",
                                noise=None,dt=-1,integrator=2,atol=1e-5,eq_time=1000,simdur=9000,seed=False)
    br_rec = h.Vector().record(nw.cells["B4"].section(0.5)._ref_BR_neuronpyxl_kcas)
    total_time = h.Vector().record(h._ref_t)
    nw.run()
    br = br_rec.as_numpy()
    t_tot = total_time.as_numpy()
    tvec = np.arange(0,9000,step=0.05)
    data = pd.DataFrame(nw.get_interpolated_cell_data("B4",tvec))
    br = np.interp(tvec,t_tot-1000,br_rec)
    t = tvec
    # snnapdata = pd.read_csv(os.path.join(snnapdatapath,"excitability.smu.out"), sep="\t").dropna(axis=1).dropna(axis=0)
    # snnapdata.columns = ["t", "V", "I_leak", "I_na", "I_k", "I_kcas", "I_kcaf", "cai", "I_app"]
    # snnapdata = snnapdata[snnapdata["t"]>=10]
    # snnapdata["t"] -= 10
    # t = data["t"] / 1000
    # tsnnap = np.array(snnapdata["t"])

    fig, ax1 = plt.subplots(3, 1, figsize=(24, 9), constrained_layout=True)
    # fig = plt.figure(figsize=(14, 10), constrained_layout=True)
    # sfigs = fig.subfigures(1, 1, width_ratios=[2, 1.2])

    # ax1 = sfigs[0].subplots(3, 1)   # left subfigure: 3 rows × 1 col
    # ax2 = sfigs[1].subplots(1, 1)   # right subfigure: 1 plot

    snnapcolor = "dodgerblue"
    nrncolor = "orangered"
    lw = 5
    fs=30

    ax1[0].plot(t,data["V"],color=nrncolor,linewidth=lw,label="NEURON")
    # ax1[0].plot(tsnnap,snnapdata["V"],color=snnapcolor,linestyle="dashed",linewidth=lw,label="SNNAP")
    ax1[0].plot([],[],color=snnapcolor,linestyle="dashed",linewidth=lw,label="SNNAP")
    ax1[0].set_ylabel("Voltage (mV)",fontsize=fs)
    ax1[0].plot([],[],color='black', linestyle='dashdot', linewidth=4,label="f[BR]")
    ax1[0].legend(frameon=False,fontsize=30)
    remove_axes(ax1[0])
    ax1[1].plot(t,data["I_kcas"],color=nrncolor,linewidth=lw)
    # ax1[1].plot(tsnnap,snnapdata["I_kcas"],color=snnapcolor,linestyle="dashed",linewidth=lw)
    ax1[1].set_ylabel(r"$I_{K_{Ca,s}}$ (nA)",fontsize=fs)
    remove_axes(ax1[1])
    #ax1[1].set_ylim((0,2))
    ax1[2].plot(t,data["cai"]*1e6,color=nrncolor,linewidth=lw)
    # ax1[2].plot(tsnnap,snnapdata["cai"],color=snnapcolor,linestyle="dashed",linewidth=lw)
    ax1[2].set_ylabel(r"$[Ca]_i$ (nM)",fontsize=fs)
    ax1[2].set_xlabel("Time (s)",fontsize=fs)
    
    ax2 = plt.twinx(ax1[2])

    ax2.plot(tvec/1000,br,color='black', linestyle='dashdot', linewidth=3)
    ax2.set_ylabel("f[BR]",fontsize=30)
    ax2.set_yticks([0.0,0.015,0.03])

    remove_axes(ax1[2],remove_x=False,remove_y=False)
    # remove_axes(ax2,remove_x=False,remove_y=Falsse)

    for ax in ax1:
        ax.tick_params(axis="both", labelsize=30)
    ax2.tick_params(axis="y", labelsize=30)

    start = 97600
    end = 99200
    # ax2.plot(t[start:end]-t[start],data["V"][start:end],label="NEURON",color=nrncolor,linewidth=lw)
    # ax2.plot(tsnnap[start:end]-tsnnap[start],snnapdata["V"][start:end],label="SNNAP",color=snnapcolor,linestyle="dashed",linewidth=lw)
    # remove_axes(ax2,remove_x=False,remove_y=True)
    # ax2.legend(frameon=False,fontsize=20)
    # ax2.set_xlabel("Time (s)",fontsize=fs)
    # plot_vertical_scalebar(ax2,bar_width=0.0005,offset=0,yoffset=2)
    # sfig_labels = ['A', 'B', 'C']

    # for subfig, label in zip([sfigs[0],sfigs[1],sfigs2], sfig_labels):
    #     # Add label to the upper left of each subfigure
    #     subfig.suptitle(label, x=0.0, y=1.06, ha='left', va='top', fontsize=22, fontweight='bold')
        
    fig.align_ylabels()
    plt.show()
    # fig.savefig(os.path.join(figpath,f"{fig_prefix}_regulation3.jpg"),bbox_inches="tight",dpi=300)
