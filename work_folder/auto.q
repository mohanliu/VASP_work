#! /bin/bash

#SBATCH -N {nodes}
#SBATCH -C knl,quad,cache
#SBATCH -p {queuetype}
#SBATCH -J Mohanknl
#SBATCH -t {walltime}
#SBATCH -A m1673
#SBATCH -o job.oe

#OpenMP settings:
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=true

#run the application:
module load vasp/20170629-knl

gunzip -f CHGCAR.gz WAVECAR.gz &> /dev/null
date +%s
ulimit -s unlimited

srun -n {ntasks} -c 4 --cpu_bind=cores vasp_std > stdout.txt 2>stderr.txt

gzip -f CHGCAR OUTCAR PROCAR WAVECAR
rm -f CHG
date +%s
