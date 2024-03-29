#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:25:23 2018

@author: muis
"""

import os
import datetime as dt
from distutils.dir_util import copy_tree
import sys
sys.path.append("..")
from path_dict import path_dict


def prepare_GTSM_yearly_runs(yr):
    yr=int(yr)
    meteo_fm_dir = path_dict['meteo_fm']
    meteo_slr_dir = path_dict['meteo_SLR']
    meteo_msl_dir = path_dict['meteo_msl']
    modelfiles_dir = path_dict['modelfiles']
    modelruns_dir = path_dict['modelruns']
    fmcontainer_dir = path_dict['fm_container']
    
    # calculate start and end times based on chosen reference time
    date_start = dt.datetime(yr,1,1)-dt.timedelta(days=17) # imposed 1 day zero, 1 day transition, 15 days spinup 
    date_end = dt.datetime(yr+1,1,1)
    
    refdate = dt.datetime(1900,1,1)
    tstart = (date_start-refdate).total_seconds()
    tstop = (date_end-refdate).total_seconds()
    
    print("reference date is ",str(refdate))
    print("tstart is ",str(tstart)," seconds since ref time")
    print("tstop  is ",str(tstop)," seconds since ref time")
    # files
    meteofile_u=os.path.join(meteo_fm_dir,f'ERA5_CDS_atm_u10_{dt.datetime.strftime(date_start, "%Y-%m-%d")}_{dt.datetime.strftime(date_end, "%Y-%m-%d")}.nc')
    meteofile_v=os.path.join(meteo_fm_dir,f'ERA5_CDS_atm_v10_{dt.datetime.strftime(date_start, "%Y-%m-%d")}_{dt.datetime.strftime(date_end, "%Y-%m-%d")}.nc')
    meteofile_p=os.path.join(meteo_fm_dir,f'ERA5_CDS_atm_msl_{dt.datetime.strftime(date_start, "%Y-%m-%d")}_{dt.datetime.strftime(date_end, "%Y-%m-%d")}.nc')
    
    SLRfile=os.path.join(meteo_slr_dir,"TotalSeaLevel_MapsSROCC_rcp85_Perc50_zero1986to2005_dflow_extrap.nc")  
    MSLcorrfile=os.path.join(meteo_msl_dir, "ERAInterim_average_msl_neg_%s1215_%s0101.nc" %(int(yr-1), int(yr)+1)) # need to be updated
    
    # copy model files and template if not exists
    run_dir = os.path.join(modelruns_dir,f'model_input_ERA5_{yr}')
    if os.path.exists(run_dir):
        raise Exception("Directory already exists ", run_dir)
    print("copying ",modelfiles_dir," to ",run_dir)
    copy_tree(modelfiles_dir, run_dir)
    
    # change templates
    keywords_MDU={'%REFDATE%':refdate.strftime("%Y%m%d"),'%TUNIT%':'S','%TSTART%':str(tstart),'%TSTOP%':str(tstop)}
    replace_all(os.path.join(run_dir,"gtsm_fine.mdu.template"), os.path.join(run_dir,"gtsm_fine.mdu"),keywords_MDU)
    
    keywords_EXT={'%METEOFILE_GLOB_U%':meteofile_u,'%METEOFILE_GLOB_V%':meteofile_v,'%METEOFILE_GLOB_P%':meteofile_p, '%METEOFILE_MSLCORR%':MSLcorrfile,'%METEOFILE_SLR%':SLRfile}
    replace_all(os.path.join(run_dir,'gtsm_fine.ext.template'),os.path.join(run_dir,"gtsm_fine.ext"),keywords_EXT) 
    
    shfile = 'sbatch_singularity_snellius_1x128cores.sh'
    shfile_template = shfile+'.template'
    workfolder=f"ERA5_{yr}"
    keywords_QSUB={'%JOBNAME%':workfolder, '%DIR_FMCONTAINER%':fmcontainer_dir}
    replace_all(os.path.join(run_dir,shfile_template),os.path.join(run_dir,shfile),keywords_QSUB)
    
    os.system("cd "+run_dir+"; chmod -R 777 *")


def replace_all(template_name,out_name,replace_dict):
    '''replace all occurrances of replace_dict keys with its values'''
    f_in  = open(template_name,'r')
    f_out = open(out_name,'w')
    data = f_in.read() # string of all file content
    for i, j in replace_dict.items(): #replace per key
        data = data.replace(i,j)
    f_out.write(data)
    f_in.close()
    f_out.close()
    
    #check for missed replacements
    msg = []
    if '%' in data:
        for line in data.split('\n'):
            if '%' in line:
                msg.append(line)
        msg_newlines = '\n'.join(msg)
        raise Exception(f'Not all keys replaced:\n{msg_newlines}')


if __name__ == "__main__":
    if len(os.sys.argv)>1:
        yr = os.sys.argv[1]       
    else: 
        raise RuntimeError('No arguments were provided')
    prepare_GTSM_yearly_runs(yr)
