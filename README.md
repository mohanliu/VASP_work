# VASP_work

### copy files in **'work_folder/'** to a working directory
- Put POSCAR files into **'poscars/'** folder
- Set up POTCAR repository
  - Download POTCAR files and save to **'pot_pbe/'** in your home directory. 
  - Copy **pot_dict.yml** from **potcar_folder/** to your home directory as well. (**pot_dict.yml** can be created in **potcar_folder/potcars_list/** by typing `python pot_python_list.py`.) 
  - Change absolute path of your **pot_dict.yml** in **job_control.py** file (line 11).
  - Change absolute path of your **pot_pbe/** in **job_control.py** file (line 15).  
- Make **check_converge.sh** executable by typing `chmod +x check_converge.sh`
- Change *kwargs* in **job_control.py**
- Set up jobs by typing `python job_control.py`


##### *Note: All python scripts here a written using python 2.7*  
