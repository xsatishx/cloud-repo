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

# 12-7-15 Notes:
# As of now this script can download data via FTP (probably Parcel too - have to check), tar mate pairs, apply Stuti's docker, and
# saves selected output from the docker to local disk (just the fpkm abundancees for the genes) 
# FEATURES TO TEST
# - Parcel download [DONE]
# FEATREUS TO ADD
# - ARK parsing [DONE]
# - Parcel upload 
# - Parcel stats
# - select data products to upload
# - make name of output generic (edit in Stuti's script run_docker.py )
# - list of results to upload as separated list
# - generalize the results folder (from geuvadis_results)
# OTHER THINGS TO UPDATE
# - Zhenyu suggested that you limit the reference database to only consider
#     entries that are for protein encoding genes
# - Separate script to automate creation and editing of reference
#     from Stuti's notes and Zhenyu's suggestion above

# Set defaults
LIST="err_list_1_of_4.11-18-15.txt.test";
USEPROXY=0;
SAVEDIR="/home/ubuntu/SCRATCH/saved_results";
TEMPDIR="/home/ubuntu/SCRATCH/";
PYTHONSCRIPT="/home/ubuntu/git/CDIS_GEUVADIS_analysis/run_docker.py";
DOCKERTAR="/home/ubuntu/SCRATCH/star_cuff_docker_1.8.tar";
PARCELIP="192.170.232.76";
ARKPREFIX="ftp";

# Parse input options
while getopts ":l:s:t:p:d:xcdh" opt; do
    case $opt in
	l)
	    echo "-l was triggered, Parameter: $OPTARG" >&2
	    LIST=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	x)
	    echo "-x was triggered, Parameter: $OPTARG" >&2
	    USEPROXY=1;
	    ;;
	s)
	    echo "-s was triggered, Parameter: $OPTARG" >&2
	    SAVEDIR=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	t)
	    echo "-t was triggered, Parameter: $OPTARG" >&2
	    TEMPDIR=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	p)
	    echo "-p was triggered, Parameter: $OPTARG" >&2
	    PYTHONSCRIPT=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	d)
	    echo "-d was triggered, Parameter: $OPTARG" >&2
	    DOCKERTAR=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	i)
	    echo "-i was triggered, Parameter: $OPTARG" >&2
	    PARCELIP=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	a)
	    echo "-a was triggered, Parameter: $OPTARG" >&2
	    ARKPARSE=1
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	b)
	    echo "-b was triggered, Parameter: $OPTARG" >&2
	    ARKPREFIX=$OPTARG
	    if [[ "$ARKPREFIX" != "ftp" && "$ARKPREFIX" != "s3" ]] ; then # reject invalid ARK prefix values
		echo "\"ftp\" and \"s3\" are the only accepted values for -b|--arkprefix"
		exit 1
	    fi
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
	# g)
	#     echo "-g was triggered, Parameter: $OPTARG" >&2
	#     GENOMEDIR=$OPTARG
	#     ;;
	# \?)
	#     echo "Using Default" >&2
	#     GENOMEDIR="/mnt/SCRATCH/geuvadis_genome/"
	#     exit 1
	#     ;;
	# :)
	#     echo "Option -$OPTARG requires an argument." >&2
	#     exit 1
	#     ;;
	u)
	    echo "-u was triggered, Parameter: $OPTARG" >&2
	    USEPARCEL=1;
	    ;;
	c)
	    echo "-c was triggered, Parameter: $OPTARG" >&2
	    CLEAN=1;
	    ;;
	z)
	    echo "-z was triggered, Parameter: $OPTARG" >&2
	    DEBUG=1;
	    ;;
	h)
	    #echo "-h was triggered, Parameter: $OPTARG" >&2 # Show the help 
	    echo "DESCRIPTION: download_and_stats_FASTQ.sh";
	    echo "Script to run Stuti's docker analysis on a list of urls and save output";
	    echo "for post-processing of the docker outputs. It expects a list of urls,";
	    echo "two urls per line (\":\" separated), each representing one member of a";
	    echo "mate pair. These are tar'ed, analyzed with the docker, and selected results";
	    echo "are saved. Creates output for combine_docker_outputs.r";
	    echo "     Downloads are with wget by default, with parcel if the option is selected";
	    echo "";
	    echo "OPTIONS:";
	    echo "     -l|--list          (string) Required - filename of list that contains the url list";
	    echo "                                 Default = \"$LIST\"";
	    echo "                                  Lines that start with a \"#\" will be skipped"
	    echo "     -x|--useproxy      (flag)   Use proxy ( proxy must be configured in ~/.bashrc )";
	    echo "     -s|--savedir       (string) Required - path for output";
	    echo "                                 Default = \"$SAVEDIR\"";
	    echo "     -t|--tempdir       (string) Dir to run Docker tool";
	    echo "                                 Default = \"$TEMPDIR\"";
	    echo "     -p|--pythonscript  (string) Python script run_docker.py";
	    echo "                                 Default = \"$PYTHONSCRIPT\"";
	    echo "     -d|--dockertar     (string) Docker tar file star_cuff_docker_1.8.tar";
	    echo "                                 Default = \"$DOCKERTAR\"";
	    echo "     -u|--useparcel     (flag)   Optional - use parcel for download (OPTION NOT FUNCTIONAL YET)";
	    echo "                                      Note: This option assumes you have Parcel installed and configured"
	    echo "                                      127.0.0.1 parcel.opensciencedatacloud.org in /etc/hosts"
	    echo "     -a|--arkparse      (flag)   Assume list contains ARKids, parse them to get URLs"
	    echo "     -b|--arkprefix     (string)      Depends on -a, ARK prefix, must be \"ftp\" or \"s3\""
	    echo "     -i|--parcelip      (string) Required with -u|--useparcel - ip address of the parcel server"
	    echo "                                 Default = $PARCELIP"
	    echo "     -c|--clean         (flag)   Optional - option to wipe non-saved results for each mate pair";
	    echo "     -z|--debug         (flag)   Optional - run in debug mode";
	    echo "     -h|--help          (flag)   Optional - display this help/usage text"
	    echo "";
	    echo "USAGE";
	    echo "     download_and_stats_FASTQ.sh -l <filename> -s <savedir> [other options]";
	    echo "";
	    echo "EXAMPLES:";
	    echo "Perform default analysis on test list:";
	    echo "     download_and_stats_FASTQ.sh -l err_list_1_of_4.11-18-15.txt.test -s ./";
	    echo "Default analysis with full logging:"
	    echo "     bash -x download_and_stats_FASTQ_beta.sh > debug.log 2>&1"
	    echo ""
	    echo "Kevin P. Keegan, 2015";
	    exit 1;
	    ;;
    
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
    esac
