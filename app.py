#=============================================================================
#   This source code is provided under the Apache 2.0 license
#   and is provided AS IS with no warranty or guarantee of fit for purpose.
#   Copyright (C) 2024 LSEG. All rights reserved.
#=============================================================================

import tkinter as tk
from Frames import Login, Main
from TickHistory import TH


# ----------------------------
# root display window and controller class
class window(tk.Tk):
# ----------------------------
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		self.title("TickHistory Venue By Day demo app")
		self.geometry("1000x800")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		# create a frame where are sub widgets are placed
		cont = tk.Frame(self)
		cont.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		cont.grid_rowconfigure(0, weight=1)
		cont.grid_columnconfigure(0, weight=1)

		# drop a status bar at the bottom
		self.statusMsg = tk.StringVar()
		lbl1 = tk.Label(self, textvariable=self.statusMsg, anchor='w', font=(None, 12), bg='#333', fg='#fff')
		lbl1.grid(row=1, column=0, sticky=(tk.W, tk.E))

		# create and hold reference to other objects
		self.th = TH(self)
		self.container = cont

		# show the login frame
		Login(cont, self)



	def setMsg(self, message):
		# set the message in the bottom status bar
		self.statusMsg.set(message)



	def login(self, frame, usr, pss):
		# login to tick history
		if usr == '' or pss == '':
			self.setMsg('Please enter a username and password')
			return

		self.setMsg('Logging to TickHistory...')
		self.update_idletasks()
		token, msg = self.th.login(usr, pss)

		if token == None:
			self.setMsg(f'Error: {msg}')
		else:
			# successful - destroy the login form and display the main UI
			self.setMsg('Received OAuth token')
			frame.grid_forget()
			frame.destroy()
			Main(self.container, self)



	def getAllPackages(self):
		# request all VBD packages from tick history
		self.setMsg('Getting all the VBD packages...')
		self.update_idletasks()
		jsn, msg = self.th.getAllPackages()

		if jsn == None:
			self.setMsg(f'Error: {msg}')
		else:
			self.setMsg('Received all VBD packages')
			return jsn



	def getSchedules(self, packageID):
		# request delivery schedule for a particulr package
		self.setMsg(f'Getting schedule for {packageID} ...')
		self.update_idletasks()
		jsn, msg = self.th.getSchedules(packageID)

		if jsn == None:
			self.setMsg(f'Error: {msg}')
		else:
			self.setMsg('Received schedule')
			return jsn



	def downloadFile(self, view, deliveryID, filename, fileSize):
		mb = 2**20
		gb = 2**30

		dSize = ''
		if fileSize >= gb:
			dSize = f'- ({fileSize/gb:.1f} GB)'
		elif fileSize >= mb:
			dSize = f'- ({fileSize/mb:.1f} MB)'

		# download the requested file
		self.setMsg(f'Downloading {filename} {dSize} ...')
		self.update_idletasks()
		self.th.downloadFile(view, deliveryID, filename, fileSize)





if __name__ == "__main__":
	mWin = window()
	mWin.mainloop()

