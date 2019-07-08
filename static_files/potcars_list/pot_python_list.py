#! /usr/bin/python

import csv
import os 
import yaml
import json

elements = []
potcars = []

with open(os.path.dirname(os.path.realpath(__file__))+'/expt_dft_elements_SG.csv','r') as f:
    data = csv.reader(f,delimiter=',')
    next(data)
    for r in data:
        elements.append(r[0].split('_')[0])
        potcars.append(r[1])


pot_dict = dict((v,w) for v,w in zip(elements,potcars))

with open('pot_dict.yml','w') as fout:
    yaml.dump(pot_dict, fout, default_flow_style = False)

with open('pot_dict.json','w') as fout:
    json.dump(pot_dict, fout, indent=4)
