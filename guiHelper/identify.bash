#!/usr/bin/env bash

source ./guiHelper/guiConfig.bash

if [ ! -e $baseDir/.reset ]; then
	touch .reset # ls -a to see hidden file
	echo "reset" >> .reset # needed to get ATR with scriptor
fi

# Identify Card as Mifare Classic 1K
isMifareClassic=0
ATR_Mifare_1k="3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A "
SAK_Mifare_1k="08"

# capture UID, ATR, and SAK
uid=$(nfc-list -t 1|sed -n 's/ //g;/UID/s/.*://p')
sleep .3 # reader is busy with nfc-list
ATRcommand="scriptor .reset"
capturedATR=$($ATRcommand | tail -1 )
atr=${capturedATR//"< OK: "/} # remove unnecessary part of string
sak=$(nfc-list -t 1|sed -n 's/ //g;/SAK/s/.*://p')


if [ "$atr" == "$ATR_Mifare_1k" ] && [ "$sak" == "$SAK_Mifare_1k" ]; then
	echo "Found Mifare Classic 1k Tag"
	echo "UID: " $uid
	echo "ATR: " $atr
	echo "SAK: " $sak	
	isMifareClassic=1
else
	echo "Unknown Card. See below for results and see terminal for any error output."
	echo "$ATRcommand output (for ATR):"	
	echo -e "$capturedATR"	
	echo "nfc-list output (for UID and SAK):"
	nfc-list
fi
