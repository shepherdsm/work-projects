### Python Modules ###
import collections
import csv
import datetime
import itertools
from operator import mul
import os
import re
import shelve
import subprocess

class RangePing(object):
	"""
	Creates an IP address range that can be pinged. Stores a bldg -> ip_range database
	file for grabbing of the IPs instead of constantly regenerating the ranges. By default stores
	the results of the ping into a CSV using the building's name.
	"""
	
	def __init__(self, start = None, subnet = None, bldg = None):
		self.delimiter = ',' # Delimiter for the CSV file.
		self.resource = 'resources'
		self.db_file = os.path.join(self.resource, 'lookup.dat') # Database file for storing Bldg -> Range
		self.net_id = start
		self.subnet = subnet
		self.bldg = bldg
		
		self._load_range()
		
	### Properties ###
	@property
	def resource(self):
		return self._resource
		
	@resource.setter
	def resource(self, value):
		if not os.path.isdir(value):
			os.mkdir(value)
			
		self._resource = value

	@property
	def bldg(self):
		return self._bldg
		
	@bldg.setter
	def bldg(self, value):
		self._bldg = value
		self._name = os.path.join(self.resource, '%s.csv' % self.bldg)

	### Private Methods ###
	def _make_ping(self, args):
		"""
		Takes in any args and creates a ping string using them.
		"""
		
		if not args:
			args = ""
			
		command = ' '.join(["ping"] + args.split() + ["%s"])
		
		return command
		
	def _make_range(self):
		"""
		Uses the given net_id / subnet to make the pingable range of IP addresses.
		NOTE: Includes the NET ID and Broadcast in the range generated. Be aware.
		Accepts both CIDR notation and the normal IP/Subnet notation.
		"""
		
		if not self.net_id:
			raise ValueError("Please provide a net id.")
		
		if not self.subnet: # We should be in CIDR notation
			try:
				self.net_id, slash = self.net_id.split('/')
			except ValueError:
				raise ValueError ("Please use either CIDR notation (xxx.xxx.xxx.xxx/xx) or have an IP and Subnet.")
				
			full, part = divmod(int(slash), 8)
			self.subnet = '.'.join(map(str, [255] * full + [256 - 2 ** (8 - part)] + [0] * (3 - full)))
			
		seg_ip = map(int, self.net_id.split('.'))
		subnet_values = [255 ^ int(i) for i in self.subnet.split('.')]
		variances = [xrange(seg_ip[i], seg_ip[i] + v + 1) for i, v in enumerate(subnet_values)]
		
		self.length = reduce(mul, [i + 1 for i in subnet_values]) - 2
		
		return variances
		
	def _parse_reply(self, reply):
		"""
		Takes in a reply returned by subprocess, and looks in it for useful information.
		Returns the following:
		yes - All replies good
		partial - Some replies
		no - No replies (They all timed out)
		unreachable - Destination unreachable
		"""
		
		pattern = '(\d+)% loss'
		num = re.findall(pattern, reply)[0]
		
		val = 'partial'
		if 'unreachable' in reply:
			val = 'unreachable'
		elif num == '0':
			val = 'yes'
		elif num == '100':
			val = 'no'
		
		return val
		
	def _save_range(self, overwrite = False):
		"""
		Saves the range in the database file if it isn't present.
		If overwrite is true, it doesn't care.
		Returns true if it was saved successfully.
		Returns False if it was unable to be saved.
		"""
		
		if not self.bldg: # We have no name to save to. Fail silently.
			return False

		db = shelve.open(self.db_file, "w")
		
		if self.bldg not in db or overwrite:
			db[self.bldg] = [str(self.range), str(self.length)]
			
		db.close()
		
		return True
			
	def _load_range(self):
		"""
		Loads the range from the database or creates the range from scratch.
		"""

		db = shelve.open(self.db_file)

		try:
			self.range = eval(db[self.bldg][0], {"__builtins__": None}, {"xrange": xrange})
			self.length = eval(db[self.bldg][1], {"__builtins__": None}, {}) - 2
		except KeyError:
			self.range = self._make_range()
		finally:
			db.close()

		if self.bldg:
			self._save_range()
			
	def _get_previous(self):
		"""
		Gets the previous results in the file.
		"""
		
		try:
			with open(self._name, 'r') as data:
				reader = csv.reader(data, delimiter = self.delimiter)
				return [row for row in reader]
		except IOError as e:
			self.save_results(overwrite = True)
			return self._get_previous()
			
	### Public Methods ###
	def get_summary(self):
		"""
		Gets a summary of the results and returns a string.
		Must be called after a range has been pinged. Raises an error otherwise.
		"""
		
		if not self.results:
			raise ValueError("Range has not been pinged yet.")
		
		results_str = "\n\n{} IPs were pinged.\n".format(len(self.results))
		for k, v in collections.Counter(a[-1] for a in self.results).items():
			if v == 1:
				word = 'was'
				end = ''
			else:
				word = 'were'
				end = 's'
			results_str += 'There {} {} result{} for "{}".\n'.format(word, v, end, k)
			
		return results_str
	
	def save_results(self, overwrite = False):
		"""
		Saves the results of the range ping.
		Must be called after a range has been pinged. Raises an error otherwise.
		Returns true if the range was successfully saved.
		Returns false otherwise.
		"""

		if not self.results:
			raise ValueError("Range has not been pinged yet.")
			
		if not self.bldg:
			return False
			
		if overwrite:
			prev_results = [['Date']]
			for ip in list(itertools.product(*self.range))[1:-1]:
				prev_results.append(['.'.join(map(str, ip))])
		else:
			prev_results = self._get_previous()
			
		prev_results[0].append(datetime.datetime.now().ctime())
		for i, r in enumerate(self.results):
			prev_results[i + 1].append(r[-1])

		with open(self._name, 'w') as tmp:
			w = csv.writer(tmp, delimiter = self.delimiter)
			w.writerows(prev_results)
			
		return True
		
	def ping(self, arguments=None):
		"""
		Takes in any arguments for the ping command and makes a ping string.
		Pings all the IP addresses in the csv file defined earlier.
		"""
		
		# Ping command
		ping = self._make_ping(arguments)
		self.results = []
		
		# Open the CSV file and ping all the IP addresses.
		for ip in list(itertools.product(*self.range))[1:-1]: # Skips the net id and broadcast
			ip = '.'.join(map(str, ip))
			tmp = [ip]
				
			command = subprocess.Popen(ping % ip, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
			res = self._parse_reply(command.communicate()[0])
				
			yield res
				
			tmp.append(res) # Passes in the reply of the communicate method
			self.results.append(tmp)