import xarray as xr
import pandas as pd
import numpy as np
import argparse
import tool_fig_config
import datetime
import wrf_load_helper
import wrf_preprocess 
import cmocean
from shared_constants import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

def relTimeInHrs(t):
    return (t - exp_beg_time.to_datetime64()) / np.timedelta64(1, 'h')

def horDecomp(da, name_m="mean", name_p="prime"):
    m = da.mean(dim="west_east").rename(name_m)
    p = (da - m).rename(name_p) 
    return m, p

def loadData(
    input_dir,
    avg_start_hours,
    hours_to_avg,
    wsm,
):

    print(f"Loading dir: {input_dir:s}, avg_start_hours = {avg_start_hours:d}, hours_to_avg = {hours_to_avg:d}")

    beg_time = wsm.start_datetime + pd.Timedelta(hours=avg_start_hours)
    end_time = beg_time + pd.Timedelta(hours=hours_to_avg)
    ds_nonavg = wrf_load_helper.loadWRFDataFromDir(
        wsm, 
        input_dir,
        beg_time = beg_time,
        end_time = end_time,
        prefix="wrfout_d01_",
        avg = None, #"ALL",
        verbose=False,
        inclusive="both",
    )
   
    ds_extra = wrf_preprocess.genBudgetAnalysis(ds_nonavg, wsm.data_interval)
    ds_extra = ds_extra.isel(time=slice(1, -1)).mean(dim="time")
    ds = wrf_load_helper.loadWRFDataFromDir(
        wsm, 
        input_dir,
        beg_time = beg_time,
        end_time = end_time,
        prefix="wrfout_d01_",
        avg = "ALL",
        verbose=False,
        inclusive="both",
    ).mean(dim="time")

    ds = xr.merge([ds, ds_extra]).mean(dim=["west_east", "west_east_stag", "south_north"])

    return ds

def plot_vertical_flux(
    data,
    output_file,
):
    cmap = plt.colormaps['viridis']
    N_cases = len(data)
    colors = cmap(np.linspace(0, 1, N_cases))

    ncol = 4
    nrow = 3

    w = [4,] * ncol
    h = [4,] * nrow

    figsize, gridspec_kw = tool_fig_config.calFigParams(
        w = w,
        h = h,
        wspace = 1.0,
        hspace = 1.0,
        w_left = 1.0,
        w_right = 1.0,
        h_bottom = 1.0,
        h_top = 1.0,
        ncol = ncol,
        nrow = nrow,
    )

    fig, ax = plt.subplots(
        nrow, ncol,
        figsize=figsize,
        subplot_kw=dict(aspect="auto"),
        gridspec_kw=gridspec_kw,
        constrained_layout=False,
        squeeze=False,
    )

    for i, (casename, ds) in enumerate(data.items()):
        
        color = colors[i]
        
        Z_W = ((ds["PHB"] + ds["PH"]) / 9.8).to_numpy()
        Z_T = (Z_W[1:] + Z_W[:-1])/2

        ax[0, 0].plot(ds["resolved_turbulent_flux_theta"], Z_T, '-', color=color, label="$\\overline{w'\\theta'}$")
        ax[0, 1].plot(ds["turbulent_flux_theta"], Z_W, '-', color=color, label="$\\overline{w'\\theta'}$ of %s" % (casename,))
        ax[0, 2].plot(ds["T"], Z_T, '-', color=color, label="$\\overline{w'\\theta'}$ of %s" % (casename,))
        ax[0, 2].set_xlim([-20, 0])
        
        #_ax.set_xlabel("[ $\\mathrm{K}$ ]")

        ax[1, 0].plot(ds["resolved_turbulent_flux_QVAPOR"], Z_T, '-', color=color, label="$\\overline{w'q'}$ of %s" % (casename,))
        ax[1, 1].plot(ds["turbulent_flux_QVAPOR"], Z_W, '--', color=color, label="$\\overline{w'q'}$")
        ax[1, 2].plot(ds["H_DIABATIC"], Z_T, '--', color=color, label="$H_{diab}$")
        #ax[1, 2].set_xlim([0.009, 0.010])
        #_ax.set_xlabel("[ $\\mathrm{K}$ ]")

        ax[2, 0].plot(ds["resolved_turbulent_flux_U"], Z_T, '-', color=color, label="$\\overline{w'q'}$ of %s" % (casename,))
        ax[2, 1].plot(ds["turbulent_flux_U"], Z_W, '--', color=color, label="$\\overline{w'u'}$")
        ax[2, 2].plot(ds["U"], Z_T, '--', color=color, label="$\\overline{w'u'}$")

        ax[2, 3].plot(ds["QKE"], Z_T, '-', color=color, label="QKE")
        #ax[2, 3].plot(ds["QBUOY"], Z_W, '-', color=color, label="QBUOY")
        #ax[2, 3].plot(ds["QWT"], Z_W, ':', color=color, label="QWT")
        #ax[2, 3].plot(ds["QSHEAR"], Z_W, '--', color=color, label="QSHEAR")
        #_ax.set_xlabel("[ $\\mathrm{K}$ ]")

 
        for _ax in ax.flatten(): 
            trans = transforms.blended_transform_factory(_ax.transAxes, _ax.transData)
            _ax.plot([0, 1], [ds["PBLH"].to_numpy()]*2, color=color, linestyle="--", transform=trans)

    for _ax in ax.flatten():

        _ax.set_ylim([0, 2000])
        _ax.set_ylabel("$z$ [ km ]")
        yticks = np.array(_ax.get_yticks())
        _ax.set_yticks(yticks, ["%.1f" % _y for _y in yticks/1e3])
        _ax.grid(visible=True, which='major', axis='both')
        _ax.legend()

    print("Save figure: ", str(output_file))
    fig.savefig(output_file, dpi=200)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input-dirs', type=str, nargs="+", help='Input directory.', required=True)
    parser.add_argument('--casenames', type=str, nargs="+", help='Input directory.', required=True)
    parser.add_argument('--avg-start-hours', type=int, nargs="+", help="The start of time ranges. It should match `--input-dirs`.", required=True)
    parser.add_argument('--hours-to-avg', type=int, help="Number of hours used to take average.", required=True)
    parser.add_argument('--exp-beg-time', type=str, help='analysis beg time', required=True)
    parser.add_argument('--wrfout-data-interval', type=int, help='Time interval between each adjacent record in wrfout files in seconds.', required=True)
    parser.add_argument('--frames-per-wrfout-file', type=int, help='Number of frames in each wrfout file.', required=True)
    parser.add_argument('--output-file', type=str, help='Output file name.', required=True)
    args = parser.parse_args()
    print(args)

    N_cases = len(args.input_dirs)
    assert len(args.casenames) == N_cases
    assert len(args.avg_start_hours) == N_cases

    wsm = wrf_load_helper.WRFSimMetadata(
        start_datetime  = pd.Timestamp(args.exp_beg_time),
        data_interval   = pd.Timedelta(seconds=args.wrfout_data_interval),
        frames_per_file = args.frames_per_wrfout_file,
    )

    data = { 
        _casename : loadData(_input_dir, _avg_start_hours, args.hours_to_avg, wsm=wsm)
        for _casename, _input_dir, _avg_start_hours in zip(args.casenames, args.input_dirs, args.avg_start_hours)
    }
    
    plot_vertical_flux(data, args.output_file)




