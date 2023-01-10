import matplotlib.pyplot as plt
import os
import numpy
import process
import cv2
import matplotlib.cm as cm
import sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-filename","--filename", help="Filename of script")
parser.add_argument("-region","--region", help="Region, used for created folders")
parser.add_argument("-bmin","--bscan-min", help="Starting Bscan number",
                    type=int)
parser.add_argument("-bmax", "--bscan-max", help="Last Bscan number",
                    type=int)

parser.add_argument("-amin","--ascan-min", help="Starting A-scan number",
                    type=int)
parser.add_argument("-amax", "--ascan-max", help="Last A-scan number",
                    type=int)


args = parser.parse_args()
if args.ascan_max is None or  args.ascan_min is None or args.bscan_max is None or args.bscan_min is None or args.filename is None:
  print("please run --help to see the arguments")
  sys.exit(0)

filename = args.filename
region = args.region
base=os.path.basename(filename)
patient_name = os.path.splitext(base)[0]


output_directory="data/"+patient_name+"/"+region

try:
  os.makedirs(output_directory)
except Exception:
  pass


txt_filename =   output_directory + "/{filename}_bscan_{bscan_min}_{bscan_max}_ascan_{ascan_min}-{ascan_max}.txt".format(filename=filename, bscan_min=args.bscan_min, bscan_max=args.bscan_max,  ascan_min=args.ascan_min, ascan_max=args.ascan_max)
txt_output = open(txt_filename,"w")
all_ratios = []
oct_scan = process.OCT(filename)
for bscan_index in range(args.bscan_min, args.bscan_max+1):
  try:
    print("Processing Bscan: ",bscan_index)
    print("Processing Bscan: ",bscan_index, file=txt_output)
    bscan = oct_scan.get_bscan(bscan_index)
    b = bscan.BScanData#, dtype=numpy.uint8).reshape((oct_scan.SizeZ, oct_scan.SizeX))

    fig, ax = plt.subplots(nrows=1, ncols=3)#, figsize=(8, 5), sharex=True, sharey=True)
    fig.tight_layout()
    ax[ 0].imshow(b)
    ax[ 0].axis('off')
    ax[ 0].set_title('Original')

    ax[ 1].imshow(bscan.Blur)
    ax[ 1].axis('off')
    ax[ 1].set_title('cv2 Blur')
    ratios = []

    for i in range(args.ascan_min, args.ascan_max):
      try:
        first_peak, second_peak , x, ratio = bscan.process_slice(i)
        ratios.append(ratio)
        all_ratios.append(ratio)
        ax[0].scatter(x=[x], y=[first_peak], c='r', s=1, marker=',', linewidths=0, alpha=.4)
        ax[0].scatter(x=[x], y=[second_peak], c='b', s=1, marker=',', linewidths=0, alpha=.4)

        ax[1].scatter(x=[x], y=[first_peak], c='r', s=1, marker=',', linewidths=0, alpha=.4)
        ax[1].scatter(x=[x], y=[second_peak], c='b', s=1, marker=',', linewidths=0, alpha=.4)
      except Exception:
        continue
    ax[2].hist(ratios, bins =[float(x)*0.1 for x in range(3,23)])
    ax[2].set_title("OIR Distribution")
    ax[2].set_ylabel("Frequency")
    ax[2].set_xlabel("OIR Value")

    fig.tight_layout()

    print(numpy.mean(ratios))
    print(numpy.mean(ratios), file=txt_output)

    mean = numpy.mean(ratios)
    median = numpy.median(ratios)
    stdev = numpy.std(ratios)
    print("BScan {bscan} Mean: ".format(bscan=bscan_index), mean)
    print("BScan {bscan} Median: ".format(bscan=bscan_index), median)
    print("BScan {bscan} Stdev: ".format(bscan=bscan_index), stdev)

    print("BScan {bscan} Mean: ".format(bscan=bscan_index), mean, file=txt_output)
    print("BScan {bscan} Median: ".format(bscan=bscan_index), median, file=txt_output)
    print("BScan {bscan} Stdev: ".format(bscan=bscan_index), stdev, file=txt_output)

    print("",  file=txt_output)

    plt.savefig(output_directory + "/{filename}_bscan_{bscan_index}_ascan_{ascan_min}-{ascan_max}.png".format(filename=filename, bscan_index=bscan_index, ascan_min=args.ascan_min, ascan_max=args.ascan_max))
    plt.close()
  except Exception:
    print("Skipping this image", filename,bscan_index) 

mean = numpy.mean(all_ratios)
median = numpy.median(all_ratios)
stdev = numpy.std(all_ratios)
print("Overall Mean: ", mean)
print("Overall Median: ", median)
print("Overall Stdev: ", stdev)
print("Overall Mean: ", mean, file=txt_output)
print("Overall Median: ", median, file=txt_output)
print("Overall Stdev: ", stdev, file=txt_output)
