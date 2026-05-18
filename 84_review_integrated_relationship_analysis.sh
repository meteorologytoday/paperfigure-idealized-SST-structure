#!/bin/bash

source 00_setup.sh


offset=$(( 24 * 10 ))
dhr=$(( 24*5 ))

for bl_scheme in MYJ MYNN25 YSU ; do
for target_lab in lab_FULL lab_SIMPLE ; do

    input_dirs=""
    hrs_beg=""
    casenames=""
    ensemble_values=""
    for U in 20 ; do
    for wnm in 040 020 010 007 005 004 ; do
    for dT in 100 ; do

        mph=""
        if [[ "$target_lab" =~ "FULL" ]]; then
            mph=on
        elif [[ "$target_lab" =~ "SIMPLE" ]]; then
            mph=off
        fi
        L=$(( $Lx / 10#$wnm ))
        preavg_dir=$( gen_preavg_dir $U )
        input_dirs="$preavg_dir/$target_lab/case_mph-${mph}_wnm${wnm}_U${U}_dT${dT}_${bl_scheme} $input_dirs"
        casenames="'\$L=$L\\mathrm{km}\$' $casenames"
        ensemble_values="$L $ensemble_values"
        hrs_beg="$( printf "%03d" $(( $offset )) ) $hrs_beg"
    done
    done
    done


    echo "Doing diagnostic simple"
    python3 src/plot_integrated_relationship.py \
        --input-dirs $input_dirs          \
        --casenames $casenames            \
        --ensemble-values $ensemble_values   \
        --ensemble-label '$L$ [ km ]'        \
        --exp-beg-time "2001-01-01 00:00:00" \
        --wrfout-data-interval 3600          \
        --frames-per-wrfout-file 12          \
        --avg-start-hours ${hrs_beg[@]}           \
        --hours-to-avg $dhr                  \
        --output-file figures/integrated_relationship/integrated_relationship-varying-L-${bl_scheme}_${target_lab}.svg


done
done
wait

echo "PLOTTING DONE."
