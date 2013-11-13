import webapp2
import jinja2
import os
import datetime
from webapp2_extras import json
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

DEFAULT_LIST_NAME = 'default_list'
ADMIN_PASSWORD = 'jklpop'

def list_key(list_name=DEFAULT_LIST_NAME):
	"""Constructs a Datastore key for a Guestbook entity with guestbook_name."""
	return ndb.Key('List', list_name)

class Volume(ndb.Model):
	"""Models an individual volume entry with date, and number"""
	volumeNumber = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=False)

class MainPage(webapp2.RequestHandler):
	def get(self):
		now = datetime.datetime.now()
		volumes_query = Volume.query(Volume.date > now, ancestor=list_key()).order(Volume.date)
		volumes = volumes_query.fetch(1)
		timeDelt = volumes[0].date - now
		volumeNumber = volumes[0].volumeNumber
		template_values = {
			'daysAway': timeDelt.days + 1,
			'volumeNumber': volumeNumber
		}
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class JSONResponse(webapp2.RequestHandler):
	def get(self):
		now = datetime.datetime.now()
		volumes_query = Volume.query(Volume.date > now, ancestor=list_key()).order(Volume.date)
		volumes = volumes_query.fetch(1)
		timeDelt = volumes[0].date - now
		volumeNumber = volumes[0].volumeNumber
		json_values = {
			'volumeNumber': volumeNumber,
			'daysAway ' : timeDelt.days + 1
		}
		self.response.write(json.encode(json_values))

class ArduinoResponse(webapp2.RequestHandler):
	def get(self):
		now = datetime.datetime.now()
		volumes_query = Volume.query(Volume.date > now, ancestor=list_key()).order(Volume.date)
		volumes = volumes_query.fetch(1)
		timeDelt = volumes[0].date - now
		self.response.write(timeDelt.days + 1)

class Admin(webapp2.RequestHandler):
	def get(self):
		template_values = {
			'message': "Please use password to see records."
		}
		template = JINJA_ENVIRONMENT.get_template('admin.html')
		self.response.write(template.render(template_values))

	def post(self):
		if self.request.get('password') == ADMIN_PASSWORD:
			if self.request.get('date') is not "":
				volume = Volume(parent=list_key())
				volume.volumeNumber = self.request.get('volumeNumber')
				volume.date = datetime.datetime.strptime(self.request.get('date'), "%m/%d/%Y")
				volume.put()
				message = "Added!"
				volumes_query = Volume.query(
				ancestor=list_key()).order(Volume.date)
				volumes = volumes_query.fetch(100)
			else:
				volumes_query = Volume.query(
				ancestor=list_key()).order(Volume.date)
				volumes = volumes_query.fetch(100)
				message = "Enter info below to add a record."
			template_values = {
				'message': message,
				'volumes': volumes
			}
		else:
			message = "Password incorrect."
			template_values = {
				'message': message,
			}
		template = JINJA_ENVIRONMENT.get_template('admin.html')
		self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/admin', Admin),
	('/json', JSONResponse),
	('/arduino', ArduinoResponse)
], debug=True)