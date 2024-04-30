from structures import Materie, Profesor, Sala, Interval, State
import utils
import random

def materii_acoperite():
    for materie in materii:
        if not materie.is_full():
            return False
        
    return True

def PCSP(vars, var_index, domains, acceptable_cost, solution, cost, max_iterations = None):
    global best_solution
    global best_cost
    global iterations

    if max_iterations is not None and iterations >= max_iterations:
        return False

    if var_index == len(vars):
        if not materii_acoperite():
            return False

        best_solution = solution
        best_cost = cost
        if acceptable_cost >= cost:
            return True
    elif not domains[vars[0]] or cost >= best_cost:
        return False
    else:
        var = vars[var_index]

        for val in domains[var]:
            iterations += 1
            
            zi, interval, sala = var
            delta_cost = 0
            
            if val is not None:
                profesor, materie = val
                
                if materie_to_obj[materie].is_full():
                    continue

                if profesor_to_obj[profesor].acoperire == 7:
                    continue

                if interval in profesor_zi_interval[profesor][zi]:
                    continue

                if zi in profesor_to_obj[profesor].constrangeri:
                    delta_cost += 1

                if str(Interval(str(interval))) in profesor_to_obj[profesor].constrangeri:
                    delta_cost += 1

                if cost + delta_cost > acceptable_cost:
                    continue

                profesor_to_obj[profesor].acoperire += 1
                materie_to_obj[materie].acoperire += sala_to_obj[sala].capacitate
                profesor_zi_interval[profesor][zi].add(interval)

            solution[var] = val
            new_cost = cost + delta_cost

            if new_cost < best_cost and new_cost <= acceptable_cost:
                if PCSP(vars, var_index + 1, domains, acceptable_cost, solution, new_cost, max_iterations):
                    return True
                
            solution.pop(var)
                
            if val is not None:
                profesor_to_obj[profesor].acoperire -= 1
                materie_to_obj[materie].acoperire -= sala_to_obj[sala].capacitate
                profesor_zi_interval[profesor][zi].remove(interval)

        return False
    
def create_vars() -> list[tuple]:
    vars = []
    for zi in zile:
        for interval in intervale:
            for sala in sali:
                vars.append((zi, interval.get_interval(), sala.get_name()))

    return vars

def create_domains(vars:list[tuple], with_random:bool=False) -> dict:
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

        if with_random:
            random.shuffle(domains[var])
        domains[var].append(None)


    return domains

def run_random_restart(acceptable_cost, max_iterations, vars):
    global iterations
    global total_iterations

    for _ in range(1, max_iterations):
        domains = create_domains(vars, True)
        iterations = 0
        random.shuffle(vars)
        PCSP(vars, 0, domains, acceptable_cost, {}, 0, max_iterations=70000)
        total_iterations += iterations

        if best_cost <= acceptable_cost:
            break

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

    global profesor_zi_interval
    profesor_zi_interval = {}
    for profesor in profesori:
        profesor_zi_interval[profesor.get_name()] = {}
        for zi in zile:
            profesor_zi_interval[profesor.get_name()][zi] = set()

    orar = {}
    for zi in zile:
        orar[zi] = {}
        for interval in intervale:
            orar[zi][interval.get_interval()] = {}
            for sala in sali:
                orar[zi][interval.get_interval()][sala.get_name()] = None

    global best_solution
    global best_cost
    global iterations
    global total_iterations
    best_solution = {}
    best_cost = 100000
    iterations = 0
    total_iterations = 0

    vars = create_vars()

    if input_path == 'inputs/orar_constrans_incalcat.yaml':
        acceptable_cost = 8

        while best_cost > acceptable_cost:
            print(f'Trying for acceptable cost: {acceptable_cost}')
            run_random_restart(acceptable_cost, 500, vars)
            acceptable_cost += 1
    else:
        acceptable_cost = 0

        vars = create_vars()
        domains = create_domains(vars)
        PCSP(vars, 0, domains, acceptable_cost, {}, 0)
        total_iterations = iterations

    for var, val in best_solution.items():
        zi, interval, sala = var
        if val is not None:
            profesor, materie = val
            orar[zi][interval][sala] = (profesor, materie)

    state = State(orar)
    print(f'Hard constraints: {state.hard_conflicts}\nSoft constraints: {state.soft_conflicts}\n')
    print(f'Total iterations: {total_iterations}')

    timetable = utils.pretty_print_timetable(orar, input_path)
    print(timetable)