#!/usr/bin/env bash

# Directories
export baseDir=$(realpath .) # home directory (mcgui)
export cdDir=$baseDir/cardDumps # directory to store cracked card dumps
export libnfcDir=$baseDir/libnfc
export hnDir=$baseDir/hardnested
export acsDir=$baseDir/acs
export mfcukDir=$baseDir/mfcuk-r65/src/mfcuk

# Attack variables
export hn=$hnDir/crypto1_bs/libnfc_crypto1_crack # compiled hard nested program
export userDir=$baseDir
export mcfcuk=$baseDir/mfcuk-r65/src/mfcuk

export uid=$(nfc-list -t 1|sed -n 's/ //g;/UID/s/.*://p') # retrieves card uid
export uidDir=$cdDir/$uid # directory to store card files
export keyFile=$uidDir/${uid}_keys.txt
export dumpFile=$uidDir/${uid}_dump.hex
export partialDumpFile=$hnDir/.partialDump.txt
