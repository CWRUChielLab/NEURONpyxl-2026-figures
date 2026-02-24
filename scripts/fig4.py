# To compile the mod files, run neuronpyxl -f gen_mods --file Excel_files/fig6.xlsx

import os
import matplotlib.pyplot as plt
import pandas as pd
from utility import remove_axes,plot_vertical_scalebar,add_snnap_path_arg
from neuronpyxl import Network
from neuron import h

parser = add_snnap_path_arg()

excelpath = "./sheets"
figpath = "./figs"
excelfile = "fig4.xlsx"
    
if __name__ == "__main__":
    args = parser.parse_args()
    snnapdatapath = os.path.join(args.snnap_data,"fig4")

    lw = 3
    fs = 22
    snnapcolor = "dodgerblue"
    nrncolor = "orangered"
    
    # Make two networks: one with hyperpolarizing and one with depolarizing current
    nw1 = Network(params_file=os.path.join(excelpath, excelfile),\
                          sim_name="synapse",noise=None,dt=-1,integrator=2,\
                          atol=1e-5,eq_time=1000,simdur=9000,seed=False)
    nw2 = Network(params_file=os.path.join(excelpath, excelfile),\
                          sim_name="depol",noise=None,dt=-1,integrator=2,\
                          atol=1e-5,eq_time=1000,simdur=9000,seed=False)
    # Run the simulations but only record the voltage
    nw1.run(voltage_only=True)
    nw2.run(voltage_only=True)

    nrn_data_hyp = (nw1.get_cell_data("A"),nw1.get_cell_data("B"))
    nrn_data_dep = (nw2.get_cell_data("A"),nw2.get_cell_data("B"))

    snnap_data_hyp = pd.read_csv(os.path.join(snnapdatapath,"synapse.smu.out"),header=None,sep="\t").drop(3,axis=1)
    snnap_data_hyp.columns = ["t","VA","VB"]
    snnap_data_hyp = snnap_data_hyp[snnap_data_hyp["t"] >= 1]
    snnap_data_hyp["t"] -= 1 # Adjust for 1 second relaxation of transient
    snnap_data_hyp = snnap_data_hyp[snnap_data_hyp["t"] <= 9]

    snnap_data_dep = pd.read_csv(os.path.join(snnapdatapath,"depol.smu.out"),header=None,sep="\t").drop(3,axis=1)
    snnap_data_dep.columns = ["t","VA","VB"]
    snnap_data_dep = snnap_data_dep[snnap_data_dep["t"] >= 1]
    snnap_data_dep["t"] -= 1 # Adjust for 1 second relaxation of transient
    snnap_data_dep = snnap_data_dep[snnap_data_dep["t"] <= 9]
    

    fig,(ax1,ax2) = plt.subplots(2,2,figsize=(12,8),height_ratios=(1,1))

    ax1[0].plot(nrn_data_hyp[0]["t"]/1000,nrn_data_hyp[0]["V"],\
                color=nrncolor,linestyle="solid",label="NEURON",linewidth=lw)
    ax1[0].plot(snnap_data_hyp["t"],snnap_data_hyp["VA"],\
                color=snnapcolor,linestyle="dashed",label="SNNAP",linewidth=lw) 
    ax1[0].set_ylim((-90,40))
    ax1[0].set_xlim((0,10))
    remove_axes(ax1[0],True,True)

    ax2[0].plot(nrn_data_hyp[1]["t"]/1000,nrn_data_hyp[1]["V"],\
                color=nrncolor,linestyle="solid",linewidth=lw)
    ax2[0].plot(snnap_data_hyp["t"],snnap_data_hyp["VB"],\
                color=snnapcolor,linestyle="dashed",linewidth=lw) 
    ax2[0].set_ylim((-90,40))
    ax2[0].set_xlabel("Time (s)", fontsize=fs)
    ax2[0].set_xlim((0,10))
    remove_axes(ax2[0],False,True)
    plot_vertical_scalebar(ax2[0],scalebar_length=20,bar_width=0.025,\
            xoffset=-0.1,yoffset=50,textoffset=0.1)

    ax1[1].plot(nrn_data_dep[0]["t"]/1000,nrn_data_dep[0]["V"],\
                color=nrncolor,linestyle="solid",label="NEURON",linewidth=lw)
    ax1[1].plot(snnap_data_dep["t"],snnap_data_dep["VA"],\
                color=snnapcolor,linestyle="dashed",label="SNNAP",linewidth=lw) 
    ax1[1].set_ylim((-90,40))
    ax1[1].set_xlim((0,10))
    remove_axes(ax1[1],True,True)
    ax1[1].legend(frameon=False,fontsize=20)


    ax2[1].plot(nrn_data_dep[1]["t"]/1000,nrn_data_dep[1]["V"],\
                color=nrncolor,linestyle="solid",linewidth=lw)
    ax2[1].plot(snnap_data_dep["t"],snnap_data_dep["VB"],\
                color=snnapcolor,linestyle="dashed",linewidth=lw) 
    ax2[1].set_ylim((-90,40))
    ax2[1].set_xlabel("Time (s)", fontsize=fs)
    ax2[1].set_xlim((0,10))
    remove_axes(ax2[1],False,True)

    fig.savefig(os.path.join(figpath,f"fig4.jpg"),bbox_inches="tight",dpi=300)
