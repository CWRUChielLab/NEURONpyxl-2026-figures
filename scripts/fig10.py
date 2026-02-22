# Run these commands to generate the data first
# neuronpyxl -f gen_mods --file Excel_files/fig10.xlsx
# neuronpyxl -f run_sim --file Excel_files/fig10.xlsx --name BMP --noise 50 1e-5 25 --duration 75000 --teq 10000 --vonly --folder fig10data

snnapdatapath = "/media/uri/uri-external-drive/SNNAP_data/fig10"
datapath = "/home/uri/my-files/projects/cwru/neuronpyxl/Dickman_etal_2025_Figures/Data"
excelpath = "./sheets"
figpath = "./figs"
fig_prefix = "Dickman_etal_Results"
excelfile = "fig10.xlsx"

import matplotlib.pyplot as plt
from matplotlib import rcParams 
from matplotlib.lines import Line2D
import scienceplots
import numpy as np
import pandas as pd
import os
import sys
plt.style.use(["no-latex", "notebook"])

legend_labels = {"darkorange": "Command-like",
                 "red": "Protraction",
                 "purple": "Closure",
                 "dodgerblue": "Retraction",
                 "forestgreen": "Retraction terminating"
                }

colors = {
    "darkorange": ["CBI2"], # command-like neuron
    "red": ["B20", "B30", "B31a", "B34", "B35", "B40", "B63"], # protraction
    "purple": ["B8"], # closure
    "dodgerblue": ["B51a", "B64a","B4"], # retraction
    "forestgreen": ["B52"] # retraction termination
}

all_cells = [(cell, color) for color, cells in colors.items() for cell in cells]
num_cells = len(all_cells)

import matplotlib.ticker as ticker
def xtickson(ax,ticks):
    ax.tick_params(axis='x', which='both', bottom=True, top=False)

    # Specify number of ticks on x-axis
    ax.set_xticks(ticks)

def ylabel(ax,text):
    ax.text(-0.05, 0.5, text, transform=ax.transAxes,
        rotation=0, va='center', ha='center', fontsize=18)

def plot_bmps(data,axs,all_cells,xlim=(0,65),snnap=True,ylab=False):
    if num_cells == 1:
        axs = [axs]  # Ensure axes is a list when there's only one subplot

    # Plot data from each cell
    for ax, (cell, color) in zip(axs, all_cells):
        t = np.array(data["t"])
        if snnap:
            ind = np.where(t > 10)[0]
            t = np.array(t[ind])
            t -= t[0]
            V = data[f"V_{cell}"][ind]
        else:
            V = data[f"V_{cell}"]
        
        ax.plot(t, V, color=color, linewidth=1,label=None)
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        ax.set_xlim(xlim)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        if ylab:
            ylabel(ax,cell)

def plot_vertical_scalebar(ax,scalebar_length=100,bar_width=0.25,xoffset=0,yoffset=0):
    from matplotlib.patches import Rectangle
    # Get axis limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Coordinates for bottom-right corner
    x_start = xlim[1] + xoffset - bar_width
    y_start = ylim[0] + yoffset

    scalebar = Rectangle((x_start, y_start), width=bar_width, height=scalebar_length,
                        color='black', linewidth=0, zorder=10)

    ax.add_patch(scalebar)

    # Optional: Add text label
    ax.text(x_start - 1, y_start + scalebar_length / 2, f'{scalebar_length} mV',
            va='center', ha='right', color='black', fontsize=14)


