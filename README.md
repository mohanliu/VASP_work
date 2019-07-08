# VASP_work

## Major Updates:
- Now support python 3.0+. **No longer** support python 2.7.

## Setting up your jobs
- Put POSCAR files into *`poscars/`* folder
- Download POTCAR files into a folder
- Make **check_converge.sh** executable by `chmod +x check_converge.sh`
- Prepare *`user_info.json`* file:
  - `user_name`: your user name on quest
  - `pot_pbe_path`: the absolute path to your POTCAR folder
  - `personal_alloc`: your personal allocation id
- Prepare *`kwarg.json`* file accordingly (Default settings can be found below) 
- Set up jobs by `python job_control.py`
- Collect your results into json file by `python output_results.py`
