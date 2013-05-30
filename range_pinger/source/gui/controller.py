### Python Modules ###
from Tkinter import *
from ttk import *

### User Modules
from ..backend.rp import RangePing
from input_frame import Input
from results_frame import Result
from messages_dialog import Message
# from messages_dialog import Message

class Gui(Frame):
	"""
	The controller class for the Rangepinger GUI. Handles connecting the backend to the frontend.
	"""
	
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		
		self._init_ui()
	
	### Private Methods ###
	def _init_ui(self):
		"""
		Puts together the user interface.
		"""
		
		self.input_frame = Input(self)
		self.input_frame.pack()
		
		button_ok = Button(self, text = "Ping", command = self._go)
		button_ok.pack()
		
		self.result_frame = Result(self)
		self.result_frame.pack()
		
	def _go(self):
		"""
		When clicked, gets the options for the input frame
		and then feeds the results to the result frame.
		"""
		self.result_frame.clear()
		
		options = self.input_frame.get_values()
		
		try:
			range = RangePing(options['ip'], options['subnet'], options['building'])
			self.result_frame.set_max(range.length)
		
			for ip in range.ping(options['args']):
				self.result_frame.make_step()
				self.parent.update_idletasks()
				
			if options['save'] == 1:
				range.save_results(options['overwrite'] == 1)
			
			Message('info', range.get_summary())
		except ValueError as e:
			Message('error', e.message)

def run():
	root = Tk()
	g = Gui(root)
	g.pack()
	root.mainloop()