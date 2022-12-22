#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:25:23 2018

@author: muis
"""
import os
import click
from datetime import date, datetime, timedelta
import shutil
from distutils.dir_util import copy_tree
import numpy as np 
  
@click.command()
@click.option('--base_dir', required=True, type=str,
              help='Project directory',)
@click.option('--date_string', required=True, type=str,
              help='String with year and month of current month (in YYYY_MM format)',)

def prepare_GTSM_monthly_runs(base_dir,date_string):  
  # calculate start and end times based on chosen reference time
  #-------------------
  tdate = datetime.strptime(date_string, '%Y_%m').date()
  spinup_period = [1,1,15,0] # imposed 1 day zero, 1 day transition, 15 days spinup 
  date_start = datetime(tdate.year,tdate.month,1)-timedelta(days=int(np.sum(spinup_period[0:3]))) 
  date_end = datetime(tdate.year,tdate.month+1,1)
  
  refdate=datetime(1900,1,1) 
  tstart=(date_start-refdate).total_seconds() 
  tstop=(date_end-refdate).total_seconds()
  
  print("reference date is ",str(refdate))
  print("tstart is ",str(tstart)," hours since ref time") 
  print("tstop  is ",str(tstop)," hours since ref time") 
  # files
  #-------------------
  meteofile_u=os.path.join(base_dir,f'meteo_ERA5_fm/ERA5_CDS_atm_u10_{datetime.strftime(date_start, "%Y-%m-%d")}_{datetime.strftime(date_end, "%Y-%m-%d")}.nc')
  meteofile_v=os.path.join(base_dir,f'meteo_ERA5_fm/ERA5_CDS_atm_v10_{datetime.strftime(date_start, "%Y-%m-%d")}_{datetime.strftime(date_end, "%Y-%m-%d")}.nc')
  meteofile_p=os.path.join(base_dir,f'meteo_ERA5_fm/ERA5_CDS_atm_msl_{datetime.strftime(date_start, "%Y-%m-%d")}_{datetime.strftime(date_end, "%Y-%m-%d")}.nc')
  
  SLRfile=os.path.join(base_dir,"meteo_SLR/TotalSeaLevel_MapsSROCC_rcp85_Perc50_zero1986to2005_dflow_extrap.nc")  
  MSLcorrfile=os.path.join(base_dir, "meteo_msl/ERAInterim_average_msl_neg_%s1215_%s0101.nc" %(int(tdate.year-1), int(tdate.year)+1)) # need to be updated
  
  templatedir=os.path.join(base_dir, "model_runs/model_template/model_input_template")
  modelfilesdir=os.path.join(base_dir, "model_runs/model_template/model_files")
  run_dir= os.path.join(base_dir, f"model_runs/slr_tide_surge_runs/model_input_ERA5_{tdate}")
      
  # copy model files and template
  #-------------------
  try:
     os.stat(run_dir)               
     raise Exception("Directory already exists ", run_dir) 
  except OSError:
      print("copying ",templatedir," to ",run_dir)
      shutil.copytree(templatedir,run_dir,symlinks=False,ignore=None)
  copy_tree(modelfilesdir, run_dir)

  ## change templates
  #-------------------
  keywords_MDU={'REFDATE':refdate.strftime("%Y%m%d"),'TSTART':str(tstart),'TSTOP':str(tstop)}
  replace_all(os.path.join(run_dir,"gtsm_fine.mdu.template"), os.path.join(run_dir,"gtsm_fine.mdu"),keywords_MDU,'%')

  keywords_EXT={'METEOFILE_GLOB_U':meteofile_u,'METEOFILE_GLOB_V':meteofile_v,'METEOFILE_GLOB_P':meteofile_p, 'METEOFILE_MSLCORR':MSLcorrfile,'METEOFILE_SLR':SLRfile}
  replace_all(os.path.join(templates_path,'gtsm_forcing.ext.template'),os.path.join(run_dir,extfile),keywords_EXT,'%') 

  keywords_QSUB={'NDOM':str(ndom),'NNODE':str(nnode),'JOBNAME':workfolder} 
  replace_all(os.path.join(templates_path,'%s.template'%(shfile)),os.path.join(run_dir,'%s'%(shfile)),keywords_QSUB,'%')

  os.system("cd "+newdir+"; chmod -R 777 *")    
  
def replace_all(template_name,out_name,key_values,special_char):
    '''replace all occurrances of key between special_chars with the values '''
    f_in  = open(template_name,'r')
    f_out = open(out_name,'w')
    for line in f_in.readlines():
        if( line.count(special_char)==2 ):
            print(">>>"+line)
            left_index=line.find(special_char)
            right_index=line.rfind(special_char)
            key=line[left_index+1:right_index]
            key_with_chars=special_char+key+special_char
            if key in key_values:
                value=key_values[key]
                line=line.replace(key_with_chars,value)
            else:
                raise Exception("Could not find key:"+key)
        f_out.write(line)
    f_in.close()
    f_out.close()
    
if __name__ == "__main__":
  prepare_GTSM_monthly_runs()
