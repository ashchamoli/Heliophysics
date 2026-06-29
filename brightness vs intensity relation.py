import re
from datetime import datetime
import os

# Get lists of FITS and NetCDF files in the /content/ directory
all_content_files = os.listdir("/content/")
fits_files_raw = sorted([f for f in all_content_files if f.startswith("SUT_T24_") and f.endswith(".fits")])
nc_files_raw = sorted([f for f in all_content_files if f.startswith("L2_AL1_MAG_") and f.endswith(".nc")])

fits_paths_by_date = {}
for fname in fits_files_raw:
    # Example: SUT_T24_1465_000582_Lev1.0_2024-10-03T10.53.12.935_0971NB04.fits
    match = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if match:
        date_str = match.group(1)
        fits_paths_by_date[date_str] = f"/content/{fname}"

nc_paths_by_date = {}
for fname in nc_files_raw:
    # Example: L2_AL1_MAG_20241011_V00.nc
    match = re.search(r'(\d{8})', fname)
    if match:
        date_str_raw = match.group(1)
        date_obj = datetime.strptime(date_str_raw, '%Y%m%d')
        formatted_date_str = date_obj.strftime('%Y-%m-%d')
        nc_paths_by_date[formatted_date_str] = f"/content/{fname}"

# Find common dates where both FITS and NetCDF files are available
common_dates = sorted(list(set(fits_paths_by_date.keys()) & set(nc_paths_by_date.keys())))

if not common_dates:
    print("No common dates found between FITS and NetCDF files for time series correlation.")
else:
    print(f"Found common dates for correlation: {common_dates}")

    # Initialize lists to store results for correlation
    correlation_dates = []
    avg_brightness_list = []
    avg_magnetic_field_list = []

    # Loop through common dates and process files
    for date_str in common_dates:
        current_fits_file = fits_paths_by_date[date_str]
        current_magnetogram_file = nc_paths_by_date[date_str]

        print(f"\nProcessing date: {date_str}")
        print(f"  FITS file: {current_fits_file}")
        print(f"  NetCDF file: {current_magnetogram_file}")

        # Process FITS file for average brightness of active region
        try:
            with fits.open(current_fits_file) as h_int:
                intensity_data = np.nan_to_num(h_int[0].data)
                # Apply active region detection logic
                img_normalised = rescale_intensity(intensity_data, out_range=(0,1))
                threshold = np.percentile(img_normalised, 95)
                ar_mask = img_normalised > threshold

                if np.any(ar_mask): # Only calculate average if an active region exists
                    avg_brightness_ar = np.mean(intensity_data[ar_mask])
                    print(f"  Average AR Brightness: {avg_brightness_ar:.2f}")
                else:
                    print(f"  No significant active region found in FITS file for {date_str}, skipping this date.")
                    continue # Skip this date if no active region

        except Exception as e:
            print(f"  Error processing FITS file for {date_str}: {e}, skipping this date.")
            continue

        # Process NetCDF file for average magnetic field strength
        try:
            with nc.Dataset(current_magnetogram_file, mode='r') as h_mag:
                # Check for Bx_gse, By_gse, Bz_gse, which are 1D time series
                if all(key in h_mag.variables for key in ['Bx_gse', 'By_gse', 'Bz_gse']):
                    bx = np.nan_to_num(h_mag.variables['Bx_gse'][:])
                    by = np.nan_to_num(h_mag.variables['By_gse'][:])
                    bz = np.nan_to_num(h_mag.variables['Bz_gse'][:])

                    # Calculate magnetic field magnitude and its average over the time series
                    b_magnitude = np.sqrt(bx**2 + by**2 + bz**2)
                    avg_b_magnitude = np.mean(b_magnitude)
                    print(f"  Average Magnetic Field Strength: {avg_b_magnitude:.2f}")

                    # If both brightness and magnetic field are successfully obtained for this date
                    correlation_dates.append(date_str)
                    avg_brightness_list.append(avg_brightness_ar)
                    avg_magnetic_field_list.append(avg_b_magnitude)

                else:
                    print(f"  Missing Bx_gse, By_gse, or Bz_gse variables in NetCDF file for {date_str}, skipping this date.")
                    continue
        except Exception as e:
            print(f"  Error processing NetCDF file for {date_str}: {e}, skipping this date.")
            continue

    # Perform time-series correlation and plotting
    if len(correlation_dates) >= 2: # Need at least two data points for correlation
        # Convert dates to datetime objects for plotting
        plot_dates = [datetime.strptime(d, '%Y-%m-%d') for d in correlation_dates]

        # Calculate Pearson and Spearman correlation coefficients
        pearson_r, _ = stats.pearsonr(avg_brightness_list, avg_magnetic_field_list)
        spearman_r, _ = stats.spearmanr(avg_brightness_list, avg_magnetic_field_list)

        print(f"\nTime Series Pearson r (Average Brightness vs. Average Magnetic Field): {pearson_r:.3f}")
        print(f"Time Series Spearman r (Average Brightness vs. Average Magnetic Field): {spearman_r:.3f}")

        # Plotting the time-series evolution of both quantities
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1) # Two subplots, 1 column, first plot
        plt.plot(plot_dates, avg_brightness_list, marker='o', linestyle='-', color='blue')
        plt.title('Average Active Region Brightness Over Time')
        plt.ylabel('Average Brightness (arbitrary units)')
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.subplot(2, 1, 2) # Second plot
        plt.plot(plot_dates, avg_magnetic_field_list, marker='o', linestyle='-', color='red')
        plt.title('Average Magnetic Field Strength Over Time')
        plt.xlabel('Date')
        plt.ylabel('Average Magnetic Field Strength (nT)') # Assuming nT for magnetic field
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.tight_layout()
        plt.show()
    else:
        print("Not enough successfully paired data points (at least 2) to compute time series correlation and plot.")
