import mmap
import sys
import cv2
import numpy
import math
import struct



class BScan(object):
  def unpack(self, _type, start):
    if _type == "i":
      end = start+4
    if _type == "d":
      end = start + 8
    if _type == "fnan":
      end = start + 4
      if self.mm[start:end] == b"\xff\xff\x7f\x7f":
        return float("NaN")
    if _type == "f":
      end = start + 4
      if self.mm[start:end] == b"\xff\xff\x7f\x7f":
        return 0.0
    return struct.unpack("<{_type}".format(_type=_type[0]),self.mm[start:end])[0]


  def min_nan(self, i):
    line = self.BScanRaw[:,i]
    for k in range(len(line)):
      if  not numpy.isnan(line[k]):
        return k  # gaussian blur on the NaN = 0 is the issue, if the NaN = first not NaN this would be fine
    return 0

  def get_first_peak(self, line, i):
    start_y = self.min_nan(i)
    #peak finding
    INNER_RETINA_PEAK_SEARCH_OFFSET = 40
    INNER_RETINA_OFFSET_FROM_PEAK = 20


    for y in range(start_y+INNER_RETINA_PEAK_SEARCH_OFFSET , len(line)):
      sub_line = line[start_y:y]
      std = numpy.std(sub_line)
      if line[y] > numpy.mean(sub_line)  + 4*std:
        break
    subline = line[y:y+INNER_RETINA_OFFSET_FROM_PEAK]
    return y+numpy.argmax(subline)

  def second_peak(self, first_peak, line):
    RPE_PEAK_SEARCH_OFFSET  = 50
    RPE_GAUSSIAN_ADJUSTED_OFFSET = 3 # move down a few pixels, the gaussian blur incorporates some EZ layer which slightly shifts up the RPE peak. This adjustment pushes down and "reverses" the gaussian
    subline = line[first_peak+RPE_PEAK_SEARCH_OFFSET:]
    max_index = first_peak + RPE_PEAK_SEARCH_OFFSET+ numpy.argmax(subline) + RPE_GAUSSIAN_ADJUSTED_OFFSET
    return max_index

  def process_slice(self,i):
    position = self.oct_scan.ScanPosition.strip(b'\x00')
    if position == b"OS":
      x = self.oct_scan.SizeX - i -2
    else:
      x = i
    line = self.Blur.reshape((self.oct_scan.SizeZ, self.oct_scan.SizeX))[:,x]
    first_peak = self.get_first_peak(line,x)
    second_peak = self.second_peak(first_peak, line)
    ratio = line[first_peak]/line[second_peak]
    return first_peak, second_peak,x, ratio



  def __init__(self, oct_scan, mm):
    self.oct_scan = oct_scan
    self.mm = mm
    self.version = self.mm[0:12]
    self.StartX = self.unpack("d",16)
    self.StartY = self.unpack("d",24)
    self.EndX = self.unpack("d",32)
    self.EndY = self.unpack("d",40)
    self.NumSeg = self.unpack("i",48)
    self.OffSeg = self.unpack("i",52)
    self.Quality = self.unpack("f",56)
    self.SegArrayFirst =  self.unpack("f", 256)

    self.BScanRaw = numpy.array([ self.unpack("fnan",self.oct_scan.BScanHdrSize+4*i) for i in range(self.oct_scan.SizeX*self.oct_scan.SizeZ)]).reshape((self.oct_scan.SizeZ, self.oct_scan.SizeX))
    self.BScanData = [ 255*(self.unpack("f",self.oct_scan.BScanHdrSize+4*i)**0.25) for i in range(self.oct_scan.SizeX*self.oct_scan.SizeZ)] # slow TODO convert to numpy
    self.BScanData = numpy.array(self.BScanData, dtype=numpy.uint8).reshape((self.oct_scan.SizeZ, self.oct_scan.SizeX))
    self.Denoised = cv2.medianBlur(self.BScanData, 15) # highly effective against salt and pepper noise https://docs.opencv.org/3.1.0/d4/d13/tutorial_py_filtering.html
    self.Denoised = cv2.fastNlMeansDenoising(self.Denoised, None, 9,13) # denoising
    self.Blur =  cv2.GaussianBlur(src=self.Denoised,ksize=(0,0),sigmaX=2) #You can change the kernel size as you want


class OCT(object):
  def unpack(self, _type, start):
    if _type == "i":
      end = start+4
    if _type == "d":
      end = start + 8
    return struct.unpack("<{_type}".format(_type=_type),self.mm[start:end])[0]

  def __init__(self, filename):
    self.filename = filename
    self.fp = open(filename,'r+b')
    self.mm = mmap.mmap(self.fp.fileno(), 0)
    self.HeaderSize = 2048
    self.version = self.mm[0:12]
    i, d="i","d"
    self.SizeX = self.unpack(i,12)
    self.NumBScans = self.unpack(i,16)
    self.SizeZ = self.unpack(i, 20)
    self.ScaleX = self.unpack(d, 24)
    self.Distance = self.unpack(d, 32)
    self.ScaleZ = self.unpack(d, 40)
    self.ScanFocus = self.unpack(d, 76)
    self.ScanPosition = self.mm[84:88]
    self.PatientID = self.mm[140:161]
    self.BScanHdrSize = self.unpack(i, 100)

    self.SizeXSlo = self.unpack(i, 48)
    self.SizeYSlo = self.unpack(i,52)
    self.SloImageSize = self.SizeXSlo*self.SizeYSlo

    self.BScanOffset = self.HeaderSize + self.SloImageSize
    self.BsBlkSize = self.BScanHdrSize + self.SizeX*self.SizeZ*4

  def get_blocksize_offset(self, i):
    return self.HeaderSize+ self.SloImageSize + i * self.BsBlkSize
    

  def get_bscan(self, i):
    return BScan(self, self.mm[self.get_blocksize_offset(i):self.get_blocksize_offset(i)+self.BsBlkSize])
    

def main():
  oct_scan = OCT("2004-005_2_72188.vol")
  attrs = vars(oct_scan)
  print('\n'.join("%s: %s" % item for item in attrs.items()))
  for i in range(oct_scan.NumBScans):
    print('BScan: '+str(i))
    bscan_test  = oct_scan.get_bscan(i)
    attrs = vars(bscan_test)
    #del attrs['mm']
    #print('\n'.join("%s: %s" % item for item in attrs.items()))

if __name__=="__main__":
  main()
