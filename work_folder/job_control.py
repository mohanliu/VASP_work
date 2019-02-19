#! /usr/bin/env python

import sys
import os
import shutil
import subprocess
import glob
import yaml

USER_name = 'mervyn' 

## Absolute path of your pot_dict.yml file
with open('/global/homes/'+USER_name[0]+'/'+USER_name+'/pot_dict.yml', 'r') as f:
    potdict = yaml.load(f)

## Absolute path of your POTCARs folder    
loc_pbe = '/global/homes/'+USER_name[0]+'/'+USER_name+'/pot_pbe'

class DFTjob():
    """
    Main class to create a DFT job
    """
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

    def setup(self, **kwargs):
        """
        Set up jobs according to the calculation state
        """
        flag, conf = self.check_conf()
        cp = os.path.join(self.path, conf)
        
        print "Task: ", cp
        if flag == 0:
            print "    setting up jobs"
            self.create(conf, **kwargs)
        elif flag == 1:
            print "    currently running"
        elif flag == 2:
            print "    Calculation is not converged"
            self.restart(conf, **kwargs)
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


    def create(self, conf, algo='Fast', **kwargs):
        """
        Create input files for a VASP calculation
        Note: Create a Job using ALGO=Fast!
        """
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
        self.set_kpoints(**kwargs)

        # INCAR setup
        if 'rlx' in conf:
            with open(os.path.join(self.global_path, 'INCAR.rlx'), 'r') as f:
                incar_tmp = f.read()
        elif 'stc' in conf:
            with open(os.path.join(self.global_path, 'INCAR.stc'), 'r') as f:
                incar_tmp = f.read()

        npar = kwargs.get('npar', 2)
        kpar = kwargs.get('kpar', 8)
        gga = kwargs.get('gga', 'PE')
        encut = kwargs.get('encut', 400)
        incar = incar_tmp.format(algo=algo, npar=npar, kpar=kpar,
                                 gga=gga, encut=encut)

        with open('INCAR', 'w') as f:
            f.write(incar)
        

        # job_script setup
        with open(os.path.join(self.global_path, 'auto.q'), 'r') as f:
            text = f.read()

        queuetype = kwargs.get('queuetype', 'regular')
        nodes = kwargs.get('nodes', 2)
        ntasks = kwargs.get('ntasks', 128)
        if 'rlx' in conf:
            walltime = kwargs.get('walltime', '2:00:00')
        elif 'stc' in conf:
            walltime = kwargs.get('walltime', '0:30:00')

        qfile = text.format(nodes=nodes, 
                            ntasks=ntasks,
                            queuetype=queuetype,
                            walltime=walltime)

        with open('auto.q', 'w') as f:
            f.write(qfile)

        # Submit job
        if self.submit == True:
            self.submitjob()

        os.chdir(self.global_path)

    def set_potcar(self, poscar_path, potcar_path):
        """
        Set up POTCAR file
        """
        with open(poscar_path, 'r') as f:
            atm_pos = f.readlines()[5].strip().split()

        pot_singles = [ os.path.join(loc_pbe, potdict[v], 'POTCAR') for v in atm_pos ]
        cmd = 'cat '+' '.join(pot_singles)+' > '+os.path.join(potcar_path)
        os.system(cmd)

    def set_kpoints(self, **kwargs):
        """ 
        Set up KPOINTS file
        """
        import setkp_surf as kp
        kppra = kwargs.get('kppra', 4000)
        ifsurf = kwargs.get('ifsurf', False)
        k = kp.main(kppra, ifsurf)


    def submitjob(self):
        """
        Submit jobs (according to current NERSC job scheduling system)
        """
        os.system('sbatch auto.q > jobid')
        #os.system('tail -1 jobid')

    def reset(self, conf):
        """
        Resubmit current calculation
        """
        print "Not Implemented yet"
        return

    def restart(self, conf, **kwargs):
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
    os.system('squeue -u ' + USER_name + ' > current_running')
    
    for p in poscars:
        # Create DFT task object
        d = DFTjob(p, conf_lst=['rlx', 'rlx2', 'stc'])

        # Kwargs for this DFT task
        kwargs = {'kppra': 4000,  # KPPRA for KPOINTS
                  'ifsurf': True, # modify KPOINTS if it is a surface slab
                  'nodes': 2,     # Number of nodes per job
                  'ntasks': 128,  # Number of tasks per job (64 cpus per node)
                  'queuetype': 'regular', # queue type (regular, debug, etc)
                  'npar': 2,      # NPAR in INCAR
                  'kpar': 8,      # KPAR in INCAR
                  'encut': 400,   # ENCUT in INCAR
                  'gga': 'PE'     # GGA in INCAR
        }

        # Whether or not to submit the job right away
        #d.submit = True

        # Create input files 
        d.setup(**kwargs)
