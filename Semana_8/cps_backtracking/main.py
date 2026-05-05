from csp import (
    ac3,
    backtracking,
    backtracking_with_inference,
    initialize,
    select_degree,
    select_mrv,
    select_mrv_degree,
)


SAMPLE_VARIABLES = ["A", "B", "C", "D", "E", "F", "G"]
SAMPLE_DOMAIN = ["Monday", "Tuesday", "Wednesday"]
SAMPLE_CONSTRAINTS = [
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


def _split_csv(text):
    return [item.strip() for item in text.split(",") if item.strip()]


def _read_csv(prompt, default=None):
    raw = input(prompt).strip()

    if not raw and default is not None:
        return default[:]

    return _split_csv(raw)


def _read_constraints(valid_names, default=None):
    print("\nRestricciones")
    print("Formato: A!=B, B!=C")
    raw = input("Ingrese restricciones separadas por coma: ").strip()

    if not raw and default is not None:
        return default[:]

    constraints = _split_csv(raw)
    valid_constraints = []

    for constraint in constraints:
        if "!=" not in constraint:
            print(f"  Se ignora '{constraint}': falta '!='")
            continue

        left, right = [part.strip() for part in constraint.split("!=", 1)]

        if left not in valid_names or right not in valid_names:
            print(f"  Se ignora '{constraint}': variable desconocida")
            continue

        if left == right:
            print(f"  Se ignora '{constraint}': una variable no puede restringirse a si misma")
            continue

        valid_constraints.append(f"{left}!={right}")

    return valid_constraints


def _read_problem():
    print("=== CSP por backtracking ===")
    use_sample = input("Usar ejemplo de cursos A-G? [s/N]: ").strip().lower()

    if use_sample == "s":
        return SAMPLE_VARIABLES[:], SAMPLE_DOMAIN[:], SAMPLE_CONSTRAINTS[:]

    variables = _read_csv("\nVariables separadas por coma (ej: A, B, C): ")
    while not variables:
        print("Debe ingresar al menos una variable.")
        variables = _read_csv("Variables separadas por coma: ")

    domain = _read_csv("Dominio separado por coma (ej: Monday, Tuesday): ")
    while not domain:
        print("Debe ingresar al menos un valor para el dominio.")
        domain = _read_csv("Dominio separado por coma: ")

    constraints = _read_constraints(set(variables))
    return variables, domain, constraints


def _read_solver():
    print("\nAlgoritmo")
    print("1. Backtracking simple")
    print("2. Backtracking con AC-3")
    choice = input("Seleccione una opcion [2]: ").strip()

    return "simple" if choice == "1" else "inference"


def _read_heuristic():
    print("\nHeuristica para seleccionar variable")
    print("1. Primera variable disponible")
    print("2. MRV")
    print("3. Degree")
    print("4. MRV + Degree")
    choice = input("Seleccione una opcion [1]: ").strip()

    heuristics = {
        "2": select_mrv,
        "3": select_degree,
        "4": select_mrv_degree,
    }

    return heuristics.get(choice)


def _print_problem(variables, domain, constraints):
    print("\nProblema ingresado")
    print(f"Variables: {', '.join(variables)}")
    print(f"Dominio: {', '.join(domain)}")
    print(f"Restricciones: {', '.join(constraints) if constraints else 'Ninguna'}")


def _print_domains(courses):
    print("\nDominios")
    for course in courses:
        print(f"  {course.name}: {course.domain}")


def _print_solution(courses):
    print("\nSolucion")
    for course in courses:
        print(f"  {course.name}: {course.value}")


def _solve_simple(courses, constraints):
    assigned = []
    solved = backtracking(courses[0], courses[1:], assigned, constraints)
    return solved


def _solve_with_inference(courses, constraints, heuristic):
    assigned = []

    if heuristic is None:
        return backtracking_with_inference(courses, assigned, constraints)

    return backtracking_with_inference(courses, assigned, constraints, select=heuristic)


def main():
    variables, domain, constraints = _read_problem()
    solver = _read_solver()
    heuristic = None

    if solver == "inference":
        heuristic = _read_heuristic()

    courses = initialize(variables, domain)
    _print_problem(variables, domain, constraints)

    ac3_courses = initialize(variables, domain)
    if ac3(ac3_courses, constraints):
        print("\nAC-3: consistente")
        _print_domains(ac3_courses)
    else:
        print("\nAC-3: inconsistente. Alguna variable se quedo sin dominio.")

    if solver == "simple":
        solved = _solve_simple(courses, constraints)
    else:
        solved = _solve_with_inference(courses, constraints, heuristic)

    if solved:
        _print_solution(courses)
    else:
        print("\nNo se encontro solucion.")


if __name__ == "__main__":
    main()
