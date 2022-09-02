from canvas import canvas
import os

client = canvas.Client(os.environ['cookie'])
courses = client.course_information()

for i in range(len(courses)):
  for assignment in client.get_upcoming_assignments(courses[i].id):
    print(assignment.name)
