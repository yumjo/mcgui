#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk 
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext

import subprocess
#import os

class MifareGUI:
	def __init__(self):
		# Sizes
		self.startWidth = 800
		self.startHeight = 300
		#tab_width = 850
		#tab_height = 200

		self.root = Tk()
		self.root.title("Mifare GUI")
		self.root.option_add('*tearOff', FALSE)		
			
		self.mainframe = ttk.Frame(self.root, width=self.startWidth, height=self.startHeight)
		self.mainframe.pack(fill=BOTH, expand=1)

		# Tabs
		self.tabs = ttk.Notebook(self.mainframe, width=self.startWidth, height=self.startHeight)
		self.tabs.pack(fill=BOTH, expand=1)
		self.cardInfoTab = ttk.Frame(self.tabs)
		self.crackingTab = ttk.Frame(self.tabs)  
		self.tabs.add(self.cardInfoTab, text='Card Information', )
		self.tabs.add(self.crackingTab, text='Cracking')

		# Card Information Tab
		# scrollbar --> need frame inside of canvas
		self.scrollWidth = self.startWidth-10 
		self.cardInfoCanvas = Canvas(self.cardInfoTab, width=self.scrollWidth, height=self.startHeight)
		self.cardInfoCanvas.bind("<Configure>", self.set_cardInfoCanvas_width)
		self.cardInfoCanvas.pack(side="left", fill=BOTH, expand=1)
		self.cardInfoScrollFrame = ttk.Frame(self.cardInfoCanvas, width=self.scrollWidth, height=self.startHeight)
		self.cardInfoScrollFrame.pack(fill=BOTH, expand=1)
		self.scrollbar = ttk.Scrollbar(self.cardInfoTab, orient=VERTICAL, command=self.cardInfoCanvas.yview)
		self.cardInfoCanvas.configure(yscrollcommand=self.scrollbar.set)
		self.scrollbar.pack(side="right", fill="y")
		self.cardInfoCanvas.create_window((0,0),window=self.cardInfoScrollFrame, anchor=NW)
		self.cardInfoScrollFrame.bind("<Configure>", self.set_scrollbar)
		
		# General
		self.divider1 = ttk.Separator(self.cardInfoScrollFrame, orient=HORIZONTAL).pack(fill=X)
		self.generalLabel = ttk.Labelframe(self.cardInfoScrollFrame, text='General')
		self.generalLabel.pack(fill=X, expand=1)
		self.generalText = Text(self.generalLabel, wrap='word', width=self.scrollWidth, height=5)
		self.generalText.pack(side="left", fill=X, expand=1)
		self.init_general_tb()

		# Sector Keys		
		self.sectorKeysLabel = ttk.Labelframe(self.cardInfoScrollFrame, text='Sector Keys')
		self.sectorKeysLabel.pack(fill=X, expand=1)
		self.sectorKeysText = Text(self.sectorKeysLabel, wrap='word', width=self.scrollWidth, height=5)
		self.sectorKeysText.pack(side="left", fill=X, expand=1)

		# Card Dump
		self.cardDumpLabel = ttk.Labelframe(self.cardInfoScrollFrame, text='Card Dump', width=self.startWidth, height=10)
		self.cardDumpLabel.pack(fill=X, expand=1)
		self.cardDumpText = Text(self.cardDumpLabel, wrap='word', width=self.scrollWidth, height=5).pack(fill=X, expand=1)
		# open file and add card dump for formatting
		# self.insertText()
		
		# Cracking Tab
		# Check Card Type
		self.divider = ttk.Separator(self.crackingTab, orient=HORIZONTAL).pack(fill=X)
		self.disclaimer = ttk.Label(self.crackingTab, text='Disclaimer: This tool only works on Mifare Classic Cards. To check that a card is Mifare Classic, click the validate button. Otherwise, run an attack. Make sure the card is placed on the reader.', background="#fffacd", anchor=W)
		self.disclaimer.pack(fill=X, expand=1, anchor=N, ipadx=90, ipady=10)
		self.disclaimer.bind("<Configure>", self.set_disclaimer_wrap)
		self.checkCardTypeBtn = ttk.Button(self.crackingTab, text="Validate", command=self.checkCardType)
		self.checkCardTypeBtn.pack(in_=self.disclaimer, side=RIGHT)
		
		# Choose an Attack
		self.attackLabel = ttk.Label(self.crackingTab, text='Choose Attack: ', anchor=N)
		self.attackLabel.pack(expand=1, ipady=10, ipadx=10, side='left', anchor=CENTER)
		self.attack = StringVar() # self.attack.get()
		self.attack.set("hn") # default hardnested
		self.cancel = BooleanVar()
		self.cancel = False
		self.cancelBtn = ttk.Button(self.attackLabel, text="Cancel", command=self.cancel_attack).pack(side='bottom')
		self.crackBtn = ttk.Button(self.attackLabel, text="Crack", command=self.crack_card).pack(side='bottom')
		self.mfoc = ttk.Radiobutton(self.attackLabel, text='nested', variable=self.attack, value='mfoc').pack(side='bottom')
		self.mfcuk = ttk.Radiobutton(self.attackLabel, text='dark side', variable=self.attack, value='mfcuk').pack(side='bottom')
		self.hn = ttk.Radiobutton(self.attackLabel, text='hard nested', variable=self.attack, value='hn').pack(side='bottom')	

		# Load a keyfile
		self.keyfile = StringVar()
		self.keyfile.set("")
		self.loadKeyfileLabel = ttk.Label(self.crackingTab, text='Load Keyfile: ', anchor=NE, width=self.startWidth/2)
		self.loadKeyfileLabel.pack(expand=1, ipadx=5, ipady=10, side='right', anchor=E)
		self.unloadKeyfileBtn = ttk.Button(self.crackingTab, text="Unload File", command=self.unload_keyfile)
		self.unloadKeyfileBtn.pack(in_=self.loadKeyfileLabel, side='bottom', anchor=E)
		self.loadKeyfileBtn = ttk.Button(self.crackingTab, text="Choose File", command=self.load_keyfile)
		self.loadKeyfileBtn.pack(in_=self.loadKeyfileLabel, side='bottom', anchor=E)
		self.keyfileLoaded = False

		# Load a cardump
		#self.loadDumpfileLabel = ttk.Label(self.crackingTab, text='Load Card Dump File: ', anchor=NE, width=self.startWidth/2)
		#self.loadDumpfileLabel.pack(expand=1, ipadx=5, ipady=20, side='right', anchor=E)
		#self.loadDumpfileBtn = ttk.Button(self.crackingTab, text="Choose File", command=self.load_dumpfile)
		#self.loadDumpfileBtn.pack(in_=self.loadDumpfileLabel, side='right', anchor=E)
		# self.dumpfileLoaded = False 
		# self.dumpfile = ""

		# Text Box for Cracking Scripts	
		self.outputLabel = ttk.Labelframe(self.crackingTab, text='Output')
		self.outputLabel.pack(expand=1, side='bottom', anchor=CENTER)
		self.outputBox = scrolledtext.ScrolledText(self.outputLabel, width=self.startWidth-10, height=self.startHeight, state='disabled', wrap='word')
		self.outputBox.pack(in_=self.outputLabel, fill=BOTH, expand=1)		

		# TODO: attacks with progress bar

	def start(self):
		self.root.mainloop()	

	# Graphical Functions
	def set_cardInfoCanvas_width(self, event):
		newWidth = event.width-10 # minus to accommodate padding
		self.cardInfoCanvas.configure(width=newWidth)
	
	def set_scrollbar(self, event):
    		self.cardInfoCanvas.configure(scrollregion=self.cardInfoCanvas.bbox("all"))
	
	def set_disclaimer_wrap(self, event):
		wraplength = event.width-90 # minus to accommodate padding
		event.widget.configure(wraplength=wraplength)

	def set_label_wrap(self, event):	
		wraplength = event.width-10 # minus to accommodate padding
		event.widget.configure(wraplength=wraplength)	

	# Text Input Functions
	def insert_outputBox(self, text):
		self.outputBox.configure(state='normal')
		self.outputBox.insert('end', text)
		self.outputBox.insert('end', '\n')
		self.outputBox.configure(state='disabled')	

	def init_general_tb(self):
		self.generalText.configure(state='normal')
		self.generalText.insert('end', "Card Type: N/A\n")
		self.generalText.insert('end', "ATR: N/A\n")
		self.generalText.insert('end', "SAK: N/A\n")
		self.generalText.configure(state='disabled')	
	
	def update_general_tb(self, text):
		self.generalText.configure(state='normal')
		self.generalText.delete('1.0', 'end')
		self.generalText.insert('end', text)
		self.generalText.configure(state='disabled')	
	
	def delete_all_text(self, textbox):
		textbox.configure(state='normal')
		textbox.delete('1.0', 'end')
		textbox.configure(state='disabled')

	# File Functions 
	def load_keyfile(self):
		filename = StringVar()
		filename.set(filedialog.askopenfilename())
		filename = filename.get()
		
		if (filename != ""):
			self.keyfileLoaded = True
			self.keyfile.set(filename)
			self.insert_outputBox("File (" + self.keyfile.get() + ") loaded.")
			#delete_all_text(self.) --> sector keys
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
		self.insert_outputBox("")

	def load_dumpfile(self):
		dumpfileLoaded = True
		self.dumpfile = filedialog.askopenfilename()

	# Command Functions
	def run_command(self, command):
		try:
			p = subprocess.Popen(command)
			#for line in iter(p.stdout.readline, b''):				
				#print(line.rstrip()) 
		except:					
			messagebox.showerror("Error", "An unexpected error occured. Check the terminal for further information.")		
		else:	
			return(p)

	def run_bash_file(self, filename):
		try:	
			output = subprocess.check_output(["bash", filename])
		except:		
			messagebox.showerror("Error", "An unexpected error occured. Check the terminal for further information.")
		else:	
			return(output) 	
	
	# Cracking Functions
	def crack_card(self):
		attackType = self.attack.get()
		if (attackType == "hn"):
			#self.insert_outputBox("Running Hard Nested Attack:")
			self.run_hn()
		elif (attackType == "mfoc"):
			self.run_mfoc()
		elif (attackType == "mfcuk"):
			self.insert_outputBox("Running Dark Side Attack.")
		else:
			self.insert_outputBox("No Attack Chosen.")

	def cancel_attack(self):
		self.cancel = True;	

	def run_hn(self):		
		self.insert_outputBox("Running hard nested attack: ")
		if (self.keyfileLoaded): 
			self.insert_outputBox("Using loaded keyfile " + self.keyfile.get())
			self.insert_outputBox("Executing 'bash guiHardnested.bash -f " + self.keyfile.get() + "' in terminal.")
			self.insert_outputBox("To cancel, close the terminal running the attack.")	
			output = self.run_command(["gnome-terminal", "--", "bash", "guiHardnested.bash", "-f", self.keyfile.get()])
		else:
			self.insert_outputBox("Executing 'bash guiHardnested.bash' in terminal.")
			self.insert_outputBox("To cancel, close the terminal running the attack.")
			output = self.run_command(["gnome-terminal", "--", "bash", "guiHardnested.bash"])
		self.insert_outputBox("")
	
	def run_mfoc(self):	
		self.insert_outputBox("Running nested attack: ")
		if (self.keyfileLoaded): 
			self.insert_outputBox("Using loaded keyfile " + self.keyfile.get())
			self.insert_outputBox("Executing 'bash guiMfoc.bash -f " + self.keyfile.get() + "' in terminal.")
			self.insert_outputBox("To cancel, close the terminal running the attack.")		
			output = self.run_command(["gnome-terminal", "--", "bash", "guiMfoc.bash", "-f", self.keyfile.get()])
		else:		
			self.insert_outputBox("Executing 'bash guiMfoc.bash' in terminal")
			self.insert_outputBox("To cancel, close the terminal running the attack.")					
			output = self.run_command(["gnome-terminal", "--", "bash", "guiMfoc.bash"])
		self.insert_outputBox("")

	# Validate Functions
	def checkCardType(self):
		output = self.run_bash_file("./identify.bash")
		self.insert_outputBox(output)
		checkWord = output.split()[0]
		if(checkWord == b'Found'):
			output = output.replace(b'Found', b'Card Type:')
			self.update_general_tb(output)
			messagebox.showinfo("Check Complete", "Valid card Found. Card Information tab updated.")
		else:
			messagebox.showerror("Attention", "Invalid Card or Error. See Terminal.")
			
def main():
	MifareGUI().start()

if __name__ == "__main__":
	main()
