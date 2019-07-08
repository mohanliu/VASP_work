# VASP_work

## Major Updates:
- Now support python 3.0+. **No longer** support python 2.7.
- Only support job submission on Quest. Contact me if you need to run this on other servers.

## Setting up your jobs
- Put POSCAR files into *`poscars/`* folder
- Download POTCAR files into a folder
- Make **check_converge.sh** executable by `chmod +x check_converge.sh`
- Prepare *`user_info.json`* file:
  - `user_name`: your user name on quest
  - `pot_pbe_path`: the absolute path to your POTCAR folder
  - `personal_alloc`: your personal allocation id
- Prepare *`kwarg.json`* file accordingly (Default settings can be found [below](https://github.com/mohanliu/VASP_work/blob/master/README.md#default-kwargs-settings)) 
- Set up jobs by `python job_control.py`
- Collect your results into json file by `python output_results.py`

### DEFAULT *kwargs* Settings:
- `kppra: 8000` 
    - KPPRA for KPOINTS
- `encut: 520`
    - ENCUT in INCAR
- `isif: 3`
    - ISIF in INCAR
- `npar: 1`
    - NPAR in INCAR
- `kpar: 4`
    - KPAR in INCAR
- `gga: 'PE'`
    - GGA in INCAR
- `user_kps: []`
    - User defined KPONINTS
- `ifsurf: False`
    - modify KPOINTS if it is a surface slab
- `nodes: 1`
    - Number of nodes per job
- `ntasks: 28`
    - Number of tasks per job (number of nodes * 28/24/20)
- `queuetype: 'short'`
    - queue type (short, normal, long, etc)
- `key: personal_alloc`
    - personal allocation on quest
- `walltime: '2:00:00'`
    - walltime: '2:00:00' for relaxation, '0:30:00' for static 
- `ifspin: 'auto'`
    - whether spin polarization is considered ('auto', 'yes', 'no')