done

# Check for requirements - fail with error if any are missing

# LIST
if [ ! -e $LIST ]; then
    echo "List $LIST not supplied or does not exist - this is required"
    exit 1
fi
# SAVEDIR is created if it does not exist - no need for check
# TEMPDIR 
if [ ! -d $TEMPDIR ]; then
    echo "Tempdir $TEMPDIR not supplied or is not a directory - this is a required argument"
    exit 1
fi
# PYTHONSCRIPT
if [ ! -e $PYTHONSCRIPT ]; then
    echo "pythonscript $PYTHONSCRIPT not supplied or does not exist - this is required"
    exit 1
fi
if [ ! -e $DOCKERTAR ]; then
    echo "dockertar $DOCKERTAR not supplied or does not exist - this is required"
    exit 1
fi

# create a directory for the outputs
mkdir -p $SAVEDIR;

# create filenames for log files 
my_fastq_log=$SAVEDIR/$LIST.FASTQ_log.txt;
my_tar_log=$SAVEDIR/$LIST.tar_log.txt;
my_run_log=$SAVEDIR/$LIST.run_log.txt;
my_error_log=$SAVEDIR/$LIST.error_log.txt;
start_date=`date`;

# write headers for log files
# error log
echo "### Error log for processing of $LIST ###"    > $my_error_log;
echo `date`                                         >> $my_error_log;
echo ""                                             >> $my_error_log;
# fastq log
echo "file_name\toriginal_url\tbasename\tmd5\tsize" > $my_fastq_log;
echo $start_date                                    >> $my_fastq_log;
echo ""                                             >> $my_fastq_log;
# tar log
echo "file_name\toriginal_url\tbasename\tmd5\tsize" > $my_tar_log;
echo $start_date                                    >> $my_tar_log;
echo ""                                             >> $my_tar_log;
# run log
echo "### Run log for processing of $LIST ###"      > $my_run_log;
echo "script: "$0                                   >> $my_run_log;
echo "arguments: "$@                                >> $my_run_log;
echo $start_date                                    >> $my_run_log;
echo ""                                             >> $my_run_log;
echo "list:            "$LIST                       >> $my_run_log;
echo "useproxy         "$USEPROXY                   >> $my_run_log;
echo "savedir:         "$SAVEDIR                    >> $my_run_log;
echo "tempdir:         "$TEMPDIR                    >> $my_run_log;
echo "pythonscript:    "$PYTHONSCRIPT               >> $my_run_log;
echo "dockertar:       "$DOCKERTAR                  >> $my_run_log;
echo "save_dir:        "$SAVEDIR                    >> $my_run_log;
echo "arkparse:        "$ARKPARSE                   >> $my_run_log;
echo "arkprefix:       "$ARKPREFIX                  >> $my_run_log
echo ""                                             >> $my_run_log;
# entry for parcel option
if [[ $USEPARCEL -eq 1 ]]; then
     echo "useparcel:       ON"                     >> $my_run_log;
