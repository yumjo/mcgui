#!/usr/bin/env bash

source ./guiHelper/guiConfig.bash # load environment variables

# Get command line argument (keyfile name)
# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
! getopt --test > /dev/null 
if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
    echo "I’m sorry, `getopt --test` failed in this environment."
    exit 1
fi

OPTIONS=f:
LONGOPTS=filename:

! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    exit 2
fi
eval set -- "$PARSED"

f=""
while true; do
    case "$1" in
        -f|--filename)
            filename=$2
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unexpected Error"
            exit 3
            ;;
    esac
done

if [ ! -d $uidDir ]; then
  mkdir $uidDir
fi

if [ ! -f "$keyFile" ]; then
	touch $keyFile # create since does not exist
fi

if [ -f "$filename" ]; then # if loaded key file exists
	mfoc -O $dumpFile -f $filename
	retval=$?
else
        mfoc -O $dumpFile
	retval=$?
fi

if [ "$retVal" == 0 ] || [ -z "$retVal"]; then
	./guiHelper/getKeysFromDump.py $dumpFile $keyFile
	echo -e "\nNested attack was successful!"
	echo -e "Click Update Files button on Cracking Tab to see changes."	
fi
echo -e "\nPress Enter to close the terminal."
read line
