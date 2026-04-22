import xarray as xr
import pandas as pd
import numpy as np
import argparse
import tool_fig_config
import wrf_load_helper 
import datetime
import os
import wrf_preprocess

def genBudgetAnalysis(
    ds,
    data_interval,
):
   
    print(ds)
    print(data_interval)
    ds = ds.mean(dim="south_north")
 
    Nx = ds.dims['west_east']
    Nz = ds.dims['bottom_top']

    Z_W = ( (ds.PHB + ds.PH) / 9.81 ).to_numpy()
    Z_T = ds["T"].copy().rename("Z_T")
    Z_T.data[:] = (Z_W[:, 1:, :] + Z_W[:, :-1, :]) / 2

    dZ_T = Z_W[:, 1:, :] - Z_W[:, :-1, :]    

    dZ_W = np.zeros_like(ds["PH"])
    dZ_Wm2 = ( dZ_T[:, 1:, :] + dZ_T[:, :-1, :] ) / 2
    dZ_W[:, 0, :] = np.inf
    dZ_W[:, -1, :] = np.inf
    dZ_W[:, 1:-1, :] = dZ_Wm2
    
    def ddz_T_to_W(a_T):
        dadz_Wm2 = (a_T[:, 1:, :] - a_T[:, :-1, :]) / dZ_Wm2
        print(dadz_Wm2.shape)
        return np.pad(dadz_Wm2, ((0,0), (1,1), (0,0)), mode="constant", constant_values=0)

    def ddz_W_to_T(a_W):
        dadz_T = (a_W[:, 1:, :] - a_W[:, :-1, :]) / dZ_T
        return dadz_T 
    
    # Compute gradient of temperature on W grid
    dthetadz = ddz_T_to_W(ds["T"].to_numpy())
    
    # Compute temperature flux on W grid
    print("Shape of dthetadz: ", dthetadz.shape)
    print("Shape of EXCH_H: ", ds["EXCH_H"].to_numpy().shape)
    theta_turbulent_flux = dthetadz * ds["EXCH_H"].to_numpy()
    
    # Compute flux convergence
    tendency_convergence_of_theta_turbulent_flux = - ddz_W_to_T(theta_turbulent_flux)
    
    # Compute change of temperature in time
    theta = ds["T"].to_numpy()
    tendency_potential_temperature = (theta[2:, :, :] - theta[:-2]) / data_interval.total_seconds()
    tendency_potential_temperature = np.pad(tendency_potential_temperature, ((1,1), (0, 0), (0,0)), mode="constant", constant_values=0)
    
    
    # Convert into DataArrays
    da_tendency_convergence_of_theta_turbulent_flux = xr.zeros_like(ds["T"]).rename("tendency_convergence_of_theta_turbulent_flux").load()
    da_tendency_convergence_of_theta_turbulent_flux.values[:, :, :] = tendency_convergence_of_theta_turbulent_flux 
    
    da_tendency_potential_temperature = xr.zeros_like(ds["T"]).rename("tendency_potential_temperature").load()
    da_tendency_potential_temperature.values[:, :, :] = tendency_potential_temperature
    ds = xr.merge([
        da_tendency_convergence_of_theta_turbulent_flux,
        da_tendency_potential_temperature,
    ])

    return ds

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input-dir', type=str, help='Input directory.', required=True)
    parser.add_argument('--time-rng', type=int, nargs=2, help="Time range in hours after --exp-beg-time", required=True)
    parser.add_argument('--exp-beg-time', type=str, help='analysis beg time', required=True)
    parser.add_argument('--wrfout-data-interval', type=int, help='Time interval between each adjacent record in wrfout files in seconds.', required=True)
    parser.add_argument('--frames-per-wrfout-file', type=int, help='Number of frames in each wrfout file.', required=True)
    parser.add_argument('--wrfout-suffix', type=str, default="")
    args = parser.parse_args()

    print(args)

    exp_beg_time = pd.Timestamp(args.exp_beg_time)
    wrfout_data_interval = pd.Timedelta(seconds=args.wrfout_data_interval)
    time_beg = exp_beg_time + pd.Timedelta(hours=args.time_rng[0])
    time_end = exp_beg_time + pd.Timedelta(hours=args.time_rng[1])
    wsm = wrf_load_helper.WRFSimMetadata(
        start_datetime  = exp_beg_time,
        data_interval   = wrfout_data_interval,
        frames_per_file = args.frames_per_wrfout_file,
    )
    
    print("Loading wrf dir: %s" % (args.input_dir,))
    ds = wrf_load_helper.loadWRFDataFromDir(
        wsm, 
        args.input_dir,
        beg_time = time_beg,
        end_time = time_end,
        suffix=args.wrfout_suffix,
        avg=None,
        verbose=False,
        inclusive="left",
    )

    DX = ds.attrs["DX"]

    ds = xr.merge([
        #ds,
        genBudgetAnalysis(ds, wsm.data_interval),
    ])#.mean(dim="time")

    Nx = len(ds.coords["west_east"])
    Lx = DX * Nx
    X_sU = DX * np.arange(Nx+1)
    X_sT = (X_sU[1:] + X_sU[:-1]) / 2


    print("Result: ", ds)

    ds.mean(dim="west_east").to_netcdf("TEST.nc")

