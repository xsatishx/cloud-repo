#!/bin/bash
####!/bin/bash -ex

# bash -x download_and_stats_FASTQ.sh > debug.log 2>&1 # run like this for verbose debugging

# use "-c" to clean

# This is a script that will
# downnload the two FASTQ for a mate pair
# tar them
# get md5 and size of the FASTQ and tar for ARKs
# analyze the tar with Stuti's docker
# save the genes.fpkm_tracking in a path suitable for subsequent processing with
# R script combine_docker_outputs.r

# input args
my_list=${1:-"err_list_1_of_4.11-18-15.txt.test"}; # list with two samples for testing (4 FASTQ)

# variables
#my_list="";
#my_list="err_list_1_of_4.11-18-15.txt.test"; # list with two samples for testing (4 FASTQ)
my_fastq_log=$my_list.FASTQ_log.txt;
my_tar_log=$my_list.tar_log.txt;
my_run_log=$my_list.run_log.txt;
my_error_log=$my_list.error_log.txt;
my_save_dir="/mnt/saved_docker_outputs/";

# write header for logs
echo "file_name\toriginal_url\tbasename\tmd5\tsize" > $my_fastq_log;
echo "" >> $my_fastq_log;
echo "file_name\toriginal_url\tbasename\tmd5\tsize" > $my_tar_log;
echo "" >> $my_tar_log;
echo "### Run log for processing of $my_list ###" > $my_run_log;
echo "" >> $my_run_log;
echo "list:            "$my_list >> $my_run_log;
if [[ $2 = "-c" ]]; then
     echo "clean:           ON" >> $my_run_log;
else
     echo "clean:           OFF" >> $my_run_log;
fi
echo "clean:"
echo "### Error log for processing of $my_list ###" > $my_error_log;
echo "" >> $my_error_log;
echo "save_dir:        $my_save_dir"       >> $my_run_log;

# create a directory for the outputs
mkdir -p $my_save_dir;

# move to /mnt/SCRATCH - where Stuti's docker expects the data to be
cd /mnt/SCRATCH/;

for i in `cat $my_list`;

# retireve targets from list - generate local filenames	 
do mate_1=`echo $i | cut -f 1 -d ":"`;
   mate_2=`echo $i | cut -f 2 -d ":"`;
   mate_1_basename=`basename $mate_1`;
   mate_2_basename=`basename $mate_2`;
   pair_name=`echo $mate_1_basename | cut -f 1 -d "_"`;
   tar_name=$pair_name.fastq.tar.gz;
   echo "processing:      $pair_name"       >> $my_run_log;
   echo "pair_name:       $pair_name"       >> $my_run_log;
   echo "mate_1:          $mate_1"          >> $my_run_log;
   echo "mate_1_basename: $mate_1_basename" >> $my_run_log;
   echo "mate_2:          $mate_2"          >> $my_run_log;
   echo "mate_1_basename: $mate_2_basename" >> $my_run_log;
   echo "tar_name:        $tar_name"        >> $my_run_log;

   # download both members of the mate pair
   echo "downloading $mate_1" >> $my_run_log;
   #wget $mate_1 2 >> $my_error_log 1 >> $my_run_log; # this causes an error
   wget $mate_1;
   echo "DONE downloading $mate_1" >> $my_run_log;
   echo "downloading $mate_2" >> $my_run_log;
   wget $mate_2;
   echo "DONE downloading $mate_2" >> $my_run_log;

   # create tar from individual mates
   echo "creating tar $tar_name" >> $my_run_log;
   tar -zcf $tar_name $mate_1_basename $mate_2_basename;
   echo "DONE creating tar $tar_name" >> $my_run_log;

   # get md5s
   echo "calculating md5's" >> $my_run_log;
   md5_mate1=`md5sum $mate_1_basename | cut -f1 -d " "`; # 2>> $my_error_log 1 >> $my_run_log;
   md5_mate2=`md5sum $mate_2_basename | cut -f1 -d " "`; # 2>> $my_error_log 1 >> $my_run_log;
   md5_tar=`md5sum $tar_name | cut -f1 -d " "`; # 2>> $my_error_log 1 >> $my_run_log;
   echo "DONE calculating md5's" >> $my_run_log;
   
   # get sizes
   echo "calculating sizes" >> $my_run_log;
   size_mate1=`stat -c%s $mate_1_basename`; # 2>> $my_error_log 1 >> $my_run_log;
   size_mate2=`stat -c%s $mate_2_basename`; # 2>> $my_error_log 1 >> $my_run_log;
   size_tar=`stat -c%s $tar_name`; # 2>> $my_error_log 1 >> $my_run_log;
   echo "DONE calculating sizes" >> $my_run_log;
   
   # print values to logs
   echo "printing calculated values to logs" >> $my_run_log;
   echo $mate_1_basename\t$mate_1\t$mate_1_basename\t$md5_mate1\t$size_mate1 >> $my_fastq_log; # mate_1 FASTQ;
   echo "DONE printing stats of $mate_1_base" >> $my_run_log;
   echo $mate_2_basename\t$mate_2\t$mate_2_basename\t$md5_mate2\t$size_mate2 >> $my_fastq_log; # mate_2 FASTQ;
   echo "DONE printing stats of $mate_2_basename" >> $my_run_log;
   echo $tar_name\t"NA"\t$pair_name\t$md5_tar\t$size_tar >> $my_tar_log; # tar created from mate_1 and mate_2
   echo "DONE printing calculated values to logs" >> $my_run_log;
   
   # Run Stuti's tool
   ## populate the filenames_1.txt file with a single jobname
