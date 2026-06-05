import astropy.units as u
from astropy.coordinates import SkyCoord
import sunpy.map
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import skimage.filters as fil
from skimage.morphology import disk, opening

fits_file = "SUT_T26_0723_002181_Lev1.0_2026-05-25T21.03.00.716_0972NB03.fits"
solar_map = sunpy.map.Map(fits_file)
clean_data= np.nan_to_num(solar_map.data)
#calculating brightness cutoff point separating active region from background plasma
otsu_thresh = fil.threshold_otsu(clean_data)
print(f"calculaated mathematical brightness cutoff point:{otsu_thresh:2f} DN")
manual_thresh=8000
print(f"manual active region cutoff point: {manual_thresh} DN")
#create binary mask(true where pixels are bright, else false)
active_mask =clean_data > manual_thresh
#clean out camera noise
refined_mask = opening(active_mask, disk(2))
#calculatig mean and standard deviation
img_mean= np.mean(clean_data)
img_std= np.std(clean_data)
otsu_thresh= img_mean+(4*img_std)

#plot 
fig= plt.figure(figsize=(8,8))
ax= fig.add_subplot(111, projection= solar_map)
#draw solar base disk
solar_map.plot(axes=ax, cmap= solar_map.cmap)
solar_map.draw_grid(axes=ax, color='white', alpha=0.2)
#contour layer
pixel_transform= ax.get_transform('pixel')
ax.contour(refined_mask, levels=[0.5], colors='cyan', linewidths=1.5, transform=pixel_transform)
#fixing centering limits b defining bottom-left and top-right coordinates in arcseconds
bottom_left= SkyCoord(-1200* u.arcsec, -1200* u.arcsec,frame=solar_map.coordinate_frame)
top_right= SkyCoord(1200* u.arcsec, 1200* u.arcsec, frame=solar_map.coordinate_frame)
#setting centering limits
ax.set_xlim(solar_map.wcs.world_to_pixel(bottom_left)[0], solar_map.wcs.world_to_pixel(top_right)[0])
ax.set_ylim(solar_map.wcs.world_to_pixel(bottom_left)[1], solar_map.wcs.world_to_pixel(top_right)[1])
#colorbar title
plt.colorbar(ax.images[0], ax=ax, label='Data Numbers(Intensity)', pad=0.08)
plt.title(f"SUIT Automated Active Region Tracking", pad=30, fontsize=14)

plt.show()
