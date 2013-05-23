### Python modules ###
from datetime import datetime

import os
import pickle
import time

### User Modules ###
import db
import login
import my_logger

### Logging ###
logger = my_logger.create_logger(__name__)

class Tools():
	"""
	Class that holds the information for the tools inventory and provides
	methods to interact with the information.
	"""
	def __init__(self):
		# Stores the checked out equipment to a given username in the form:
		# {user: [timestamp, bldg, items]}
		db.update_db()
		self._state_file = os.path.join(*'resources state.pickle'.split())
		self.transactions = self._load_transactions()
		
	### Private Functions ###
	def _make_timestamp(self):
		"""
		Gets the current time as a timestamp.
		"""
		logger.debug("Get a timestamp")
		return time.mktime(datetime.today().timetuple())
		
	def _load_transactions(self):
		"""
		Loads the transactions (if any) from serialized data.
		"""
		logger.debug("Enter")
		try:
			with open(self._state_file, 'rb') as tmp:
				logger.debug("There is a file.")
				tmp_dict = pickle.load(tmp)
				logger.debug("Dictionary loaded from file: %s" % tmp_dict)
		except IOError as e: # File doesn't exists
			logger.debug("Exit - No file. Error message: %s" % e)
			tmp_dict = {}
			
		return tmp_dict
		
	def _save_transactions(self):
		"""
		Saves the current transactions of a program to serialized data.
		"""
		logger.debug("Enter")
		
		with open(self._state_file, 'wb') as tmp:
			logger.debug("Dumping transactions: %r" % self.transactions)
			pickle.dump(self.transactions, tmp)
		
		logger.debug("Exit")
		
	### Public Functions ###
	def get_building_by_user(self, user):
		"""
		Returns the building a user is checked out for.
		"""
		
		return self.transactions[user][1]

	def get_users(self):
		"""
		Returns the users in the program as a list.
		"""
		logger.debug("Fetch users")
		
		return login.get_users()
		
	def trim_items(self, items):
		"""
		Takes a list of items and trims from it any items that are already checked out
		because of an interesting bug where a currently checked out item can be clicked
		and registered as being clicked despite having the command removed.
		"""
		logger.debug("Enter")
		
		if self.transactions:
			all_items = set.union(*[self.transactions[u][-1] for u in self.transactions.keys()])
		else:
			return items
			
		tmp = items.copy()
		
		for i in items:
			if i in all_items:
				logger.debug("Removing %r" % i)
				tmp.remove(i)
				
		logger.debug("Exit")
		return tmp

	def checkout_items(self, user, items, bldg):
		"""
		Checks out the list of items passed to it, updating self.transactions.
		"""
		logger.debug("Entering")

		if user in self.transactions:
			logger.debug("User in transactions.")
			ts = self.transactions[user][0] # Use the current timestamp
			old_items = self.transactions[user][-1]
		else:
			logger.debug("User not in transactions.")
			ts = self._make_timestamp()
			old_items = set()
			
		logger.debug("Information being added: Timestamp Out: %r\nBldg: %r\nItems: %r" % (ts, bldg, items))
		db.check_items(items) # Updates the file containing checked in/out items
		
		items.update(old_items)
		logger.debug("Full item list: %r" % items)
		self.transactions[user] = [ts, bldg, items] # Update the user transaction
		
		self._save_transactions()
		logger.debug("Exititing")
		
	def checkin_items(self, user):
		"""
		Checks in the list of items passed to it.
		Stores the items into a logfile as timestamp_out;timestamp_in;user;bldg;items
		Returns the start and stop timestamp for the items.
		"""
		logger.debug("Entering")
		
		if not user in self.transactions:
			logger.warn("There should be a user in the transactions when checking out items.")
			raise KeyError

		ts, bldg, items = self.transactions.pop(user) # Remove the user.
		
		logger.info("%s;%s;%s;%s;%s" % (ts, self._make_timestamp(), user, bldg, items)) # Add the session to the log file.

		db.check_items(items) # Updates the file containing checked in/out items
		self._save_transactions()
		logger.debug("Exiting")
		
	def get_keys(self):
		"""
		Returns a list of the keys.
		"""
		logger.debug("Getting the keys")
		
		return db.get_items('keys')
		
	def get_tools(self):
		"""
		Returns a list of the tools.
		"""
		logger.debug("Getting the tools")
		
		return db.get_items('tools')
		
	def get_out(self):
		"""
		Returns a list of the items that are currently checked out.
		"""
		logger.debug("Getting items checked out.")
		
		return db.items_out()
		
	def get_out_by_user(self, user):
		"""
		Returns the items checked out by a current user.
		"""
		logger.debug("Enter")
		
		try:
			items = self.transactions[user][-1]
			logger.debug("Items out: %r" % items)
		except KeyError:
			logger.debug("No items")
			items = set()
			
		logger.debug("Exit")
		return items
		
	def add_user(self, u, p):
		"""
		Adds a user to the password database.
		Returns a boolen for success and a message.
		"""
		logger.debug("Entering")

		try:
			login.add_user(u, p)
		except ValueError as e:
			logger.debug("Exiting - failure")
			return False, e.message
			
		logger.debug("Exiting - success")
		return True, "%s has been added." % u
		
	def remove_user(self, u):
		"""
		Removes a user from the password database.
		Returns a boolean with a message.
		"""
		logger.debug("Entering")
		
		if login.remove_user(u):
			logger.debug("Exiting - success")
			return True, "%s has been removed." % u

		logger.debug("Exiting - failure")
		return False, "%s does not exist." % u
		
	def update_user(self, u, p):
		"""
		Updates a user in the password database.
		Returns a boolean with a message.
		"""
		logger.debug("Entering")
		val, msg = self.add_user(u, p)
		
		if val:
			msg = "%s has been updated." % u
		
		logger.debug("Exiting")
		return val, msg
		
	def check_login(self, u, p):
		"""
		Verifies a user's login credentials.
		Returns true or false and a message.
		"""
		logger.debug("Entering")
		
		try:
			val = login.validate_user(u, p)
		except ValueError as e:
			logger.debug("Exiting - failure")
			return False, e.message
		
		if val:
			logger.debug("Exiting - success")
			return True, "Login successful!"
		else:
			logger.debug("Exiting - failure")
			return False, "Login failed."