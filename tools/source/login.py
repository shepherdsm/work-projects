### Python Modules ###
import hashlib
import os
import re
import shelve

### User Modules ###
import my_logger

### Globals ###
RSC_D = 'resources'
PASS_F = os.path.join(RSC_D, 'pass')

### Logging ###
logger = my_logger.create_logger(__name__)

### Private Functions ###
def _crypt_pass(p):
	"""
	Encrypts the password and returns the hex digest.
	"""
	logger.debug("Entering")
	
	crypt = hashlib.sha512(p).hexdigest()
	
	logger.debug("Exiting")
	return crypt
	
def _validate_pass(p):
	"""
	Makes sure the password meets the correct spefications.
	"""
	logger.debug ("Entering")
	
	pattern = "\d{4,}"
	if not re.match(pattern, p):
		logger.debug("PIN was too short.")
		raise ValueError("PIN must be 4+ numbers in length.")
	if p.count(p[0]) == len(p):
		logger.debug("PIN can't contain all of the same digits.")
		raise ValueError("PIN must not contain all the same digits.")
		
	logger.debug("Exiting")

### Public Functions ###
def validate_user(u, p):
	"""
	Validates a user against their password. There must be a password and
	username passed to the function.
	Throws an exception to be handled if the password isn't properly validated.
	Or if there is no username or password.
	"""
	logger.debug("Entering")
	if not u:
		raise ValueError("Enter a username.")
	if not p:
		raise ValueError("Enter a PIN.")
	
	pass_file = shelve.open(PASS_F)
	
	try:
		_validate_pass(p)
	except ValueError:
		raise
	
	try:
		test_pass = pass_file[u]
	except KeyError:
		logger.debug("No username in pass file matching %s." % (u))
		return False
	finally:
		pass_file.close()
		
	if _crypt_pass(p) == test_pass:
		return True
	return False
		
	logger.debug("Exiting")
	
def get_users():
	"""
	Returns the users of the program.
	"""
	logger.debug("Entering")
	
	pass_file = shelve.open(PASS_F)
	users = pass_file.keys()
	pass_file.close()
	
	try:
		users.remove('root')
	except KeyError:
		pass
	
	logger.debug("Users: %s" % users)
	logger.debug("Exiting")
	return users
	
def remove_user(u):
	"""
	Removes a user from the password file.
	"""
	logger.debug("Entering")
	
	pass_file = shelve.open(PASS_F, writeback=True)
	
	try:
		pass_file.pop(u)
	except KeyError:
		logger.debug("No user %s found. Exiting 'silently'." % u)
		return False
	finally:
		pass_file.close()
	
	logger.debug("Exiting")
	return True
	
def add_user(u, p):
	"""
	Adds a user to the password file.
	Throws an exception if the password is not valid.
	"""
	logger.debug("Entering")
	assert u and p, "Please supply a username and PIN"
	
	try:
		_validate_pass(p)
	except ValueError:
		raise
	
	pass_file = shelve.open(PASS_F, writeback=True)
	pass_file[u] = _crypt_pass(p)
	pass_file.close()
	
	logger.debug("Exiting")
	
def update_user(u, p):
	"""
	Updates a user.
	Throws an exception if the password is not valid.
	"""
	logger.debug("Entering")
	add_user(u, p)
	logger.debug("Exiting")