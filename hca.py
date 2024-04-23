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
        return '(' + str(self.start) + ', ' + str(self.end) + ')'

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
            self.orar = self.create_empty_orar()
        else:
            self.orar = orar

        self.compute_conflicts()

    def create_empty_orar(self):
        orar = {}

        for zi in zile:
            orar[zi] = {}
            for _, interval_obj in intervale.items():
                orar[zi][interval_obj.get_interval()] = {}
                for _, sala_obj in sali.items():
                    orar[zi][interval_obj.get_interval()][sala_obj.get_name()] = None

        return orar
    
    def compute_conflicts(self):
        self.hard_conflicts = 0
        self.soft_conflicts = 0

        profesor_zi_interval = {}
        profesor_ore_predate = {}

        materie_acoperire = {}
        for materie in materii:
            materie_acoperire[materie] = 0

        for zi in self.orar:
            for interval in self.orar[zi]:
                for sala in self.orar[zi][interval]:
                    if self.orar[zi][interval][sala] is None:
                        continue

                    profesor, materie = self.orar[zi][interval][sala]

                    # Hard constraint 2
                    if profesor not in profesor_zi_interval:
                        profesor_zi_interval[profesor] = {}

                    if zi not in profesor_zi_interval[profesor]:
                        profesor_zi_interval[profesor][zi] = set()

                    if interval in profesor_zi_interval[profesor][zi]:
                        self.hard_conflicts += 1
                    else:
                        profesor_zi_interval[profesor][zi].add(interval)

                    # Hard constraint 3
                    if profesor not in profesor_ore_predate:
                        profesor_ore_predate[profesor] = 1
                    else:
                        profesor_ore_predate[profesor] += 1

                    if profesor_ore_predate[profesor] == 8:
                        self.hard_conflicts += 1

                    # Hard constraint 5
                    materie_acoperire[materie] += sali[sala].get_capacitate()

                    # Hard constraint 6
                    if not profesori[profesor].in_materii(materie):
                        self.hard_conflicts += 1

                    # Hard constraint 7
                    if not sali[sala].in_materii(materie):
                        self.hard_conflicts += 1

                    # Soft constraint interval
                    string_interval = str(interval[0]) + '-' + str(interval[1])
                    if profesori[profesor].in_constrangeri(string_interval):
                        self.soft_conflicts += 1

                    # Soft constraint zi
                    if profesori[profesor].in_constrangeri(f'{zi}'):
                        self.soft_conflicts += 1

        # Hard constraint 5
        for materie in materie_acoperire:
            if materie_acoperire[materie] < materii[materie].get_capacitate():
                self.hard_conflicts += 1
        
    def get_conflicts(self) -> int:
        return (self.hard_conflicts, self.soft_conflicts)
    
    def is_final(self) -> bool:
        return self.hard_conflicts == 0 and self.soft_conflicts == 0
    
    def apply_move(self, old_pos: tuple, value: tuple, new_pos: tuple):
        old_zi, old_interval, old_sala = old_pos
        new_zi, new_interval, new_sala = new_pos

        new_orar = deepcopy(self.orar)
        new_orar[old_zi][old_interval][old_sala] = None
        new_orar[new_zi][new_interval][new_sala] = value

        return State(new_orar)
    
    def get_next_states(self):
        """
        Generator function that yields all possible states that can be reached
        from the current state
        """

        for zi in zile:
            for interval in intervale:
                interval = intervale[interval].get_interval()

                for sala in sali:
                    if self.orar[zi][interval][sala] is not None:
                        continue

                    for profesor in profesori:
                        for materie in profesori[profesor].materii:
                            if self.orar[zi][interval][sala] is not None:
                                continue

                            if not sali[sala].in_materii(materie):
                                continue

                            if not profesori[profesor].in_materii(materie):
                                continue

                            yield self.apply_move((zi, interval, sala), (profesor, materie), (zi, interval, sala))
                                
    def get_orar(self) -> dict:
        return self.orar
    
    def clone(self):
        return State(deepcopy(self.orar))
    
def stochastic_hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial.clone()
    
    while iters < max_iters:
        iters += 1
        h_conflicts, s_conflicts = state.get_conflicts()
        conflicts = h_conflicts + s_conflicts

        lista = [x for x in list(state.get_next_states()) if conflicts >= x.get_conflicts()[0] + x.get_conflicts()[1]]

        if len(lista) == 0 or state.is_final():
            break

        state = random.choice(lista)

    return state.is_final(), iters, states, state

def hca_main(timetable_specs: dict, input_path: str):
    global materii, sali, profesori, zile, intervale

    materii = {}
    for materie in timetable_specs[utils.MATERII]:
        materii[materie] = Materie(materie, timetable_specs[utils.MATERII][materie])

    sali = {}
    for sala in timetable_specs[utils.SALI]:
        sali[sala] = Sala(sala,\
                            timetable_specs[utils.SALI][sala][utils.CAPACITATE],\
                            timetable_specs[utils.SALI][sala][utils.MATERII])

    profesori = {}
    for profesor in timetable_specs[utils.PROFESORI]:
        profesori[profesor] = Profesor(profesor,\
                        timetable_specs[utils.PROFESORI][profesor][utils.MATERII],\
                        timetable_specs[utils.PROFESORI][profesor][utils.CONSTRANGERI])
        
    intervale = {}
    for interval in timetable_specs[utils.INTERVALE]:
        intervale[interval] = Interval(interval)
        
    zile = timetable_specs[utils.ZILE]
        
    _, _, _, state = stochastic_hill_climbing(State(), 1000)
    timetable = utils.pretty_print_timetable(state.get_orar(), input_path)
    print(state.hard_conflicts, state.soft_conflicts)
    print(timetable)

    output_path = input_path.replace('inputs', 'my_outputs').replace('.yaml', '.txt')
    with open(output_path, 'w') as f:
        f.write(timetable)
