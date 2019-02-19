#!/usr/bin/python
# Modified by Mohan, July 31st, 2016
# Acknowledge to Jiangang He

import os
import sys
import numpy as np

class KPOINTS:
    def __init__(self):
        """
        Initialization
        Format: currentfile [FILE] [KPPRA] [k-point shift]
        (All the parameters are optional)
        Read POSCAR/CONTCAR, get KPPRA and k-point shift
        """
        if len(sys.argv) > 1 and not sys.argv[1].isdigit():
            f = open(sys.argv[1],'r')
            raw_in = sys.argv[2:]
        else:
            try:
                f = open('POSCAR', 'r') # default POSCAR/CONTCAR file
            except IOError:    
                print "Need input file, either POSCAR or CONTCAR!!!"
                exit()
            else:
                raw_in = sys.argv[1:]
        self.lat = f.readlines()
        f.close()

        try:
            in_param = map(int,raw_in)
        except:
            print "Check input format!!!"
            exit()

        if len(in_param) == 2:
            self.diff = min(in_param) # value of k-point shift
            self.kppra = max(in_param) # value of KPPRA
            # Here we assume kppra is always greater than diff 
        elif len(in_param) == 0:
            self.diff = 0
            self.kppra = 8000
        elif len(in_param) == 1:
            self.diff = 0
            self.kppra = in_param[0]
        else:
            print "Too many inputs!!!"
            exit()

        if self.kppra < 100:
            print "Too small KPRRA (increase input or modify source code)"
            exit()
        elif abs(self.diff)**3 > self.kppra:
            print "Dangerous amount of k-point shift"
            exit()

        self.kps = [0,0,0] # Initial k-points 

    def write_output(self, user_kps=[]):
        """
        KPOINTS file written format
        Input:
            :: user_kps :: list
        """
        if user_kps == []:
            kpoints = self.kps
        else:
            kpoints = user_kps
            
        if min(kpoints) > 0:
            fw = open('KPOINTS','w')
            fw.write('KPOINTS\n') 
            fw.write('0\n') 
            fw.write('Gamma\n')
            fw.write('%d %d %d\n' %tuple(kpoints))
            fw.write('0 0 0\n')
            fw.close()
        else:
            print "Non-positive k-point!! Refuse to write KPOINTS file!"
            exit()

    def get_kpoints(self,ifwrite='yes'):
        """
        Calculate k-points by a given KPPRA
        Write KPOINTS file
        """
        a11  = float(self.lat[2].split()[0])
        a12  = float(self.lat[2].split()[1])
        a13  = float(self.lat[2].split()[2])
        a21  = float(self.lat[3].split()[0])
        a22  = float(self.lat[3].split()[1])
        a23  = float(self.lat[3].split()[2])
        a31  = float(self.lat[4].split()[0])
        a32  = float(self.lat[4].split()[1])
        a33  = float(self.lat[4].split()[2])
        
        x0 = [a11, a12, a13]
        x1 = [a21, a22, a23]
        x2 = [a31, a32, a33]
        
        self.natom = sum(map(int,self.lat[6].split()))
        # Number of atoms in POSCAR/CONTCAR
        
        l0 = np.linalg.norm(x0)
        l1 = np.linalg.norm(x1)
        l2 = np.linalg.norm(x2)

        self.cell_norm = [l0, l1, l2]
        
        N = (l0*l1*l2*self.kppra/self.natom)**(1.0/3.0)
        
        k0 = int(N/l0)
        k1 = int(N/l1)
        k2 = int(N/l2)

        klist = [k0,k1,k2]
        flag = 0
        kn = klist[:]

        if len(set(klist)) == 1:
            if (np.prod(np.array(kn))*self.natom) < self.kppra:
                kn = [v+1 for v in kn]
        elif len(set(klist)) == 3:
            while (np.prod(np.array(kn))*self.natom) < self.kppra and flag < 3:
                kn[klist.index(sorted(klist)[flag])] += 1
                flag += 1
        else:
            while (np.prod(np.array(kn))*self.natom) < self.kppra and flag < 2:
                tmp = sorted(set(klist))[flag]
                tmp_ind = []
                for i in range(3):
                    if klist[i] == tmp:
                        tmp_ind.append(i)
                kn = [kn[i]+1 if i in tmp_ind else kn[i] for i in range(3)]
                flag += 1

        self.kps = kn
                 
        if (np.prod(np.array(kn))*self.natom) < self.kppra:
            print "===== WARNING ====="
            print "K-points generate method may not be appropriate!"
            print "Check source code!!!!"
            print "==================="
            exit()

        #if ifwrite == 'yes':
        #    self.write_output()

    def modification_to_surface(self):
        vaxis = self.cell_norm.index(max(self.cell_norm))
        self.kps[ vaxis ] = 1

    def delta_kpoints(self):
        """
        Shift k-points
        Write KPOITNS file
        """
        self.get_kpoints('no')
        ori_kp = self.kps
        omk = min(ori_kp)
        nmk = omk+self.diff
        self.kps = [v*nmk/omk for v in ori_kp]
        self.write_output()
    
def main(kppra, ifsurf, user_kps=[], diff=0):
    kc = KPOINTS()
    kc.kppra = kppra
    kc.diff = diff

    if kc.diff == 0:
        kc.get_kpoints()
        if ifsurf:
            kc.modification_to_surface()
        kc.write_output(user_kps)

    else:
        kc.delta_kpoints()
        if ifsurf:
            kc.modification_to_surface()
        kc.write_output(user_kps)
