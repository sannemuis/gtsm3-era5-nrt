#!/bin/bash
#SBATCH -t 20:00:00
#SBATCH -p thin
#SBATCH -N 1

# load modules
module purge
module load 2021

pdir="/gpfs/work1/0/einf3499/tides_CDS_extended"

# loop over months and years
for yr in {1952..1978..1}; do
  for mnth in {1..12..1}; do
  (
    echo $yr $mnth $pdir
    conda run -n gtsm3-era5-nrt-slm python p1b_download_tides.py $yr $mnth $pdir
  ) &
  done
done
wait

