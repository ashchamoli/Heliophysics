from astropy.coordinates.builtin_frames.supergalactic import r
from astropy.units.astrophys import R
from math import dist
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from skimage import exposure
from skimage.measure import label, regionprops
import glob
import os # Import os to check directory contents

print("Starting processing for temporal evolution of active region area.")

# Debugging: List contents of /content/ to verify files are present
print(f"Contents of /content/ at DffFofWddlTq execution: {os.listdir('/content/')}")

# Robustly load all fits files from the content directory that match the pattern
# Use os.listdir to get all files and then filter explicitly
all_content_files = os.listdir("/content/")
fits_files = sorted([f"/content/{fname}" for fname in all_content_files if fname.startswith("SUT_T24_") and fname.endswith(".fits")])

print(f"Files found after robust search: {fits_files}")

if not fits_files:
    print("No FITS files found matching /content/SUT_T24_*.fits. Please check the path and file existence.")
else:
    print(f"Processing {len(fits_files)} FITS files...")
    timestamps = []
    area_km2 = [] # Initialize area_km2 as an empty list
    target_centroid= None
    distance_threshold= 400

    for file in fits_files:
        with fits.open(file) as hdul:
            data = hdul[0].data
            header = hdul[0].header

            # Handle nan values
            data = np.nan_to_num(data)

            # Extract date and pixel scale information
            time_obs = header.get('DATE-OBS', 'Unknown')
            cdelt1 = header.get('CDELT1', 1.0)
            cdelt2 = header.get('CDELT2', 1.0)

            # Preprocess and threshold (using Otsu as a robust method, or keep percentile)
            img_normalised = exposure.rescale_intensity(data, out_range=(0, 1))
            threshold = np.percentile(img_normalised, 95) # Using 95th percentile as previously discussed
            binary_mask = img_normalised > threshold

            # Label connected components
            labeled_mask = label(binary_mask)
            regions = regionprops(labeled_mask)

            if not regions:
                timestamps.append(time_obs)
                area_km2.append(0.0) # Append 0 if no regions found
                continue
            selected_region= None
            if target_centroid is None:
                  selected_region= max(regions,key=lambda r: r.area)
                  target_centroid= selected_region.centroid
            else:
                  closest_region= None
                  min_distance= float('inf')
                  for r in regions:
                     dist= np.sqrt((r.centroid[0]-target_centroid[0])**2+(r.centroid[1]- target_centroid[1])**2)
                     if dist<min_distance and dist<distance_threshold:
                       min_distance= dist
                       closest_region= r

                  if closest_region is not None:
                      selected_region= closest_region
                      target_centroid= selected_region.centroid
                  else:
                      continue
            #extract pixel area from selected_region
            pixel_area = selected_region.area

            # Convert pixel area to physical area (arcsecond to km)
            # Assuming cdelt1 and cdelt2 are in arcseconds/pixel
            # And 725 km/arcsec is a rough conversion factor at the Sun's surface
            arcsec_area = pixel_area * (cdelt1 * cdelt2)
            area_km = arcsec_area * (725**2)

            timestamps.append(time_obs)
            area_km2.append(area_km)

    # Plotting the time-series evolution
    if timestamps:
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, area_km2, marker='o', linestyle='-', color='crimson')
        plt.xticks(rotation=45)
        plt.xlabel("Observation Time UTC")
        plt.ylabel("Active Region Area (km^2)")
        plt.title("Temporal Evolution of Target Active Region")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
