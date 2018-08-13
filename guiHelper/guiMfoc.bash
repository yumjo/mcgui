#!/usr/bin/env bash

source ./guiConfig.bash # load environment variables

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

if [ -f "$filename" ]; then # if loaded key file exists
	mfoc -O $dumpFile -f $filename
else
        mfoc -O $dumpFile
fi
