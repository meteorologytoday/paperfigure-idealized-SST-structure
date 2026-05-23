#!/bin/bash

source 00_setup.sh

for U in "${Us[@]}"; do 
    python3 src/check_files.py --U $U --input-root $( gen_gendata_dir $U )/preavg --data-type preavg
done
