### User Modules ###
from item import Item
import my_logger

### Logging ###
logger = my_logger.create_logger(__name__)

class Shelf(list):
	"""
	Contains a collection of item objects, and allows a few methods for
	determing their state and modifying them.
	"""
	
	def __init__(self, parent = "", items = None):
		logger.debug("Enter")
		
		list.__init__([])
		
		if items:
			self.extend([self._make_button(i, parent) for i in items])
			self.update_names() # Dictionary for name -> button lookup
		
		logger.debug("Exit")
		
	### Private Functions ###
	def _make_button(self, item, parent):
		"""
		Takes an item name and returns a button
		"""
		logger.debug("Create button")
		
		return Item(parent, item)
		
	def _find_button(self, name):
		"""
		Takes an item name and finds the associated button.
		"""
		logger.debug("Enter")
		
		try:
			button = self.names[name]
		except KeyError:
			logger.debug("Name not found")
			button = None
			
		logger.debug("Exit")	
		return button
		
	def _make_button_list(self, items):
		"""
		Takes a list of names and returns a list of buttons.
		"""
		button_list = []
		
		for name in items:
			b = self._find_button(name)
			if b:
				button_list.append(b)
				
		return button_list
		
	### Public Functions ###
	def update_names(self):
		"""
		Updates the name dictionary inside the shelf.
		"""
		logger.debug("Update names.")
		
		self.names = {i.name: i for i in self}
	
	def get_item_names(self):
		"""
		Returns a list of item names.
		"""
		logger.debug("Get Item Names")
		
		return set(self.names.keys())
		
	def items_out(self):
		"""
		Returns a set of items that are currently out for the given session.
		"""
		logger.debug("Items Out")
		
		return {item for item in self if item.is_out() and item.is_clickable()}
		
	def items_out_by_name(self):
		"""
		Returns a set of items that are out by name.
		"""
		logger.debug("Items out by name.")
		
		return {item.name for item in self if item.is_out() and item.is_clickable()}
		
	def remove_clicks(self):
		"""
		Removes the click of all buttons in the shelf.
		"""
		logger.debug("Enter")
		
		for b in self:
			b.remove_click()
			
		logger.debug("Exit")
		
	def mark_out(self, items):
		"""
		Removes the ability for items to be clicked.
		"""
		logger.debug("Enter")
		
		for b in self._make_button_list(items):
			b.swap_photo()
			b.remove_click()
			
		logger.debug("Exit")