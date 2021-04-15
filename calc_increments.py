import numpy as np
from read_trwind import read_trwind_file
from read_grib_variable import read_grib_variables
import grid_check
import sys
from find_tc_center_indx import find_center_indx 
from netCDF4 import Dataset

#Calculates analysis increments
# If storm relative coordinates are used, the background file will
# be moved to colocate its center at "tc_center_height_level" with 
# the analysis file. The lats and lons will be the relative lat and lon
# distance from the ceenter in the analysis

#######################
# USER INPUTS
#######################
background_grib=str(sys.argv[1]) #Background grib file
background_tr=str(sys.argv[2])   #Background trwind file
analysis_grib=str(sys.argv[3])   #Analysis grib file
analysis_tr=str(sys.argv[4])     #Analysis trwind file
storm_relative_coords=str(sys.argv[5])=="True" #Calculate Increments in storm 
                                               #relative coords
tc_center_height_level=float(sys.argv[6]) #Vertical level to center storms upon if storm_relative_coords is True
output_filename=str(sys.argv[7]) #Output filename, will be appended with either er or sr for "earth relative" or "storm relative"

#######################
# PROGRAM INPUTS
#######################
latcoord="latitude"              #Latitude coordinate name
loncoord="longitude"             #Longitude coordinate name
vertcoord="heightAboveSea"       #Vertical coordinate name

variables_grib=["u","v","w","t","pres","q"] #Vars in grib file to calc incs
variables_tr=["twind","rwind"]              #Vars in trwind file to calc incs

#######################
# START CODE EXECUTION
#######################

#Read background grib and tr files
lats_grib_back,lons_grib_back,vardict_grib_back = \
  read_grib_variables(background_grib,latcoord,loncoord,vertcoord,*variables_grib)

lons_tr_back,lats_tr_back,verts_tr_back,twind_back,rwind_back,tc_lons_back,tc_lats_back=\
  read_trwind_file(background_tr,vertcoord)

#Check trwind and grib grid for background
if not grid_check.check_grib_tr(lons_grib_back,lons_tr_back,lats_grib_back,lats_tr_back,0.001):
   print("Did not pass grib/trwind file check for background")
   sys.exit()

#Read analysis grib and tr files
lats_grib_anal,lons_grib_anal,vardict_grib_anal = \
  read_grib_variables(analysis_grib,latcoord,loncoord,vertcoord,*variables_grib)

lons_tr_anal,lats_tr_anal,verts_tr_anal,twind_anal,rwind_anal,tc_lons_anal,tc_lats_anal=\
  read_trwind_file(analysis_tr,vertcoord)

#Check trwind and grib grid for analysis
if not grid_check.check_grib_tr(lons_grib_anal,lons_tr_anal,lats_grib_anal,lats_tr_anal,0.001):
   print("Did not pass grib/trwind file check for analysis")
   sys.exit()

#Check that the background and analysis grids are identical
if not grid_check.check_grid_same(lons_grib_back,lons_grib_anal,lats_grib_back,lats_grib_anal,0.001):
   print("The grids from background and analysis don't seem to be the same")
   sys.exit()

#Add variables from trwind list to the grib list
if len(variables_tr)>0:
   if "twind" in variables_tr:
      vardict_grib_back.update({"twind":twind_back})
      vardict_grib_anal.update({"twind":twind_anal})
      variables_grib.append("twind")
   if "rwind" in variables_tr:
      vardict_grib_back.update({"rwind":rwind_back})
      vardict_grib_anal.update({"rwind":rwind_anal})
      variables_grib.append("rwind")

#Calculate increments 
if not storm_relative_coords:
   print("Starting increment calculations, earth relative coords")

   #Grib variables
   vardict_incs = {}
   for var in variables_grib:
      print(" Working on: {}".format(var))
      thisinc = vardict_grib_anal[var]-vardict_grib_back[var]
      vardict_incs.update({var:thisinc})

   height_indx = np.where(verts_tr_back == tc_center_height_level)[0][0]
   lon0_back = tc_lons_back[height_indx]
   lat0_back = tc_lats_back[height_indx]
   lon0_anal = tc_lons_anal[height_indx]
   lat0_anal = tc_lats_anal[height_indx]

#Storm relative coordinates
else:
   print("Starting increment calculations, storm relative coords")

   #Find indicies of tc center for background and analysis files
   height_indx = np.where(verts_tr_back == tc_center_height_level)[0][0]
   lon0_back = tc_lons_back[height_indx]
   lat0_back = tc_lats_back[height_indx]
   lon0_anal = tc_lons_anal[height_indx]
   lat0_anal = tc_lats_anal[height_indx]

   lat_indx_back,lon_indx_back = find_center_indx(lons_grib_back,lats_grib_back,lon0_back,lat0_back)
   lat_indx_anal,lon_indx_anal = find_center_indx(lons_grib_anal,lats_grib_anal,lon0_anal,lat0_anal)

   #Find difference in center indicies between background and analysis
   dlat_indx = lat_indx_anal - lat_indx_back
   dlon_indx = lon_indx_anal - lon_indx_back

   #Find pad amount for the background variable arrays 
   pad_lat = abs(dlat_indx)
   pad_lon = abs(dlon_indx)

   testvar = vardict_grib_back[variables_grib[0]]
   K,I,J = np.shape(testvar)
   istart = pad_lat - dlat_indx
   iend = pad_lat - dlat_indx + I
   jstart = pad_lon - dlon_indx
   jend = pad_lon - dlon_indx + J

   #Grib variables
   vardict_incs = {}
   for var in variables_grib:
      print(" Working on: {}".format(var))

      thisvar_back = vardict_grib_back[var]
      thisvar_anal = vardict_grib_anal[var]

      thisvar_back_pad = np.pad(thisvar_back,((0,0),(pad_lat,pad_lat),(pad_lon,pad_lon)),mode="constant",constant_values=np.nan)

      thisinc = thisvar_anal - thisvar_back_pad[:,istart:iend,jstart:jend]

      vardict_incs.update({var:thisinc})

#Save increments to file
if storm_relative_coords:
   filename = output_filename+"_sr.nc"
else:
   filename = output_filename+"_er.nc"
print("Writting output to : {}".format(filename))
   
ncfile= Dataset(filename,mode="w",format='NETCDF4')
ncfile.title="Analysis Increments"

vert_dim = ncfile.createDimension(vertcoord,len(verts_tr_back))
vert_var = ncfile.createVariable(vertcoord,np.float32,(vertcoord))
vert_var[:] = verts_tr_back

lat_dim = ncfile.createDimension('y',len(lats_grib_anal))
lat_var = ncfile.createVariable('latitude',np.float32,('y'))
if storm_relative_coords:
   lat_var[:] = lats_grib_anal-lat0_anal
else:
   lat_var[:] = lats_grib_anal

lon_dim = ncfile.createDimension('x',len(lons_grib_anal))
lon_var = ncfile.createVariable('longitude',np.float32,('x'))
if storm_relative_coords:
   lon_var[:] = lons_grib_anal-lon0_anal
else:
   lon_var[:] = lons_grib_anal

nc_vars = []
for i,var in enumerate(variables_grib):
   nc_vars.append(ncfile.createVariable(var,np.float32,(vertcoord,'y','x')))
   nc_vars[i][:,:,:] = vardict_incs[var]

ncfile.lat0_back=lat0_back
ncfile.lon0_back=lon0_back
ncfile.lat0_anal=lat0_anal
ncfile.lon0_anal=lon0_anal

if storm_relative_coords:
   ncfile.center_height=tc_center_height_level

ncfile.close() 

print("Done calculating analysis increments")
