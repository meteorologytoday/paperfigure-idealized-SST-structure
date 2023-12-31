#!/bin/bash

source 00_setup.sh

mkdir -p $fig_dir

plot_codes=(
    $sh 11_plot_ocean_SST_anaylsis.sh "BLANK"
    $sh 12_plot_sounding.sh "BLANK"
    $sh 13_plot_snapshot.sh "BLANK"
    $sh 14_plot_spatial_anoamly.sh "BLANK"
    $sh 15_plot_test_steady_state.sh "BLANK"
    $sh 16_plot_total_flux_decomposition.sh "BLANK"
)


N=$(( ${#plot_codes[@]} / 3 ))
echo "We have $N file(s) to run..."
for i in $( seq 1 $(( ${#plot_codes[@]} / 3 )) ) ; do
    PROG="${plot_codes[$(( (i-1) * 3 + 0 ))]}"
    FILE="${plot_codes[$(( (i-1) * 3 + 1 ))]}"
    OPTS="${plot_codes[$(( (i-1) * 3 + 2 ))]}"
    echo "=====[ Running file: $FILE ]====="
    set -x
    eval "$PROG $FILE $OPTS" & 
done


wait

echo "Figures generation is complete."
echo "Please run 03_postprocess_figures.sh to postprocess the figures."
