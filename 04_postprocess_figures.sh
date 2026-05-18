#!/bin/bash

source 00_setup.sh

echo " ===== Plotting U = 20 m/s ===== "

finalfig_pdf_dir=$finalfig_dir/pdf
finalfig_png_dir=$finalfig_dir/png
finalfig_svg_dir=$finalfig_dir/svg


echo "Making output directory '${finalfig_dir}'..."
mkdir -p $finalfig_dir
mkdir -p $finalfig_pdf_dir
mkdir -p $finalfig_png_dir
mkdir -p $finalfig_svg_dir


echo "Making final figures... "

echo "Figure 2: Merge experiment design and vertical profile..."
svg_stack.py                                \
    --direction=h                           \
    $fig_static_dir/experiment_design.svg \
    $fig_dir/sounding_U20.svg        \
    > $fig_dir/merged-exp.svg



echo "Figure 4: Merge vertical... "
for bl_scheme in MYNN25 MYJ YSU ; do 
for dT in 000; do
for wnm in 000 ; do
   
    hrs_beg=240
    dhr=$( get_dhr $bl_scheme ) 
    hrs_end=$(( $hrs_beg + $dhr ))
    hrs=${hrs_beg}-${hrs_end}
 
    svg_stack.py \
        --direction=v \
        $fig_dir/snapshots-full_dhr-$dhr/lab_SIMPLE/case_mph-off_wnm${wnm}_U20_dT${dT}_${bl_scheme}/snapshot-full-vertical-profile_${hrs}.svg \
        $fig_dir/snapshots-full_dhr-$dhr/lab_FULL/case_mph-on_wnm${wnm}_U20_dT${dT}_${bl_scheme}/snapshot-full-vertical-profile_${hrs}.svg \
        > $fig_dir/merged-snapshot-vertical-profile_wnm${wnm}_U20_dT${dT}_${bl_scheme}.svg
done
done
done



echo "Figure 5 and 6: Merge snapshots... "
for bl_scheme in MYNN25 MYJ YSU ; do 
for dT in 100; do
for wnm in 010 ; do
 
    hrs_beg=240
    dhr=$( get_dhr $bl_scheme ) 
    hrs_end=$(( $hrs_beg + $dhr ))
    hrs=${hrs_beg}-${hrs_end}
    
    svg_stack.py \
        --direction=h \
        $fig_dir/snapshots_dhr-${dhr}/lab_SIMPLE/case_mph-off_wnm${wnm}_U20_dT${dT}_${bl_scheme}/snapshot-part1_${hrs}.svg \
        $fig_dir/snapshots_dhr-${dhr}/lab_FULL/case_mph-on_wnm${wnm}_U20_dT${dT}_${bl_scheme}/snapshot-part1_${hrs}.svg \
        > $fig_dir/merged-snapshot_wnm${wnm}_U20_dT${dT}_${bl_scheme}_part1.svg

    svg_stack.py \
        --direction=v \
        $fig_dir/snapshots_dhr-${dhr}/lab_SIMPLE/case_mph-off_wnm${wnm}_U20_dT${dT}_${bl_scheme}/snapshot-part2_${hrs}.svg \
        $fig_dir/snapshots_dhr-${dhr}/lab_FULL/case_mph-on_wnm${wnm}_U20_dT${dT}_${bl_scheme}/snapshot-part2_${hrs}.svg \
        > $fig_dir/merged-snapshot_wnm${wnm}_U20_dT${dT}_${bl_scheme}_part2.svg

done
done
done