"""
def genBudgetAnalysis(
    ds,
    data_interval,
):
    
    ref_ds = ds.mean(dim=['time'], keep_attrs=True)
    Nx = ref_ds.dims['west_east']
    Nz = ref_ds.dims['bottom_top']

    X_sU = ds.DX * np.arange(Nx+1) / 1e3
    X_sT = (X_sU[1:] + X_sU[:-1]) / 2
    X_T = np.repeat(np.reshape(X_sT, (1, -1)), [Nz,], axis=0)
    X_W = np.repeat(np.reshape(X_sT, (1, -1)), [Nz+1,], axis=0)
    dX_sT = ds.DX * np.arange(Nx)

    Z_W = ( (ds.PHB + ds.PH) / 9.81 ).to_numpy()
    Z_T = ds["T"].copy().rename("Z_T")
    Z_T.data[:] = (Z_W[:, 1:, :] + Z_W[:, :-1, :]) / 2

    dZ_T = ds["T"].copy().rename("dZ_T")
    dZ_T.data[:] = Z_W[:, 1:, :] - Z_W[:, :-1, :]    


    dZ_U = np.zeros_like(ds["U"])
    dZ_U[:, :, :-1] = ( (dZ_T + dZ_T.roll(west_east=1)) / 2 ).to_numpy()
    dZ_U[:, :, -1] = dZ_U[:, :, 0]

    dZ_UW = (dZ_U[:, 1:, :] + dZ_U[:, :-1, :]) / 2 

    ds = ds.assign_coords(dict(
        west_east = X_sT, 
        west_east_stag = X_sU,
    ))

    merge_data = []

    W = ds["W"].to_numpy()
    dWdx_UW = (ds["W"] - ds["W"].roll(west_east=1)) / (2 * ds.DX)
    dWdx_UW = dWdx_UW.to_numpy() # Notice this UW grid miss the right most U
   
    dUdz_UW = (U[:, 1:, :] - U[:, :-1, :]) / dZ_UW
   
    print(dWdx_UW.shape) 
    print(dUdz_UW.shape) 
    DEFO_term_tmp = - dWdx_UW[:, 1:-1, :] * dUdz_UW[:, :, :-1]
    DEFO_term_tmp = (DEFO_term_tmp + np.roll(DEFO_term_tmp, -1, axis=2)) / 2
    DEFO_term_tmp = (DEFO_term_tmp[:, 1:, :] + DEFO_term_tmp[:, :-1, :]) / 2
    
    DEFO_term = xr.zeros_like(ds["T"]).rename("DEFO_term")
    DEFO_term[:, 1:-1, :] = DEFO_term_tmp
 
    # DIV cont
    DIV_term = - DIV**2
    DIV_term = DIV_term.rename("DIV_term")
 
    # Vorticity term
    VOR = xr.zeros_like(ds["T"]).rename("VOR")
    tmp = ( ds["V"] - ds["V"].roll(west_east=1) ) / ds.DX
    tmp = (tmp.roll(west_east=-1) + tmp ) / 2.0
    VOR.data[:] = tmp[:]

    VOR_term = f0 * VOR
    VOR_term = VOR_term.rename("VOR_term")
   
    # P laplacian
    p = ds["PB"] + ds["P"]
    LAP_p = ( p.roll(west_east=-1) + p.roll(west_east=1) - 2 * p ) / ds.DX**2
    BPG_term = - LAP_p / RHO
    BPG_term = BPG_term.rename("BPG_term")

    # Vertical mixing

    U = ds["U"].to_numpy()
    dUdz_UW = (U[:, 1:, :] - U[:, :-1, :]) / dZ_UW
    dUdz_UW = np.pad(dUdz_UW, ((0, 0), (1, 1,), (0, 0)), mode='constant', constant_values=0)
    dUdz_W = (dUdz_UW[:, :, 1: ] + dUdz_UW[:, :,:-1] ) / 2

    mom_flux = - ds["EXCH_M"].to_numpy() * dUdz_W
    MFLUX_CVG = - ( mom_flux[:, 1:, :] - mom_flux[:, :-1, :] )  / dZ_T.to_numpy()
    
    VM_term = xr.zeros_like(ds["T"]).rename("VM_term")
    VM_term.data[:] = MFLUX_CVG
    VM_term = ( VM_term.roll(west_east=-1) - VM_term.roll(west_east=1) ) / (2 * ds.DX  )

    VM_term_indirect = dDIVdt_est - DIV_term - BPG_term - VOR_term - DEFO_term
    VM_term_indirect = VM_term_indirect.rename("VM_term_indirect")


    dDIVdt = DIV_term + BPG_term + VOR_term + DEFO_term + VM_term
    dDIVdt = dDIVdt.rename("dDIVdt")
 
    merge_data.append(DIV)
    merge_data.append(dDIVdt)
    merge_data.append(dDIVdt_est)
    merge_data.append(DEFO_term)
    merge_data.append(VOR_term)
    merge_data.append(DIV_term)
    merge_data.append(BPG_term)
    merge_data.append(VM_term)
    merge_data.append(VM_term_indirect)
    merge_data.append(Z_T.rename("Z_T"))

    new_ds = xr.merge(merge_data)

    return new_ds

"""



