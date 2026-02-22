# To compile the mod files, run neuronpyxl -f gen_mods --file Excel_files/fig6.xlsx

import sys
import os
sys.path.append("../")
import scienceplots
import pandas as pd
import matplotlib.pyplot as plt
from neuronpyxl import network
plt.style.use(["no-latex", "notebook"])

snnapdatapath = "/media/uri/uri-external-drive/SNNAP_data/fig6"
excelpath = "./Excel_files"
figpath = "./figs"
fig_prefix = "Dickman_etal_Results"
excelfile = "fig6.xlsx"

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
        
def plot_vertical_scalebar(ax,scalebar_length=20,bar_width=0.25,xoffset=1,yoffset=10):
    from matplotlib.patches import Rectangle
    # Get axis limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Coordinates for bottom-right corner
    x_start = xlim[1] - bar_width - xoffset
    y_start = ylim[0] + yoffset

    scalebar = Rectangle((x_start, y_start), width=bar_width, height=scalebar_length,
                        color='black', linewidth=0, zorder=10)

    ax.add_patch(scalebar)

    # Optional: Add text label
    ax.text(x_start-xoffset, y_start + scalebar_length / 2, f'{scalebar_length} mV',
            va='center', ha='right', color='black', fontsize=16)
    
if __name__ == "__main__":

    lw = 3
    fs = 30
    
    nw1 = network.Network(params_file=os.path.join(excelpath, excelfile),\
                          sim_name="synapse",noise=None,dt=-1,integrator=2,\
                          atol=1e-5,eq_time=1000,simdur=9000,seed=False)
    nw2 = network.Network(params_file=os.path.join(excelpath, excelfile),\
                          sim_name="depol",noise=None,dt=-1,integrator=2,\
                          atol=1e-5,eq_time=1000,simdur=9000,seed=False)
    nw1.run(voltage_only=True)
    nw2.run(voltage_only=True)

    data1 = (nw1.get_cell_data("A"),nw1.get_cell_data("B"))
    data2 = (nw2.get_cell_data("A"),nw2.get_cell_data("B"))

    snnap_data = pd.read_csv(os.path.join(snnapdatapath,"synapse.smu.out"),header=None,sep="\t").drop(3,axis=1)
    snnap_data.columns = ["t","VA","VB"]
    snnap_data = snnap_data[snnap_data["t"] >= 1]
    snnap_data["t"] -= 1
    snnap_data = snnap_data[snnap_data["t"] <= 9]

    snnap_data2 = pd.read_csv(os.path.join(snnapdatapath,"depol.smu.out"),header=None,sep="\t").drop(3,axis=1)
    snnap_data2.columns = ["t","VA","VB"]
    snnap_data2 = snnap_data2[snnap_data2["t"] >= 1]
    snnap_data2["t"] -= 1
    snnap_data2 = snnap_data2[snnap_data2["t"] <= 9]

    snnapcolor = "dodgerblue"
    nrncolor = "orangered"

    fig,(ax1,ax2) = plt.subplots(2,2,figsize=(12,8),height_ratios=(1,1))

    ax1[0].plot(data1[0]["t"]/1000,data1[0]["V"],color=nrncolor,linestyle="solid",label="NEURON",linewidth=lw)
    ax1[0].plot(snnap_data["t"],snnap_data["VA"],color=snnapcolor,linestyle="dashed",label="SNNAP",linewidth=lw) 
    ax1[0].set_ylim((-90,40))
    ax1[0].set_xlim((0,10))
    # ax1.set_ylabel("Neuron A",rotation=0,fontsize=20)
    remove_axes(ax1[0],True,True)
    #ax1[0].legend(frameon=False,fontsize=20)


    ax2[0].plot(data1[1]["t"]/1000,data1[1]["V"],color=nrncolor,linestyle="solid",linewidth=lw)
    ax2[0].plot(snnap_data["t"],snnap_data["VB"],color=snnapcolor,linestyle="dashed",linewidth=lw) 
    ax2[0].set_ylim((-90,40))
    # ax2.set_ylabel("Neuron B",rotation=0,fontsize=20)
    ax2[0].set_xlabel("Time (s)", fontsize=fs)
    ax2[0].set_xlim((0,10))
    ax2[0].set_xticks([0,0.5])
    remove_axes(ax2[0],False,True)
    plot_vertical_scalebar(ax2[0],scalebar_length=20,bar_width=0.025,\
            xoffset=0.1,yoffset=50)
                           #plot_vertical_scalebar(ax2)

    ax1[1].plot(data2[0]["t"]/1000,data2[0]["V"],color=nrncolor,linestyle="solid",label="NEURON",linewidth=lw)
    ax1[1].plot(snnap_data2["t"],snnap_data2["VA"],color=snnapcolor,linestyle="dashed",label="SNNAP",linewidth=lw) 
    ax1[1].set_ylim((-90,40))
    ax1[1].set_xlim((0,10))
    # ax1.set_ylabel("Neuron A",rotation=0,fontsize=20)
    remove_axes(ax1[1],True,True)
    ax1[1].legend(frameon=False,fontsize=20)


    ax2[1].plot(data2[1]["t"]/1000,data2[1]["V"],color=nrncolor,linestyle="solid",linewidth=lw)
    ax2[1].plot(snnap_data2["t"],snnap_data2["VB"],color=snnapcolor,linestyle="dashed",linewidth=lw) 
    ax2[1].set_ylim((-90,40))
    # ax2.set_ylabel("Neuron B",rotation=0,fontsize=20)
    ax2[1].set_xlabel("Time (s)", fontsize=fs)
    ax2[1].set_xlim((0,10))
    ax2[1].set_xticks([0,0.5])
    remove_axes(ax2[1],False,True)
    plt.show() 
    fig.savefig(os.path.join(figpath,f"{fig_prefix}_es.jpg"),bbox_inches="tight",dpi=300)