else
     echo "useparcel:       OFF"                    >> $my_run_log;
fi
# entry for clean option
if [[ $CLEAN -eq 1 ]]; then
     echo "clean:           ON"                     >> $my_run_log;
else
     echo "clean:           OFF"                    >> $my_run_log;
fi
# entry for debug option
if [[ $DEBUG -eq 1 ]]; then
     echo "debug:           ON"                     >> $my_run_log;
else
     echo "debug:           OFF"                    >> $my_run_log;
fi
echo ""                                             >> $my_run_log;

# move to $TEMPDIR - where Stuti's docker expects the data to be
mkdir -p $TEMPDIR;
cd $TEMPDIR;

for i in `cat $LIST`;
	
do
    echo ""                                  >> $my_run_log;
    echo `date`                              >> $my_run_log;  
    # skip line if it starts with #
    echo $i | grep -e '^#' &> /dev/null
    if [[ $? != 0 ]]; then
	# retireve targets from list - generate local filenames

	# option for parsing ark to get ftp or s3 URL from ARK
	if [[ $ARKPARSE == 1  ]]; then
	    ark_1=`echo $i | cut -f 1 -d ":"`;
	    ark_2=`echo $i | cut -f 2 -d ":"`;
	    echo "ark_1:           $ark_1"       >> $my_run_log;
	    echo "ark_1:           $ark_2"       >> $my_run_log;
	    mate_1=`ARK_parser_beta.py $ark_1 -s $ARKPREFIX`;
	    mate_2=`ARK_parser_beta.py $ark_2 -s $ARKPREFIX`;
	else
	    mate_1=`echo $i | cut -f 1 -d ":"`;
	    mate_2=`echo $i | cut -f 2 -d ":"`;
	fi
	mate_1_basename=`basename $mate_1`;
	mate_2_basename=`basename $mate_2`;
	pair_name=`echo $mate_1_basename | cut -f 1 -d "_"`;
	tar_name=$pair_name.fastq.tar.gz;
	
	echo "pair_name:       $pair_name"       >> $my_run_log;
	echo "mate_1:          $mate_1"          >> $my_run_log;
	echo "mate_1_basename: $mate_1_basename" >> $my_run_log;
	echo "mate_2:          $mate_2"          >> $my_run_log;
	echo "mate_2_basename: $mate_2_basename" >> $my_run_log;
	echo "tar_name:        $tar_name"        >> $my_run_log;

	# download both members of the mate pair
	# This section will be supplemented with code to download with Parcel from the object store
	if [[ $USEPARCEL -eq 1 ]]; then
	    # download with parcel
	    # start parcel in a separate screen session
	    echo "Starting parcel session with server $PARCELIP" >> $my_run_log;
	    screen -dmS parcel
	    screen -S parcel -X stuff "parcel-tcp2udt $PARCELIP:9000\n"
	    # perform downloads with parcel

	    if [[ $USEPROXY -eq 1 ]]; then
		export no_proxy="griffin-objstore.opensciencedatacloud.org"
		function with_proxy() {
		    PROXY='http://cloud-proxy:3128'
		    http_proxy="${PROXY}" https_proxy="${PROXY}" $@
		}
		with_proxy wget $mate_1;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_1 withOUT parcel" >> $my_run_log;
		echo "downloading $mate_2" >> $my_run_log;
	    else
		wget $mate_1;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_1 withOUT parcel" >> $my_run_log;
		echo "downloading $mate_2" >> $my_run_log;
	    fi

	    if [[ $USEPROXY -eq 1 ]]; then
		export no_proxy="griffin-objstore.opensciencedatacloud.org"
		function with_proxy() {
		    PROXY='http://cloud-proxy:3128'
		    http_proxy="${PROXY}" https_proxy="${PROXY}" $@
		}
		with_proxy wget $mate_2;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_2" >> $my_run_log;
	    else
		wget $mate_2;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_2" >> $my_run_log;
	    fi
		
	    # quit parcel session
	    screen -r parcel -X kill
	    echo `date`                              >> $my_run_log;
	    echo "parcel session with server $PARCELIP TERMINATED" >> $my_run_log;
	else
	    # download without parcel
	    echo "downloading $mate_1 withOUT parcel" >> $my_run_log;
	    #wget $mate_1 2 >> $my_error_log 1 >> $my_run_log; # this causes an error

	    if [[ $USEPROXY -eq 1 ]]; then
		export no_proxy="griffin-objstore.opensciencedatacloud.org"
		function with_proxy() {
		    PROXY='http://cloud-proxy:3128'
		    http_proxy="${PROXY}" https_proxy="${PROXY}" $@
		}
		with_proxy wget $mate_1;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_1 withOUT parcel" >> $my_run_log;
		echo "downloading $mate_2" >> $my_run_log;
	    else
		wget $mate_1;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_1 withOUT parcel" >> $my_run_log;
		echo "downloading $mate_2" >> $my_run_log;
	    fi
	    
	    if [[ $USEPROXY -eq 1 ]]; then
		export no_proxy="griffin-objstore.opensciencedatacloud.org"
		function with_proxy() {
		    PROXY='http://cloud-proxy:3128'
		    http_proxy="${PROXY}" https_proxy="${PROXY}" $@
		}
		with_proxy wget $mate_2;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_2" >> $my_run_log;
	    else
		wget $mate_2;
		echo `date`                              >> $my_run_log;
		echo "DONE downloading $mate_2" >> $my_run_log;
	    fi
	    
	    
	fi
	# create tar from individual mates
	echo "creating tar $tar_name" >> $my_run_log;
	tar -zcf $tar_name $mate_1_basename $mate_2_basename;
	echo `date`                              >> $my_run_log;
	echo "DONE creating tar $tar_name" >> $my_run_log;
	
	# get md5s
	echo "calculating md5's" >> $my_run_log;
	md5_mate1=`md5sum $mate_1_basename | cut -f1 -d " "`; # 2>> $my_error_log 1 >> $my_run_log;
	md5_mate2=`md5sum $mate_2_basename | cut -f1 -d " "`; # 2>> $my_error_log 1 >> $my_run_log;
	md5_tar=`md5sum $tar_name | cut -f1 -d " "`; # 2>> $my_error_log 1 >> $my_run_log;
	echo `date`                              >> $my_run_log;
	echo "DONE calculating md5's" >> $my_run_log;
	
	# get sizes
	echo "calculating sizes" >> $my_run_log;
	size_mate1=`stat -c%s $mate_1_basename`; # 2>> $my_error_log 1 >> $my_run_log;
	size_mate2=`stat -c%s $mate_2_basename`; # 2>> $my_error_log 1 >> $my_run_log;
	size_tar=`stat -c%s $tar_name`; # 2>> $my_error_log 1 >> $my_run_log;
	echo `date`                              >> $my_run_log;
	echo "DONE calculating sizes" >> $my_run_log;
	
	# print values to logs
	echo "printing calculated values to logs" >> $my_run_log;
	echo $mate_1_basename\t$mate_1\t$mate_1_basename\t$md5_mate1\t$size_mate1 >> $my_fastq_log; # mate_1 FASTQ;
	echo "DONE printing stats of $mate_1_base" >> $my_run_log;
	echo $mate_2_basename\t$mate_2\t$mate_2_basename\t$md5_mate2\t$size_mate2 >> $my_fastq_log; # mate_2 FASTQ;
	echo "DONE printing stats of $mate_2_basename" >> $my_run_log;
	echo $tar_name\t"NA"\t$pair_name\t$md5_tar\t$size_tar >> $my_tar_log; # tar created from mate_1 and mate_2
	echo `date`                              >> $my_run_log;
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
	sudo docker load -i $DOCKERTAR;
	sudo python $PYTHONSCRIPT;
	#sudo -k;
	echo `date`                              >> $my_run_log;
	echo "DONE with Docker processing" >> $my_run_log;
	# get the output
	echo "saving Docker output" >> $my_run_log;
	## mkdir for output that my R script can use to combine outputs later
	sudo mkdir -p $SAVEDIR/$pair_name/star_2_pass/;
	## move the genes.fpkm_tracking file to the save location
	echo "DOING THIS:" >> $my_run_log;
	echo "sudo cp /mnt/SCRATCH/geuvadis_results/$pair_name/star_2_pass/genes.fpkm_tracking $SAVEDIR$pair_name/star_2_pass/" >> $my_run_log;
	sudo cp /mnt/SCRATCH/geuvadis_results/$pair_name/star_2_pass/genes.fpkm_tracking $SAVEDIR/$pair_name/star_2_pass/

	# Once the new file sotre is ready, copy these results:
	# May want to generalize upload results argument to accept a list of results to upload
	# ~/SCRATCH/geuvadis_results/qc                     # this is a directory
	# ~/SCRATCH/geuvadis_results/star_2_pass            # this is a directory
	# ~/SCRATCH/geuvadis_results/$pair_star.log         # this is a file
	# exclude these:
	# ~/SCRATCH/geuvadis_results/$pair_name_fastq_files # this is a directory
	# ~/SCRATCH/geuvadis_results/tmp                    # this is a directory

	# Push results to store:
	
	echo `date`                              >> $my_run_log;
	echo "DONE saving Docker output" >> $my_run_log;
	
	# cleanup (if flag is used)
	if [[ $CLEAN -eq 1 ]]; then
	    echo "cleanup" >> $my_run_log;
	    sudo rm -R /mnt/SCRATCH/geuvadis_results/$pair_name;
	    sudo rm $mate_1_basename;
	    sudo rm $mate_2_basename;
	    sudo rm $tar_name;
	    echo `date`                              >> $my_run_log;
	    echo "Done with cleanup" >> $my_run_log;
	else
	    echo `date`                              >> $my_run_log;
	    echo "No cleanup" >> $my_run_log;
	fi
	
	# # copy current logs to the output directory
	# echo "copying logs" >> $my_run_log;
	# sudo cp $my_fastq_log $SAVEDIR/;
	# sudo cp $my_tar_log $SAVEDIR/;
	# sudo cp $my_error_log $SAVEDIR/;
	# sudo cp $my_run_log $SAVEDIR/;
	# echo "Done copying logs" >> $my_run_log;
	
	echo `date`                              >> $my_run_log;
	echo "ALL DONE WITH  $pair_name" >> $my_run_log;
	echo "" >> $my_run_log;
	
	# close sudo su
	# sudo -k;
	# close tmux session
	# exit;
	
    fi;
