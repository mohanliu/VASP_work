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

USER_name = 'mlc152'

class CollectCONTCAR(jc.DFTjob):
    def __init__(self, poscar):
        jc.DFTjob.__init__(self, poscar)
        if not os.path.exists('CONTCARs'):
            os.mkdir('CONTCARs')
        self.contcars_container = os.path.join(self.global_path, 'CONTCARs')
        self.collect_contcar()

    def collect_contcar(self):
        final_state_path = None
        for c in self.conf_lst:
            cp = os.path.join(self.path, c)
            if not os.path.exists(cp):
                return
            else:
                os.chdir(cp)
                out = subprocess.check_output([os.path.join(self.global_path, 'check_converge.sh'), os.path.join(self.global_path, 'current_running')])
                if "True" in out:
                    os.chdir(self.global_path)
                    final_state_path = cp
            os.chdir(self.global_path)
        ctp = os.path.join(final_state_path, 'CONTCAR')
        name = '_'.join(final_state_path.strip().split('/')[1:])
        dst = os.path.join(self.contcars_container, 'CONTCAR_'+name)
        shutil.copy(ctp, dst)
        return

if __name__ == "__main__":
    poscars = glob.glob('poscars/*')
    os.system('squeue -u '+USER_name+' > current_running')


    for p in poscars:
        name = '_'.join(p.split('/')[1].split('_')[1:])
        CollectCONTCAR(p)
