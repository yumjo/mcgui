#!/usr/bin/env python3

import sys

def addToList(l, item):
	item = item.strip()
	if (item not in l):	
		l.append(item)
def main():
	dumpfile = sys.argv[1]
	keyfile = sys.argv[2]
	keysList = []
	
	with open(keyfile, "rt") as file:
		for key in file:
			addToList(keysList, key)

	with open(dumpfile, "rb") as file:
		file.seek(0)
		for sector in range(0, 16):		 
			trash = file.read(48)
			keyA = file.read(6)
			trash = file.read(4)
			keyB = file.read(6)
			keyA = keyA.hex()
			keyB = keyB.hex()
			addToList(keysList, keyA)
			addToList(keysList, keyB)
	
	with open(keyfile, "w") as file:
		for key in keysList:
			file.write(key)
			file.write("\n")

if __name__ == "__main__":
	main()