done;

echo "" >> $my_run_log
echo `date`                              >> $my_run_log;
echo "ALL DONE PROCESSING $LIST" >> $my_run_log

# # From Satish 12-3-15 # INSTALLING AND USING PARCEL
# # Install
# python setup.py develop
# sudo apt-get install python-pip
# sudo python setup.py develop
# # Setup
# sudo vi /etc/hosts  - add 127.0.0.1 parcel.opensciencedatacloud.org
# parcel-tcp2udt 192.170.232.76:9000 &
# parcel-udt2tcp localhost:9000 &
# wget https://parcel.opensciencedatacloud.org:9000/asgc-geuvadis/ERR188021.tar.gz
# # so if u see here.. I have  'python setup.py develop' twice.. this is because it failed first and then I had to do a apt-get install python-pip

# Notes:
# SCRATCH/
# case $key in
#     -e|--extension)
#     EXTENSION="$2"
#     shift # past argument
#     ;;
#     -s|--searchpath)
#     SEARCHPATH="$2"
#     shift # past argument
#     ;;
#     -l|--lib)
#     LIBPATH="$2"
#     shift # past argument
#     ;;
#     --default)
#     DEFAULT=YES
#     ;;
#     *)
#             # unknown option
#     ;;
# esac
# shift # past argument or value
# done
# echo FILE EXTENSION  = "${EXTENSION}"
# echo SEARCH PATH     = "${SEARCHPATH}"
# echo LIBRARY PATH    = "${LIBPATH}"
# echo "Number files in SEARCH PATH with EXTENSION:" $(ls -1 "${SEARCHPATH}"/*."${EXTENSION}" | wc -l)
# if [[ -n $1 ]]; then
#     echo "Last line of file specified as non-opt/last argument:"
#     tail -1 $1
# fi


