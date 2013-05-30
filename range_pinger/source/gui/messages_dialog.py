import tkMessageBox

class Message():
	"""
	Class allowing for easy access to dialog windows.
	Designed to be used and thrown away.
	"""
	
	def __init__(self, type, msg):
		"""
		Type is what kind of dialog you want, and msg is what you want displayed.
		info -> showinfo
		error -> showerror
		warn -> showwarning
		"""
		
		self._make_dialog(type)(message = msg) # Displays the dialog
		
	def _make_dialog(self, type):
		"""
		Holds the information for each type.
		"""
		
		funcs = {'info': tkMessageBox.showinfo,
					 'error': tkMessageBox.showerror,
					 'warn': tkMessageBox.showwarning}
					 
		try:
			return funcs[type]
		except KeyError:
			raise ValueError("Not a valid dialog box.")