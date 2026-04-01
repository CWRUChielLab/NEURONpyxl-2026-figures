import numpy as np
import sys
import os
import pandas as pd
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import scienceplots
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D  # For legend
plt.style.use(["no-latex", "notebook"])
datapath = os.path.join(os.getcwd(),"Dickman_etal_2025_Figures/Data/fig12-13")
sys.path.append(datapath)
figpath = "./figs"
sys.path.append(figpath)
fig_prefix = "Dickman_etal_Results"
xfontsize = 30
yfontsize = 30
titlefont_size = 30
param1 = "vdg_g_B64s_kpp"
param2 = "cs_g_B30_B63_fast"
filename = "results.csv"
#####################################################################

chiel_data = pd.read_csv(os.path.join(datapath, "gillchiel_2020_data.csv"), header=[0,1,2])
bmp_dur = {"retraction": {"loaded":chiel_data[("loaded","retraction","dur")].mean(), \
                          "unloaded": chiel_data[("unloaded","retraction","dur")].mean()},\
           "protraction": {"loaded":chiel_data[("loaded","protraction","dur")].mean(), \
                           "unloaded": chiel_data[("unloaded","protraction","dur")].mean()}\
           }
print(bmp_dur)
def mindur(param1, param2, df, d1_col, d2_col, d1target, d2target):
    errors = np.sqrt((df[d1_col] - d1target) ** 2 + (df[d2_col] - d2target) ** 2)
    min_idx = errors.idxmin()  # Get index of minimum error
    row = df.iloc[min_idx]
    print(row)
    return {param1: row[param1], param2: row[param2]}

def get_params():
    # if speed == "fast":

    file = os.path.join(datapath, filename)
    df = pd.read_csv(file, header=0).dropna(axis=0) 
    d1target = bmp_dur["protraction"]["loaded"]*1000
    d2target = bmp_dur["retraction"]["loaded"]*1000
    md_loaded = mindur(param1, param2, df,"protraction","retraction",d1target,d2target)

    d1target = bmp_dur["protraction"]["unloaded"]*1000
    d2target = bmp_dur["retraction"]["unloaded"]*1000
    md_unloaded = mindur(param1, param2, df,"protraction","retraction",d1target,d2target)
    
    return {"loaded": md_loaded, "unloaded": md_unloaded}


params = get_params()
print(params)
file = os.path.join(datapath, filename)
df = pd.read_csv(file, header=0).dropna(axis=0)
df["protraction"] /= 1000
df["retraction"] /= 1000
df["std1"] /= 1000
df["std2"] /= 1000

df["cv1"] = df["std1"] / df["protraction"]
df["cv2"] = df["std2"] / df["retraction"]

def plot_ax(bmp, ax, sigma, delta, ylabel=True, contour=True,cv=False):
    xcol = param1
    ycol = param2
    
    # x = df[xcol].to_numpy()
    # y = df[ycol].to_numpy()
    # z = df[bmp].to_numpy()

    # if contour:
    #     vmax = max(max(df["protraction"]), max(df["retraction"]))
    #     vmin = min(min(df["protraction"]), min(df["retraction"]))
    # elif cv:
    #     vmax = max(max(df["cv1"]), max(df["cv2"]))
    #     vmin = max(min(df["cv1"]), min(df["cv2"]))
    # else:
    #     vmax = max(max(df["std1"]), max(df["std2"]))
    #     vmin = max(min(df["std1"]), min(df["std2"]))

    df_pivot = df.pivot_table(index=ycol, columns=xcol, values=bmp)
    mesh = ax.pcolormesh(df_pivot.columns, df_pivot.index, df_pivot.values,\
                         cmap="coolwarm", shading="auto",vmin=None,vmax=None)
    ax.set_title(bmp.capitalize(), fontsize=titlefont_size)
    
    ax.scatter([params["loaded"][xcol]], [params["loaded"][ycol]], marker="*", c="springgreen",\
               edgecolors="white", s=800, linewidths=1.5,alpha=1,zorder=2,label="Loaded")
    ax.scatter([params["unloaded"][xcol]], [params["unloaded"][ycol]], marker="*", c="magenta",\
            edgecolors="white", s=800, linewidths=1.5,alpha=1,zorder=2,label="Unloaded")
    return mesh

fig,axs = plt.subplots(1,2,figsize=(14,10), constrained_layout=True)

# PLOT BMP DURATIONS
pc11 = plot_ax("protraction", axs[0], 1.4, 0.2,True,True,False)
pc21 = plot_ax("retraction", axs[1], 1.5, 0.2, False,True,False)

axs[1].set_yticklabels([])

axs[0].set_ylabel(r"$\bar{g}$ of B30 to B63 connection ($\mu$S)")
# PLOT STANDARD ERRORS

error = "cv"
axs[0].set_xlabel(r"$\bar{g}$ of slow potassium in B64s ($\mu$S)",fontsize=xfontsize)
axs[0].set_ylabel(r"$\bar{g}$ of B30 to B63 connection ($\mu$S)",fontsize=xfontsize)
axs[1].set_xlabel(r"$\bar{g}$ of slow potassium in B64s ($\mu$S)",fontsize=xfontsize)
axs[0].tick_params(axis="x",labelsize=xfontsize)
axs[1].tick_params(axis="x",labelsize=xfontsize)
axs[0].tick_params(axis="y",labelsize=xfontsize)

orientation = "horizontal"
location = "bottom"
shrink = 0.7
c1 = fig.colorbar(pc11, ax=axs[0], shrink=shrink, location=location,\
               pad=0.05,orientation=orientation)
c2 = fig.colorbar(pc21, ax=axs[1], shrink=shrink, location=location,\
        pad=0.05,orientation=orientation)
c1.ax.tick_params(labelsize=22)
c2.ax.tick_params(labelsize=22)
c1.set_label("Phase duration (s)", fontsize=30)
c2.set_label("Phase duration (s)", fontsize=30)
# legend_labels = ["Loaded", "Unloaded"]
plt.legend(fontsize=30)

for ax_group in [axs]:
    for ax in ax_group:
        ax.set(adjustable='box', aspect=1.0/ax.get_data_ratio())
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.0005, hspace=0)
plt.show()
fig.savefig(os.path.join(figpath,f"{fig_prefix}_heatmap2.jpg"),bbox_inches="tight",dpi=300)
