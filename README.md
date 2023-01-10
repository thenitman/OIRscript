There are two versions of this software to be applied to the two different OCT file systems. 

Heidelberg files must be in .vol format. 

Cirris Files must be in .img format

Required software: 
-Python version X
-Matlab
-Xtools (if performing on Mac) 


Heidelberg Instructions: 

In Folder Heidelberg

setup
1. run `pip3 install -r requirements.txt` in the Heidelberg folder
  you may need to run `sudo pip3 install -r requirements.txt` depending on your local configurations
2. Place all vol files into the Heidelberg folder 
3. Run RUN_ALL.sh or run `sh run_file.sh {filename.vol}`
4. output is outputted to the data folder

Cirrus Instructions: 

1) Get some example .img data to `/data' folder
2) Run update_A_scan_ROI.m
3) Run process_folder_of_OCT_scans.m
4) This will process all the .img files found from /data folder with the associated custom croppings and generate txt files and pngs
5)run bash data/process.sh which will output a tsv of media, mean and standard deviations for each of the samples
