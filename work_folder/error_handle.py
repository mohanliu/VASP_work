#! /usr/bin/env python

import sys
import os
import shutil
import subprocess
import glob
import yaml

global_path = os.getcwd()

path = []
with open('log', 'r') as f:
    for l in f:
        if 'Task' in l:
            tmp = l.strip().replace('Task:', '').replace('./', '').strip()
        elif 'not converged' in l:
            path.append(tmp)
        else:
            continue

with open(os.path.join(global_path, 'auto.q'), 'r') as f:
    text = f.read()



qfile = text.format(nodes='4', ntasks='256', queuetype='regular', walltime='8:00:00')
qfile_stc = text.format(nodes='2', ntasks='128', queuetype='regular', walltime='2:00:00')


for p in path:
    os.chdir(os.path.join(global_path, p))
    print os.getcwd()


    if 'rlx' in p:
        with open('auto.q', 'w') as f:
            f.write(qfile)
    elif 'stc' in p:
        with open('auto.q', 'w') as f:
            f.write(qfile_stc)

    os.system('sbatch auto.q > jobid')
    os.system('tail -1 jobid')
