#=============================================================================
#   This source code is provided under the Apache 2.0 license
#   and is provided AS IS with no warranty or guarantee of fit for purpose.
#   Copyright (C) 2024 LSEG. All rights reserved.
#=============================================================================

import tkinter as tk
import tkinter.ttk as ttk

# ----------------------------
# Login frame for getting user tick history credentials
class Login(ttk.Frame):
# ----------------------------
	def __init__(self, parent, controller):
		ttk.Frame.__init__(self, parent, relief=tk.GROOVE, borderwidth=5, padding=20)

		username = tk.StringVar()
		password = tk.StringVar()

		lbl1 = ttk.Label(self, text='Login to TickHistory', font=(None, 25))
		lblUser = ttk.Label(self, text='Username', font=(None, 12))
		lblPass = ttk.Label(self, text='Password', font=(None, 12))
		entUser = ttk.Entry(self, width=7, textvariable=username)
		entPass = ttk.Entry(self, width=7, textvariable=password, show='*')
		btn = ttk.Button(self, text="Login", command=lambda: controller.login(self, username.get(), password.get()))

		self.grid(row=0, column=0)
		lbl1.grid(row=0, column=0, columnspan=2, pady=10)
		lblUser.grid(row=1, column=0, pady=10)
		lblPass.grid(row=2, column=0, pady=10)
		entPass.grid(row=2, column=1, pady=10, sticky=(tk.W, tk.E))
		btn.grid(row=3, column=1, pady=10)
		entUser.grid(row=1, column=1, pady=10, sticky=(tk.W, tk.E))

		entUser.focus()





# ----------------------------
# Main frame for layout of the user interface
class Main(ttk.Frame):
# ----------------------------
	def __init__(self, parent, controller):
		ttk.Frame.__init__(self, parent, style='MainFrame.TFrame')
		pFrame = Package(self, controller)
		lbl1 = ttk.Label(self, text='VBD\nPackages', font=(None, 10, 'bold'), style='MainFrame.TLabel')
		btn1 = ttk.Button(self, text="Refresh", command=self.loadPackages)

		sFrame = Schedules(self, controller)
		lbl2 = ttk.Label(self, text='Delivery\nSchedule', font=(None, 10, 'bold'), style='MainFrame.TLabel')
		btn2 = ttk.Button(self, text="Retrieve", command=self.getSchedules)

		self.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		self.columnconfigure(1, weight=1)
		self.rowconfigure(1, weight=2)
		self.rowconfigure(3, weight=2)

		lbl1.grid(row=0, column=0, sticky=(tk.N), pady=20)
		btn1.grid(row=1, column=0, sticky=(tk.N), pady=20)
		pFrame.grid(row=0, column=1, rowspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))

		lbl2.grid(row=2, column=0, sticky=(tk.N), pady=20)
		btn2.grid(row=3, column=0, sticky=(tk.N), pady=20)
		sFrame.grid(row=2, column=1, rowspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))

		self.controller = controller
		self.pFrame = pFrame
		self.sFrame = sFrame

		# configure styles for the app
		style = ttk.Style()
		style.configure("Treeview.Heading", font=(None, 10, 'bold'))
		style.configure('MainFrame.TFrame', background='#dfd')
		style.configure('MainFrame.TLabel', background='#dfd')



	def loadPackages(self):
		# request packages data
		jsonMsg = self.controller.getAllPackages()
		if jsonMsg != None:
			# update the UI
			self.pFrame.displayPackages(jsonMsg)



	def getSchedules(self):
		# find which package is selected
		entry = self.pFrame.getSelectedPackageDetails()
		if entry == None:
			self.controller.setMsg('Select a package first')
		else:
			jsonMsg = self.controller.getSchedules(entry['PackageId'])
			if jsonMsg != None:
				# update the UI
				self.sFrame.displaySchedule(jsonMsg)





# ----------------------------
# Packages sub frame for diplaying the list of all VBD packages available to the user
class Package(ttk.Frame):
# ----------------------------
	def __init__(self, parent, controller):
		ttk.Frame.__init__(self, parent, relief=tk.GROOVE, padding=0)

		tree = ttk.Treeview(self, selectmode='browse')
		vsb = ttk.Scrollbar(self, orient="vertical", command=tree.yview)
		tree.configure(yscrollcommand=vsb.set)
		jD = tk.Text(self, font=(None, 10), height=5, bg='#aaa')
		jD.tag_configure("bold", font=(None, 10, 'bold'))

		# add tree headers
		col = 'PackageName'
		tree["columns"] = [col]
		tree.column('#0',  minwidth=0, width=50, stretch='no')
		tree.heading('#0', text='#')
		tree.column(col, anchor="w")
		tree.heading(col, text=col, anchor='w')

		tree.bind('<<TreeviewSelect>>', self.itemSelected)

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
		jD.grid(row=1, column=0, columnspan=2, sticky=(tk.E, tk.W))

		self.tree = tree
		self.jsonDetails = jD



	def displayPackages(self, jsn):
		# clear previous table first
		for row in self.tree.get_children():
			self.tree.delete(row)
		# clear json display panel
		self.jsonDetails.delete(1.0, tk.END)

		# insert data into table
		index = 1
		for entry in jsn['value']:
			#print(entry)
			self.tree.insert('', 'end', text=index, values=[entry['PackageName']])
			index += 1

		self.jsonMsg = jsn



	def getSelectedPackageDetails(self):
		try:
			# get the highlighted entry from the table
			curItem = self.tree.focus()
			curItemText = self.tree.item(curItem)
			packageName = curItemText['values'][0]

			# look up package details from the package name
			for entry in self.jsonMsg['value']:
				if entry['PackageName'] == packageName:
					return entry
			return None
		except:
			return None



	def itemSelected(self, event):
		# display the selected table row details in the detail pane
		self.jsonDetails.delete(1.0, tk.END)

		entry = self.getSelectedPackageDetails()
		if entry != None:
			for key in entry:
				self.jsonDetails.insert(tk.END, f'{key}:', 'bold')
				self.jsonDetails.insert(tk.END, f'\t\t{entry[key]}\n')






