import matplotlib.pyplot as plt
import cv2
import matplotlib.cm as cm
import sys
if len(sys.argv) == 1:
  filename = "2004-005_2_72188.vol"
else: 
  filename = sys.argv[1]

import numpy
import process
oct_scan = process.OCT(filename)
bscan = oct_scan.get_bscan(45)
bscan.BScanData
b = bscan.BScanData#, dtype=numpy.uint8).reshape((oct_scan.SizeZ, oct_scan.SizeX))

fig, ax = plt.subplots(nrows=1, ncols=3)#, figsize=(8, 5), sharex=True, sharey=True)


print("denoisnig")


# put a red dot, size 40, at 2 locations:


ax[ 0].imshow(b)
ax[ 0].axis('off')
ax[ 0].set_title('Original')

cv2denoise = bscan.Denoised
ax[ 1].imshow(cv2denoise)
ax[ 1].axis('off')
ax[ 1].set_title('cv2 Denoised')

ax[ 2].imshow(bscan.Blur)
ax[ 2].axis('off')
ax[ 2].set_title('cv2 Blur')

for i in range(80):
  first_peak, second_peak , x = bscan.process_slice(i)
  ax[0].scatter(x=[x], y=[first_peak], c='r', s=1, marker=',', linewidths=0, alpha=.4)
  ax[0].scatter(x=[x], y=[second_peak], c='b', s=1, marker=',', linewidths=0, alpha=.4)

  ax[1].scatter(x=[x], y=[first_peak], c='r', s=1, marker=',', linewidths=0, alpha=.4)
  ax[1].scatter(x=[x], y=[second_peak], c='b', s=1, marker=',', linewidths=0, alpha=.4)

print(oct_scan.ScanPosition.strip(b'\x00') )
print(oct_scan.Distance)
#plt.show()
plt.savefig(filename+".png")
