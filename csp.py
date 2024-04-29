from copy import deepcopy, copy
from structures import Materie, Profesor, Sala, Interval, State
import utils

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

def PCSP(vars, domains, constraints, acceptable_cost, solution, cost):
    global best_solution
    global best_cost
    global iterations
    if not vars:
        print("New best: " + str(cost) + " - " + str(solution))
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
        val = domains[var].pop(0)
        iterations += 1
        if val is not None:
            profesor, materie = val
        _, _, sala = var

        if val is not None:
            profesor_to_obj[profesor].acoperire += 1
            materie_to_obj[materie].acoperire += sala_to_obj[sala].capacitate

        new_solution = copy(solution)
        new_solution[var] = val

        new_constraints = fixed_constraints(new_solution, constraints)

        new_cost = 0
        for constraint in new_constraints:
            if check_constraint(new_solution, constraint) == False:
                new_cost += 1

        if new_cost < best_cost and new_cost <= acceptable_cost:
            if PCSP(vars[1:], domains, constraints, acceptable_cost, new_solution, new_cost) == True:
                return True
            
        if val is not None:
            profesor_to_obj[profesor].acoperire -= 1
            materie_to_obj[materie].acoperire -= sala_to_obj[sala].capacitate

        return PCSP(vars, deepcopy(domains), constraints, acceptable_cost, solution, cost)
    
def create_vars(zile:list, intervale:list[Interval], sali:list[Sala]) -> list[tuple]:
    vars = []
    for zi in zile:
        for interval in intervale:
            for sala in sali:
                vars.append((zi, interval.get_interval(), sala.get_name()))

    return vars

def create_domains(vars:list[tuple], materii:list[Materie], profesori:list[Profesor]) -> dict:
    domains = {}
    for var in vars:
        _, _, sala = var
        domains[var] = []
        for materie in materii:
            for profesor in profesori:
                if materie.name in profesor.materii and materie.name in sala_to_obj[sala].materii:
                    domains[var].append((profesor.get_name(), materie.get_name()))

    return domains

def create_constraints(vars:list[tuple], zile:list, intervale:list[Interval], sali:list[Sala]) -> list[tuple]:
    constraints = []
    
    """
    • într-un interval orar, un profesor poate tine o singură materie, într-o singură
    sală.

    • un profesor poate tine ore în maxim 7 intervale pe săptămână.

    • toti studentii de la o materie trebuie să aibă alocate ore la acea materie.
    Concret, suma capacitătilor sălilor peste toate intervalele în care se tin ore la
    materia respectivă trebuie să fie mai mare sau egală decât numărul de studenti
    la materia respectivă
    """

    for var in vars:
        constraints.append(([var], lambda x: True))

    return constraints

def csp_main(timetable_specs: dict, input_path: str):
    global interval_to_obj, materie_to_obj, profesor_to_obj, sala_to_obj

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

    vars = create_vars(zile, intervale, sali)
    domains = create_domains(vars, materii, profesori)
    constraints = create_constraints(vars, zile, intervale, sali)

    global best_solution
    global best_cost
    global iterations
    best_solution = {}
    best_cost = 10000000
    iterations = 0
    acceptable_cost = 0

    PCSP(vars, copy(domains), constraints, acceptable_cost, {}, 0)

    for var, val in best_solution.items():
        zi, interval, sala = var
        if val is not None:
            profesor, materie = val
            orar[zi][interval][sala] = (profesor, materie)

    state = State(orar)
    print(state.hard_conflicts, state.soft_conflicts)

    timetable = utils.pretty_print_timetable(orar, input_path)
    print(timetable)