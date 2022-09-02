from bs4 import BeautifulSoup
import requests

class canvas:
  def index_segment(text, index, end):
    x, y = text.index(index)+len(index), text.index(index)+len(index)
    while text[x] != end: x += 1
    return text[y:x]
    
  class Client:
    def __init__(self, cookie):
      self.cookie = cookie
      self.client = requests.Session()
      self.client.headers = {'cookie': cookie}
    
    def course_information(self):
      data = self.client.get('https://mvla.instructure.com/api/v1/dashboard/dashboard_cards')
      course_data = []
      for course in data.json():
        course_data.append(canvas.Course(course))
      return course_data

    def get_assignments(self, course_id, limit=10):
      return list(map(lambda a: canvas.Assignment(self.client, a), self.get_assignments_raw(course_id, limit)))

    def get_upcoming_assignments(self, course_id):
      assignments = []
      for assignment in self.get_assignments_raw(course_id, limit=50):
        if assignment['attempt'] is None and assignment['graded_at'] is None:
          assignments.append(canvas.Assignment(self.client, assignment))
      return assignments

    def get_past_assignments(self, course_id, limit=10):
      assignments = []
      for assignment in self.get_assignments_raw(course_id, limit):
        if assignment['attempt'] != None:
          assignments.append(canvas.Assignment(self.client, assignment))
      return assignments

    def get_missing_assignments(self, course_id):
      assignments = []
      for assignment in self.get_assignments_raw(course_id, limit=50):
        if assignment['missing'] is True:
          assignments.append(canvas.Assignment(self.client, assignment))
      return assignments
    
    def get_assignments_raw(self, course_id, limit=10):
      data = self.client.get(f'https://mvla.instructure.com/api/v1/courses/{course_id}/students/submissions?per_page={limit}')
      return data.json()

  class Course:
    def __init__(self, raw_data):
      self.id = raw_data['id']
      self.dl = raw_data['image']
      self.name = raw_data['originalName']
      self.term = raw_data['term']
      self.links = [item['label'] for item in raw_data['links']]

  class Assignment:
    def __init__(self, client, raw_data):
      data = client.get(f'https://mvla.instructure.com/api/v1/courses/{canvas.index_segment(raw_data["preview_url"], "courses/", "/")}/assignments/{raw_data["assignment_id"]}').json()
      self.name = data['name'].strip()
      self.id = raw_data['assignment_id']
      try:
        self.due = raw_data['cached_due_date'].split('T')[0]
      except AttributeError: self.due = None
      try:
        self.score = raw_data['score']
      except KeyError: self.score = None
      self.submission_types = data['submission_types']
      if raw_data['attempt'] is None: self.completed = False
      else: self.completed = True
  
