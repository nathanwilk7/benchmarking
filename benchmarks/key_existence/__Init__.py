from locust import User, task, between

import benchmarks.utils as u


class KeyExistence(User):
	abstract = True
	insert_i = 0
	select_i = 0
	wait_time = between(0.1, 0.2)

	# NOTE multiple inheritence/composition/other? avoid duplicating init/setup/teardown for all benchmark classes?
	def __init__(self, environment):
		super().__init__(environment)
		self.request_event = environment.events.request
		self.user_setup()

	def environment_setup():
		pass

	def user_setup(self):
		pass

	@task
	def insert_helper(self):
		# TODO this validator pattern is awkward and stupid
		def insert_validator(u, i):
			if i is None:
				return False
			return True
		u.do_task(self, 'insert', self.insert, insert_validator, [self.insert_i])
		self.insert_i += 1

	def insert(self, i):
		raise NotImplementedError()

	@task
	def select_helper(self):
		def select_validator(u, i):
			if i is not None and i > u.insert_i:
				return False
			if i is None and u.select_i < u.insert_i:
				return False
			return True

		# import pdb; pdb.set_trace()
		u.do_task(self, 'select', self.select, select_validator, [self.select_i])
		self.select_i += 1

	def select(self, i):
		raise NotImplementedError()

	def user_teardown(self):
		pass

	def environment_teardown():
		pass
