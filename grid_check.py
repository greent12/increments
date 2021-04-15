import numpy as np

def check_grib_tr(lons_grib,lons_tr,lats_grib,lats_tr,thresh):
   dlons = np.abs(lons_tr[0,:]-lons_grib)
   dlats = np.abs(lats_tr[:,0]-lats_grib)

   ret = False
   if np.all(dlons<thresh) and np.all(dlats<thresh):
      ret=True

   return ret

def check_grid_same(lons_back,lons_anal,lats_back,lats_anal,thresh):
   dlons = np.abs(lons_back-lons_anal)
   dlats = np.abs(lats_back-lats_anal)

   ret = False
   if np.all(dlons<thresh) and np.all(dlats<thresh):
      ret=True

   return ret

