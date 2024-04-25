import random
import utils
from copy import copy, deepcopy

class Interval:
    def __init__(self, interval: str):
        interval = interval[1:-1].split(',')
        self.start = int(interval[0])
        self.end = int(interval[1])

    def get_interval(self) -> tuple:
        return self.start, self.end
    
    def __str__(self) -> str:
        return str(self.start) + '-' + str(self.end)

class Materie:
    def __init__(self, name: str, capacitate: int):
        self.name = name
        self.capacitate = capacitate

    def get_capacitate(self) -> int:
        return self.capacitate
    
    def get_name(self) -> str:
        return self.name
    
    def __str__(self) -> str:
        return self.name + ' ' + str(self.capacitate)

class Profesor:
    def __init__(self, name: str, materii: list, constrangeri: list):
        self.name = name
        self.materii = set(materii)
        self.constrangeri = [x[1:] for x in constrangeri if x[0] == '!']
        
        new_constrangeri = []
        for constrangere in self.constrangeri:
            if '-' in constrangere:
                start, end = constrangere.split('-')
                start, end = int(start), int(end)
                new_constrangeri += [str(x) + '-' + str(x + 2) for x in range(start, end, 2)]
            else:
                new_constrangeri.append(constrangere)

        self.constrangeri = new_constrangeri

    def get_name(self) -> str:
        return self.name
    
    def in_materii(self, materie: str) -> bool:
        return materie in self.materii
    
    def in_constrangeri(self, constrangere: str) -> bool:
        return constrangere in self.constrangeri
    
    def __str__(self) -> str:
        return self.name + ' ' + str(self.materii)
    
class Sala:
    def __init__(self, name: str, capacitate: int, materii: list):
        self.name = name
        self.capacitate = capacitate
        self.materii = set(materii)

    def get_name(self) -> str:
        return self.name
    
    def get_capacitate(self) -> int:
        return self.capacitate
    
    def in_materii(self, materie: str) -> bool:
        return materie in self.materii
    
    def __str__(self) -> str:
        return self.name + ' ' + str(self.capacitate) + ' ' + str(self.materii)
    
class State:
    def __init__(self, orar: dict=None):
        if orar is None:
            self.orar = self.create_first_state()
        else:
            self.orar = orar

        self.compute_conflicts()

    def create_first_state(self):
        orar = {}

        for zi in zile:
            orar[zi] = {}
            for interval in intervale:
                orar[zi][interval.get_interval()] = {}
                for sala in sali:
                    orar[zi][interval.get_interval()][sala.get_name()] = None

        return orar
    
    def compute_conflicts(self):
        self.hard_conflicts = 0
        self.soft_conflicts = 0

        profesor_zi_interval = {}

        profesor_ore_predate = {}
        for profesor in profesori:
            profesor_ore_predate[profesor.get_name()] = 0
            profesor_zi_interval[profesor.get_name()] = {}

            for zi in zile:
                profesor_zi_interval[profesor.get_name()][zi] = set()

        materie_acoperire = {}
        for materie in materii:
            materie_acoperire[materie.get_name()] = 0

        capacitate_materie = {}
        for materie in materii:
            capacitate_materie[materie.get_name()] = materie.get_capacitate()

        string_to_sala = {}
        for sala in sali:
            string_to_sala[sala.get_name()] = sala

        string_to_profesor = {}
        for profesor in profesori:
            string_to_profesor[profesor.get_name()] = profesor

        for zi in self.orar:
            for interval in self.orar[zi]:
                for sala in self.orar[zi][interval]:
                    if self.orar[zi][interval][sala] is None:
                        continue

                    profesor, materie = self.orar[zi][interval][sala]

                    # Hard constraint 2
                    if interval in profesor_zi_interval[profesor][zi]:
                        self.hard_conflicts += 1
                    else:
                        profesor_zi_interval[profesor][zi].add(interval)

                    # Hard constraint 3
                    profesor_ore_predate[profesor] += 1

                    if profesor_ore_predate[profesor] == 8:
                        self.hard_conflicts += 1

                    # Hard constraint 5
                    materie_acoperire[materie] += string_to_sala[sala].get_capacitate()

                    # Hard constraint 6
                    if not string_to_profesor[profesor].in_materii(materie):
                        self.hard_conflicts += 1

                    # Hard constraint 7
                    if not string_to_sala[sala].in_materii(materie):
                        self.hard_conflicts += 1

                    # Soft constraint interval
                    string_interval = str(interval[0]) + '-' + str(interval[1])
                    if string_to_profesor[profesor].in_constrangeri(string_interval):
                        self.soft_conflicts += 1

                    # Soft constraint zi
                    if string_to_profesor[profesor].in_constrangeri(f'{zi}'):
                        self.soft_conflicts += 1

        # Hard constraint 5
        for materie in materie_acoperire:
            if materie_acoperire[materie] < capacitate_materie[materie]:
                self.hard_conflicts += 1

        self.materie_acoperire = materie_acoperire
        self.profesor_ore_predate = profesor_ore_predate
        self.profesor_zi_interval = profesor_zi_interval
        
    def get_conflicts(self) -> int:
        return (self.hard_conflicts, self.soft_conflicts)
    
    def is_final(self) -> bool:
        return self.hard_conflicts == 0 and self.soft_conflicts == 0
    
    def apply_move(self, value: tuple, pos: tuple):
        zi, interval, sala = pos

        new_orar = deepcopy(self.orar)
        new_orar[zi][interval][sala] = value

        return State(new_orar)
    
    def get_next_states(self):
        """
        Generator function that yields all possible states that can be reached
        from the current state
        """
        curr_materii = []
        for materie in materii:
            if self.materie_acoperire[materie.get_name()] < materie.get_capacitate():
                curr_materii.append(materie)

        curr_profesori = []
        for profesor in profesori:
            if self.profesor_ore_predate[profesor.get_name()] < 7:
                curr_profesori.append(profesor)

        for materie in curr_materii:
            for profesor in curr_profesori:
                zile_preferate = []
                for zi in zile:
                    if zi in profesor.constrangeri:
                        zile_preferate.append(zi)
                    else:
                        zile_preferate.insert(0, zi)

                intervale_preferate = []
                for interval in intervale:
                    if str(interval) in profesor.constrangeri:
                        intervale_preferate.append(interval)
                    else:
                        intervale_preferate.insert(0, interval)

                for zi in zile_preferate:
                    for interval in intervale_preferate:
                        if interval.get_interval() in self.profesor_zi_interval[profesor.get_name()][zi]:
                            continue

                        for sala in sali:
                            if self.orar[zi][interval.get_interval()][sala.get_name()] is not None:
                                continue

                            if not sala.in_materii(materie.get_name()):
                                continue

                            if not profesor.in_materii(materie.get_name()):
                                continue

                            yield self.apply_move((profesor.get_name(), materie.get_name()),\
                                                  (zi, interval.get_interval(), sala.get_name()))
                                
    def get_orar(self) -> dict:
        return self.orar
    
    def clone(self):
        return State(deepcopy(self.orar))
    
