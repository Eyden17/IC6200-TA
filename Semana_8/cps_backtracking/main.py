from csp import backtracking, initialize

variables = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
domain = ['Monday', 'Tuesday', 'Wednesday']
constraints = [
    "A!=B",
    "A!=C",
    "B!=C",
    "B!=D",
    "B!=E",
    "C!=E",
    "C!=F",
    "D!=E",
    "E!=F",
    "E!=G",
    "F!=G",
]
# variables <- list of courses
# domain <- list of possible days
# constraints <- list of incompatibilities


# function main
#     courses <- initialize(variables, domain)
#     first course <- first element of courses
#     remaining courses <- all elements except the first
#     assigned courses <- empty list

#     if backtracking(first course, remaining courses, assigned courses, constraints)
#         for each course in courses
#             print the name and assigned value of the course
#     otherwise
#         print "No solution found"

def main():

    courses = initialize(variables, domain)
    first_course = courses[0]
    remaining_courses = courses[1:]
    assigned_courses = []

    if backtracking(first_course, remaining_courses, assigned_courses, constraints):
        for course in courses:
            print(course.name, course.value)
    else:
        print("No solution found")

main()

# run main
