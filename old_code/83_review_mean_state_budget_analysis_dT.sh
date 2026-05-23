#!/bin/bash

source 00_setup.sh


offset=$(( 24 * 10 ))
dhr=$(( 24*5 ))

for target_lab in lab_SIMPLE lab_FULL ; do
   
    dTs=()
    if [[ "$target_lab" =~ "FULL" ]]; then
        dTs=( 010 030 050 100 150 200 250 300 )
    elif [[ "$target_lab" =~ "SIMPLE" ]]; then
        dTs=( 100 150 200 250 300 )
    fi
 
    input_dirs=""
    hrs_beg=""
    casenames=""
    for U in 20 ; do
    for bl_scheme in MYNN25 ; do
    for wnm in 010 ; do

    for dT in "${dTs[@]}"; do
    #for dT in 050 100 200 300; do

        mph=""
        if [[ "$target_lab" =~ "FULL" ]]; then
            mph=on
        elif [[ "$target_lab" =~ "SIMPLE" ]]; then
            mph=off
        fi
        preavg_dir=$( gen_preavg_dir $U )
        input_dirs="$preavg_dir/$target_lab/case_mph-${mph}_wnm${wnm}_U${U}_dT${dT}_${bl_scheme} $input_dirs"
        casenames="\$\\Delta\\mathrm{SST}=$dT\\,\\mathrm{K}\$ $casenames"

        hrs_beg="$( printf "%03d" $(( $offset )) ) $hrs_beg"
    done
    done
    done
    done

    echo "Doing diagnostic simple"
    python3 src/plot_vertical_flux_profiles.py \
        --input-dirs $input_dirs          \
        --casenames $casenames            \
        --exp-beg-time "2001-01-01 00:00:00" \
        --wrfout-data-interval 3600          \
        --frames-per-wrfout-file 12          \
        --avg-start-hours ${hrs_beg[@]}      \
        --hours-to-avg $dhr                  \
        --output-file figures/mean_state_budget_analysis_varying-dSST-${target_lab}.svg

done


wait

echo "PLOTTING DONE."
