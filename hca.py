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

    def get_name(self) -> str:
        return self.name
    
    def in_materii(self, materie: str) -> bool:
        return materie in self.materii
    
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
                    if materie not in materie_acoperire:
                        materie_acoperire[materie] = sali[sala].get_capacitate()
                    else:
                        materie_acoperire[materie] += sali[sala].get_capacitate()

                    # Hard constraint 6
                    if not profesori[profesor].in_materii(materie):
                        self.hard_conflicts += 1

                    # Hard constraint 7
                    if not sali[sala].in_materii(materie):
                        self.hard_conflicts += 1

        # Hard constraint 5
        for materie in materie_acoperire:
            if materie_acoperire[materie] < materii[materie].get_capacitate():
                self.hard_conflicts += 1
        
    def get_conflicts(self) -> int:
        return (self.hard_conflicts, self.soft_conflicts)
    
    def is_final(self) -> bool:
        return self.hard_conflicts == 0 and self.soft_conflicts == 0
    
    def apply_move(self, old_pos: tuple, value: tuple, new_pos: tuple):
        pass
    
    def get_next_states(self):
        pass
                                
    def get_orar(self) -> dict:
        return self.orar
    
    def clone(self):
        return State(deepcopy(self.orar))

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
        
    state = State()

    print(utils.pretty_print_timetable(state.get_orar(), input_path))
