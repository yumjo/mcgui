#!/usr/bin/env bash

source ./guiHelper/guiConfig.bash # load environment variables

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

# write
nfc-mfclassic W a $filename

# sleep to give reader time to be freed from previous operation
sleep .3 

# read
nfc-mfclassic R a output.hex $filename

# compare output
diff output.hex $filename # if not output, then same
retVal=$?

if [ $retVal == 0 ]; then
	echo -e "\nClone was successful!"	
else
	echo -e "\nClone was not successful."
fi
rm output.hex
echo -e "\nPress Enter to close the terminal."
read line
