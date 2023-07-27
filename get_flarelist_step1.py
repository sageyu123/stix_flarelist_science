import pandas as pd
import matplotlib.pyplot as plt 
from astropy import units as u 
import astrospice
from astropy.time import Time
from sunpy.coordinates import frames
from sunpy.net import Fido, attrs as a
from stixpy.net.client import STIXClient
import matplotlib.pyplot as plt
import numpy as np 

import flarelist_fns

tstart = Time("2021-01-01")
tend = Time("2023-05-01")

""" -----------------------------------------------------------
Step 1: Get the operational flarelist from the STIX dataceneter.
-----------------------------------------------------------""" 
#flarelist_operational = flarelist_fns.get_flarelist_from_datacenter(tstart=tstart, tend=tend, save_csv=True)
flarelist_operational = pd.read_csv("stix_operational_flare_list_20210101_20230501.csv")



""" ------------------------------------------------------
Step 2: Find the pixel data available for each flare event.
----------------------------------------------------------""" 

# get only flares above 10000 counts in 4-10 keV energy band
flarelist_gt_10000 = flarelist_operational[flarelist_operational["LC0_PEAK_COUNTS_4S"]>=10000]
print(len(flarelist_operational), len(flarelist_gt_10000))

# get available pixel data
#flarelist_w_files = flarelist_fns.get_available_data_from_fido(flarelist_gt_10000, save_csv=True)
# if you want to read the files from an already saved file:
flarelist_w_files = pd.read_csv("stix_operational_list_with_file_info_20210302_20230430.csv")
print(np.sum(flarelist_w_files["number_available_files"]>0)/len(flarelist_gt_10000))


""" -----------------------------------------------------------------
Step 3: For each event with pixel data - determine which file to use.
---------------------------------------------------------------------""" 
flarelist_files = flarelist_w_files[flarelist_w_files["number_available_files"]>0]
flarelist_files.reset_index(inplace=True, drop=True)



def plot_available_files():
	flarelist_w_files.groupby("number_available_files").count()["flare_id"].plot.bar()
	plt.xlabel("Number of available pixel files")
	plt.ylabel("Number of flares")
	_ = plt.xticks(rotation=0)
	plt.title("Pixel file availability for flares > 10000 counts at peak 4-10 keV")

# need this if you need to read the flarelist_files from a saved csv
if isinstance(flarelist_files["available_file_request_IDs"].iloc[0], str)
	request_ids = flarelist_files["available_file_request_IDs"].map(lambda x: x.strip('][').split(', '))
else:
	request_ids = flarelist_files["available_file_request_IDs"]
flarelist_files.loc[:, "UIDs"] = request_ids

""" -----------------------------------------------------------------
Step 4: Download the available data from Fido (only use first pixel UID).
---------------------------------------------------------------------""" 

aux_paths = []
pixel_paths = []
for i in range(len(flarelist_files)):
    row = flarelist_files.iloc[i]
    tstart, tend, request_id = row["start_UTC"], row["end_UTC"], int(row["UIDs"][0])
    pixel_paths.append(flarelist_fns.get_pixel_data(tstart, tend, request_id))
    aux_paths.append(flarelist_fns.get_aux_data(tstart, tend))


flarelist_files.loc[:, "aux_paths"] = aux_paths
flarelist_files.loc[:, "pixel_paths"] = pixel_paths

len_aux = np.array([len(x) for x in flarelist_files["aux_paths"]])
len_sci = np.array([len(x) for x in flarelist_files["pixel_paths"]])


# drop cases where no pixel data
flarelist_files.reset_index(inplace=True, drop=True)

# drop unneeded columns
flarelist_files.drop(columns= ["CFL_X_arcsec", "CFL_Y_arcsec"], inplace=True)
