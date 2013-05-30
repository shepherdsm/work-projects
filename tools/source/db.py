### Python modules ###
import os
import shelve

from datetime import datetime
from time import mktime

### User Modules ###
import my_logger

### Globals ###
RSC_D = 'resources'
DB_F = os.path.join(RSC_D, 'tools')
FILES = ('tools', 'keys')
DAT_FILE = os.path.join(RSC_D, '%s.dat')

### Logging ###
logger = my_logger.create_logger(__name__)

### Public Functions ###
def update_db():
	"""
	Populates the tools database with the inventory read from the .dat file.
	"""
	logger.debug("Entered")

	if not os.path.exists(DB_F):
		logger.debug("No tools database")
		
		for f in FILES:
			with open(DAT_FILE % f, 'r') as temp:
				check_items(map(str.strip, temp.read().split()))
		
			logger.debug("Database created.")
	else: # We have a database, but are there more tools to add?
		logger.debug("Updating existing database")
		db = shelve.open(DB_F)
		
		current_tools = set(db.keys()) # All the tools and keys
		
		new_tools = set()
		for f in FILES:
			with open(DAT_FILE % f, 'r') as temp:
				new_tools.update(map(str.strip, temp.read().split()))
		
		new_tools -= current_tools
		
		logger.debug("New tools to add\n%r" % new_tools)
		
		if new_tools:
			check_items(new_tools)
			
		logger.debug("Database updated.")
		
	logger.debug("Exiting")
	
def get_items(name):
	"""
	Returns a list of the items defined by name.
	"""
	logger.debug("Enter")
	
	if name in FILES:
		with open(DAT_FILE % name) as tmp:
			return [i.strip() for i in tmp]
	else:
		raise ValueError("'%s' not a valid DAT file." % name)
		
def items_out():
	"""
	Returns a list of the items that are marked as out.
	"""
	logger.debug("Enter")
	
	db = shelve.open(DB_F)
	
	items_out = [k for k, v in db.items() if not v]
	
	logger.debug("Items out: %r" % items_out)
	
	db.close()
	
	logger.debug("Exit")
	
	return items_out

def check_items(items):
	"""
	Updates the tools database which tracks the overall status of the tools.
	Reverses the truth value for each item passed to the function.
	"""
	logger.debug("Entered")
	
	db = shelve.open(DB_F, writeback=True)
	
	logger.debug("DB before checking\n%r" % db)
	logger.debug("Items to check\n%r" % items)
	
	# Removing items from checked out to checked in
	for i in items:
		if i in db:
			db[i] = not db[i] # Reverse the status of the item.
		else:
			db[i] = True # If there is no item, check it.
		
	logger.debug("DB after checking\n%r" % db)

	db.close()
	
	logger.debug("Exiting")
	
if __name__ == '__main__':
	update_db()