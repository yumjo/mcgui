The Mifare Cracking GUI (mcgui) identifies, cracks, and clones both original and hardened Mifare Classic cards. Mcgui provides a simple user interface for existing Mifare cracking functions. The available cracking options through mcgui are the [Dark Side](https://eprint.iacr.org/2009/137.pdf), [Hard Nested](http://www.cs.ru.nl/~rverdult/Ciphertext-only_Cryptanalysis_on_Hardened_Mifare_Classic_Cards-CCS_2015.pdf), and [Nested](http://www.cs.ru.nl/~flaviog/publications/Pickpocketing.Mifare.pdf) attacks.  

# Requirements
- **USB NFC reader:** Mcgui was tested with a ACR122U reader. Mcgui configures libnfc to work with this reader's driver.
- **Linux OS:** The OS cannot be virtualized as the USB controller for virtual machines does play well with NFC readers. The installation script is tailored to Fedora and Ubuntu. The script was tested on Fedora 28 and Ubuntu 18.0.1 LTS.
- **Mifare Classic Cards:** Mcgui was tested with Mifare Classic 1K cards, original and hardened.

# Installation
To install, type in a terminal (will need sudo privileges): 
```
git clone https://github.com/yumjo/mcgui 
cd mcgui 
bash install.bash
```

The [install.bash](install.bash) downloads and configures all the necessary programs. The installed programs (not including their dependencies) are: 
- [crypto1_bs](https://github.com/aczid/crypto1_bs)
- [libnfc](https://github.com/nfc-tools/libnfc)
- [mfoc](https://github.com/nfc-tools/mfoc)
- [mfcuk](https://github.com/nfc-tools/mfcuk)
- [pcsc-tools](https://github.com/LudovicRousseau/pcsc-tools)

_Note: A modified version of [miLazyCracker](https://github.com/nfc-tools/miLazyCracker) is used to run the hard nested attack. See [hardnested.bash](hardnested/hardnested.bash) for more information._

# Starting mcgui
For libnfc to work, the pcscd service needs to be running. If mcgui was just installed, than the installation script has started the service and mcgui can be run with `./mcgui.py`. The program needs to be run from within the mcgui directory so the necessary helper files can be found.

If mcgui has already been installed, but the computer has since been restarted or the pcscd service has been stopped for another reason, then pcscd needs to be started again with `sudo service pcscd start` before running mcgui. 

# Using mcgui
## Cracking Tab
- **Validate:** This button identifies the card currently on the reader. If successful, it retrieves the UID, ATR, and SAK. If the card has been cracked with the GUI before and the UID is recognized, mcgui will automatically load the corresponding key file and card dump in the Card Information tab.
- **Crack:** Crack runs the selected attack with the hard nested attack as the default. The hard nested script runs both the nested and hard nested attacks, so this selection can be run on both original and hardened cards. 
- **Keyfile & Dumpfile Buttons:** A keyfile can be loaded to use with the hard nested and nested attacks. A dumpfile can be loaded for cloning. If an attack modifies these files (i.e. new keys found), the update files button will update the Card Information tab to reflect the changes. 
- **Clone:** Clone attempts to write the loaded card dump to the card currently on the reader. A verfication window will pop up before the operation runs to ensure the user really wants to write to the card on the reader. 

## Card Information Tab
- The card information tab presents the information that has been retrieved during successful cracking tab operations, such as recovered keys and the cracked card dump.
