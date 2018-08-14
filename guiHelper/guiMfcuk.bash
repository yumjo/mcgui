#!/usr/bin/env bash

source ./guiHelper/guiConfig.bash # load environment variables

LD_LIBRARY_PATH=${userDir}/prefix/lib ${mcfcuk} -C -R 0:A -v 3

if [ $retVal == "0" ]; then
	echo -e "\nNested attack was successful!"	
fi
echo -e "\nPress Enter to close the terminal."
read line
