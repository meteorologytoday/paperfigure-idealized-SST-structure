#!/bin/bash

source 00_setup.sh


offset=$(( 24 * 10 ))
dhr=$(( 12 ))

for U in 15 ; do
for bl_scheme in MYNN25 ; do
for wnm in 010 ; do
for dT in 100 ; do

    preavg_dir=$( gen_preavg_dir $U )
    input_dir=$preavg_dir/lab_FULL/case_mph-on_wnm${wnm}_U${U}_dT${dT}_${bl_scheme}

    hrs_beg=$( printf "%03d" $(( $offset )) )
    hrs_end=$( printf "%03d" $(( $offset + $dhr )) )

    echo "Doing diagnostic simple"
    python3 src/compute_mean_state_budget.py \
        --input-dir "$input_dir"      \
        --exp-beg-time "2001-01-01 00:00:00" \
        --wrfout-data-interval 3600          \
        --frames-per-wrfout-file 12          \
        --time-rng $hrs_beg $hrs_end

done
done
done
done

wait

echo "PLOTTING DONE."
