import numpy as np

def find_center_indx(lons1d,lats1d,lon0,lat0):
   dlons = np.abs(lons1d-lon0)
   dlats = np.abs(lats1d-lat0)
   
   lon_indx = np.where(np.min(dlons) == dlons)[0][0]
   lat_indx = np.where(np.min(dlats) == dlats)[0][0]

   return lat_indx,lon_indx
