#!/usr/bin/env bash

# General variables
export baseDir=~/nfc # home directory for project
export cdDir=$baseDir/cardDumps # directory to store cracked card dumps
export libnfcDir=$baseDir/libnfc
export hnDir=$baseDir/hardnested
export acsDir=$baseDir/acs
export username=liveuser # user running code, need sudo privileges
export userDir=$username/nfc/libnfc # bash global variable needed for mfcuk install
export scriptDir=/run/media/liveuser/F818-39AC # update if not current directory
export hn=$baseDir/hardnested/crypto1_bs/libnfc_crypto1_crack # compiled hard nested program

# Attack variables
export uid=$(nfc-list -t 1|sed -n 's/ //g;/UID/s/.*://p') # retrieves card uid
export uidDir=$baseDir/cardDumps/$uid # directory to store card files
if [ ! -d $uidDir ]; then
  mkdir $uidDir
fi

export keyFile=$uidDir/${uid}_keys.txt
if [ ! -f "$keyFile" ]; then
	touch $keyFile # create since does not exist
fi
export dumpFile=$uidDir/${uid}_Dump.hex
export partialDumpFile=$hnDir/.partialDump.txt
