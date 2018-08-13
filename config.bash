#!/usr/bin/env bash

# directories created by this repo
export baseDir=$(dirname "$0") # home directory for project
export cdDir=$baseDir/cardDumps # directory to store cracked card dumps
export libnfcDir=$baseDir/libnfc
export acsDir=$baseDir/acs # directory for ACR122U Driver files
export hnDir=$baseDir/hardnested
export guiDir=$baseDir/guiHelper

# directories created by other repos
export mfcukDir=$baseDir/mfcuk-r65
export mfocDir=$baseDir/mfoc

# installation variables
export os=$(cat /etc/os-release | sed q)
export ubuntuOS='NAME="Ubuntu"' 
export username=$(whoami) # user running code, need sudo privileges
export userDir=$username/$libnfcDir # variable needed for mfcuk install

# attack variables
export hn=$hnDir/crypto1_bs/libnfc_crypto1_crack # compiled hard nested program
export mfcuk=$mfcukDir/src/mfcuk
export mfoc=$mfocDir/src/mfoc/ # although mfoc can be run in any directory 
