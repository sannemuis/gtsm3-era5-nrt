#!/bin/bash
#SBATCH -t 5:00:00
#SBATCH -p thin
#SBATCH -N 1

# load modules
module purge
module load 2021

# loop over months and years
for yr in {1979..2018..1}; do
(
  echo $yr 
  conda run -n gtsm3-era5-nrt-slm python p00_download_GTSM_waterlevels.py $yr 
) &
done
wait
