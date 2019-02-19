#! /usr/bin/env python

import sys
import os
import shutil
import subprocess
import glob
import json
import job_control as jc
import re
import numpy as np

class Result(jc.DFTjob):
    def __init__(self, poscar):
        jc.DFTjob.__init__(self, poscar)
        self.result = {}
        self.check_result()

    def check_result(self):
        print self.path
        for c in self.conf_lst:
            cp = os.path.join(self.path, c)
            if not os.path.exists(cp):
                return
            else:
                os.chdir(cp)
                out = subprocess.check_output([os.path.join(self.global_path, 'check_converge.sh'), os.path.join(self.global_path, 'current_running')])
                if "True" in out:
                    os.chdir(self.global_path)
                    print "    ", c, " is converged"
                    self.result[ c ] = self.read_oszicar(cp)
                    if c == 'rlx2':
                        self.result[ 'A' ] = self.read_surf_area(cp)
                    continue
            os.chdir(self.global_path)
        return

    def read_oszicar(self, conf_path):
        """
        Read converged energy from OSZICAR
        """
        oz = os.path.join(conf_path, 'OSZICAR')
        
        with open(oz, 'r') as f:
            for line in f:
                if re.search(' F= ', line):
                    final_line = line.strip()

        v = final_line.split()[2]
        return float(v)

    def read_surf_area(self, conf_path):
        """
        Read surface area from CONTCAR
        """
        ct = os.path.join(conf_path, 'CONTCAR')
        
        with open(ct, 'r') as f:
            dat = f.readlines()[2:5]
            a1 = np.array(map(float, dat[0].strip().split()))
            a2 = np.array(map(float, dat[1].strip().split()))
            return np.linalg.norm(np.cross(a1, a2))

if __name__ == "__main__":
    poscars = glob.glob('poscars/*')
    os.system('squeue -u mervyn > current_running')

    output = {}
    
    for p in poscars:
        name = '_'.join(p.split('/')[1].split('_')[1:])
        d = Result(p)
        output[ name ] = d.result

    with open(os.path.basename(os.getcwd())+'_result.json', 'w') as f:
        json.dump(output, f, indent=4, ensure_ascii = False)
