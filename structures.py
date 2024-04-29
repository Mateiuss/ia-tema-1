from copy import deepcopy

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
        self.acoperire = 0

    def get_capacitate(self) -> int:
        return self.capacitate
    
    def get_acoperire(self) -> int:
        return self.acoperire
    
    def is_full(self) -> bool:
        return self.acoperire >= self.capacitate
    
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
        self.acoperire = 0

    def get_name(self) -> str:
        return self.name
    
    def is_full(self) -> bool:
        return self.acoperire == 7
    
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
    def __init__(self, orar: dict=None, data=None):
        if orar is None:
            self.orar = self.create_first_state()
        else:
            self.orar = orar

        self.compute_conflicts()

    def create_first_state(self):
        orar = {}

        for zi in State.zile:
            orar[zi] = {}
            for interval in State.intervale:
                orar[zi][interval.get_interval()] = {}
                for sala in State.sali:
                    orar[zi][interval.get_interval()][sala.get_name()] = None

        return orar
    
    def compute_conflicts(self):
        self.hard_conflicts = 0
        self.soft_conflicts = 0

        profesor_zi_interval = {}

        profesor_ore_predate = {}
        for profesor in State.profesori:
            profesor_ore_predate[profesor.get_name()] = 0
            profesor_zi_interval[profesor.get_name()] = {}

            for zi in State.zile:
                profesor_zi_interval[profesor.get_name()][zi] = set()

        materie_acoperire = {}
        for materie in State.materii:
            materie_acoperire[materie.get_name()] = 0

        capacitate_materie = {}
        for materie in State.materii:
            capacitate_materie[materie.get_name()] = materie.get_capacitate()

        string_to_sala = {}
        for sala in State.sali:
            string_to_sala[sala.get_name()] = sala

        string_to_profesor = {}
        for profesor in State.profesori:
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
        curr_materii = []
        for materie in State.materii:
            if self.materie_acoperire[materie.get_name()] < materie.get_capacitate():
                curr_materii.append(materie)

        curr_profesori = []
        for profesor in State.profesori:
            if self.profesor_ore_predate[profesor.get_name()] < 7:
                curr_profesori.append(profesor)

        for materie in curr_materii:
            for profesor in curr_profesori:
                if not profesor.in_materii(materie.get_name()):
                    continue

                # heurisitc for ordering the days
                zile_preferate = []
                for zi in State.zile:
                    if zi in profesor.constrangeri:
                        zile_preferate.append(zi)
                    else:
                        zile_preferate.insert(0, zi)

                # heurisitc for ordering the intervals
                intervale_preferate = []
                for interval in State.intervale:
                    if str(interval) in profesor.constrangeri:
                        intervale_preferate.append(interval)
                    else:
                        intervale_preferate.insert(0, interval)

                for zi in zile_preferate:
                    for interval in intervale_preferate:
                        if interval.get_interval() in self.profesor_zi_interval[profesor.get_name()][zi]:
                            continue

                        for sala in State.sali:
                            if self.orar[zi][interval.get_interval()][sala.get_name()] is not None:
                                continue

                            if not sala.in_materii(materie.get_name()):
                                continue

                            yield self.apply_move((profesor.get_name(), materie.get_name()),\
                                                  (zi, interval.get_interval(), sala.get_name()))
                                
    def get_orar(self) -> dict:
        return self.orar
    
    def clone(self):
        return State(deepcopy(self.orar))