def first_choice_hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial.clone()
    
    while iters < max_iters:
        iters += 1
        minim = 3 * state.get_conflicts()[0] + state.get_conflicts()[1]

        if state.is_final():
            break
        
        not_found = True

        for neigh in list(state.get_next_states()):
            confls = neigh.get_conflicts()
            sum = 3 * confls[0] + confls[1]
            states += 1

            if sum <= minim:
            # if confls[1] < minim[1]:
                minim = sum
                state = neigh
                not_found = False
                # break

        if not_found:
            break
        
    return state.is_final(), iters, states, state

def stochastic_hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial
    
    while iters < max_iters:
        iters += 1
        state_conflicts = state.get_conflicts()
        state_conflicts = state_conflicts[0] + state_conflicts[1]

        lista = [x for x in list(state.get_next_states())\
                  if state_conflicts >= x.get_conflicts()[0] + x.get_conflicts()[1]]

        if len(lista) == 0 or state.is_final():
            break

        state = random.choice(lista)

    return state.is_final(), iters, states, state

def random_restart_hill_climbing(
    initial: State,
    max_restarts: int = 100, 
    run_max_iters: int = 100, 
):
    
    total_iters, total_states = 0, 0
    
    state = initial
    restarts = 0

    while restarts < max_restarts:
        print(restarts)
        is_final, iters, states, state = first_choice_hill_climbing(state, run_max_iters)

        total_iters += iters
        total_states += states

        if is_final:
            break
        else:
            state = State()
            restarts += 1
    
    return is_final, total_iters, total_states, state

def hca_main(timetable_specs: dict, input_path: str):
    global materii, sali, profesori, zile, intervale

    materii = []
    for materie in timetable_specs[utils.MATERII]:
        materii.append(Materie(materie, timetable_specs[utils.MATERII][materie]))
    # sort by capacity in descending order (materii is a list)
    materii.sort(key=lambda x: x.get_capacitate(), reverse=True)

    sali = []
    for sala in timetable_specs[utils.SALI]:
        sali.append(Sala(sala,\
                            timetable_specs[utils.SALI][sala][utils.CAPACITATE],\
                            timetable_specs[utils.SALI][sala][utils.MATERII]))
    # sort by least number of materii in descending order and after that by capacity in descending order
    sali.sort(key=lambda x: (len(x.materii), x.get_capacitate()), reverse=True)

    profesori = []
    for profesor in timetable_specs[utils.PROFESORI]:
        profesori.append(Profesor(profesor,\
                        timetable_specs[utils.PROFESORI][profesor][utils.MATERII],\
                        timetable_specs[utils.PROFESORI][profesor][utils.CONSTRANGERI]))
    # sort in ascending order by number of materii
    profesori.sort(key=lambda x: len(x.materii))
        
    intervale = []
    for interval in timetable_specs[utils.INTERVALE]:
        intervale.append(Interval(interval))
        
    zile = timetable_specs[utils.ZILE]
        
    _, _, _, state = first_choice_hill_climbing(State())
    timetable = utils.pretty_print_timetable(state.get_orar(), input_path)
    print(state.hard_conflicts, state.soft_conflicts)
    print(timetable)

    output_path = input_path.replace('inputs', 'my_outputs').replace('.yaml', '.txt')
    with open(output_path, 'w') as f:
        f.write(timetable)