name_pairs=(

# Main Text
    sst_analysis_20240101.svg                                                                      fig01
    merged-exp.svg                                                                                 fig02
    timeseries/timeseries_wnm010_U20_dT100_MYNN25_timeseries_smooth-25_000-360.svg                 fig03
    merged-snapshot-vertical-profile_wnm000_U20_dT000_MYNN25.svg                                   fig04
    merged-snapshot_wnm010_U20_dT100_MYNN25_part1.svg                                              fig05
    merged-snapshot_wnm010_U20_dT100_MYNN25_part2.svg                                              fig06
    dF_flux_decomposition_varying_dSST/lab_FULL/dF_flux_decomposition_onefig_U20_wnm010_varying_dSST_MYNN25_hr240-360.svg  fig07
    integrated_relationship/integrated_relationship-varying-dT-MYNN25_lab_FULL.svg                        fig08
    dF_flux_decomposition_varying_wnm/lab_FULL/dF_flux_decomposition_onefig_U20_dSST100_varying_wnm_MYNN25_hr240-360.svg   fig09
    integrated_relationship/integrated_relationship-varying-L-MYNN25_lab_FULL.svg                  fig10
    linearity_analysis/linearity_vary_wnm_lab_FULL_dSST100_U20_MYNN25_hr240-360.svg                fig11
    merged-div_analysis_lab_SIMPLE_U20_dT100_MYNN25.svg                                            fig12 
    merged-div_analysis_lab_FULL_U20_dT100_MYNN25.svg                                              fig13
    merged-div_analysis_lab_SIMPLE_U10_dT100_MYNN25.svg                                            fig14 
    merged-div_analysis_lab_FULL_U10_dT100_MYNN25.svg                                              fig15 

# Supplementary
    cloud_rain_snapshots_dhr-1/lab_FULL/case_mph-on_wnm010_U20_dT100_MYNN25/cloud_rain_240-241.svg   figS01
# MYJ
    timeseries/timeseries_wnm010_U20_dT100_MYJ_timeseries_smooth-25_000-360.svg                      figS02
    merged-snapshot-vertical-profile_wnm000_U20_dT000_MYJ.svg                                        figS03
    merged-snapshot_wnm010_U20_dT100_MYJ_part1.svg                                                   figS04
    merged-snapshot_wnm010_U20_dT100_MYJ_part2.svg                                                   figS05
    dF_flux_decomposition_varying_dSST/lab_FULL/dF_flux_decomposition_onefig_U20_wnm010_varying_dSST_MYJ_hr240-360.svg  figS06
    integrated_relationship/integrated_relationship-varying-dT-MYJ_lab_FULL.svg                      figS07
    dF_flux_decomposition_varying_wnm/lab_FULL/dF_flux_decomposition_onefig_U20_dSST100_varying_wnm_MYJ_hr240-360.svg   figS08
    integrated_relationship/integrated_relationship-varying-L-MYJ_lab_FULL.svg                       figS09
    linearity_analysis/linearity_vary_wnm_lab_FULL_dSST100_U20_MYJ_hr240-360.svg                     figS10

# YSU
    timeseries/timeseries_wnm010_U20_dT100_YSU_timeseries_smooth-25_000-360.svg                      figS11
    merged-snapshot-vertical-profile_wnm000_U20_dT000_YSU.svg                                        figS12
    merged-snapshot_wnm010_U20_dT100_YSU_part1.svg                                                   figS13
    merged-snapshot_wnm010_U20_dT100_YSU_part2.svg                                                   figS14
    dF_flux_decomposition_varying_dSST/lab_FULL/dF_flux_decomposition_onefig_U20_wnm010_varying_dSST_YSU_hr240-360.svg  figS15
    integrated_relationship/integrated_relationship-varying-dT-YSU_lab_FULL.svg                      figS16
    dF_flux_decomposition_varying_wnm/lab_FULL/dF_flux_decomposition_onefig_U20_dSST100_varying_wnm_YSU_hr240-360.svg   figS17
    integrated_relationship/integrated_relationship-varying-L-YSU_lab_FULL.svg                       figS18
    linearity_analysis/linearity_vary_wnm_lab_FULL_dSST100_U20_YSU_hr240-360.svg                     figS19
)

N=$(( ${#name_pairs[@]} / 2 ))
echo "We have $N figure(s) to rename and convert into pdf files."
for i in $( seq 1 $N ) ; do

    {

    src_file="${name_pairs[$(( (i-1) * 2 + 0 ))]}"
    dst_file_pdf="${name_pairs[$(( (i-1) * 2 + 1 ))]}.pdf"
    dst_file_png="${name_pairs[$(( (i-1) * 2 + 1 ))]}.png"
    dst_file_svg="${name_pairs[$(( (i-1) * 2 + 1 ))]}.svg"
 
    echo "$src_file => $dst_file_svg"
    cp $fig_dir/$src_file $finalfig_svg_dir/$dst_file_svg
   
    echo "$src_file => $dst_file_pdf"
    cairosvg $fig_dir/$src_file -o $finalfig_pdf_dir/$dst_file_pdf

    echo "$src_file => $dst_file_png"
    magick $finalfig_pdf_dir/$dst_file_pdf $finalfig_png_dir/$dst_file_png

    } &
done

wait

echo "Done."
