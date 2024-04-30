from copy import deepcopy, copy
from structures import Materie, Profesor, Sala, Interval, State
import utils
import os

def get_constraints(var, constraints):
    return [x for x in constraints if var in x[0]]

def fixed_constraints(solution, constraints):
    ans = []

    # print(f'Solution: {solution}')
    for constraint in constraints:
        ok = True

        for var in constraint[0]:
            # print(f'Var: {var}')
            if var not in solution:
                ok = False
                break

        if ok == True:
            ans.append(constraint)

    return ans

def check_constraint(solution, constraint):
    return constraint[1](*[y for x, y in solution.items() if x in constraint[0]])

def materii_acoperite():
    for materie in materii:
        if not materie.is_full():
            return False
        
    return True
        
def profesori_acoperiti():
    for profesor in profesori:
        if profesor.acoperire > 7:
            return False

    return True

def profesor_acelasi_interval(*argv):
    constrangeri = 0

    profesori_folositi = set()
    for arg in argv:
        if arg is None:
            continue

        profesor, _ = arg
        if profesor in profesori_folositi:
            constrangeri += 1
        else:
            profesori_folositi.add(profesor)

    return constrangeri

def preferinte_profesori(zi, interval, val):
    if val is None:
        return 0

    profesor, _ = val
    constrangeri = 0

    if zi in profesor_to_obj[profesor].constrangeri:
        constrangeri += 1

    if str(interval) in profesor_to_obj[profesor].constrangeri:
        constrangeri += 1

    return constrangeri

def create_constraints(vars:list[tuple]) -> list[tuple]:
    constraints = []

    # Constrangeri hard
    for zi in zile:
        for interval in intervale:
            vars_for_constraint = [(zi, interval.get_interval(), sala.get_name()) for sala in sali]
            constraints.append((vars_for_constraint, lambda *x: profesor_acelasi_interval(*x)))

    # Constrangeri soft
    for zi in zile:
        for interval in intervale:
            for sala in sali:
                tmp_lambda = lambda x, y: lambda z: preferinte_profesori(x, y, z)
                lambda_func = tmp_lambda(zi, interval)
                constraints.append(([(zi, interval.get_interval(), sala.get_name())], lambda_func))

    return constraints

def PCSP(vars, domains, constraints, acceptable_cost, solution, cost):
    global best_solution
    global best_cost
    global iterations
    if best_cost == 0:
        return True
    if not vars:
        # print("New best: " + str(cost) + " - " + str(solution))
        if not materii_acoperite():
            return False

        best_solution = solution
        best_cost = cost
        if acceptable_cost >= cost:
            return True
    elif not domains[vars[0]]:
        return False
    elif cost == best_cost:
        return False
    else:
        var = vars[0]

        for val in domains[var]:
            if best_cost == 0:
                return True
            
            if val is not None:
                profesor, materie = val
                
                if materie_to_obj[materie].is_full():
                    continue

                if profesor_to_obj[profesor].acoperire >= 7:
                    continue
            _, _, sala = var

            if val is not None:
                profesor_to_obj[profesor].acoperire += 1
                materie_to_obj[materie].acoperire += sala_to_obj[sala].capacitate

            if not profesori_acoperiti():
                if val is not None:
                    profesor_to_obj[profesor].acoperire -= 1
                    materie_to_obj[materie].acoperire -= sala_to_obj[sala].capacitate
                continue

            new_solution = solution
            new_solution[var] = val

            new_constraints = fixed_constraints(new_solution, constraints)

            new_cost = 0
            for constraint in new_constraints:
                new_cost += check_constraint(new_solution, constraint)

            if new_cost < best_cost and new_cost <= acceptable_cost:
                if PCSP(vars[1:], domains, constraints, acceptable_cost, new_solution, new_cost):
                    return True
                
            new_solution.pop(var)
                
            if val is not None:
                profesor_to_obj[profesor].acoperire -= 1
                materie_to_obj[materie].acoperire -= sala_to_obj[sala].capacitate
    
def create_vars() -> list[tuple]:
    vars = []
    for zi in zile:
        for interval in intervale:
            for sala in sali:
                vars.append((zi, interval.get_interval(), sala.get_name()))

    return vars

def create_domains(vars:list[tuple]) -> dict:
    domains = {}
    for var in vars:
        _, _, sala = var
        domains[var] = []
        for materie in materii:
            if materie.name not in sala_to_obj[sala].materii:
                continue

            for profesor in profesori:
                if materie.name in profesor.materii:
                    domains[var].append((profesor.get_name(), materie.get_name()))

        domains[var].append(None)

    return domains

def csp_main(timetable_specs: dict, input_path: str):
    global interval_to_obj, materie_to_obj, profesor_to_obj, sala_to_obj
    global sali, materii, profesori, intervale, zile

    materii = []
    materie_to_obj = {}
    for materie in timetable_specs[utils.MATERII]:
        materii.append(Materie(materie, timetable_specs[utils.MATERII][materie]))
        materie_to_obj[materie] = materii[-1]

    sali = []
    sala_to_obj = {}
    for sala in timetable_specs[utils.SALI]:
        sali.append(Sala(sala,\
                            timetable_specs[utils.SALI][sala][utils.CAPACITATE],\
                            timetable_specs[utils.SALI][sala][utils.MATERII]))
        sala_to_obj[sala] = sali[-1]
        
    profesori = []
    profesor_to_obj = {}
    for profesor in timetable_specs[utils.PROFESORI]:
        profesori.append(Profesor(profesor,\
                        timetable_specs[utils.PROFESORI][profesor][utils.MATERII],\
                        timetable_specs[utils.PROFESORI][profesor][utils.CONSTRANGERI]))
        profesor_to_obj[profesor] = profesori[-1]
        
    intervale = []
    interval_to_obj = {}
    for interval in timetable_specs[utils.INTERVALE]:
        intervale.append(Interval(interval))
        interval_to_obj[interval] = intervale[-1]

    zile = timetable_specs[utils.ZILE]

    State.materii = materii
    State.sali = sali
    State.profesori = profesori
    State.intervale = intervale
    State.zile = zile

    orar = {}
    for zi in zile:
        orar[zi] = {}
        for interval in intervale:
            orar[zi][interval.get_interval()] = {}
            for sala in sali:
                orar[zi][interval.get_interval()][sala.get_name()] = None

    vars = create_vars()
    domains = create_domains(vars)
    constraints = create_constraints(vars)

    global best_solution
    global best_cost
    global iterations
    best_solution = {}
    best_cost = 100000
    iterations = 0
    acceptable_cost = 0

    PCSP(vars, domains, constraints, acceptable_cost, {}, 0)

    for var, val in best_solution.items():
        zi, interval, sala = var
        if val is not None:
            profesor, materie = val
            orar[zi][interval][sala] = (profesor, materie)

    state = State(orar)
    print(state.hard_conflicts, state.soft_conflicts)
    print(best_cost, iterations)

    timetable = utils.pretty_print_timetable(orar, input_path)
    print(timetable)

    if not os.path.exists('my_outputs'):
        os.makedirs('my_outputs')

    output_path = input_path.replace('inputs', 'my_outputs').replace('.yaml', '.txt')
    with open(output_path, 'w') as f:
        f.write(timetable)