def remove_axes(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks([])

if __name__ == "__main__":

    snnap_data = {
            "clean": (pd.read_csv(os.path.join(snnapdatapath,"BMP_clean1.smu.out"), sep="\t", header=None).dropna(axis=1),
                      pd.read_csv(os.path.join(snnapdatapath,"BMP_clean2.smu.out"), sep="\t", header=None).dropna(axis=1)),
            "noisy": (pd.read_csv(os.path.join(snnapdatapath,"BMP_noise1.smu.out"), sep="\t", header=None).dropna(axis=1),
                      pd.read_csv(os.path.join(snnapdatapath,"BMP_noise2.smu.out"), sep="\t", header=None).dropna(axis=1))
            }
    nrn_data = {
            "clean": (pd.HDFStore(os.path.join(datapath,"fig10data/BMP_clean1.h5"))["membrane"],
                      pd.HDFStore(os.path.join(datapath,"fig10data/BMP_clean2.h5"))["membrane"]),
            "noisy": (pd.HDFStore(os.path.join(datapath,"fig10data/BMP_noise1.h5"))["membrane"],
                      pd.HDFStore(os.path.join(datapath,"fig10data/BMP_noise2.h5"))["membrane"])
            }
    
    snnapcols = ["t","V_B20","V_B30","V_B31a","V_B34","V_B35","V_B4",\
                "V_B40","V_B51a","V_B52","V_B63","V_B64a","V_B8","V_CBI2"]

    for f1,f2 in snnap_data.values():
        f1.columns = snnapcols
        f2.columns = snnapcols
    
    for f1,f2 in nrn_data.values():
        f1["t"] /= 1000
        f2["t"] /= 1000 
    
    # Create figure
    xlim = (0,75)
        
    fig = plt.figure(figsize=(25,10),constrained_layout=True)
    sfigs = fig.subfigures(2,2, width_ratios=(1.1,1),height_ratios=(2.5,1))
    ax1 = sfigs[0,0].subplots(num_cells,1,sharey=True)
    ax2 = sfigs[0,1].subplots(num_cells,1,sharey=True)
    ax3 = sfigs[1,0].subplots(2,1,sharey=True)
    ax4 = sfigs[1,1].subplots(2,1,sharey=True)

    plot_bmps(snnap_data["noisy"][1],ax1,all_cells, xlim,True,True)
    plot_bmps(nrn_data["noisy"][0],ax2,all_cells,xlim,False,False)

    sfigs[0,0].suptitle("SNNAP",fontsize=25)
    sfigs[0,1].suptitle("NEURON",fontsize=25)

    handles, labels = plt.gca().get_legend_handles_labels()
    extension = []
    for c, label in legend_labels.items():
        extension.append(Line2D([0], [0], label=label, color=c, linewidth=4))
    handles.extend(extension)

    fig.legend(handles=handles,loc='lower center',frameon=False,fancybox=False, 
            shadow=False,ncol=5,bbox_to_anchor=(0.5, -0.06),fontsize=20)

    plot_vertical_scalebar(ax2[-2],bar_width=0.3,yoffset=30,xoffset=0)

    times = (28,38) # B80
    cell = "B52" 
    
    first_spike = lambda v: np.where(np.diff(np.signbit(v)))[0][0]
    time_to_index  = lambda t,t0: np.argmin(np.abs(t-t0))
    irange = lambda t, v: slice(
        time_to_index(t, t[first_spike(v)] - 5),
        time_to_index(t, t[first_spike(v)] + 5)
    )

    traces_snnap = {}
    for k,(v1,v2) in snnap_data.items():
        mask1 = irange(v1["t"],v1[f"V_{cell}"])
        mask2 = irange(v2["t"],v2[f"V_{cell}"])
        traces_snnap.setdefault(k,{"t":[],"V": []})
        traces_snnap[k]["t"].append(v1["t"][mask1].to_numpy())
        traces_snnap[k]["t"].append(v2["t"][mask2].to_numpy())
        traces_snnap[k]["V"].append(v1[f"V_{cell}"][mask1].to_numpy())
        traces_snnap[k]["V"].append(v2[f"V_{cell}"][mask2].to_numpy())

    traces_nrn = {}
    for k,(v1,v2) in nrn_data.items():
        mask1 = irange(v1["t"],v1[f"V_{cell}"])
        mask2 = irange(v2["t"],v2[f"V_{cell}"])
        traces_nrn.setdefault(k,{"t":[],"V": []})
        traces_nrn[k]["t"].append(v1["t"][mask1].to_numpy())
        traces_nrn[k]["t"].append(v2["t"][mask2].to_numpy())
        traces_nrn[k]["V"].append(v1[f"V_{cell}"][mask1].to_numpy())
        traces_nrn[k]["V"].append(v2[f"V_{cell}"][mask2].to_numpy())
    
    bcolor1 = "black"
    bcolor2 = "forestgreen"

    ax3[0].plot(traces_snnap["clean"]["t"][0]-traces_snnap["clean"]["t"][0][0],traces_snnap["clean"]["V"][0],color=bcolor1)
    ax3[0].plot(traces_snnap["clean"]["t"][1]-traces_snnap["clean"]["t"][1][0],traces_snnap["clean"]["V"][1],color=bcolor2)
    ax3[1].plot(traces_snnap["noisy"]["t"][0]-traces_snnap["noisy"]["t"][0][0],traces_snnap["noisy"]["V"][0],color=bcolor1)
    ax3[1].plot(traces_snnap["noisy"]["t"][1]-traces_snnap["noisy"]["t"][1][0],traces_snnap["noisy"]["V"][1],color=bcolor2)

    ax4[0].plot(traces_nrn["clean"]["t"][0]-traces_nrn["clean"]["t"][0][0],traces_nrn["clean"]["V"][0],color=bcolor1)
    ax4[0].plot(traces_nrn["clean"]["t"][1]-traces_nrn["clean"]["t"][1][0],traces_nrn["clean"]["V"][1],color=bcolor2)
    ax4[1].plot(traces_nrn["noisy"]["t"][0]-traces_nrn["noisy"]["t"][0][0],traces_nrn["noisy"]["V"][0],color=bcolor1)
    ax4[1].plot(traces_nrn["noisy"]["t"][1]-traces_nrn["noisy"]["t"][1][0],traces_nrn["noisy"]["V"][1],color=bcolor2)

    for ax in ax4.flatten():
        ax.set_ylim(ax3[1].get_ylim())
    remove_axes(ax3[0])
    remove_axes(ax4[0])
    
    ax4[1].spines["top"].set_visible(False)
    ax4[1].spines["right"].set_visible(False)
    ax3[1].spines["top"].set_visible(False)
    ax3[1].spines["right"].set_visible(False)
    ax3[1].spines["bottom"].set_visible(False)
    ax4[1].spines["bottom"].set_visible(False)
    ax3[1].set_yticks([-50,0])
    ax3[1].set_xticks([])
    ax4[1].set_xticks([])

    plt.show() 
    fig.savefig(os.path.join(figpath,f"{fig_prefix}_full_network.png"), bbox_inches='tight', dpi=300)
