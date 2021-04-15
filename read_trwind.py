import xarray as xr
import sys
import numpy as np

def read_trwind_file(file,vert_coord):

   ''' 
    Reads nc file containing tangential/radial winds as well as tc lat and lon centers created by calc trwind scripts

    Inputs
    ------
    file : str
      path to input nc file
    vert_coord : str
      the vertical coordinate that is going to be read, should correspond to what was used to create the input file

    Outputs
    -------
    lons : numpy.ndarray
       2d array of lons (nlat,nlon)
    lats : numpy.ndarray
       2d array of lats (nlat,nlon)
    verts : numpy.ndarray
       1d array containing the values for the vertical coordinate
    twind : numpy.ndarray
       3d array of tangential winds in m/s (nvert,nlat,nlon)
    rwind : numpy.ndarray
       3d array of radial winds in m/s (nvert,nlat,nlon)
    tc_lons : numpy.ndarray
       1d array of tc center longitudes (nvert)
    tc_lats : numpy.ndarray
       1d array of tc center latitudes (nvert)
   '''
   
   #Check that file has .nc extension
   if not file.endswith(".nc"):
      sys.exit("Input must be a netcdf (.nc) file... exiting")

   #Read nc file with xarray
   data = xr.open_dataset(file)

   #Exctract lats and lons, if not 2d, put them in a mesh
   lats = data.latitude.values
   lons = data.longitude.values

   if lats.ndim == 1 and lons.ndim == 1:
      lons,lats = np.meshgrid(lons,lats)

   #Get vertical coordinate
   try:
      verts = data.coords[vert_coord].values
   except:
      print("Vertical coordinate {} could not be found in file... exiting".format(vert_coord))

   #Read tangential and radial winds
   twind = data.twind.values
   rwind = data.rwind.values

   #TC lat and lon centers
   tc_lons = data.tc_center_lons.values
   tc_lats = data.tc_center_lats.values

   return lons,lats,verts,twind,rwind,tc_lons,tc_lats


