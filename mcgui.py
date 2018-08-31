#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk 
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext
import subprocess

class MifareGUI:
	def __init__(self):
		# Sizes
		self.startWidth = 750
		self.startHeight = 400
		self.labelWidth = self.startWidth		
		self.labelHeight = 5

		# guiHelper files
		fileDir = "./guiHelper/"
		self.identify = fileDir + "identify.bash"
		self.hardnested = fileDir + "guiHardnested.bash"
		self.findKeysFile = fileDir + "findKeysFile.bash"
		self.findDumpFile = fileDir + "findDumpFile.bash"
		self.helptxtFile = fileDir + "help.txt"

		self.root = Tk()
		self.root.title("Mifare Cracking GUI")
		self.root.option_add('*tearOff', FALSE)		
			
		self.mainframe = ttk.Frame(self.root, width=self.startWidth, height=self.startHeight)
		self.mainframe.pack(fill=BOTH, expand=1)

		# Tabs
		self.tabs = ttk.Notebook(self.mainframe, width=self.startWidth, height=self.startHeight)
		self.tabs.pack(fill=BOTH, expand=1)
		self.cardInfoTab = ttk.Frame(self.tabs)
		self.crackingTab = ttk.Frame(self.tabs)
		self.helpTab = ttk.Frame(self.tabs)  
		self.tabs.add(self.crackingTab, text='Cracking')
		self.tabs.add(self.cardInfoTab, text='Card Information')
		self.tabs.add(self.helpTab, text='Help')
		
		# Cracking Tab
		# Check Card Type
		self.divider2 = ttk.Separator(self.crackingTab, orient=HORIZONTAL).pack(fill=X)
		self.disclaimer = ttk.Label(self.crackingTab, text='Disclaimer: This tool only works on Mifare Classic cards. To check that a card is Mifare Classic, click the validate button. Otherwise, run an attack. Make sure the card is placed on the reader.', background="#fffacd", anchor=W)
		self.disclaimer.pack(fill=X, expand=1, anchor=N, ipadx=90, ipady=10)
		self.disclaimer.bind("<Configure>", self.set_disclaimer_wrap)
		self.checkCardTypeBtn = ttk.Button(self.crackingTab, text="Validate", command=self.check_card_type)
		self.checkCardTypeBtn.pack(in_=self.disclaimer, side=RIGHT)
		
		# Attack Label
		self.attackLabel = ttk.Label(self.crackingTab, text='Choose Attack: ', anchor=N)
		self.attackLabel.pack(expand=1, ipady=10, ipadx=10, side='left', anchor=CENTER)
		self.attack = StringVar() # self.attack.get()
		self.attack.set("hn") # default hardnested
		self.cloneBtn = ttk.Button(self.attackLabel, text="Clone", command=self.clone_card).pack(side='bottom')
		self.crackBtn = ttk.Button(self.attackLabel, text="Crack", command=self.crack_card).pack(side='bottom')
		self.mfoc = ttk.Radiobutton(self.attackLabel, text='nested', variable=self.attack, value='mfoc').pack(side='bottom')
		self.mfcuk = ttk.Radiobutton(self.attackLabel, text='dark side', variable=self.attack, value='mfcuk').pack(side='bottom')
		self.hn = ttk.Radiobutton(self.attackLabel, text='hard nested', variable=self.attack, value='hn').pack(side='bottom')	
		
		# File Label
		self.fileLabel = ttk.Label(self.crackingTab, anchor=NE)
		self.fileLabel.pack(expand=1, side='right')
		# Load a keyfile
		self.keyfile = StringVar()
		self.keyfile.set("")
		self.loadKeyfileLabel = ttk.Label(self.fileLabel, text='Load Keyfile: ', anchor=NE, width=self.startWidth/2)
		self.unloadKeyfileBtn = ttk.Button(self.fileLabel, text="Unload File", command=self.unload_keyfile)
		self.loadKeyfileBtn = ttk.Button(self.fileLabel, text="Choose File", command=self.load_keyfile)
		self.keyfileLoaded = False
		# Load a dumpfile
		self.dumpfile = StringVar()
		self.dumpfile.set("")
		self.loadDumpfileLabel = ttk.Label(self.fileLabel, text='Load Dumpfile: ', anchor=NE, width=self.startWidth/2)
		self.unloadDumpfileBtn = ttk.Button(self.fileLabel, text="Unload File", command=self.unload_dumpfile)
		self.loadDumpfileBtn = ttk.Button(self.fileLabel, text="Choose File", command=self.load_dumpfile)
		self.dumpfileLoaded = False
		# Update files
		self.updateBtn = ttk.Button(self.fileLabel, text="Update Files", command=self.update_files)
		# packing (pack opposite to how appear because side='bottom')
		self.updateBtn.pack(in_=self.fileLabel, padx=10, pady=10, side='bottom', anchor=E)
		self.loadDumpfileLabel.pack(expand=1, ipadx=5, ipady=10, padx=10, pady=10, side='bottom')
		self.unloadDumpfileBtn.pack(in_=self.loadDumpfileLabel, side='bottom', anchor=E)
		self.loadDumpfileBtn.pack(in_=self.loadDumpfileLabel, side='bottom', anchor=E)
		self.unloadKeyfileBtn.pack(in_=self.loadKeyfileLabel, side='bottom', anchor=E)
		self.loadKeyfileBtn.pack(in_=self.loadKeyfileLabel, side='bottom', anchor=E)
		self.loadKeyfileLabel.pack(expand=1, ipadx=5, ipady=10, side='bottom')

		# Output 	
		self.outputLabel = ttk.Labelframe(self.crackingTab, text='Output')
		self.outputLabel.pack(expand=1, side='bottom', anchor=CENTER)
		self.outputBox = scrolledtext.ScrolledText(self.outputLabel, width=self.startWidth-10, height=self.startHeight, state='disabled', wrap='word')
		self.outputBox.pack(in_=self.outputLabel, fill=BOTH, expand=1)
		# TODO: Dynamic Font resizing		
		#self.outputBox.config(font=(None, 12))
		#self.outputLabel.bind("<Configure>", self.set_font_size)

		# Card Information Tab
		# General
		self.divider1 = ttk.Separator(self.cardInfoTab, orient=HORIZONTAL).pack(fill=X)
		self.generalLabel = ttk.Labelframe(self.cardInfoTab, text='General')
		self.generalLabel.pack(fill=BOTH, expand=1)
		self.generalText = Text(self.generalLabel, wrap='word', state='disabled', width=self.labelWidth, height=self.labelHeight)
		self.generalText.pack(side="left",fill=BOTH, expand=1)
		self.init_general_tb()

		# Sector Keys		
		self.sectorKeysLabel = ttk.Labelframe(self.cardInfoTab, text='Sector Keys')
		self.sectorKeysLabel.pack(fill=BOTH, expand=1)
		self.sectorKeysText = scrolledtext.ScrolledText(self.sectorKeysLabel, wrap='word', state='disabled', width=self.labelWidth, height=self.labelHeight)
		self.sectorKeysText.pack(side="left",fill=BOTH, expand=1)

		# Card Dump
		self.cardDumpLabel = ttk.Labelframe(self.cardInfoTab, text='Card Dump')
		self.cardDumpLabel.pack(fill=BOTH, expand=1)
		self.cardDumpText = scrolledtext.ScrolledText(self.cardDumpLabel, wrap='word',  state='disabled', width=self.labelWidth, height=self.labelHeight+5)
		self.cardDumpText.pack(fill=BOTH, expand=1)

		# Help Tab
		self.divider3 = ttk.Separator(self.helpTab, orient=HORIZONTAL).pack(fill=X)
		helpText = open(self.helptxtFile, "r").readlines()
		self.help = ttk.Label(self.helpTab, text="\n".join(helpText))
		self.help.pack(fill=X, expand=1, anchor=N)
		self.help.bind("<Configure>", self.set_help_wrap)	
	
	# Start Function	
	def start(self):
		self.root.mainloop()
		# start pcscd service
		# self.run_command_noput(["sudo", "service", "pcscd", "start"])	
	
	# Graphical Functions
	def set_cardInfoCanvas_width(self, event):
		newWidth = event.width-10 # minus to accommodate padding
		self.cardInfoCanvas.configure(width=newWidth)
	
	def set_scrollbar(self, event):
    		self.cardInfoCanvas.configure(scrollregion=self.cardInfoCanvas.bbox("all"))
	
	def set_disclaimer_wrap(self, event):
		wraplength = event.width-90 # minus to accommodate padding
		event.widget.configure(wraplength=wraplength)

	def set_help_wrap(self, event):
		wraplength = event.width
		event.widget.configure(wraplength=wraplength)

	# General text input functions
	def delete_all_text(self, textbox):
		textbox.configure(state='normal')
		textbox.delete('1.0', 'end')
		textbox.configure(state='disabled')

	def insert_text(self, textbox, text):
		textbox.configure(state='normal')
		textbox.insert('end', text)
		textbox.configure(state='disabled')

	# Specific Text Input Functions
	def insert_outputBox(self, text):
		self.outputBox.configure(state='normal')
		self.outputBox.insert('end', text)
		self.outputBox.insert('end', '\n')
		self.outputBox.configure(state='disabled')	

	def init_general_tb(self):
		self.generalText.configure(state='normal')
		self.generalText.insert('end', "Card Type: N/A\n")
		self.generalText.insert('end', "UID: N/A\n")
		self.generalText.insert('end', "ATR: N/A\n")
		self.generalText.insert('end', "SAK: N/A\n")
		self.generalText.configure(state='disabled')	
	
	def update_general_tb(self, text):		
		self.generalText.configure(state='normal')
		self.generalText.delete('1.0', 'end')
		self.generalText.insert('end', text)
		self.generalText.configure(state='disabled')

	def update_keys(self, uid):	
		output = self.run_command_output(["bash", self.findKeysFile, "-u", uid])	
		self.delete_all_text(self.sectorKeysText)		
		self.insert_text(self.sectorKeysText, output)
		checkput = output.split()
		if(checkput[0] == b'Found'):
			self.keyfile.set(checkput[2].decode('utf-8'))
			self.keyfileLoaded = True
			return True
		else:
			return False
		self.insert_outputBox("")

	def update_dump(self, uid):
		output = self.run_command_output(["bash", self.findDumpFile, "-u", uid])	
		self.delete_all_text(self.cardDumpText)		
		self.insert_text(self.cardDumpText, output)
		checkput = output.split()
		if(checkput[0] == b'Found'):
			self.dumpfile.set(checkput[2].decode('utf-8'))
			self.dumpfileLoaded = True
			return True
		else:
			return False
		self.insert_outputBox("")
	
	def update_files(self):
		if (self.keyfileLoaded == True):
			self.insert_outputBox("Using " + self.keyfile.get() + " to update sector keys.")
			# add keys to card information			
			self.delete_all_text(self.sectorKeysText)
			filename = self.keyfile.get()			
			file = open(filename, "rt")
			self.insert_text(self.sectorKeysText, "Sector keys updated.\n")
			self.insert_text(self.sectorKeysText, file.read())
			file.close()
			self.insert_outputBox("Card Information updated with sector keys.")
		else:
			self.insert_outputBox("No keyfile loaded to update.")
		if (self.dumpfileLoaded == True):
			self.dumpfileLoaded = True
			filename = self.dumpfile.get()
			self.dumpfile.set(filename)
			self.insert_outputBox("Using " + self.dumpfile.get() + " to update card dump.")
			# add dump to card information			
			self.delete_all_text(self.cardDumpText)			
			self.insert_text(self.cardDumpText, "Dumpfile updated.\n")
			output = self.run_command_output(["hexdump", "-vC", filename])
			self.insert_text(self.cardDumpText, output)
			self.insert_outputBox("Card Information updated with card dump.")
		else:
			self.insert_outputBox("No dumpfile loaded to update.")
		self.insert_outputBox("")

	# File Functions 
	def load_keyfile(self):
		filename = StringVar()
		filename.set(filedialog.askopenfilename())
		filename = filename.get()
		
		if (filename != ""):
			self.keyfileLoaded = True
			self.keyfile.set(filename)
			self.insert_outputBox("File (" + self.keyfile.get() + ") loaded.")
			# add keys to card information			
			self.delete_all_text(self.sectorKeysText)			
			file = open(filename, "rt")
			self.insert_text(self.sectorKeysText, "Keyfile loaded.\n")
			self.insert_text(self.sectorKeysText, file.read())
			file.close()
			self.insert_outputBox("Card Information updated with sector keys.")
			
		else:
			if (self.keyfile.get() != ""):
				self.insert_outputBox("File (" + self.keyfile.get() + ") still loaded.")
			else:
				self.keyfile.set("")
				self.insert_outputBox("No keyfile loaded.")
		self.insert_outputBox("") 	

	def unload_keyfile(self):
		self.keyfileLoaded = False
		filename = self.keyfile.get()
		if (filename == ""):
			self.insert_outputBox("No keyfile loaded.")
		else:
			
			self.insert_outputBox("File (" + filename + ") no longer loaded.")
			self.keyfile.set("")
			self.delete_all_text(self.sectorKeysText)
			self.insert_text(self.sectorKeysText, "Keyfile unloaded.")
		self.insert_outputBox("")

	def load_dumpfile(self):
		filename = StringVar()
		filename.set(filedialog.askopenfilename())
		filename = filename.get()
		
		if (filename != ""):
			self.dumpfileLoaded = True
			self.dumpfile.set(filename)
			self.insert_outputBox("File (" + self.dumpfile.get() + ") loaded.")
			# add dump to card information			
			self.delete_all_text(self.cardDumpText)			
			self.insert_text(self.cardDumpText, "Dumpfile loaded.\n")
			output = self.run_command_output(["hexdump", "-vC", filename])
			self.insert_text(self.cardDumpText, output)
			self.insert_outputBox("Card Information updated with card dump.")
			
		else:
			if (self.dumpfile.get() != ""):
				self.insert_outputBox("File (" + self.dumpfile.get() + ") still loaded.")
			else:
				self.dumpfile.set("")
				self.insert_outputBox("No dumpfile loaded.")
		self.insert_outputBox("") 

	def unload_dumpfile(self):
		self.dumpfileLoaded = False
		filename = self.dumpfile.get()
		if (filename == ""):
			self.insert_outputBox("No dumpfile loaded.")
		else:
			
			self.insert_outputBox("File (" + filename + ") no longer loaded.")
			self.dumpfile.set("")
			self.delete_all_text(self.cardDumpText)
			self.insert_text(self.cardDumpText, "Dumpfile unloaded.")
		self.insert_outputBox("")

	# Command Functions
	def run_command_noput(self, command):
		try:
			subprocess.Popen(command)
		except:					
			messagebox.showerror("Error", "An unexpected error occured. Check the terminal for further information.")		
		else:	
			return(0) # subprocess successful

	def run_command_output(self, command):
		try:	
			output = subprocess.check_output(command)
		except:		
			messagebox.showerror("Error", "An unexpected error occured. Check the terminal for further information.")
		else:	
			return(output) 	
	
	# Cracking Functions
	def crack_card(self):
		attackType = self.attack.get()
		if (attackType == "hn"):
			self.run_hn()
		elif (attackType == "mfoc"):
			self.run_mfoc()
		elif (attackType == "mfcuk"):
			self.run_mfcuk()
		else:
			self.insert_outputBox("No Attack Chosen.")

	def run_hn(self):		
		self.insert_outputBox("Running hard nested attack: ")
		self.insert_outputBox("To cancel, close the terminal running the attack.")
		if (self.keyfileLoaded): 
			self.insert_outputBox("Using loaded keyfile " + self.keyfile.get())
			self.insert_outputBox("Executing 'bash guiHardnested.bash -f keyfile' in terminal.")	
			self.run_command_noput(["gnome-terminal", "--", "bash", self.hardnested, "-f", self.keyfile.get()])
		else:
			self.insert_outputBox("Executing 'bash guiHardnested.bash' in terminal.")
			self.run_command_noput(["gnome-terminal", "--", "bash", self.hardnested])
		self.insert_outputBox("")
	
	def run_mfoc(self):	
		self.insert_outputBox("Running nested attack: ")
		self.insert_outputBox("To cancel, close the terminal running the attack.")
		if (self.keyfileLoaded): 
			self.insert_outputBox("Using loaded keyfile " + self.keyfile.get())
			self.insert_outputBox("Executing 'bash guiMfoc.bash -f keyfile' in terminal.")		
			self.run_command_noput(["gnome-terminal", "--", "bash", "./guiHelper/guiMfoc.bash", "-f", self.keyfile.get()])
		else:		
			self.insert_outputBox("Executing 'bash guiMfoc.bash' in terminal")					
			self.run_command_noput(["gnome-terminal", "--", "bash", "./guiHelper/guiMfoc.bash"]) 
			# for some reason does not work with self.mfoc variable
		self.insert_outputBox("")

	def run_mfcuk(self):
		self.insert_outputBox("Running dark side attack: ")
		self.insert_outputBox("To cancel, close the terminal running the attack.")
		self.insert_outputBox("Executing 'bash guiMfcuk.bash' in terminal")
		self.run_command_noput(["gnome-terminal", "--", "bash", "./guiHelper/guiMfcuk.bash"])
		self.insert_outputBox("")

	# Clone Functions
	def clone_card(self):
		if (self.dumpfileLoaded):
			answer = messagebox.askyesno(message='Are you sure you want to change the data on this card?', icon='question', title='Clone card')
			if (answer == True ):
				self.insert_outputBox("Cloning card: ")
				self.insert_outputBox("To cancel, close the terminal running the attack.")
				self.insert_outputBox("Executing 'bash guiClone.bash' in terminal")
				self.run_command_noput(["gnome-terminal", "--", "bash", "./guiHelper/guiClone.bash", "-f", self.dumpfile.get()])
			else:
				self.insert_outputBox("Cloning cancelled.")
		else:
			self.insert_outputBox("There is no loaded card dump information.")
		self.insert_outputBox("")

	# Validate Functions
	def check_card_type(self):
		output = self.run_command_output(["bash", self.identify])
		self.insert_outputBox(output)
		checkWord = output.split()[0]
		if(checkWord == b'Found'):
			output = output.replace(b'Found', b'Card Type:')
			self.update_general_tb(output)
			self.uid = output.split()[7]
			result1 = self.update_keys(self.uid)
			result2 = self.update_dump(self.uid)
			if(result1 == True):
				self.insert_outputBox("Found keyfile for this UID.")
			if(result2 == True):
				self.insert_outputBox("Found dumpfile for this UID.")
			messagebox.showinfo("Check Complete", "Valid card found. Card Information tab updated.")
		else:
			messagebox.showerror("Attention", "Invalid Card or Error.")
		self.insert_outputBox("")
			
def main():
	MifareGUI().start()

if __name__ == "__main__":
	main()
