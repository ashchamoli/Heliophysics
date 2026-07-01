import numpy as np
import matplotlib.pyplot as plt
import sunpy.map
from skimage.morphology import opening, disk

# Selecting the second FITS file (index 1)
selected_file = fits_files[1]
print(f"Processing file: {selected_file}")

# Load the map
smap = sunpy.map.Map(selected_file)
original_data = smap.data.copy()

#  Flat-field correction  
# For example: corrected_data = (original_data - dark_frame) / flat_frame
corrected_data = original_data # Using original data for now

#  Normalise intensity values 
# Replace NaNs with a reasonable value (e.g., mean) for normalization or remove them
# For display, we can just mask them, but for numerical operations, filling is better.
data_for_norm = np.nan_to_num(corrected_data, nan=np.nanmean(corrected_data))

# Normalize data to 0-1 range
min_val = np.min(data_for_norm)
max_val = np.max(data_for_norm)
normalized_data = (data_for_norm - min_val) / (max_val - min_val)

# Threshold segmentation and morphological operations
# Active region detection using adaptive threshold
img_mean = np.nanmean(corrected_data)
img_std = np.nanstd(corrected_data)
adaptive_thresh = img_mean + (4 * img_std)
active_mask = corrected_data > adaptive_thresh

# Refine boundaries with morphological opening
refined_mask = opening(active_mask, disk(2))

#: Plot contours and use false color maps
fig_single, ax_single = plt.subplots(figsize=(8, 8))

# Display the normalized data with a false-color map
im_single = ax_single.imshow(normalized_data, origin='lower', cmap='viridis')
ax_single.axis('off')

# Plot contours of detected active regions
ax_single.contour(refined_mask, levels=[0.5], colors='red', linewidths=1.5)

plt.colorbar(im_single, ax=ax_single, label='Normalized Intensity')

# Set title
ax_single.set_title(f"Processed Active Region: {smap.date.strftime('%Y-%m-%d %H:%M:%S')}", fontsize=14)

plt.show()
