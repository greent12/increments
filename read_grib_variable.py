import xarray as xr
import numpy as np
import sys

def read_grib_variables(filename,latcoord,loncoord,vertcoord,*args):
   try:
      data_array=xr.open_dataset(filename,engine='cfgrib',
                                 backend_kwargs={'filter_by_keys':
                                       {'typeOfLevel':vertcoord}})
   except:
      print("Error when reading {} with xarray...exiting.".format(filename))
      sys.exit()

   vardict={}
   for variable in args:
      if not variable in data_array.variables:
         print("Wanted variable {} not in grib file".format(variable))
      else:
         vardict.update({variable:data_array[variable].values}) 

   try:
      lats = data_array[latcoord].values
      lons = data_array[loncoord].values
   except:
      print("Lats or lons could not be extracted")
      sys.exit()

   data_array.close()

   return lats,lons,vardict
  
