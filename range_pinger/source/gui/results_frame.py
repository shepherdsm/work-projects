### Python Modules ###
from Tkinter import *
from ttk import *

class Result(LabelFrame):
	"""
	Defines the result frame for displaying the IP addresses that have been pinged.
	"""
	
	def __init__(self, parent, text = "Progress"):
		LabelFrame.__init__(self, parent, text = text)
		
		self.value = 0
		
		self._init_ui()
		
	### Private Methods ###
	def _init_ui(self):
		"""
		Initializes the main frame for displaying results from the ping program.
		"""
		
		self.progressbar = Progressbar(self, orient = HORIZONTAL, length = 200, mode = 'determinate', value = 0)
		self.progressbar.pack()
		
	### Public Methods ###
	def clear(self):
		"""
		Clears the progress bar.
		"""
		
		self.progressbar['value'] = 0
		
	def set_max(self, m):
		"""
		Sets the max value of the progress bar.
		"""
		
		self.progressbar.configure(maximum = m)
		
	def make_step(self, a = 1):
		"""
		Moves the progress bar by a amount.
		"""
		
		self.progressbar['value'] += a