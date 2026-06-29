import cv2
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from skimage.filters import threshold_otsu, threshold_local
from skimage.exposure import rescale_intensity

#load data and normalize
with fits.open("/content/SUT_T24_1465_000582_Lev1.0_2024-10-03T10.53.12.935_0971NB04.fits") as hdul:
  raw_data= np.nan_to_num(hdul[0].data)
img= rescale_intensity(raw_data, out_range=(0,255)).astype(np.uint8)

#Otsu thresholding
thresh_otsu_val= threshold_otsu(img)
mask_otsu= img> (thresh_otsu_val*1.5)

#Adaptive thresholding
mask_adaptive= img>threshold_local(img, block_size=151, method='gaussian',offset=25)

#evaluation function
def evaluate_mask(mask, name):
  num_labels, labels_im= cv2.connectedComponents(mask.astype(np.uint8))
  total_area= np.sum(mask)
  #subtracted 1 to exclude main background component
  print(f"[{name}]) Detected StructureCount:{num_labels-1}| total area coverage(pixels):{total_area}")
  return num_labels -1, total_area

print("Segmentation Benchmarks")
otsu_counts, otsu_area= evaluate_mask(mask_otsu,"Otsu")
adap_counts, adap_area= evaluate_mask(mask_adaptive, "Adaptive")

#Visualising and comparision matrix
fig, axes= plt.subplots(1,3, figsize=(15,5))
axes[0].imshow(img, cmap='gray', origin='lower') # Changed cmap to 'gray' for intensity images
axes[0].set_title("Original Aditya-L1 Image")
axes[0].axis('off')

axes[1].imshow(mask_otsu, cmap='gray', origin='lower')
axes[1].set_title("Otsu Threshold")
axes[1].axis('off')

axes[2].imshow(mask_adaptive, cmap='gray', origin='lower')
axes[2].set_title("Adaptive Threshold")
axes[2].axis('off')

plt.tight_layout()
plt.show()
