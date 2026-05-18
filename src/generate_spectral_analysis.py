import xarray as xr
import pandas as pd
import numpy as np
import argparse
import tool_fig_config
import wrf_load_helper 
import datetime
import os
from pathlib import Path

plot_infos = dict(

    SST = dict(
        selector = None,
        wrf_varname = "TSK",
        unit = "K",
    ), 


    TA = dict(
        selector = dict(bottom_top=0),
        wrf_varname = "T",
        label = "$\\Theta_{A}$",
        unit = "K",
    ), 

    TOA = dict(
        wrf_varname = "TOA",
        label = "$\\Theta_{OA}$",
        unit = "K",
    ), 

    QOA = dict(
        wrf_varname = "QOA",
        label = "$Q_{OA}$",
        unit = "g / kg",
    ), 

    CH = dict(
        wrf_varname = "CH",
        label = "$C_{H}$",
    ), 

    CQ = dict(
        wrf_varname = "CQ",
        label = "$C_{Q}$",
    ), 

    UA = dict(
        selector = dict(bottom_top=0),
        wrf_varname = "U",
        label = "$u_{A}$",
        unit = "$ \\mathrm{m} \\, / \\, \\mathrm{s}$",
    ), 

    VA = dict(
        selector = dict(bottom_top=0),
        wrf_varname = "V",
        label = "$v_{A}$",
        unit = "$ \\mathrm{m} \\, / \\, \\mathrm{s}$",
    ), 



)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--labels', type=str, nargs="+", help='Input directories.', required=True)
    parser.add_argument('--input-dirs', type=str, nargs="+", help='Input directories.', required=True)
    parser.add_argument('--input-dirs-base', type=str, nargs="+", help='Input directories.', required=True)
    parser.add_argument('--output', type=str, help='Output filename in png.', required=True)
    parser.add_argument('--no-display', action="store_true")
    parser.add_argument('--time-rng', type=int, nargs=2, help="Time range in hours after --exp-beg-time", required=True)
    parser.add_argument('--exp-beg-time', type=str, help='analysis beg time', required=True)
    parser.add_argument('--wrfout-data-interval', type=int, help='Time interval between each adjacent record in wrfout files in seconds.', required=True)
    parser.add_argument('--frames-per-wrfout-file', type=int, help='Number of frames in each wrfout file.', required=True)
    parser.add_argument('--number-of-harmonics', type=int, help='Number of frames in each wrfout file.', default=None)
    parser.add_argument('--varnames', type=str, nargs="+", help="Varnames to do the analysis.", required=True)
    parser.add_argument('--wrfout-suffix', type=str, default="")
    parser.add_argument('--magnitude-threshold', type=float, help='The threshold that set direction=0 if magnitude is too low.', default=1e-5)

    args = parser.parse_args()
    print(args)
    labels = args.labels
    if labels is None:
        labels = [ "%d" % i for i in range(len(args.input_dirs)) ]
        
    elif len(labels) != len(args.input_dirs):
        raise Exception("Length of `--labels` (%d) does not equal to length of `--input-dirs` (%d). " % (
            len(labels),
            len(args.input_dirs),
        ))

    same_base = False
    if len(args.input_dirs_base) == 1:
       
        args.input_dirs_base = [ args.input_dirs_base[0] ] * len(args.input_dirs) 


    if np.all( [ input_dir_base == args.input_dirs_base[0] for input_dir_base in args.input_dirs_base  ] ):
        same_base = True
        print("# same_base = ", same_base)


    if len(args.input_dirs_base) != len(args.input_dirs):
        
        raise Exception("Length of `--input-dirs-base` (%d) does not equal to length of `--input-dirs` (%d). " % (
            len(args.input_dirs_base),
            len(args.input_dirs),
        ))

 
    exp_beg_time = pd.Timestamp(args.exp_beg_time)
    wrfout_data_interval = pd.Timedelta(seconds=args.wrfout_data_interval)
    time_beg = exp_beg_time + pd.Timedelta(hours=args.time_rng[0])
    time_end = exp_beg_time + pd.Timedelta(hours=args.time_rng[1])

    wsm = wrf_load_helper.WRFSimMetadata(
        start_datetime  = exp_beg_time,
        data_interval   = wrfout_data_interval,
        frames_per_file = args.frames_per_wrfout_file,
    )
    
    # Loading     
                
   
    data = []
    for i in range(len(args.input_dirs)):
        input_dir_base = args.input_dirs_base[i] 
        input_dir      = args.input_dirs[i]
        label = args.labels[i] 
        print("Loading base wrf dir: %s" % (input_dir_base,))
        if i == 0 or not same_base:
            ds_base = wrf_load_helper.loadWRFDataFromDir(
                wsm, 
                input_dir_base,
                beg_time = time_beg,
                end_time = time_end,
                suffix=args.wrfout_suffix,
                avg="ALL",
                verbose=False,
                inclusive="left",
            ).isel(time=0)


        Nx = len(ds_base.coords["west_east"])
        X_sU = ds_base.DX * np.arange(Nx+1)
        X_sT = (X_sU[1:] + X_sU[:-1]) / 2
        freq = np.fft.fftfreq(Nx, d=ds_base.DX)

        freq_N = Nx // 2
         
     
        print("Loading the %d-th wrf dir: %s" % (i, input_dir,))
        ds = wrf_load_helper.loadWRFDataFromDir(
            wsm, 
            input_dir,
            beg_time = time_beg,
            end_time = time_end,
            suffix=args.wrfout_suffix,
            avg="ALL",
            verbose=False,
            inclusive="left",
        ).isel(time=0)
        
        ds_each_case = []

        for varname in args.varnames + ["SST",]:
            plot_info=plot_infos[varname]
            selector = plot_info["selector"] if "selector" in plot_info else None
            wrf_varname = plot_info["wrf_varname"] if "wrf_varname" in plot_info else varname
            
            da_base = ds_base[wrf_varname]
            da = ds[wrf_varname]
            
            
            if selector is not None:
                da_base = da_base.isel(**selector)
                da      = da.isel(**selector)
             
            if "south_north" in da.dims:
                da = da.isel(south_north=0)
                da_base = da_base.isel(south_north=0)
            
            elif "south_north_stag" in da.dims:
                da = da.isel(south_north_stag=0)
                da_base = da_base.isel(south_north_stag=0)
            
            dvar = da - da_base
            dvar = dvar.to_numpy()
            
            if varname == "UA":
                dvar = ( dvar[1:] + dvar[:-1] ) / 2
            
            # Compute transfer function
            sp = np.fft.fft(dvar) / Nx
            mag = np.abs(sp)
            ang = np.angle(sp, deg=True)
            ang[mag < args.magnitude_threshold] = 0.0
            
            _data = np.stack([mag, ang])[None, :, :]
            ds_each_case.append(xr.DataArray(
                name=varname,
                data=_data,
                dims=["ens", "fourier_component", "harmonic"],
                coords=dict(
                    ens=[label,],
                    fourier_component=["mag", "ang"],
                    harmonic=np.arange(len(sp)),
                ),
            ))
        
        print(xr.merge(ds_each_case))
        data.append(xr.merge(ds_each_case))

    data = xr.merge(data)

    output_file = Path(args.output)
    output_file.parent.mkdir(exist_ok=True, parents=True)    
    print(f"Output file to: {str(output_file)}")
    data.to_netcdf(output_file)
