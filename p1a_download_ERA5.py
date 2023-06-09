#!/usr/bin/env python

import os
import datetime as dt
import calendar
import cdsapi


def download_era5(tstart,outdir):
    # find times for monthly downlods
    tstart = dt.datetime.strptime(tstart, "%Y-%m").date()
    lastday = calendar.monthrange(tstart.year,tstart.month)[1]
    dayarray = ["{:02}".format(iday) for iday in range(1,lastday+1)]     
    # daily download
    print ("######### ERA-5 from CDS #########")
    os.makedirs(outdir,exist_ok=True)
    # I/O - download the data
    for day in dayarray:
        print (f'getting data for {tstart.year}-{tstart.month:02d}-{day}')
        tday = dt.datetime(day=int(day),month=tstart.month,year=tstart.year).date()
        targetfile = os.path.join(outdir,"ERA5_CDS_atm_%s.nc" %(tday))
        if os.path.exists(targetfile):
            print('already downloaded')
            pass
        if os.path.isfile(targetfile)==False: 
            c = cdsapi.Client()
            c.retrieve('reanalysis-era5-single-levels',
                {'product_type':'reanalysis',
                'format':'netcdf',
                'variable':['10m_u_component_of_wind','10m_v_component_of_wind','mean_sea_level_pressure'],
                'year':tstart.year,
                'month':[f"{tstart.month:02}"],
                'day':day,
                'time':['00:00','01:00','02:00','03:00','04:00','05:00',
                        '06:00','07:00','08:00','09:00','10:00','11:00',
              	        '12:00','13:00','14:00','15:00','16:00','17:00',
                        '18:00','19:00','20:00','21:00','22:00','23:00']
                },targetfile)


if __name__ == "__main__":
    # read input arguments
    if len(os.sys.argv)>1:
        tstart=os.sys.argv[1]
        outdir=os.sys.argv[2]
    else:
        #tstart = '1960-01'
        #outdir = './TEMP_meteo_ERA5'
        raise RuntimeError('No arguments were provided\nFirst argument should indicate startdate as "yyyy-mm".\n Second argument for outdir. Script will download monthly files per day')
    download_era5(tstart,outdir)
