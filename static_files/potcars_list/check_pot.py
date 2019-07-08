#! /usr/bin/python

import os
import sys
import re

# Get dict of VASP recommended potpaw
import pot_python_list as ppl
potdict = ppl.pot_dict

# Write POTCAR from list of files
loc_pbe = '/global/homes/m/mervyn/pot_pbe/'
pot_singles = [loc_pbe+potdict[v]+'/POTCAR' for v in ['Pt','Cu','O','Au']]
#pot_singles = [loc_pbe+potdict[v]+'/POTCAR' for v in potdict.keys()]

# Function to get ENMAX from POTCARs
def get_enmax(pot_file) : 
    try:
        for line in open(pot_file,'r'):
            if re.search('ENMAX', line):
                return float(line.split()[2][:-1])
    except IOError:
        return None

def get_enmin(pot_file) : 
    try:
        for line in open(pot_file,'r'):
            if re.search('ENMIN', line):
                return float(line.split()[5])
    except IOError:
        return None

# ENMIN/ENMAX in POTCAR
enmax = {}
enmin = {}
for x in pot_singles:
    v = x.split('/')[-2]
    enmax[v] = get_enmax(x)
    enmin[v] = get_enmin(x)
print enmax
print enmin
print enmax.keys()[enmax.values().index(max(enmax.values()))]
print enmin.keys()[enmin.values().index(max(enmin.values()))]
#enmax = [get_enmax(x) for x in pot_singles]
#enmin = [get_enmin(x) for x in pot_singles]

