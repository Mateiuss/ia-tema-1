from structures import Materie, Profesor, Sala, Interval, State
import utils
import os
import random

def materii_acoperite():
    for materie in materii:
        if not materie.is_full():
            return False
        
    return True

def profesor_acelasi_interval(zi, interval, profesor, solution):
    for var, val in solution.items():
        if val is None:
            continue

        zi_, interval_, _ = var
        profesor_, _ = val

        if zi_ == zi and interval_ == interval and profesor_ == profesor:
            return True
        
    return False

def PCSP(vars, domains, acceptable_cost, solution, cost):
    global best_solution
    global best_cost
    global iterations
    if best_cost == acceptable_cost:
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
            if best_cost == acceptable_cost:
                return True
            
            zi, interval, sala = var
            delta_cost = 0
            
            if val is not None:
                profesor, materie = val
                
                if materie_to_obj[materie].is_full():
                    continue

                if profesor_to_obj[profesor].acoperire >= 7:
                    continue

                if profesor_acelasi_interval(zi, interval, profesor, solution):
                    continue

                profesor_to_obj[profesor].acoperire += 1
                materie_to_obj[materie].acoperire += sala_to_obj[sala].capacitate

                if zi in profesor_to_obj[profesor].constrangeri:
                    delta_cost += 1

                if str(Interval(str(interval))) in profesor_to_obj[profesor].constrangeri:
                    delta_cost += 1

            solution[var] = val
            new_cost = cost + delta_cost

            if new_cost < best_cost and new_cost <= acceptable_cost:
                if PCSP(vars[1:], domains, acceptable_cost, solution, new_cost):
                    return True
                
            solution.pop(var)
                
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
        # random.shuffle(domains[var])

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
    # sali.sort(key=lambda x: (-len(x.materii), x.get_capacitate()), reverse=True)
        
    profesori = []
    profesor_to_obj = {}
    for profesor in timetable_specs[utils.PROFESORI]:
        profesori.append(Profesor(profesor,\
                        timetable_specs[utils.PROFESORI][profesor][utils.MATERII],\
                        timetable_specs[utils.PROFESORI][profesor][utils.CONSTRANGERI]))
        profesor_to_obj[profesor] = profesori[-1]
    # profesori.sort(key=lambda x: len(x.materii))
        
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

    global best_solution
    global best_cost
    global iterations
    best_solution = {}
    best_cost = 100000
    iterations = 0
    acceptable_cost = 0

    PCSP(vars, domains, acceptable_cost, {}, 0)

    for var, val in best_solution.items():
        zi, interval, sala = var
        if val is not None:
            profesor, materie = val
            orar[zi][interval][sala] = (profesor, materie)

    state = State(orar)
    print(f'Hard constraints: {state.hard_conflicts}\nSoft constraints: {state.soft_conflicts}\n')

    timetable = utils.pretty_print_timetable(orar, input_path)
    print(timetable)

    if not os.path.exists('my_outputs'):
        os.makedirs('my_outputs')

    output_path = input_path.replace('inputs', 'my_outputs').replace('.yaml', '.txt')
    with open(output_path, 'w') as f:
        f.write(timetable)