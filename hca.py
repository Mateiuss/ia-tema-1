import utils
from copy import copy

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
        if orar is None:
            self.orar = self.create_initial_state()
        else:
            self.orar = orar

        self.conflicts = conflicts
        self.compute_conflicts()

    def create_initial_state(self):
        profesori.sort(key=lambda x: len(x.materii))
        sali.sort(key=lambda x: (x.capacitate, -len(x.materii)), reverse=True)
        materii.sort(key=lambda x: x.capacitate, reverse=True)
        
        orar = {}
        for zi in zile:
            orar[zi] = {}
            
            for interval in intervale:
                orar[zi][interval.get_interval()] = {}
                
                for sala in sali:
                    orar[zi][interval.get_interval()][sala.get_name()] = None

        for materie in materii:
            capacitate_curenta = 0
            materie_out = False

            for profesor in profesori:
                if not profesor.in_materii(materie.get_name()):
                    continue

                profesor_out = False

                for zi in zile:
                    for interval in intervale:
                        for sala in sali:
                            if not sala.in_materii(materie.get_name()):
                                continue

                            if orar[zi][interval.get_interval()][sala.get_name()] is not None:
                                continue

                            if profesor.get_ore_predate() == 7:
                                profesor_out = True
                                break

                            if capacitate_curenta >= materie.get_capacitate():
                                materie_out = True
                                break

                            orar[zi][interval.get_interval()][sala.get_name()] = (profesor.get_name(), materie)
                            profesor.inc_ore_predate()
                            capacitate_curenta += sala.get_capacitate()

                            break
                        if profesor_out or materie_out:
                            break

                    if profesor_out or materie_out:
                        break

        # print(utils.pretty_print_timetable(orar, 'inputs/dummy.yaml'))

        return orar
    
    def compute_conflicts(self):
        self.conflicts = 0

        for zi in zile:
            for interval in intervale:
                for sala in sali:
                    if self.orar[zi][interval.get_interval()][sala.get_name()] is None:
                        continue

                    prof, _ = self.orar[zi][interval.get_interval()][sala.get_name()]
                    prof = [profesor for profesor in profesori if profesor.get_name() == prof][0]

                    for constrangere in prof.constrangeri:
                        if constrangere in zile:
                            if constrangere != zi:
                                self.conflicts += 1
                        elif constrangere[0] == '!':
                            if constrangere[1:] == zi:
                                self.conflicts += 1
                            elif constrangere[1:] == str(interval.start) + '-' + str(interval.end):
                                self.conflicts += 1
                        else:
                            if constrangere != str(interval.start) + '-' + str(interval.end):
                                self.conflicts += 1
        
    def get_conflicts(self) -> int:
        return self.conflicts
    
    def is_final(self) -> bool:
        return self.conflicts == 0
    
    def apply_move(self, old_pos: tuple, value: tuple, new_pos: tuple):
        prof, materie = value
        old_zi, old_interval, old_sala = old_pos
        new_zi, new_interval, new_sala = new_pos

        new_orar = self.orar.copy()
        new_orar[new_zi] = new_orar[new_zi].copy()
        new_orar[new_zi][new_interval] = new_orar[new_zi][new_interval].copy()
        new_orar[new_zi][new_interval][new_sala] = (prof, materie)

        new_orar[old_zi] = new_orar[old_zi].copy()
        new_orar[old_zi][old_interval] = new_orar[old_zi][old_interval].copy()
        new_orar[old_zi][old_interval][old_sala] = None

        return State(new_orar)
    
    def get_next_states(self):
        for zi in zile:
            for interval in intervale:
                for sala in sali:
                    if self.orar[zi][interval.get_interval()][sala.get_name()] is None:
                        continue

                    prof, materie = self.orar[zi][interval.get_interval()][sala.get_name()]
                    prof = [profesor for profesor in profesori if profesor.get_name() == prof][0]

                    for zi_noua in zile:
                        for interval_nou in intervale:
                            for sala_noua in sali:
                                if zi_noua == zi and interval_nou.get_interval() == interval.get_interval() and sala_noua.get_name() == sala.get_name():
                                    continue

                                if self.orar[zi_noua][interval_nou.get_interval()][sala_noua.get_name()] is not None:
                                    continue

                                if not sala_noua.in_materii(materie.get_name()):
                                    continue

                                if not prof.in_materii(materie.get_name()):
                                    continue

                                yield self.apply_move(\
                                                    (zi, interval.get_interval(), sala.get_name()), \
                                                    (prof.get_name(), materie), \
                                                    (zi_noua, interval_nou.get_interval(), sala_noua.get_name()))
                                
    def get_orar(self) -> dict:
        return self.orar
    
    def clone(self):
        return State(copy(self.orar), self.conflicts)


def hca_main(timetable_specs: dict):
    global materii, profesori, sali, intervale, zile

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

    zile = timetable_specs[utils.ZILE]

    result = hill_climbing(State(), 1000).get_orar()
    print(utils.pretty_print_timetable(result, 'inputs/dummy.yaml'))

def hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial.clone()
    minim = state.get_conflicts()
    
    while iters < max_iters:
        print(minim, states)
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
        
    return state
