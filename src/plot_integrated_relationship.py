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
    ensemble_value,
    input_dir,
    avg_start_hours,
    hours_to_avg,
    wsm,
):

    print(f"Loading dir: {input_dir:s}, avg_start_hours = {avg_start_hours:d}, hours_to_avg = {hours_to_avg:d}")

    beg_time = wsm.start_datetime + pd.Timedelta(hours=avg_start_hours)
    end_time = beg_time + pd.Timedelta(hours=hours_to_avg)
    ds = wrf_load_helper.loadWRFDataFromDir(
        wsm, 
        input_dir,
        beg_time = beg_time,
        end_time = end_time,
        prefix="wrfout_d01_",
        avg = None, #"ALL",
        verbose=False,
        inclusive="both",
    )
   
    ds_extra = wrf_preprocess.genTKEBudget(ds, integrate_threshold=1000).rolling(time=25).mean()
    ds = ds["PBLH"]]
    ds = xr.merge([ds_nonavg, ds_extra]).mean(dim=["west_east", "south_north"])
    #ds = xr.merge([ds, ds_extra]).mean(dim=["west_east", "west_east_stag", "south_north"])
    #ds = ds_extra
    ds = ds.expand_dims(ensemble=[ensemble_value,])
    return ds

def plot(
    ds,
    output_file,
):

    plotting_variables = [
        (["N2"], "total"),
        (["PBLH"], "total"),
        (["near_surface_QKE"], "total"),
        ([f"near_surface_{v}" for v in ["DTKE", "QBUOY", "QSHEAR", "QDISS", "QWT"]], "remove_mean"),
    ]

    ncol = len(plotting_variables)
    nrow = 1
    
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
   
    for i, (varnames, policy) in enumerate(plotting_variables):
   
        for varname in varnames: 
            da = ds[varname]
            offset = 0.0
            if policy == "total":
                pass
            elif policy == "remove_mean":
                offset = - da.mean()
            else:
                raise Exception(f"Unknown Policy: {str(policy)}")

            print("da.std = ", da.std(dim="time"))

            ax[0,i].errorbar(
                ds.coords["ensemble"],
                da.mean(dim="time") + offset,
                yerr=da.std(dim="time"),
                fmt='o-',
                markersize=6,
                capsize=5,
                linewidth=1.5, elinewidth=1.5, label=varname
            )

    for _ax in ax.flatten():
        _ax.grid(visible=True, which='major', axis='both')
        _ax.legend()

    print("Save figure: ", str(output_file))
    fig.savefig(output_file, dpi=200)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input-dirs', type=str, nargs="+", help='Input directory.', required=True)
    parser.add_argument('--casenames', type=str, nargs="+", help='Input directory.', required=True)
    parser.add_argument('--ensemble-values', type=float, nargs="+", help='Input directory.', required=True)
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
    assert len(args.ensemble_values) == N_cases

    wsm = wrf_load_helper.WRFSimMetadata(
        start_datetime  = pd.Timestamp(args.exp_beg_time),
        data_interval   = pd.Timedelta(seconds=args.wrfout_data_interval),
        frames_per_file = args.frames_per_wrfout_file,
    )

    data = xr.merge([ 
        loadData(_ensemble_value, _input_dir, _avg_start_hours, args.hours_to_avg, wsm=wsm)
        for _ensemble_value, _casename, _input_dir, _avg_start_hours in zip(args.ensemble_values, args.casenames, args.input_dirs, args.avg_start_hours)
    ])
    
    plot(data, args.output_file)




