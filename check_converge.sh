#! /bin/bash

if [ -f jobid ]
    then
    jobid=`tail -1 jobid|awk '{print $4}'`
else
    echo No jobid stored
    exit
fi

if [ -z $jobid ]
    then
    exit
fi

js=`grep $jobid $1|wc -l`

if [[ $js == 0 ]]
    then
    nsw_steps=`grep "F=" OSZICAR |wc -l`

    if [[ $(grep "NELM *=" INCAR |wc -l) == 0 ]]
        then 
        nelm=60
    else
        nelm=`grep "NELM *=" INCAR |awk -F= '{print $2}' |sed 's/ *//g'`
    fi

    if [[ $(grep "NSW *=" INCAR |wc -l) == 0 ]]
        then 
        nsw=60
    else
        nsw=`grep "NSW *=" INCAR |awk -F= '{print $2}' |sed 's/ *//g'`
    fi

    if [ -f OUTCAR ]
        then
        ionic_cvg=`grep "reached required" OUTCAR |wc -l`
        elec_ucvg=`grep "aborting loop EDIFF was not reached (unconverged)" OUTCAR |wc -l`
        elec_cvg=`grep "aborting loop because EDIFF is reached" OUTCAR |wc -l`
    elif [ -f OUTCAR.gz ]
        then
        ionic_cvg=`zgrep "reached required" OUTCAR.gz |wc -l`
        elec_ucvg=`zgrep "aborting loop EDIFF was not reached (unconverged)" OUTCAR.gz |wc -l`
        elec_cvg=`zgrep "aborting loop because EDIFF is reached" OUTCAR.gz |wc -l`
    fi
    if [[ $ionic_cvg == 1 ]]
        then
        if [[ $elec_ucvg -ge $nsw_steps ]]
            then 
            echo False
        else
            echo True
        fi
    elif [[ $nsw == 0 ]]
        then
        if [[ $elec_cvg == 1 ]]
            then
            steps=`grep "^.*:" OSZICAR |tail -1 |awk -F: '{print $2}' |awk '{print $1}'`
            if [[ $nelm == $steps ]]
                then
                echo "False"
            else
                echo "True (Electronic)"
            fi
        else
            echo False
        fi
    else
        echo False
    fi
else
    echo Job is still in queue.
fi