# ----------------------------
# Schedules sub frame for displaying the delivery schedules of a selected packages
class Schedules(ttk.Frame):
# ----------------------------
	def __init__(self, parent, controller):
		ttk.Frame.__init__(self, parent, relief=tk.GROOVE)

		lbl1 = ttk.Label(self, text='Package Date:', font=(None, 10, 'bold'))
		combo = ttk.Combobox(self, width=30, state="readonly")
		tree = ttk.Treeview(self, selectmode='browse')
		vsb = ttk.Scrollbar(self, orient="vertical", command=tree.yview)
		jD = tk.Text(self, font=(None, 10), height=10, width=40, bg='#aaa')
		jD.tag_configure("bold", font=(None, 10, 'bold'))
		btn1 = ttk.Button(self, text="Download", style='Dload.TButton', command=self.downloadFile)
		progress = tk.DoubleVar()
		pb = ttk.Progressbar(self, variable=progress)
		tree.configure(yscrollcommand=vsb.set)

		# add tree headers
		cols = {'Name': 200, 'Frequency': 10, 'Size (KB)': 10, 'Released Date': 50}
		tree["columns"] = list(cols.keys())
		tree.column('#0', minwidth=0, width=50, stretch='no')
		tree.heading('#0', text='#')
		for col in list(cols.keys()):
			tree.column(col, anchor="w", width=cols[col])
			tree.heading(col, text=col, anchor='w')

		combo.bind("<<ComboboxSelected>>", self.dateSelected)
		tree.bind('<<TreeviewSelect>>', self.itemSelected)

		self.columnconfigure(1, weight=1)
		self.rowconfigure(1, weight=1)
		lbl1.grid(row=0, column=0, padx=5)
		combo.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
		tree.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=5)
		vsb.grid(row=1, column=2, sticky=(tk.N, tk.S))
		jD.grid(row=1, column=3, sticky=(tk.N, tk.S), padx=5)
		btn1.grid(row=2, column=0, sticky=(tk.W), pady=5, padx=5)
		pb.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)

		style = ttk.Style()
		style.configure("Dload.TButton", font=(None, 10, 'bold'))

		self.tree = tree
		self.jsonDetails = jD
		self.combo = combo
		self.progress = progress
		self.controller = controller



	def dateSelected(self, event):
		# clear previous table first
		for row in self.tree.get_children():
			self.tree.delete(row)
		# clear json display panel
		self.jsonDetails.delete(1.0, tk.END)

		# insert data into table
		index = 1
		for e in self.dateIndexed[self.combo.get()]:
			self.tree.insert('', 'end', text=index, values=[e['Name'], e['Frequency'], f'{int(e["FileSizeBytes"]/1024):,}', e['ReleaseDateTime'][:10]])
			index += 1

		# scroll to top
		self.tree.yview_moveto(0)



	def itemSelected(self, event):
		# display the selected table row details in the detail pane
		self.jsonDetails.delete(1.0, tk.END)

		entry = self.getSelectedPackageDetails()
		if entry != None:
			for key in entry:
				self.jsonDetails.insert(tk.END, f'{key}:', 'bold')
				self.jsonDetails.insert(tk.END, f'\t\t{entry[key]}\n')



	def getSelectedPackageDetails(self):
		try:
			# get the highlighted entry from the table
			curItem = self.tree.focus()
			curItemText = self.tree.item(curItem)
			iName = curItemText['values'][0]

			# look up package details from the package name
			for entry in self.jsonMsg['value']:
				if entry['Name'] == iName:
					return entry
			return None
		except:
			return None



	def displaySchedule(self, jsn):
		# reformat the json to the date indexed format for easy navigation
		dI = {}
		for entry in jsn['value']:
			crDate = entry['CreateDateTime'][:10]
			if not crDate in dI:
				dI[crDate] = []
			dI[crDate].append(entry)

		self.combo['values'] = list(dI.keys())

		self.dateIndexed = dI
		self.jsonMsg = jsn

		# select the recent date
		self.combo.current(0)
		# trigger selected ebent
		self.dateSelected(None)



	def downloadFile(self):
		entry = self.getSelectedPackageDetails()
		if entry != None:
			self.setProgress(0)
			self.controller.update_idletasks()
			self.controller.downloadFile(self, entry['PackageDeliveryId'], entry['Name'], entry['FileSizeBytes'])
		else:
			self.controller.setMsg('Select a file to download')



	def setProgress(self, percent):
		self.progress.set(percent)