cat >filenames_1.txt<<EOF
$pair_name.fastq.tar.gz
EOF
   ## run load and run the docker tool
   echo "running the Docker..." >> $my_run_log;

   # start sudo su
   # tmux;
   # sudo su;
   sduo docker load -i /mnt/star_cuff_docker_1.8.tar;
   sudo python run_docker.py;
   #sudo -k;
   echo "DONE with Docker processing" >> $my_run_log;
   # get the output
   echo "saving Docker output" >> $my_run_log;
   ## mkdir for output that my R script can use to combine outputs later
   sudo mkdir -p $my_save_dir$pair_name/star_2_pass/;
   ## move the genes.fpkm_tracking file to the save location
   echo "DOING THIS:" >> $my_run_log;
   echo "sudo cp /mnt/SCRATCH/geuvadis_results/$pair_name/star_2_pass/genes.fpkm_tracking $my_save_dir$pair_name/star_2_pass/" >> $my_run_log;
   sudo cp /mnt/SCRATCH/geuvadis_results/$pair_name/star_2_pass/genes.fpkm_tracking $my_save_dir$pair_name/star_2_pass/genes.fpkm_tracking
   echo "DONE saving Docker output" >> $my_run_log;
   
   # cleanup (if flag is used)
   if [[ $2 = "-c" ]]; then
       echo "cleanup" >> $my_run_log;
       sudo rm -R /mnt/SCRATCH/geuvadis_results/$pair_name;
       sudo rm $mate_1_basename;
       sudo rm $mate_2_basename;
       echo "Done with cleanup" >> $my_run_log;
   else
       echo "No cleanup" >> $my_run_log;
   fi

   # copy current logs to the output directory
   echo "copying logs" >> $my_run_log;
   sudo cp $my_fastq_log $my_save_dir/;
   sudo cp $my_tar_log $my_save_dir/;
   sudo cp $my_error_log $my_save_dir/;
   sudo cp $my_run_log $my_save_dir/;
   echo "Done copying logs" >> $my_run_log;
   
   echo "ALL DONE WITH  $pair_name" >> $my_run_log;

   # close sudo su
   # sudo -k;
   # close tmux session
   # exit;
   
done;

echo "" >> $my_run_log
echo "ALL DONE PROCESSING $my_list" >> $my_run_log

