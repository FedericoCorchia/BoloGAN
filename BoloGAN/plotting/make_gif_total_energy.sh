#!/bin/bash
source ../utils/config.sh
echo $GAN_name


gif_dir=${input_dir_gan}/gif_tot_energy/
mkdir -p ${gif_dir}/png
mkdir -p ${gif_dir}/pdf
mkdir -p ${gif_dir}/C
mkdir -p ${gif_dir}/eps
MaxRuntime=30*60*60 

echo Create log dir
log_dir=log
rm -rf ${log_dir}
mkdir -p ${log_dir}

echo Create error dir
error_dir=error
rm -rf ${error_dir}
mkdir -p ${error_dir}

echo Create output dir
output_dir=output
rm -rf ${output_dir}
mkdir -p ${output_dir}

echo Create script dir
script_dir=scripts
mkdir -p ${script_dir}



echo " Running in: $PWD"

particle="photons"

tag_log=gif_${particle}_${minEta}_${maxEta}
output_file=${output_dir}/${tag_log}.out
script=${script_dir}/${tag_log}.sh
log_file=${log_dir}/${tag_log}.log
error_file=${error_dir}/${tag_log}.error
condor_template=condorTEMPLATE.sub
condor_file=${script_dir}/condor_${tag_log}.sub

cp $condor_template ${condor_file}
    
sed -i "s!@SCRIPT@!${script}!g" ${condor_file}
sed -i "s!@LOG@!${log_file}!g" ${condor_file}
sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
sed -i "s!@MEM@!${memory}!g" ${condor_file}
sed -i "s!@TAG@!${tag_log}!g" ${condor_file}
sed -i "s!@MAIL@!${USER}@cern.ch!g" ${condor_file}    


      

cat > $script << EOF
#!/bin/bash


time python3 ${PWD}/plots_totalenergy_gif.py -emin $min_epoch -emax $max_epoch -step $step -b ${binningFile} -norm ${norm} -l ${label} -idg ${input_dir_checkpoint} -v ${input_dir} -p ${pid} -e1 ${minEta} -e2 ${maxEta}  -o ${gif_dir}


EOF

    echo $script
    chmod 775 $script
   ./${script}
   condor_submit ${condor_file}
