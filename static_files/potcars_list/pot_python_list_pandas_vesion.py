#! /usr/bin/python

import csv
import pandas as pd

df = pd.read_csv('expt_dft_elements_SG.csv')
num = df.shape[0]
name = df.columns

elements = map(lambda x: x.split('_')[0],df[name[0]].values.tolist())
potcars = df[name[1]].values.tolist()

pot_dict = dict((v,w) for v,w in zip(elements,potcars))
