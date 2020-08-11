class ModuleAdminCommand:
	"""
	Class used for creating admin commands for modules.
	These are only accessible through the main UI

	Args:
		trigger (string): The trigger for the command used in the UI
		action (func): Function to call when the command is triggered
		usage (string): Example usage displayed in help
		description (string): Description of the function of the command displayed in help
	"""
	def __init__(self, trigger, action, usage='', description=''):
		self.trigger = trigger
		self.action = action
		self.usage = usage
		self.description = description

	def execute(self, params=[]):
		self.action(*params)

class ModuleBase:
	"""
	Base class for all modules. Every module needs to inherit from this class.
	Instances are created automatically from the event loop
	"""
	def __init__(self, event_loop, voltron):
		self.admin_commands = {}
		self.voltron = voltron
		self.event_loop = event_loop

		self.setup()

		self.voltron.register_module(self)

	def setup(self):
		"""
		This function will be called when the module is initialized.
		It should be overridden by the module
		"""
		pass

	def shutdown(self):
		"""
		This function will be called when the module is shut down
		It should be overridden by the module
		"""
		pass

	## Helper function
	def save_module_data(self, data):
		self.voltron.save_module_data(self, data)

	def get_module_data(self):
		return self.voltron.get_module_data(self)

	def event_listen(self, event_type, callback, event_params=None):
		self.event_loop.register_event(event_type, callback, event_params)

	def send_chat_message(self, message):
		self.voltron.send_chat_message(message)

	def get_prompt(self, prompt=None, callback=None):
		return self.voltron.ui.mod_prompt(prompt, callback)

	def terminate_prompt(self, ident):
		self.voltron.ui.terminate_mod_prompt(ident)

	def update_status_text(self, text=None):
		self.voltron.ui.update_status_text(text)

	def buffer_print(self, type, msg):
		self.voltron.buffer_queue.put((type, msg))

	def register_admin_command(self, command):
		if command.trigger in self.admin_commands:
			raise Exception('Trigger {} already exists'.format(command.trigger))

		self.admin_commands[command.trigger] = command

	def available_admin_commands(self):
		return self.admin_commands.keys()

	def admin_command(self, trigger):
		return self.admin_commands.get(trigger, None)