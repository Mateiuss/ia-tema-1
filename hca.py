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
        self.constrangeri = set(constrangeri)
        self.ore_predate = 0

    def get_name(self) -> str:
        return self.name
    
    def in_materii(self, materie: str) -> bool:
        return materie in self.materii
    
    def in_constrangeri(self, materie: str) -> bool:
        return materie in self.constrangeri
    
    def get_ore_predate(self) -> int:
        return self.ore_predate
    
    def inc_ore_predate(self):
        self.ore_predate += 1
    
    def __str__(self) -> str:
        return self.name + ' ' + str(self.materii) + ' ' + str(self.constrangeri)
    
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
    def __init__(self, orar: dict=None, conflicts: int=0):
        pass

    def create_initial_state(self):
        pass
    
    def compute_conflicts(self):
        pass
        
    def get_conflicts(self) -> int:
        return self.conflicts
    
    def is_final(self) -> bool:
        return self.conflicts == 0
    
    def apply_move(self, old_pos: tuple, value: tuple, new_pos: tuple):
        pass
    
    def get_next_states(self):
        pass
                                
    def get_orar(self) -> dict:
        return self.orar
    
    def clone(self):
        return State(copy(self.orar), self.conflicts)


def hca_main(timetable_specs: dict, input_file: str):
    global materii, profesori, sali, intervale, zile

    zile = timetable_specs[utils.ZILE]

    materii = []
    for materie, capacitate in timetable_specs[utils.MATERII].items():
        materii.append(Materie(materie, capacitate))

    profesori = []
    for profesor, val in timetable_specs[utils.PROFESORI].items():
        profesori.append(Profesor(profesor, val[utils.MATERII], val[utils.CONSTRANGERI]))

    sali = []
    for sala, val in timetable_specs[utils.SALI].items():
        sali.append(Sala(sala, val[utils.CAPACITATE], val[utils.MATERII]))

    intervale = []
    for interval in timetable_specs[utils.INTERVALE]:
        intervale.append(Interval(interval))


def hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial.clone()
    minim = state.get_conflicts()
    
    while iters < max_iters:
        iters += 1
        minim = state.get_conflicts()

        if state.is_final():
            break
        
        not_found = True

        for neigh in list(state.get_next_states()):
            confls = neigh.get_conflicts()
            states += 1

            if minim > confls:
                minim = confls
                state = neigh
                not_found = False

        if not_found:
            break
        
    return state.is_final(), iters, states, state
