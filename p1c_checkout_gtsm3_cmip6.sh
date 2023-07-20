#!/bin/bash
# Since authentication is required for the SVN repos, this script should be executed and not submitted

# load modules
module purge
module load 2021

#get dir_modelfiles as variable
dir_modelfiles=$(python path_dict.py modelfiles)

cd dir_modelfiles

#checkout gtsm3_cmip6 repos folder to dir_modelfiles
svn checkout https://repos.deltares.nl/repos/global_tide_surge_model/trunk/gtsm3_cmip6 .

#remove non-template ext and mdu to avoid issues
rm *.ext
rm *.mdu