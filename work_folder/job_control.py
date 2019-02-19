#! /usr/bin/env python

import sys
import os
import shutil
import subprocess
import glob
import yaml

with open('/global/homes/m/mervyn/pot_dict.yml', 'r') as f:
    potdict = yaml.load(f)

""" 
This script is for KNL nodes VASP calculations

To modify according to different cluster
1. loc_in: global potcar locations
2. setkp_surf.py: main() function to create KPOINTS accordingly
3. auto.q format
4. INCAR.rlx and INCAR.stc setups
5. submit() function
6. check_converge.sh: change jobid format and check queue command

"""

loc_in = '/global/homes/m/mervyn/my_new_potcars'
loc_pbe = '/global/homes/m/mervyn/pot_pbe'

class DFTjob():
    def __init__(self, poscar, path='.', conf_lst=None, submit=False):
        if conf_lst == None:
            self.conf_lst = [ 'rlx', 'rlx2', 'stc' ]
        else:
            self.conf_lst = conf_lst
        self.name = '_'.join(poscar.split('_')[ 1: ])
        self.path = os.path.join(path, self.name)
        self.global_path = os.getcwd()
        self.submit = submit

        # Create the folder
        if not os.path.exists(self.path):
            print "Create a new job!"
            os.mkdir(self.path)
            shutil.copyfile(poscar, os.path.join(self.path, 'POSCAR')) 

    def setup(self):
        flag, conf = self.check_conf()
        cp = os.path.join(self.path, conf)
        
        print "Task: ", cp
        if flag == 0:
            print "    setting up jobs"
            self.create(conf)
        elif flag == 1:
            print "    currently running"
        elif flag == 2:
            print "    Calculation is not converged"
            self.restart(conf)
        elif flag == 3:
            print "    Converged"
        elif flag == 4:
            print "    Held"
            #self.restart(conf)
        else:
            print "    Something went wrong"

        self.conf = conf
        self.state = flag

    def check_conf(self):
        """
        Return state and configuration info
        state code:
        0: Empty
        1: Running
        2: Unconverged
        3: Converged
        4: Held
        """
        for c in self.conf_lst:
            cp = os.path.join(self.path, c)
            if not os.path.exists(cp):
                return 0, c
            else:
                os.chdir(cp)
                out = subprocess.check_output([os.path.join(self.global_path, 
                                                         'check_converge.sh'),
                                               os.path.join(self.global_path,
                                                         'current_running')])
                if "in queue" in out:
                    os.chdir(self.global_path)
                    return 1, c
                elif "False" in out:
                    os.chdir(self.global_path)
                    return 2, c
                elif "True" in out:
                    os.chdir(self.global_path)
                    continue
                else:
                    os.chdir(self.global_path)
                    print out
                    return 4, c
        return 3, c


    def create(self, conf, algo='Fast'):
        cp = os.path.join(self.path, conf) # Conf path

        if not os.path.exists(cp):
            os.mkdir(cp)

        p = self.path

        # POSCAR setup
        if self.conf_lst.index(conf) == 0:
            try: 
                shutil.copyfile(os.path.join(p, 'POSCAR'),
                                os.path.join(cp, 'POSCAR'))
            except:
                print "Not able to write POSCAR"
                shutil.rmtree(cp)
                return

        else:
            index = self.conf_lst.index(conf) - 1
            pp = os.path.join(p, self.conf_lst[ index ])
            try:
                shutil.copyfile(os.path.join(pp, 'CONTCAR'),
                                os.path.join(cp, 'POSCAR'))
            except:
                print "Not able to write POSCAR"
                shutil.rmtree(cp)
                return

        os.chdir(cp)

        # POTCAR setup
        self.set_potcar('POSCAR', 'POTCAR')

        # KPOINTS setup
        self.set_kpoints()

        # INCAR setup
        if 'rlx' in conf:
            with open(os.path.join(self.global_path, 'INCAR.rlx'), 'r') as f:
                incar_tmp = f.read()
        elif 'stc' in conf:
            with open(os.path.join(self.global_path, 'INCAR.stc'), 'r') as f:
                incar_tmp = f.read()

        incar = incar_tmp.format(algo=algo)

        with open('INCAR', 'w') as f:
            f.write(incar)
        

        # job_script setup
        with open(os.path.join(self.global_path, 'auto.q'), 'r') as f:
            text = f.read()

        if 'rlx' in conf:
            qfile = text.format(nodes='2', 
                                ntasks='128',
                                queuetype='regular', 
                                walltime='2:00:00')
        if 'stc' in conf:
            qfile = text.format(nodes='2', 
                                ntasks='128',
                                queuetype='regular', 
                                walltime='0:30:00')

        with open('auto.q', 'w') as f:
            f.write(qfile)

        # Submit job
        if self.submit == True:
            self.submitjob()

        os.chdir(self.global_path)

    def set_potcar(self, poscar_path, potcar_path):
        with open(poscar_path, 'r') as f:
            atm_pos = f.readlines()[5].strip().split()

        #pot_singles = [ os.path.join(loc_in, 'POTCAR_'+v) for v in atm_pos ]
        pot_singles = [ os.path.join(loc_pbe, potdict[v], 'POTCAR') for v in atm_pos ]
        cmd = 'cat '+' '.join(pot_singles)+' > '+os.path.join(potcar_path)
        os.system(cmd)

    def set_kpoints(self ):
        import setkp_surf as kp
        k = kp.main()


    def submitjob(self):
        os.system('sbatch auto.q > jobid')
        #os.system('tail -1 jobid')

    def reset(self, conf):
        """
        Resubmit current calculation
        """
        print "Not Implemented yet"
        return

    def restart(self, conf):
        """
        Restart current calculation
        """
        cp = os.path.join(self.path, conf) # Conf path
        cp_bk = os.path.join(self.path, conf+'_bk') # Conf path

        if os.path.exists(cp_bk):
            return

        print "    This will restart the calculation"

        os.rename(cp, cp_bk) # Rename the conf_files
        self.create(conf, algo='Normal') # Recreate the calculation



        # Remove the future calculations
        i = self.conf_lst.index(conf)
        try:
            cfs = self.conf_lst[i+1:]
            for cf in cfs:
                cpf = os.path.join(self.path, cf) # Conf path
                shutil.rmtree(cpf) # Remove the files 
        except:
            pass


if __name__ == "__main__":
    poscars = glob.glob('poscars/*')
    os.system('squeue -u mervyn > current_running')
    
    for p in poscars:
        d = DFTjob(p)
        d.submit = True
        d.setup()

        #d.submit = True
        #d.create(d.conf)
