from locust import User, task, between

import benchmarks.utils as u


class KeyExistence(User):
	abstract = True
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
		u.do_task(self, 'insert', self.insert)

	def insert(self):
		raise NotImplementedError()

	@task
	def select_helper(self):
		# TODO check that select results are correct?
		u.do_task(self, 'select', self.select)

	def select(self):
		raise NotImplementedError()

	def user_teardown(self):
		pass

	def environment_teardown():
		pass
