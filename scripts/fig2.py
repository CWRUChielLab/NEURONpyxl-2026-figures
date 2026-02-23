import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
from matplotlib.lines import Line2D
import argparse
from pathlib import Path
from neuronpyxl import Network
from utility import remove_axes

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
excelfile = "fig2.xlsx"

# Set up error variables
err_analytical = {"snnap": [], "nrn": []}
err_nrn_snnap = []
dt_list = np.array([0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001])

def get_v_nrn(tvec,dt):
    """Function to run a NEURON simulation using neuronpyxl.
    Runs the main.smu simulation from the spreadsheet with constant
    timestep dt.
    Interpolates to the provided time vector.
    """
    nw = Network(
        params_file=os.path.join(excelpath, excelfile),
        sim_name="main",
        noise=None,
        integrator=2,
        eq_time=0,
        dt=dt,
        atol=1e-5,
        simdur=9000,
        seed=False
    )
    nw.run()
    data = nw.get_interpolated_cell_data("cell",tvec)
    
    return np.array(data["V"])


def get_v_snnap(dt,snnap_datapath):
    """Function to read data from the SNNAP file
    in the snnap_datapath, corresponding to the given timestep dt.
    Data was pre-generated in snnap for this model for different timesteps.
    """

    # Get the data from the correct file
    data = pd.read_csv(os.path.join(snnap_datapath,f"fig2/data_{dt}.out"),\
                       sep="\t").dropna(axis=1).dropna(axis=0)
    data.columns = ["t", "V", "a", "b"]
    return data["t"].to_numpy(), data["V"].to_numpy()


def get_v_an(t, t0, tf, e0, i0, g, C):
    """Return the analytical solution of the voltage to the equation in the paper.
    """
    tau = C / g * 1000
    
    v = np.where(
        t <= t0, e0,
        np.where(t <= tf, e0 + i0 / g * (1 - np.exp(-(t - t0) / tau)),
                 e0 + i0 / g * np.exp(-(t - tf) / tau))
    )
    
    return v


def get_tvec(dt, simdur):
    return np.linspace(dt, simdur+dt)


def err(v1, v2):
    # Return the RMSE between 2 volage traces,
    # assuming they are recorded at the same time steps
    return np.sqrt(np.mean(np.power(v1-v2,2)))

    
def linearfit(x,y): # Basic linear regression
    slope, intercept,_,_,_ = linregress(x,y)
    print(slope)
    return slope*x+intercept

def run_simulations():
    args = parser.parse_args()
    snnap_path = args.snnap_data
    
    # Compute RMSE between snnap, neuron, and exact for different epochs
    for dt in dt_list:
        t_snnap, v_snnap = get_v_snnap(dt,snnap_path)
        v_nrn = get_v_nrn(t_snnap*1000,dt)
        v_an = get_v_an(t_snnap*1000, 2000, 7000, -60, 2, 0.1, 0.007)
        err_analytical["snnap"].append(err(v_snnap, v_an))
        err_analytical["nrn"].append(err(v_nrn, v_an))
        err_nrn_snnap.append(err(v_nrn, v_snnap))

    tvec = np.linspace(0,9000,num=10000)
    v_an = get_v_an(tvec, 2000, 7000, -60, 2, 0.1, 0.007)
    nw = Network(
        params_file=os.path.join(excelpath, excelfile),
        sim_name="main",
        noise=None,
        integrator=2,
        eq_time=0,
        dt=-1,
        atol=1e-6,
        simdur=9000,
        seed=False
    )
    nw.run(voltage_only=True)
    data = nw.get_interpolated_cell_data("cell",tvec)
    v_nrn_var = data["V"]
    err_var = err(v_an,v_nrn_var)
    print(f"Variable timestep error: {err_var}")

    # Plot snnap, nrn, and exact solution together
    t_snnap, v_snnap = get_v_snnap(0.1,snnap_path)
    v_nrn = get_v_nrn(t_snnap*1000,0.1)
    v_an = get_v_an(t_snnap*1000, 2000, 7000, -60, 2, 0.1, 0.007)

    return t_snnap,v_snnap,v_nrn,v_an

def plot(axs,t,v_snnap,v_nrn,v_an):
    lw = 3.0
    fontsize = 30
    labelsize = 22

    ax1,ax2 = axs
    ax1.plot(t,v_snnap,label="SNNAP",color="dodgerblue",linestyle="solid",linewidth=lw)
    ax1.plot(t,v_nrn,label="NEURON",color="orangered",linestyle="dashed",linewidth=lw)
    ax1.plot(t,v_an,label="Exact",color="teal",linestyle="dotted",linewidth=lw)
    
    ax1.set_xlabel("Time (s)",fontsize=fontsize)
    ax1.set_ylabel("Voltage (mV)",fontsize=fontsize)

    ax1.set_ylim((-63,-34))
    ax1.set_xticks([0,2,4,6,8])
    ax1.set_yticks([-60,-50,-40,-30])
    ax1.tick_params(axis="both",labelsize=labelsize)
    ax1.legend(loc="upper left",frameon=False,fontsize=labelsize)

    remove_axes(ax1)

    # Matplotlib style
    lw = 1.5
    ls = "dashed"
    m = "^"
    s = 100
    a = 1.0
    ec = "none"

    # Plot snnap, nrn, exact against each other for different epochs
    x = np.log10(dt_list)
    y_snnap = np.log10(err_analytical["snnap"])
    y_nrn = np.log10(err_analytical["nrn"])
    # y_nrn_snnap = np.log10(err_nrn_snnap)
    
    ax2.plot(x,linearfit(x,y_snnap),\
            linestyle=ls,color="dodgerblue",alpha=a,linewidth=lw
            )
    ax2.plot(x,linearfit(x,y_nrn),\
            linestyle=ls,color="red",alpha=a,linewidth=lw
            )

    ax2.scatter(x,y_snnap,
                c="dodgerblue",s=s,zorder=3,marker=m,\
                edgecolors=ec,alpha=a,label='SNNAP vs. Exact'
            )
    ax2.scatter(x,y_nrn,
                c="red",s=s,zorder=2,marker=m,\
                edgecolors=ec,alpha=a,label='NEURON vs. Exact'
            )

    ax2.set_xticks(
        [-3,-2,-1],
        [r"$10^{-3}$",r"$10^{-2}$",r"$10^{-1}$"]
    )
    ax2.set_yticks(
        [-2,-3,-4,-5,-6],
        [r"$10^{-2}$",r"$10^{-3}$",r"$10^{-4}$",r"$10^{-5}$",r"$10^{-6}$"]
    )
    ax2.tick_params(axis="both",labelsize=labelsize)

    # Add legend
    custom_line = Line2D([0], [0], color='black', linestyle='--',\
                         linewidth=2,label="Linear fit")
    ax2.legend(handles=plt.gca().get_legend_handles_labels()[0] + \
               [custom_line],loc="upper left",frameon=False,fontsize=fontsize)

    # Label axes
    ax2.set_ylabel("RMSE", fontsize=fontsize)
    ax2.set_xlabel("dt (ms)", fontsize=fontsize)
    
    remove_axes(ax2)
    

if __name__ == "__main__":
    t,v_snnap,v_nrn,v_an = run_simulations()
    fig, axs = plt.subplots(1,2,figsize=(14, 7),constrained_layout=True)
    plot(axs,t,v_snnap,v_nrn,v_an)
    fig.savefig(os.path.join(figpath,f"fig2.jpg"),bbox_inches="tight",dpi=300)