# Description
This is the code to generate the figures of the paper "Examining the SST Tendency Forced by Atmospheric Rivers" submitted to XXX journal.

# Prerequisite

1. Python >= 3.7
    - Matplotlib
    - Cartopy
    - Numpy
    - Scipy
    - netCDF4
2. ImageMagick >= 6.9.10


# File descriptions

- `00_setup.sh` : basic setup.
- `01_main.sh`  : A complete run-through generating the figures.
- `02_gendata.sh` : Generate all the pre-processing data
- `03_make_figures.sh` : Generate all figures.
- `04_postprocess_figures.sh` : Post-processing figures and put together the numbering. 


# Reproducing Figures

1. Clone this project.
2. Download files `data.tar.gz` and `gendata.tar.gz` from [Zenodo.org](https://zenodo.org/records/14247083) to this project folder.
3. Decompress the files `data.tar.gz` and `gendata.tar.gz` with the command `tar -xzvf [filename]`. You should see two directories generated: `data` and `gendata`.
4. If there is any need to regenerate the "delta analysis", which produce files in `gendata/delta_analysis_style-STYLE1` please run `93_generate_delta_analysis.sh`.
4. Run `94_pack_data.sh`.
5. Run `95_generate_coherence_analysis.sh`.
6. Run `96_generate_Ro_vary_wnm.sh`.
7. Run `03_make_figures.sh`.
8. Run `04_postprocess_figures.sh`.
9. The figures are generated in the folder `final_figures`.




# Notes

## Download data

You can programmitically download the data using Zenedo access token. The code to download the data is in `download/download.py`. You should see the following data:

1. `data.tar.gz`
2. `gendata.tar.gz.split.[XX]`, wherer XX = 00, 01, ..., 04.

Then merge the split data through `cat gendata.tar.gz.split.?? > gendata.tar.gz`. After that, untar two files into working directory. Done. 

## For authors to create `gendata` from `data`

- Run `91_generate_hourly_avg.sh` to produce hourly mean data every 12 hours.
- Run `92_make_softlinks.sh` to make proper softlinks. For dSST=0 case is shared across different SST wavenumbers/wavelengths.
- Run `93_generate_delta_analysis.sh` to generate analysis for air-sea flux decompositions.
- Run `94_pack_data.sh` to pack data generated from `93_generate_delta_analysis.sh` into single netCDF files.

# Main Figures

1. SST map and spectrum
2. Exp design + vertical profile
3. Time series.
4. Reference atmosphere state.
5. Atmospheric response plot part 1: cross-section.
6. Atmospheric response plot part 2: horizontal mean.
7. Air-sea flux decomposition as a function of dSST.
8. Boundary layer property analysis as a function of dSST.
9. Air-sea flux decomposition as a function of wavelength L.
10. Boundary layer property analysis as a function of L.
11. Spectrum analysis.
12. Divergence budget analysis 1.
13. Divergence budget analysis 2.
14. Divergence budget analysis 3.
15. Divergence budget analysis 4.

# Supplementary Figures

1. One hour snapshot of simulation.
2-19. Analysis for MYJ and YSU schemes.
