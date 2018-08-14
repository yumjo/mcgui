#!/usr/bin/env bash

! getopt --test > /dev/null 
if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
    echo "I’m sorry, `getopt --test` failed in this environment."
    exit 1
fi

OPTIONS=u:
LONGOPTS=uid:

! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    exit 2
fi
eval set -- "$PARSED"

u=-
while true; do
    case "$1" in
        -u|--uid)
            uid=$2
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

baseDir=$(realpath .)
cdDir=$baseDir/cardDumps/
filename="${cdDir}${uid}/${uid}_dump.hex"

if [ -f "$filename" ]; then # if loaded key file exists
	echo "Found dumpfile ${filename} -- See below for file contents."	
	hexdump -vC $filename
else
	echo "No dumpfile found for this UID."
fi
