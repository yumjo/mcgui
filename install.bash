#!/usr/bin/env bash

# to run: bash install.bash 
# Tested on Fedora 28 and Ubuntu 18.04.1 LTS

# Useful web-pages:
# https://github.com/nfc-tools
# https://gist.github.com/ceres-c/b84935799f5d65a4e41328d3ceaa075c
# http://barisguvercin.com/mifare-1k-cracking/
# https://firefart.at/post/how-to-crack-mifare-classic-cards/

source ./config.bash # load config environment variables

mkdir $cdDir $libnfcDir $acsDir # $baseDir, $guiDir, & $hnDir already created

if [ $os == $ubuntuOS ]; then
	sudo apt-get install autoconf automake make -y
	# hexdump/xxd works without hexedit install
else # Fedora
	sudo dnf install autoconf automake hexedit -y # optional: sudo nano
fi

# install acsc library --> driver for acr122u nfc reader
cd $acsDir
wget https://www.acs.com.hk/download-driver-unified/9232/ACS-Unified-PKG-Lnx-115-P.zip
unzip ACS-Unified-PKG-Lnx-115-P.zip
cd ACS-Unified-PKG-Lnx-115-P/acsccid_linux_bin-1.1.5/fedora/27 #no 28 version
sudo rpm -ihv pcsc-lite-acsccid-1.1.5-1.fc27.x86_64.rpm
rm $acsDir/ACS-Unified-PKG-Lnx-115-P.zip

# install 1.7.1 libnfc for system and for mfoc --> doesn't work with mfcuk
# Manual installation for driver configuration
cd $libnfcDir
wget https://github.com/nfc-tools/libnfc/releases/download/libnfc-1.7.1/libnfc-1.7.1.tar.bz2
tar xvjf libnfc-1.7.1.tar.bz2
cd libnfc-1.7.1
if [ $os == $ubuntuOS ]; then
	sudo apt-get install pcsc-tools libpcsclite1 libpcsclite-dev libusb-0.1-4 libusb-dev libtool build-essential git libglib2.0-dev pcscd -y
	autoreconf -vis
	./configure --with-drivers=acr122_usb --prefix=/usr --sysconfdir=/etc
	make clean all
	sudo make install
	sudo mkdir /etc/nfc
	sudo cp libnfc.conf.sample /etc/nfc/libnf.conf
else
	sudo dnf install pcsc-tools pcsc-lite pcsc-lite-devel libusb-devel -y
	sudo dnf install libnfc libnfc-devel libnfc-examples -y
	./configure --with-drivers=acr122_usb # acr122_pcsc is deprecated
	make clean all
	sudo make install
fi

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
autoreconf -is
LIBNFC_CFLAGS=-I${userDir}/prefix/include LIBNFC_LIBS="-L${userDir}/prefix/lib -lnfc" ./configure --prefix=${userDir}/prefix
make
# to run: 
# cd to executable mfcuk file
# LD_LIBRARY_PATH=${userDir}prefix/lib ./mfcuk -C -R 0:A -v 3
# this way, can specify which libnfc version to use

# To make libnfc work (see libnfc readme troubleshooting section):
# create blacklist and add pn533_usb
if [ $os == $ubuntuOS ]; then
	sudo cp $libnfcDir/libnfc-1.7.1/contrib/linux/blacklist-libnfc.conf /etc/modprobe.d/blacklist-libnfc.conf
else
	sudo cp /usr/share/libnfc/blacklist-libnfc.conf /etc/modprobe.d/blacklist-libnfc.conf
fi
sudo bash -c 'echo "blacklist pn533_usb" >> /etc/modprobe.d/blacklist-libnfc.conf'
# sudo nano /etc/modprobe.d/blacklist-libnfc.conf # check blacklist

# edit info.plist --> line 55, change ifdDriverOptions 0x0000 to 0x0005
if [ $os == $ubuntuOS ]; then
	sudo awk 'NR==55 {$0="        <string>0x0005</string>"} 1' /etc/libccid_Info.plist | sudo tee /etc/libccid_Info.plist > /dev/null 
#sudo nano /usr/lib64/pcsc/drivers/ifd-ccid.bundle/Contents/Info.plist #check
else
	sudo awk 'NR==55 {$0="'\t'<string>0x0005</string>"} 1' /usr/lib64/pcsc/drivers/ifd-ccid.bundle/Contents/Info.plist | sudo tee /usr/lib64/pcsc/drivers/ifdccid.bundle/Contents/Info.plist > /dev/null 
#sudo nano /usr/lib64/pcsc/drivers/ifd-ccid.bundle/Contents/Info.plist #check
fi

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
# if need to add Crapto Code to crypto1_bs
# cp crapto files (crapto1-v3.3.tar.xz & craptev1-v1.1.tar.xz) into crypto1_bs directory 
# sudo tar Jxvf craptev1-v1.1.tar.xz
# sudo mkdir crapto1-v3.3
# sudo tar Jxvf crapto1-v3.3.tar.xz -C crapto1-v3.3
make
# to run: bash hardnested.bash

# for python gui
if [ $os == $ubuntuOS ]; then
	sudo apt-get install python3 python3-tk -y 
else
	sudo dnf install python3 python3-tkinter -y	
fi
chmod +x $baseDir/mcgui.py 
# to run: ./mcgui.py

# Start cracking
sudo service pcscd start
# sudo service pcscd status # should be active now, q to exit
# nfc-list should correctly open device at this point if want to test
