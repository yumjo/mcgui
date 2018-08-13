#!/usr/bin/env bash

baseDir=~/nfc
if [ ! -e $baseDir/.reset ]; then
	touch .reset # ls -a to see hidden file
	echo "reset" >> .reset # needed to get ATR with scriptor
fi

# Identify Card as Mifare Classic 1K
isMifareClassic=0
ATR_Mifare_1k="3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A "
SAK_Mifare_1k="08"

# capture ATR and SAK
ATRcommand="scriptor .reset"
capturedATR=$($ATRcommand | tail -1 )

SAKcommand="nfc-list"
capturedSAK=$($SAKcommand | tail -2 )

# remove unnecessary part of strings
foundATR=${capturedATR//"< OK: "/}
foundSAK=${capturedSAK//"SAK (SEL_RES): "/}
foundSAK=$(echo $foundSAK) # removes newline/spaces

if [ "$foundATR" == "$ATR_Mifare_1k" ] && [ "$foundSAK" == "$SAK_Mifare_1k" ]; then
	echo "Found Mifare Classic 1k Tag"
	echo "ATR: " $foundATR
	echo "SAK: " $foundSAK	
	isMifareClassic=1
else
	echo -e "Unknown Card. See terminal for any error output."
	echo "$ATRcommand output (for ATR):"	
	echo -e "$capturedATR"	
	echo "$SAKcommand output (for SAK):"
	echo "$capturedSAK"	
fi
