
run(){
  bscanmin=$1
  bscanmax=$2
  ascanmin=$3
  ascanmax=$4
  region=$5
  ls *vol |xargs  -n1 -I{} -P 8 python3 process_bscans.py  -bmin $bscanmin -bmax $bscanmax -amin $ascanmin -amax $ascanmax -region $region -filename {}
}

run 16 30 185 335 superior
run 41 55 8 150 temporal
run 66 80 185 335 inferior
