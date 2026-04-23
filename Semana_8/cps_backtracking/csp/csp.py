import copy

# class Course
#     function __init__(name, domain)
#         name <- name
#         domain <- domain
#         value <- empty

#     function assign(value)
#         value of the course <- value

#     function remove assignment
#         value of the course <- empty
class Course:
    def __init__(self, name, domain):
        self.name = name
        self.domain = domain
        self.value = None
    
    def assign(self, value):
        self.value = value

    def remove_assignment(self):
        self.value = None

    def __str__(self):
        return f"{self.name}: {self.value}"

# function initialize(variables, domain)
#     courses <- empty list

#     for each variable in variables
#         course <- new course with that variable and a copy of the domain
#         add course to courses

#     return courses

def initialize(variables, domain):
    courses = []

    for var in variables:
        courses.append(Course(var, copy.deepcopy(domain)))

    return courses

# function is consistent(course, assigned courses, constraints)
#     assigned by name <- dictionary of assigned courses using the name as key

#     for each constraint in constraints
#         left, right <- split the constraint by "!="

#         if the course is not left and is not right
#             continue with the next constraint

#         other name <- right if the course is left, otherwise left
#         other course <- assigned course with that name

#         if other course does not exist or has no assigned value
#             continue with the next constraint

#         if the current course value is equal to the other course value
#             return false

#     return true
def is_consistent(course, assigned_courses, constraints):
    assigned_by_name = {c.name: c for c in assigned_courses}

    for constraint in constraints:
        left, right = constraint.split("!=")

        if course.name != left and course.name != right:
            continue

        other_name = right if course.name == left else left

        other_course = assigned_by_name.get(other_name)
    
        if other_course == None or other_course.value == None :
            continue

        if course.value == other_course.value:
            return False
    return True

# function backtracking(course, remaining courses, assigned courses, constraints)
#     for each day in the domain of the course
#         assign that day to the course

#         if the assignment is not consistent
#             remove the assignment from the course
#             continue with the next day

#         add the course to assigned courses

#         if there are no remaining courses
#             return true

#         next course <- first course in remaining courses
#         next remaining courses <- all remaining courses except the first one

#         if backtracking(next course, next remaining courses, assigned courses, constraints)
#             return true

#         remove the last assigned course
#         remove the assignment from the current course

#     return false


def backtracking(course, remaining_courses, assigned_courses, constraints):
    for day in course.domain:
        course.assign(day)

        if not is_consistent(course, assigned_courses, constraints):
            course.remove_assignment()
            continue

        assigned_courses.append(course)

        if remaining_courses == []:
            return True

        next_course = remaining_courses[0]
        next_remaining_courses = remaining_courses[1:]

        if backtracking(next_course, next_remaining_courses, assigned_courses, constraints):
            return True

        assigned_courses.remove(course)
        course.remove_assignment()

    return False
