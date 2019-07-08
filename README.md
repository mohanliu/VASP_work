# VASP_work

### Major Updates:
- Now support python 3.0+. **No longer** support python 2.7.


### copy files in **'work_folder/'** to a working directory
- Put POSCAR files into **'poscars/'** folder
- Set up POTCAR repository
  - Download POTCAR files and save to **'pot_pbe/'** in your home directory. 
  - Change absolute path of your **pot_pbe/** in **job_control.py** file (line 17).  
- Make **check_converge.sh** executable by typing `chmod +x check_converge.sh`
- Change *kwargs* in **job_control.py**
- Set up jobs by typing `python job_control.py`


