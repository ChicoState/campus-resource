# Campus Resource

A Website to Manage, Book, and Schedule Resources for Students

## Data Model

```mermaid

classDiagram

Resource <-- Reservation
Student <-- Reservation
User <|-- Admin
User <|-- Student
  
class User{
    - id: int
    - username: string
    - email: string
    - password_hash: string
    - register(username: string, email: string, password: string) User
    - login(username: string, password: string) boolean
}

class Resource{
  - resourceName: string
  - availability: bool
  - id: int
  - description: string
  - location: string
  - category: string
  - created_at: datetime
  + register(resourceName: string, location: string, : string)
}

  class Admin{
    + addResource()
    + removeResource()
    + editResource()
    + bookStudent(studentId, resource, time)
    + removeBooking(resource, time)
  }

class Reservation{
	- id: int
	- resource: Resource
	- student: Student
	- start_time: datetime
	- end_time: datetime
  + viewReservation()
}

class Student{
    + reserve(Resource, time: datetime)
    + cancel(Reservation)
}
```
