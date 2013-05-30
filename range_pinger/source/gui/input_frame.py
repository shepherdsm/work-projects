### Python Modules ###
from Tkinter import *
from ttk import *

class Input(Frame):
	"""
	Creates an input frame to control user customizations to the range pinger program.
	"""
	
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.bldg = StringVar()
		self.count = StringVar()
		self.time = StringVar()
		self.ip = StringVar()
		self.subnet = StringVar()
		self.save = IntVar()
		self.overwrite = IntVar()
		
		self._set_defaults()
		self._init_ui()
		
	### Private Methods ###
	def _set_defaults(self):
		"""
		Sets defaults for the variables used.
		"""
		
		self.count.set("4")
		self.time.set("2000")
		self.save.set(1)
		
	def _init_ui(self):
		"""
		Creates the UI used for the input class.
		"""
		
		bldg_entry = self._create_input_box('Bldg', self.bldg)
		count_entry = self._create_input_box("Count", self.count)
		time_entry = self._create_input_box("Time (Milliseconds)", self.time)
		ip_entry = self._create_input_box("IP", self.ip)
		subnet_entry = self._create_input_box("Subnet", self.subnet)
		
		save_checkbox = Checkbutton(self, text = "Save", variable = self.save)
		overwrite_checkbox = Checkbutton(self, text = "Overwrite", variable = self.overwrite)
		
		bldg_entry.grid(row = 0, column = 0)
		count_entry.grid(row = 0, column = 2)
		time_entry.grid(row = 0, column = 4)
		
		ip_entry.grid(row = 1, column = 0, columnspan = 2)
		subnet_entry.grid(row = 1, column = 3, columnspan = 2)
		
		save_checkbox.grid(row = 2, column = 0, columnspan = 2)
		overwrite_checkbox.grid(row = 2, column = 3, columnspan = 2)		
		
	def _create_input_box(self, label, variable, **kwargs):
		"""
		Creates and returns a label frame with an input box inside of it.
		Does not pack the frame.
		"""
		
		frame = LabelFrame(self, text = label, **kwargs)
		
		entry = Entry(frame, textvariable = variable, **kwargs)
		entry.pack()
		
		return frame
		
	### Public Methods ###
	def get_values(self):
		"""
		Returns the import results as a dictionary.
		
		Arguments - Arguments to be passed to the ping command.
		Building - What building this range is pinging.
		Ip - Either the IP/CIDR or the IP and subnet.
		Save - Whether or not to save the results. Defaults to save.
		Overwrite - Overwrite an existing file with the current results. Defaults to no.
		"""
		
		results_dic = {'args': "-n %s -w %s" % (self.count.get(), self.time.get()),
							 'building': self.bldg.get(),
							 'ip': '%s' % self.ip.get(),
							 'subnet': '%s' % self.subnet.get(),
							 'save': self.save.get(),
							 'overwrite': self.overwrite.get()}
							 
		return results_dic