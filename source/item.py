### Python Modules ###
import os
import string

from Tkinter import PhotoImage, TOP, TclError
from ttk import *

### User Modules
import my_logger

### Logging ###
logger = my_logger.create_logger(__name__)

### Globals ###
D_IMAGES = 'images'
D_ITEMS = 'items'
D_OTHER = 'other'
F_OUT = 'out'
F_NO = 'no_photo'

class Item(Button):
	"""
	Constructs a button with a picture on it showing whether an item is checked in or out.
	"""
	
	def __init__(self, parent, name):
		logger.debug("Enter")
		
		Button.__init__(self, parent)
		
		self.name = name
		
		self.d_base = os.path.join(os.getcwd(), D_IMAGES, '{}', '%s.gif')
		self.d_images = self.d_base.format(D_ITEMS)
		self.d_other = self.d_base.format(D_OTHER)
		
		try:
			self.p_base = self._create_photo(self.d_images, name)
		except TclError:
			self.p_base = self._create_photo(self.d_other, F_NO)

		self.p_swap = self._create_photo(self.d_other, F_OUT)
		
		self.configure(image=self.p_base, command=self.swap_photo, text=self._pretty_name(name), compound=TOP)
		
		self.bind("<Return>", lambda e: self.swap_photo())
		
		logger.debug("Exit")
	
	### Private Functions ###
	def _pretty_name(self, name):
		"""
		Returns a 'prettified' name of the string.
		"""
		logger.debug("Pretty Name")
		
		return string.capwords(name.replace('_', ' '))
		
	def _create_photo(self, path, name):
		"""
		Creates a photo for use on the button.
		"""
		logger.debug("Create photo.\nPath: %r\nName: %r" % (path, name))
		
		return PhotoImage(format='gif', file=path % (name), name=name)
	
	### Public Functions ###
	def swap_photo(self):
		"""
		Swaps the photo from "Out" to "In" and changes the picture.
		"""
		logger.debug("Enter")

		# Image is the same as the base name
		if self['image'][0] == self.p_base.name:
			self.configure(image=self.p_swap) # Out image is displayed
		else:
			self.configure(image=self.p_base) # In image is displayed
		
		logger.debug("Exit")
		
	def is_out(self):
		"""
		Returns true if the item is "out".
		"""
		logger.debug("Is Out")
		
		return self['image'][0] == 'out'
		
	def is_clickable(self):
		"""
		Returns true if the button is "clickable".
		"""
		logger.debug("Clickable")

		return self['command'] != ""
		
	def remove_click(self):
		"""
		Removes the ability for the image to be clicked and configures it to show the out item.
		"""
		logger.debug("Enter")
		
		self['command'] = ""
		self.unbind("<Return>")
		
		logger.debug("Exit")