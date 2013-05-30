#!/usr/bin/env python

"""
Tools GUI program. Written and designed for SCOII Network Integration.
Controls the status of tools being checked in and out of the work center.

Author: Scott Shepherd
Version: 2.0
"""

### Python modules ###
import itertools
import os
from Tkinter import *
from ttk import *
import tkMessageBox

### User modules ###
from source.shelf import Shelf
from source.tools import Tools
from source import my_logger

### Logging ###
logger = my_logger.create_logger(__name__)

### Globals ###
WIDTH = 300
HEIGHT = 200
ADMIN = 'root'
COMMON_TOOLS = 9 # Number of tools to consider "Common"
COMMON_KEYS = 3 # Number of keys to consider "Common"
SHELF_LENGTH = 3

class ToolsGui(Frame):
	"""
	GUI designed to control the tools program.
	"""
	
	def __init__(self, parent):
		logger.debug("Enter")
		
		Frame.__init__(self, parent)
		
		# Functionality for interacting with the tools program
		self.tools = Tools()
		self.parent = parent
		
		# Username and password used for logging in
		self.user = StringVar("")
		self.pw = StringVar("")
		self.building = StringVar("")
		
		# Holds the items that have been inventoried throughout the day
		self.inventory = set()
		
		self.pack()
		
		self._kick_off()
		
		logger.debug("Exit")

	### Private Functions ###		
	def _setup_frame(self, name):
		"""
		Configures the same basic options across frames.
		"""
		
		return Frame(self.parent, name = name, padding = (50, 50))
		
	def _kick_off(self):
		logger.debug("Enter")
		
		self.current_frame = self._make_frame('login')
		self.current_frame.pack()
		
		logger.debug("Exit")
		
	def _center_window(self, frame, w = WIDTH, h = HEIGHT):
		"""
		Centers the window using the w and h given as the top left corner.
		"""
		
		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()
		
		x = (sw - w) / 2
		y = (sh - h) / 2
		
		frame.geometry('%dx%d+%d+%d' % (w, h, x, y))
		
	def _switch_frame(self, next_frame):
		"""
		Changes the current frame to the next frame, and updates the prev_frame variable.
		"""
		logger.debug("Enter")
		logger.debug("Current frame %r" % self.current_frame._name)
		
		self.current_frame.pack_forget()
		self.current_frame.destroy()
		self.current_frame = self._make_frame(next_frame)
		self.current_frame.pack()
		
		logger.debug("Exit")
		
	def _make_frame(self, frame_name):
		"""
		Takes in the frame name and dispatches the proper frame creation method.
		Raises ValueError if the frame name isn't valid.
		"""
		logger.debug("Enter")
		
		FRAMES = {'login': self._create_frame_login,
						   'main': self._create_frame_main,
						   'in': self._create_frame_in,
						   'out': self._create_frame_out,
						   'search': self._create_frame_search,
						   'admin': self._create_frame_admin}
						   
		try:
			func = FRAMES[frame_name]
		except KeyError:
			logger.warn("Exit - Failure. No valid frame name.")
			raise ValueError("Invalid frame name.")
			
		logger.debug("Exit - Success")
		return func(frame_name)
		
	def _get_login(self):
		"""
		Returns the login information from the user/PIN box, and then clears them.
		"""
		logger.debug("Enter")
		
		user = self.user.get()
		pw = self.pw.get()
		
		self.user.set("")
		self.pw.set("")
		
		logger.debug("Exit")
		return user, pw
		
	def _modify_user(self, add = True):
		"""
		Adds a user to the password file.
		"""
		logger.debug("Enter")
		
		if add:
			func = self.tools.add_user
		else:
			func = self.tools.update_user
			
		self._create_dialog_msg(*func(*self._get_login()))
		
		logger.debug("Exit")
		
	def _remove_user(self):
		"""
		Removes a user from the program.
		"""
		logger.debug("Enter")
		
		user = self._get_login()[0]
		
		if user == ADMIN:
			self._create_dialog_msg(False, "Can't remove root.")
		else:
			self._create_dialog_msg(*self.tools.remove_user(user))
		
		logger.debug("Exit")
	
	def _check_login(self):
		"""
		Checks a login for a user to see if it's valid.
		"""
		logger.debug("Enter")
		
		user, pw = self._get_login()
		val, msg = self.tools.check_login(user, pw)
		
		if val:
			logger.debug("Login successful!")
			if user == ADMIN:
				frame_next = 'admin'
			else:
				self.current_user = user
				frame_next = 'main'
			self._switch_frame(frame_next)
		else:
			self._create_dialog_msg(val, msg)
			
		logger.debug("Exit")
		
	def _remove_items(self):
		"""
		It looks like that when a window is destroyed, the children get destroyed, but a reference
		is kept in the below attributes. However, it appears Python doesn't want to overwrite them
		if it doesn't have to when a frame is recalled. So, we'll delete the items between frame calls
		to force them being recreated. This is called in the _create_main_frame to make sure that
		they're deleted before any item is shown.
		
		TL;DR: Magic that makes the images work.
		"""
		
		try:
			del self.common_tools
			del self.uncommon_tools
			del self.common_keys
			del self.uncommon_keys
		except AttributeError:
			pass
			
		try:
			del self.items_out
		except AttributeError:
			pass
	
	def _logout(self):
		logger.debug("Enter")
		
		self._switch_frame('login')
		
		logger.debug("Exit")
		
	def _create_login_buttons(self, parent, func):
		"""
		Creates login buttons for add frame and login frame.
		Users a grid layout.
		"""
		logger.debug("Enter")
		
		Label(parent, text = "User").grid(row = 0, column = 0)
		
		entry_user = Entry(parent, textvariable = self.user)
		entry_user.focus_set()
		entry_user.grid(row = 0, column = 1, columnspan = 2)
		
		Label(parent, text = "PIN").grid(row = 1, column = 0)
		entry_pin = Entry(parent, textvariable = self.pw, show = '*')
		entry_pin.bind("<Return>", func)
		entry_pin.bind("<KP_Enter>", func)
		entry_pin.grid(row = 1, column = 1, columnspan = 2)
		
		logger.debug("Exit")
		
	def _get_building_number(self):
		"""
		Creates the dialog for a building number box then returns the building #.
		"""
		logger.debug("Enter")
		
		self._create_dialog_get_building()
		
		building = self.building.get()
		self.building.set("")
		
		logger.debug("Exit")
		return building	
		
	def _check_in(self, all = True):
		"""
		Allows the user to check in any items they may have.
		Items is a list of items to check in.
		"""
		logger.debug("Enter")
		
		if all:
			logger.debug("All tools")
			
			try:
				self.inventory.update(self.tools.get_out_by_user(self.current_user))
				self.tools.checkin_items(self.current_user)
				self._create_dialog_msg(True, "All of your items have been checked in.")
			except KeyError:
				self._create_dialog_msg(False, "You have no items to check in.")
		else:
			logger.debug("Some tools")
			
			items_out = self.items_out.items_out_by_name()
			all_items = self.tools.get_out_by_user(self.current_user)
			self.inventory.update(all_items)
			recheck_out = all_items - items_out
			
			logger.debug("Items out: %r\nAll items: %r\nRechecking: %r" % (items_out, all_items, recheck_out))
			
			try:
				self.tools.checkin_items(self.current_user) # Check in all items
			except KeyError:
				self._create_dialog_msg(False, "You have no items to check in.")
			
			if recheck_out:
				self.tools.checkout_items(self.current_user, recheck_out, self._get_building_number()) # Check out items left over
				
			self._create_dialog_msg(True, "You have checked in:\n%s" % self._pretty_names(items_out))
			
		self._switch_frame('login')
		
		logger.debug("Exit")
		
	def _check_out(self):
		"""
		Allows the user to check out items.
		"""
		logger.debug("Enter")
		
		item_lists = [self.common_tools, self.uncommon_tools, self.common_keys, self.uncommon_keys]
		item_set = Shelf()
			
		for item in item_lists:
			item_set.extend(item.items_out()) # Update latest checked out items.
				
		item_set.update_names()
		item_set_names = self.tools.trim_items(item_set.items_out_by_name())
			
		# Make sure we have some items checked out.
		if not item_set_names:
			self._create_dialog_msg(False, "Please either hit 'Cancel' or select some items to check out.")
			return
			
		item_set.remove_clicks()
		
		for item in item_set_names:
			if 'laptop' in item or 'lrduo' in item:
				self._create_dialog_acknowledge() # Should display only if a fluke or laptop is in the items list
				break

		self.tools.checkout_items(self.current_user, item_set_names, self._get_building_number())
		self.inventory.update(item_set_names)
		
		self._switch_frame('login')
		
		logger.debug("Exit")
		
	def _cancel(self, frame = 'main'):
		"""
		A cancel button for getting out of a certain frame.
		"""
		logger.debug("Enter")
		
		self._switch_frame(frame)
		
		logger.debug("Exit")
		
	def _expand(self, button, frame):
		"""
		Expands or collapses the frame then updates the text in button.
		"""
		logger.debug("Enter")
		
		if frame.winfo_manager() == 'pack':
			logger.debug("Packed -> Unpacked")
			
			frame.pack_forget()
			button['text'] = 'Expand'
		else:
			logger.debug("Unpacked -> Packed")
			
			frame.pack()
			button['text'] = 'Collapse'
			
		logger.debug("Exit")
				
	def _grid_buttons(self, items, column_length = SHELF_LENGTH):
		"""
		Populates the item grids.
		"""
		logger.debug("Enter")
			
		rows = (len(items) / column_length) + 1
			
		for i in range(rows):
			for index, item in enumerate(items[i * column_length: (i + 1) * column_length]):
				item.grid(row = i, column = index)

		logger.debug("Exit")
		return items
		
	def _pretty_names(self, item_list):
		"""
		Takes a list of item names and returns a newline 'separated' string of 'prettified' item names.
		"""
		
		return '\n'.join(item.replace('_', ' ').title() for item in item_list)
		
	### Widget - Frames ###
	def _create_frame_login(self, name):
		"""
		Creates and returns the login frame.
		"""
		logger.debug("Enter")
		
		frame = Frame(self.parent, name = name)
		
		self._create_login_buttons(frame, lambda e: self._check_login())
		
		button_login = Button(frame, text = "Login", command = self._check_login)
		button_login.bind("<Return>", lambda e: self._check_login())
		button_login.bind("<KP_Enter>", lambda e: self._check_login())
		button_login.grid(row = 2, column = 2)
		
		button_search = Button(frame, text = "Search")
		#button_search.grid(row = 3, column = 0)
		
		button_inventory = Button(frame, text = "Inventory", command = self._create_dialog_inventory)
		button_inventory.bind("<Return>", lambda e: self._create_dialog_msg(True, "Inventory the following items:\n%s" % self._pretty_names(self.inventory)))
		button_inventory.bind("<KP_Enter>", lambda e: self._create_dialog_msg(True, "Inventory the following items:\n%s" % self._pretty_names(self.inventory)))
		#button_inventory.grid(row = 3, column = 1)
		
		button_out = Button(frame, text = "Out", command = self._create_dialog_items_out)
		button_out.bind("<Return>", lambda e: self._create_dialog_items_out())
		button_out.bind("<KP_Enter>", lambda e: self._create_dialog_items_out())
		button_out.grid(row = 2, column = 0)
		
		logger.debug("Exit")
		return frame
		
	def _create_frame_admin(self, name):
		"""
		Creates and returns the admin frame.
		"""
		logger.debug("Enter")
		
		frame = Frame(self.parent, name = name)
		
		button_add = Button(frame, text = "Add User", command = lambda: self._create_dialog_modify_user('Add', True))
		button_add.bind("<Return>", lambda e: self._create_dialog_modify_user('Add', True))
		button_add.bind("<KP_Enter>", lambda e: self._create_dialog_modify_user('Add', True))
		button_add.pack(side = LEFT)
		
		button_remove = Button(frame, text = "Remove User", command = self._create_dialog_remove_user)
		button_remove.bind("<Return>", lambda e: self._create_dialog_remove_user())
		button_remove.bind("<KP_Enter>", lambda e: self._create_dialog_remove_user())
		button_remove.pack(side = LEFT)
		
		button_update = Button(frame, text = "Update User", command = lambda: self._create_dialog_modify_user('Update', False))
		button_update.bind("<Return>", lambda e: self._create_dialog_modify_user('Update', False))
		button_update.bind("<KP_Enter>", lambda e: self._create_dialog_modify_user('Update', False))
		button_update.pack(side = LEFT)
		
		button_logout = Button(frame, text = "Logout", command = self._logout)
		button_logout.bind("<Return>", lambda e: self._logout())
		button_logout.bind("<KP_Enter>", lambda e: self._logout())
		button_logout.pack(side = LEFT)
		
		logger.debug("Exit")
		return frame
		
	def _create_frame_main(self, name):
		"""
		Creates and returns the main frame.
		"""
		logger.debug("Enter")
		
		self._remove_items()
		
		frame = Frame(self.parent, name = name)
		
		button_out = Button(frame, text = "Check Out", command = lambda: self._switch_frame('out'))
		button_out.bind("<Return>", lambda e: self._switch_frame('out'))
		button_out.bind("<KP_Enter>", lambda e: self._switch_frame('out'))
		button_out.focus_set()
		button_out.pack()
		
		button_in = Button(frame, text = "Check In", command = lambda: self._switch_frame('in'))
		button_in.bind("<Return>", lambda e: self._switch_frame('in'))
		button_in.bind("<KP_Enter>", lambda e: self._switch_frame('in'))
		button_in.pack()
		
		button_logout = Button(frame, text = "Logout", command = self._logout)
		button_logout.bind("<Return>", lambda e: self._logout())
		button_logout.bind("<KP_Enter>", lambda e: self._logout())
		button_logout.pack()
		
		logger.debug("Exit")
		return frame
		
	def _create_frame_out(self, name):
		"""
		Creates and returns the check out frame.
		"""
		logger.debug("Enter")
		
		def _split_shelves(items, split):
			return items[:split], items[split:]

		frame = Frame(self.parent, name = name)
		
		# Display two pages of items wrapped with a labeled box.
		frame_items = Frame(frame, name = "items")
		frame_items.pack()
		
		frame_tools = LabelFrame(frame_items, text = "Tools", name = "frame_tools")
		frame_tools.pack(side = LEFT, anchor = N)
		
		frame_common_tools = Frame(frame_tools, name = "common_tools")
		frame_common_tools.pack()

		
		button_tools_expand = Button(frame_tools, text = "Expand")
		button_tools_expand.pack()
		
		frame_uncommon_tools = Frame(frame_tools, name = "uncommon_tools")
		
		
		frame_keys = LabelFrame(frame_items, text = "Keys", name = "frame_keys")
		frame_keys.pack(side = RIGHT, anchor = N)
		
		frame_common_keys = Frame(frame_keys, name = "common_keys")
		frame_common_keys.pack()
		
		
		button_keys_expand = Button(frame_keys, text = "Expand")
		button_keys_expand.pack()
		
		frame_uncommon_keys = Frame(frame_keys, name = "uncommon_keys")

		button_tools_expand['command'] = lambda: self._expand(button_tools_expand, frame_uncommon_tools)
		button_tools_expand.bind("<Return>", lambda e: self._expand(button_tools_expand, frame_uncommon_tools))
		button_tools_expand.bind("<KP_Enter>", lambda e: self._expand(button_tools_expand, frame_uncommon_tools))
		
		button_keys_expand['command'] = lambda: self._expand(button_keys_expand, frame_uncommon_keys)
		button_keys_expand.bind("<Return>", lambda: self._expand(button_keys_expand, frame_uncommon_keys))
		button_keys_expand.bind("<KP_Enter>", lambda: self._expand(button_keys_expand, frame_uncommon_keys))
		
		tools = self.tools.get_tools()
		common_tools, uncommon_tools = _split_shelves(tools, COMMON_TOOLS)
		
		keys = self.tools.get_keys()
		common_keys, uncommon_keys = _split_shelves(keys, COMMON_KEYS)
		
		self.common_tools = Shelf(frame_common_tools, common_tools)
		self.uncommon_tools = Shelf(frame_uncommon_tools, uncommon_tools)
		self.common_keys = Shelf(frame_common_keys, common_keys)
		self.uncommon_keys = Shelf(frame_uncommon_keys, uncommon_keys)
		
		self._grid_buttons(self.common_tools)
		self._grid_buttons(self.uncommon_tools)
		self._grid_buttons(self.common_keys)
		self._grid_buttons(self.uncommon_keys)
		
		items_out = self.tools.get_out()
		
		self.common_tools.mark_out(items_out)
		self.uncommon_tools.mark_out(items_out)
		self.common_keys.mark_out(items_out)
		self.uncommon_keys.mark_out(items_out)

		frame_buttons = Frame(frame)
		frame_buttons.pack()
		
		button_out = Button(frame_buttons, text = "Check Out", command = lambda: self._check_out())
		button_out.bind("<Return>", lambda e: self._check_out())
		button_out.bind("<KP_Enter>", lambda e: self._check_out())
		button_out.pack()
		
		button_cancel = Button(frame_buttons, text = "Cancel", command = self._cancel)
		button_cancel.bind("<Return>", lambda e: self._cancel())
		button_cancel.bind("<KP_Enter>", lambda e: self._cancel())
		button_cancel.pack()
		
		logger.debug("Exit")
		return frame
		
	def _create_frame_in(self, name):
		"""
		Creates and returns the check-in frame.
		"""
		logger.debug("Enter")
		
		frame = Frame(self.parent, name = name)
		
		button_all = Button(frame, text = "Check All", command = self._check_in)
		button_all.bind("<Return>", lambda e: self._check_in())
		button_all.bind("<KP_Enter>", lambda e: self._check_in())
		button_all.focus_set()
		button_all.pack()
		
		frame_items_out = Frame(frame)
		frame_items_out.pack()
		
		items_out = self.tools.get_out_by_user(self.current_user)
		self.items_out = Shelf(frame_items_out, items_out)
		
		self._grid_buttons(self.items_out)
		
		if len(self.items_out) == 0:
			Label(frame_items_out, text = "You have no items to check in.").pack()
		
		button_some = Button(frame, text = "Check Selected", command = lambda: self._check_in(all = False))
		button_some.bind("<Return>", lambda e: self._check_in(all = False))
		button_some.bind("<KP_Enter>", lambda e: self._check_in(all = False))
		button_some.pack()
		
		button_cancel = Button(frame, text = "Cancel", command = self._cancel)
		button_cancel.bind("<Return>", lambda e: self._cancel())
		button_cancel.bind("<KP_Enter>", lambda e: self._cancel())
		button_cancel.pack()
		
		return frame
		
	def _create_frame_search(self, name):
		pass
		
	### Widget - Dialogs ###
	def _setup_dialog(self, w = 200, h = 100):
		"""
		Config initial dialog box settings.
		"""
		logger.debug("Enter")
		
		window = Toplevel(self.parent, takefocus = True)
		window.transient(self.parent)
		window.grab_set()
		self._center_window(window, w, h)
		
		logger.debug("Exit")
		
		return window
		
	def _create_dialog_get_building(self):
		"""
		Dialog used to get the building from the user.
		"""
		logger.debug("Enter")
		
		window = self._setup_dialog()
		
		Label(window, text = "Building").pack()
		
		entry_building = Entry(window, textvariable = self.building)
		entry_building.focus_set()
		entry_building.bind("<Return>", lambda e: window.destroy())
		entry_building.bind("<KP_Enter>", lambda e: window.destroy())
		entry_building.pack()
		
		button_ok = Button(window, text = "Ok", command = window.destroy)
		button_ok.bind("<Return>", lambda e: window.destroy())
		button_ok.bind("<KP_Enter>", lambda e: window.destroy())
		button_ok.pack()
		
		window.wait_window(window)

	def _create_dialog_acknowledge(self):
		logger.debug("Enter")
		
		msg = "I acknowledge receipt of and responsibility IAW AFI 23-111\nfor the items listed herein."
		
		self._create_dialog_msg(True, msg)
		
		logger.debug("Exit")

	def _create_dialog_msg(self, val, msg):
		"""
		Displays a message in a dialog.
		"""
		logger.debug("Enter")
		
		if val:
			tkMessageBox.showinfo("Information", msg)
		else:
			tkMessageBox.showerror("Error", msg)
			
		logger.debug("Exit")
		
	def _create_dialog_remove_user(self):
		"""
		Creates the dialog box for removing a user from the program.
		"""
		logger.debug("Enter")
		
		window = self._setup_dialog(w = 260, h = 100)
		
		Label(window, text = "User").grid(row = 0, column = 0)
		
		entry_user = Entry(window, textvariable = self.user)
		entry_user.focus_set()
		entry_user.grid(row = 0, column = 1, columnspan = 2)
		
		button_remove = Button(window, text = "Remove", command = self._remove_user)
		button_remove.bind("<Return>", lambda e: self._remove_user())
		button_remove.bind("<KP_Enter>", lambda e: self._remove_user())
		button_remove.grid(row = 2, column = 0)
		
		button_list = Button(window, text = "List Users", command = lambda: self._create_dialog_msg(True, '\n'.join(self.tools.get_users())))
		button_list.bind("<Return>", lambda e: self._create_dialog_msg(True, '\n'.join(self.tools.get_users())))
		button_list.bind("<KP_Enter>", lambda e: self._create_dialog_msg(True, '\n'.join(self.tools.get_users())))
		button_list.grid(row = 2, column = 1)
		
		button_cancel = Button(window, text = "Cancel", command = window.destroy)
		button_cancel.bind("<Return>", lambda e: window.destroy())
		button_cancel.bind("<KP_Enter>", lambda e: window.destroy())
		button_cancel.grid(row = 2, column = 2)
		
		window.wait_window(window)
		
		logger.debug("Exit")
		
	def _create_dialog_modify_user(self, text, add):
		"""
		Creates the dialog box for updating a user in the program.
		"""
		logger.debug("Enter")
		
		window = self._setup_dialog()
		
		self._create_login_buttons(window, lambda e: self._modify_user(add))
		
		button_add = Button(window, text = text, command = lambda: self._modify_user(add))
		button_add.bind("<Return>", lambda e: self._modify_user(add))
		button_add.bind("<KP_Enter>", lambda e: self._modify_user(add))
		button_add.grid(row = 2, column = 0)
		
		button_cancel = Button(window, text = "Cancel", command = window.destroy)
		button_cancel.bind("<Return>", lambda e: window.destroy())
		button_cancel.bind("<KP_Enter>", lambda e: window.destroy())
		button_cancel.grid(row = 2, column = 2)
		
		window.wait_window(window)
		
		logger.debug("Exit")
		
	def _create_dialog_items_out(self):
		"""
		Creates a dialog for displaying who has what checked out.
		"""
		logger.debug("Enter")
		
		window = self._setup_dialog(w = 700, h = 550)
		
		frame_holder = []
		
		if self.tools.transactions != {}:
			for user in self.tools.transactions.keys():
				Label(window, text = '%s - %s' % (user.capitalize(), self.tools.get_building_by_user(user))).pack()
			
				tmp = Frame(window)
				tmp.pack()

				items = self.tools.transactions[user][-1]
				
				shelf_tmp = Shelf(tmp, items)
				shelf_tmp.remove_clicks()
				
				self._grid_buttons(shelf_tmp)
				
		else:
			Label(window, text = "No items are currently out.").pack()
			
		button_ok = Button(window, text = "Ok", command = window.destroy)
		button_ok.bind("<Return>", lambda e: window.destroy())
		button_ok.bind("<KP_Enter>", lambda e: window.destroy())
		button_ok.focus_set()
		button_ok.pack()
		
		window.wait_window(window)
		
		logger.debug("Exit")
		
	def _create_dialog_inventory(self):
		"""
		Creates a dialog for display what items need to be inventoried.
		"""
		
		if self.tools.get_out():
			self._create_dialog_msg(False, "There are items still checked out.")
		else:
			window = self._setup_dialog(w = 700, h = 550)
		
			frame_inv = Frame(window)
			frame_inv.pack()
		
			Label(frame_inv, text = "Inventory").pack()
		
			frame_items = Frame(frame_inv)
			frame_items.pack()
			
			self.inventory.intersection_update(self.tools.get_tools())
		
			shelf_tmp = Shelf(frame_items, self.inventory)
			self._grid_buttons(shelf_tmp)
		
			button_done = Button(frame_inv, text = "Done", command = window.destroy)
			button_done.bind("<Return>", lambda e: window.destroy())
			button_done.bind("<KP_Enter>", lambda e: window.destroy())
			button_done.pack()
		
			window.wait_window(window)
		
def main():
	root = Tk()
#	root.wm_state('zoomed') # Prolly not portable. Oh well.
	app = ToolsGui(root)
	root.mainloop()
	
if __name__ == '__main__':
	main()
