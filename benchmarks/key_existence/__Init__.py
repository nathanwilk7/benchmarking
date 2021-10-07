from locust import User, task, between

import benchmarks.utils as u


class KeyExistence(User):
	abstract = True
	benchmark_name = 'KeyExistence' # TODO use filepath/module name?
	wait_time = between(0.1, 0.2)

	def __init__(self, environment):
		# TODO init implementation to reset stuff? How to spin up infra like docker
		super().__init__(environment)
		self.request_event = environment.events.request
		self.setup()

	def setup(self): # TODO separate out user startup vs app startup?
		pass

	@task
	def insert_helper(self):
		u.do_task(self, 'insert', self.insert)

	def insert(self):
		raise NotImplementedError()

	@task
	def select_helper(self):
		u.do_task(self, 'select', self.select)

	def select(self):
		raise NotImplementedError()