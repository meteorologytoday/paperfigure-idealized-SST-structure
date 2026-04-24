#!/bin/bash

source 00_setup.sh


offset=$(( 24 * 10 ))
dhr=$(( 24*5 ))

input_dirs=""
hrs_beg=""
for U in 20 ; do
for bl_scheme in MYNN25 ; do
for wnm in 020 004 ; do
for dT in 100 ; do

    preavg_dir=$( gen_preavg_dir $U )
    input_dirs="$preavg_dir/lab_FULL/case_mph-on_wnm${wnm}_U${U}_dT${dT}_${bl_scheme} $input_dirs"

    hrs_beg="$( printf "%03d" $(( $offset )) ) $hrs_beg"

done
done
done
done

echo "Doing diagnostic simple"
python3 src/plot_vertical_flux_profiles.py \
    --input-dirs $input_dirs[@]      \
    --exp-beg-time "2001-01-01 00:00:00" \
    --wrfout-data-interval 3600          \
    --frames-per-wrfout-file 12          \
    --avg-start-hours ${hrs_beg[@]}           \
    --hours-to-avg $dhr                  \
    --no-display                         \
    --output-file figures/test.svg


wait

echo "PLOTTING DONE."
