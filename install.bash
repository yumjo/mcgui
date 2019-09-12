#!/usr/bin/env bash

# to run: bash install.bash 
# Tested on Ubuntu 18.04.3 LTS (Bionic Beaver)

# Useful web-pages:
# https://github.com/nfc-tools
# https://gist.github.com/ceres-c/b84935799f5d65a4e41328d3ceaa075c
# http://barisguvercin.com/mifare-1k-cracking/
# https://firefart.at/post/how-to-crack-mifare-classic-cards/

source ./config.bash # load config environment variables

mkdir $cdDir $libnfcDir $acsDir # $baseDir, $guiDir, & $hnDir already created

sudo apt-get install autoconf automake make -y
sudo apt install hexedit # hexdump/xxd works without hexedit install, but can't easily edit hexdump

# install acsc library --> driver for acr122u nfc reader
cd $acsDir
wget https://www.acs.com.hk/download-driver-unified/10312/ACS-Unified-PKG-Lnx-116-P.zip
unzip ACS-Unified-PKG-Lnx-116-P.zip
cd ACS-Unified-PKG-Lnx-116-P/acsccid_linux_bin-1.1.6/ubuntu/bionic/
sudo dpkg -i libacsccid1_1.1.6-1~ubuntu18.04.1_amd64.deb
sudo apt-get install -f
cd $acsDir/ACS-Unified-PKG-Lnx-116-P/acsccid_linux_bin-1.1.6/
rm -rf debian/ epel/ fedora/ opensuse/ raspbian/ sle/

# install 1.7.1 libnfc for system and for mfoc --> doesn't work with mfcuk
# Manual installation for driver configuration
cd $libnfcDir
wget https://github.com/nfc-tools/libnfc/releases/download/libnfc-1.7.1/libnfc-1.7.1.tar.bz2
tar xvjf libnfc-1.7.1.tar.bz2
cd libnfc-1.7.1

# needed for live usb build or won't find packages
sudo add-apt-repository universe
sudo apt-get install pcsc-tools libpcsclite1 libpcsclite-dev libusb-0.1-4 libusb-dev libtool build-essential git libglib2.0-dev pcscd libnfc-bin libtool-bin -y
autoreconf -vis --force # force because libtool version mismatch error
./configure --with-drivers=acr122_usb --prefix=/usr --sysconfdir=/etc
make clean all
sudo make install
sudo mkdir /etc/nfc
sudo cp libnfc.conf.sample /etc/nfc/libnfc.conf
rm $libnfcDir/libnfc-1.7.1.tar.bz2

# get 1.5.1 libnfc tar from github, extract, and move into
# libnfc version to run with mfcuk
cd $libnfcDir
sudo wget https://github.com/nfc-tools/libnfc/releases/download/libnfc-1.5.1/libnfc-1.5.1.tar.gz
tar xvzf libnfc-1.5.1.tar.gz
cd libnfc-1.5.1 # inside directory
./configure --prefix=${userDir}/prefix --sysconfdir=/etc/nfc --enable-serial-autoprobe 
make && sudo make install
rm $libnfcDir/libnfc-1.5.1.tar.gz -f

# download mfcuk (Dark Side) --> key cracker for weak cards
cd $baseDir
git clone https://github.com/nfc-tools/mfcuk.git mfcuk-r65 # need r65 version
cd ./mfcuk-r65
git reset --hard 1b6d022
autoreconf -vis
LIBNFC_CFLAGS=-I${userDir}/prefix/include LIBNFC_LIBS="-L${userDir}/prefix/lib -lnfc" ./configure --prefix=${userDir}/prefix
sudo awk 'NR==197 {$0="LIBS = $(LIBNFC_LIBS)"} 1' ${userDir}/mfcuk-r65/src/Makefile | sudo tee ${userDir}/mfcuk-r65/src/Makefile > /dev/null
make
# to run: 
# cd to executable mfcuk file
# LD_LIBRARY_PATH=${userDir}prefix/lib ./mfcuk -C -R 0:A -v 3
# this way, can specify which libnfc version to use

# To make libnfc work (see libnfc readme troubleshooting section):
# create blacklist and add pn533_usb
sudo cp $libnfcDir/libnfc-1.7.1/contrib/linux/blacklist-libnfc.conf /etc/modprobe.d/blacklist-libnfc.conf
sudo bash -c 'echo "blacklist pn533_usb" >> /etc/modprobe.d/blacklist-libnfc.conf'
# sudo nano /etc/modprobe.d/blacklist-libnfc.conf # check blacklist

# edit info.plist --> line 53, change ifdDriverOptions 0x0000 to 0x0005
sudo awk 'NR==53 {$0="        <string>0x0005</string>"} 1' /usr/lib/pcsc/drivers/ifd-acsccid.bundle/Contents/Info.plist | sudo tee /usr/lib/pcsc/drivers/ifd-acsccid.bundle/Contents/Info.plist > /dev/null 

# stop services on blacklist (they prevent libnfc from working)
sudo modprobe -r pn533_usb pn533 nfc

# install mfoc (Nested)
#   checks use of default keys or use with one known key (mfcuk)
#   will use system 1.7.1 libnfc 
cd $baseDir
git clone https://github.com/nfc-tools/mfoc.git # commit dd0ce5c
cd ./mfoc
autoreconf -is
./configure
make && sudo make install
# to run: mfoc -h
# mfoc -O card_dump / hexdump -vC card_dump 

# install Hardnested attack
cd $hnDir
git clone https://github.com/aczid/crypto1_bs # commit 89de1ba 
cd crypto1_bs
sudo mkdir $hnDir/crypto1_bs/crapto1-v3.3
# if need to add Crapto Code to crypto1_bs
# cp crapto files (crapto1-v3.3.tar.xz & craptev1-v1.1.tar.xz) into crypto1_bs directory 
# sudo tar Jxvf craptev1-v1.1.tar.xz
# sudo mkdir crapto1-v3.3
# sudo tar Jxvf crapto1-v3.3.tar.xz -C crapto1-v3.3
make
# to run: bash hardnested.bash

# for python gui
sudo apt-get install python3 python3-tk -y 
chmod +x $baseDir/mcgui.py 
# to run: ./mcgui.py or python3 mcgui.py

# Start cracking
sudo service pcscd start
# sudo service pcscd status # should be active now, q to exit
# nfc-list should correctly open device at this point if want to test
