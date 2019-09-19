#! /usr/bin/env python

import sys
import os
import shutil
import subprocess
import glob
import json

## Absolute path of your pot_dict.json file
with open('static_files/pot_dict.json', 'r') as f:
    potdict = json.load(f)

## Collect user information from json
with open('user_info.json', 'r') as f:
    info = json.load(f)

personal_alloc = info['personal_alloc']
loc_pbe = info['pot_pbe_path'] 
USER_name = info['user_name']

class DFTjob(object):
    """
    Main class to create a DFT job
    """
    def __init__(self, poscar, path='.', conf_lst=None, submit=False, from_scratch=False):
        if conf_lst == None:
            self.conf_lst = [ 'rlx', 'rlx2', 'stc' ]
        else:
            self.conf_lst = conf_lst
        self.name = '_'.join(poscar.split('_')[ 1: ])
        self.path = os.path.join(path, self.name)
        self.global_path = os.getcwd()
        self.submit = submit

        if from_scratch:
            self.hard_cleanup()

        # Create the folder
        if not os.path.exists(self.path):
            print("Create a new folder: ", self.path)
            os.mkdir(self.path)
            shutil.copyfile(poscar, os.path.join(self.path, 'POSCAR')) 

    def setup(self, **kwargs):
        """
        Set up jobs according to the calculation state
        """
        flag, conf = self.check_conf()
        cp = os.path.join(self.path, conf)
        
        print("Task: ", cp)
        if flag == 0:
            print("    setting up jobs")
            self.create(conf, **kwargs)
        elif flag == 1:
            print("    currently running")
        elif flag == 2:
            print("    Calculation is not converged")
            self.restart(conf, **kwargs)
        elif flag == 3:
            print("    Converged")
        elif flag == 4:
            print("    Held")
            #self.restart(conf)
        else:
            print("    Something went wrong")

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
                out = subprocess.check_output(['../../check_converge.sh','../../current_running']).decode("utf-8") 
                
                if "in queue" in out:
                    os.chdir(self.global_path)
                    return 1, c
                elif "False" in out:
                    os.chdir(self.global_path)
                    return 2, c
                elif "True" in out:
                    os.chdir(self.global_path)
                    continue
                elif "No jobid stored" in out:
                    print("No job submitted!")
                    os.chdir(self.global_path)
                    return 4, c
                else:
                    os.chdir(self.global_path)
                    print(out)
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
        if self.conf_lst.index(conf) == 0: # if still on relax
            if os.path.exists(os.path.join(self.path,conf+'_bk')): # if there is a backup file (if this is a restart)
                backup_count = 2
                while os.path.exists(os.path.join(self.path,conf+'_bk_'+str(backup_count))): # finds most recent backup (higher # = more recent)
                    backup_count += 1
                if os.path.exists(os.path.join(self.path,conf+'_bk_'+str(backup_count-1))): # checks if there are multiple backups
                    path_to_contcar = os.path.join(self.path,conf+'_bk_'+str(backup_count-1))
                else: path_to_contcar = os.path.join(self.path,conf+'_bk')
                try:
                    if os.stat(os.path.join(path_to_contcar,'CONTCAR')).st_size != 0:
                        print('     Starting from previous CONTCAR...')
                        shutil.copyfile(os.path.join(path_to_contcar,'CONTCAR'),os.path.join(cp,'POSCAR'))
                    else:
                        shutil.copyfile(os.path.join(p,'POSCAR'),os.path.join(cp,'POSCAR'))
                except:
                    shutil.copyfile(os.path.join(p,'POSCAR'),os.path.join(cp,'POSCAR'))
            else: #if there is no backup file (brand new calculation) 
                try: 
                    shutil.copyfile(os.path.join(p, 'POSCAR'),
                                os.path.join(cp, 'POSCAR'))
                except:
                    print("Not able to write POSCAR")
                    shutil.rmtree(cp)
                    return

        else:
            index = self.conf_lst.index(conf) - 1
            pp = os.path.join(p, self.conf_lst[ index ])
            try:
                shutil.copyfile(os.path.join(pp, 'CONTCAR'),
                                os.path.join(cp, 'POSCAR'))
            except:
                print("Not able to write POSCAR")
                shutil.rmtree(cp)
                return

        os.chdir(cp)

        # POTCAR setup
        self.set_potcar('POSCAR', 'POTCAR')

        # KPOINTS setup
        self.set_kpoints(**kwargs)

        # INCAR setup
        if 'rlx' in conf:
            with open(self.global_path+'/static_files/INCAR.rlx', 'r') as f:
                incar_tmp = f.read()
        elif 'stc' in conf:
            with open(self.global_path+'/static_files/INCAR.stc', 'r') as f:
                incar_tmp = f.read()

        npar = kwargs.get('npar', 1)
        kpar = kwargs.get('kpar', 4)
        gga = kwargs.get('gga', 'PE')
        encut = kwargs.get('encut', 520)
        isif = kwargs.get('isif', 3)

        # consider spin polarization
        if_spin = kwargs.get('if_spin', 'auto')
        if if_spin == 'auto':
            spin_tag, magmom_str = self.set_magmom('POSCAR')
            if spin_tag == 1: 
                ispin = 'ISPIN = 1'
                magmom = ''
            elif spin_tag == 2:
                ispin = 'ISPIN = 2'
                magmom = 'MAGMOM = {}'.format(magmom_str)
        elif if_spin == 'no':
            ispin = 'ISPIN = 1'
            magmom = ''
        elif if_spin == 'yes':
            spin_tag, magmom_str = self.set_magmom('POSCAR')
            ispin = 'ISPIN = 2'
            mamgom = 'MAGMOM = {}'.format(magmom_str)


        incar = incar_tmp.format(algo=algo, npar=npar, kpar=kpar, isif=isif,
                                 ispin=ispin, magmom=magmom, gga=gga, encut=encut)

        with open('INCAR', 'w') as f:
            f.write(incar)

        # job_script setup
        with open(self.global_path+'/static_files/auto.q', 'r') as f:
            text = f.read()
        name = self.name
        nodes = kwargs.get('nodes', 4)
        ntasks = kwargs.get('ntasks', 32)
        key = kwargs.get('key', personal_alloc)
        if 'rlx' in conf:
            queuetype = kwargs.get('queuetype','Normal')
            walltime = kwargs.get('walltime', '24:00:00')
        elif 'stc' in conf:
            queuetype = kwargs.get('queuetype','short')
            walltime = kwargs.get('walltime', '4:00:00')

        qfile = text.format(nodes=nodes, 
                            ntasks=ntasks,
                            name=name,
                            queuetype=queuetype,
                            key=key,
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

    def set_magmom(self, poscar_path):
        """
        Set up MAGMOM tag
        Return spin_tag (int: 1 or 2), magmom_str (string)
        """
        with open(poscar_path, 'r') as f:
            lines = f.readlines()
            atm_pos = lines[5].strip().split()
            atm_num = list(map(int, lines[6].strip().split()))

        with open(self.global_path+'/static_files/element_elec.csv', 'r') as f:
            lines = f.readlines()
            d_elec_dict = {}
            f_elec_dict = {}
            for l in lines[1:]:
                e, d, f = l.strip().split(',')
                d_elec_dict[e] = int(d)
                f_elec_dict[e] = int(f)

        spin_tag = 1
        magmom_str = ''
        for a, n in zip(atm_pos, atm_num):
            if d_elec_dict[a] > 0 and d_elec_dict[a] < 10:
                spin_tag = 2
                magmom_str += '{}*{:.3f} '.format(n, 5)
            elif f_elec_dict[a] > 0 and f_elec_dict[a] < 14:
                spin_tag = 2
                magmom_str += '{}*{:.3f} '.format(n, 7)
            else:
                magmom_str += '{}*{:.3f} '.format(n, 0)

        return spin_tag, magmom_str.strip()


    def set_kpoints(self, **kwargs):
        """ 
        Set up KPOINTS file
        """
        from helper_functions import setkp_surf as kp

        kppra = kwargs.get('kppra', 8000)
        ifsurf = kwargs.get('ifsurf', False)
        user_kps = kwargs.get('user_kps', [])

        kp.main(kppra=kppra, ifsurf=ifsurf, user_kps=user_kps)

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
        print("Not Implemented yet")
        return

    def restart(self, conf, **kwargs):
        """
        Restart current calculation
        """
        cp = os.path.join(self.path, conf) # Conf path
        cp_bk = os.path.join(self.path, conf+'_bk') # Conf path

        if os.path.exists(cp_bk):
            backup_count = 2
            while os.path.exists(cp_bk+'_'+str(backup_count)):
                backup_count += 1
            
            if backup_count > 10:
                print('THERE IS SOMETHING WRONG!!! ***')
                return
            name = cp_bk+'_'+str(backup_count)
            os.rename(cp,name)
            print('Made new backup ' + str(name))
            
        else:
            print("    This will restart the calculation")
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

    def hard_cleanup(self):
        """
        Dangerous! This will remove all calculation folders.
        """
        if os.path.exists(self.path):
            shutil.rmtree(self.path) # Remove the files 

if __name__ == "__main__":
    poscars = glob.glob('poscars/POSCAR*')
    os.system('squeue -u ' + USER_name + ' > current_running')
    submit_tag = True
    ans = input("Submit jobs? <YES> or others:")
    if ans == 'YES':
        print("Let's submit all jobs!")
        submit_tag = True
    else:
        print("No job will be submitted")
        submit_tag = False
        print()
    print('All activity will be written to log.txt...')
    # Get kwargs from kwargs.json file
    with open('kwargs.json', 'r') as kj:
        kwargs = json.load(kj)
    with open('log.txt', 'w+') as f:
        sys.stdout = f   
        for p in poscars:
            # Create DFT task object, conf list can include as many rlx steps as desired
            d = DFTjob(p, conf_lst=['rlx', 'rlx2', 'stc'])

            # Kwargs for this DFT task
            """
            DEFAULT Settings:
                kppra: 8000                     # KPPRA for KPOINTS
                encut: 520                      # ENCUT in INCAR
                isif: 3                         # ISIF in INCAR
                npar: 1                         # NPAR in INCAR
                kpar: 4                         # KPAR in INCAR
                gga: 'PE'                       # GGA in INCAR
                user_kps: []                    # User defined KPONINTS
                ifsurf: False                   # modify KPOINTS if it is a surface slab
                nodes: 1                        # Number of nodes per job
                ntasks: 28                      # Number of tasks per job (number of nodes * 28/24/20)
                queuetype: 'short'              # queue type (short, normal, long, etc)
                key: personal_alloc             # personal allocation on quest
                walltime: '2:00:00'             # walltime: '2:00:00' for relaxation, '0:30:00' for static 
                ifspin: 'auto'                  # whether spin polarization is considered ('auto', 'yes', 'no')
            """
            # Whether or not to submit the job right away
            d.submit = submit_tag

            # Create input files 
            d.setup(**kwargs)
