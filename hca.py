import utils, os
from structures import Materie, Sala, Profesor, Interval, State
    
def hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial.clone()
    
    while iters < max_iters:
        iters += 1
        hard_conflicts, soft_conflicts = state.get_conflicts()

        if state.is_final():
            break
        
        not_found = True
        min_hard_conflicts, min_soft_conflicts = float('inf'), float('inf')
        min_state = None

        for neigh in list(state.get_next_states()):
            # print(f'Neighbor state: {neigh.get_conflicts()}')
            neigh_hard_conflicts, neigh_soft_conflicts = neigh.get_conflicts()

            # Prioritize based on hard constraints first
            if neigh_hard_conflicts < hard_conflicts\
                  or (neigh_hard_conflicts == hard_conflicts and neigh_soft_conflicts <= soft_conflicts):
                hard_conflicts = neigh_hard_conflicts
                soft_conflicts = neigh_soft_conflicts
                state = neigh
                not_found = False

            if neigh_hard_conflicts < min_hard_conflicts\
                  or (neigh_hard_conflicts == min_hard_conflicts and neigh_soft_conflicts <= min_soft_conflicts):
                min_hard_conflicts = neigh_hard_conflicts
                min_soft_conflicts = neigh_soft_conflicts
                min_state = neigh

        if not_found:
            if min_state is not None:
                state = min_state
            else:
                break
        
    return state.is_final(), iters, states, state

def hca_main(timetable_specs: dict, input_path: str):
    materii = []
    for materie in timetable_specs[utils.MATERII]:
        materii.append(Materie(materie, timetable_specs[utils.MATERII][materie]))

    sali = []
    for sala in timetable_specs[utils.SALI]:
        sali.append(Sala(sala,\
                            timetable_specs[utils.SALI][sala][utils.CAPACITATE],\
                            timetable_specs[utils.SALI][sala][utils.MATERII]))
    sali.sort(key=lambda x: (-len(x.materii), x.get_capacitate()), reverse=True)

    profesori = []
    for profesor in timetable_specs[utils.PROFESORI]:
        profesori.append(Profesor(profesor,\
                        timetable_specs[utils.PROFESORI][profesor][utils.MATERII],\
                        timetable_specs[utils.PROFESORI][profesor][utils.CONSTRANGERI]))
    profesori.sort(key=lambda x: len(x.materii))
        
    intervale = []
    for interval in timetable_specs[utils.INTERVALE]:
        intervale.append(Interval(interval))
        
    zile = timetable_specs[utils.ZILE]

    materie_nr_profesori = {}
    for materie in materii:
        materie_nr_profesori[materie.get_name()] = 0

    for profesor in profesori:
        for materie in profesor.materii:
            materie_nr_profesori[materie] += 1

    materii.sort(key=lambda x: (materie_nr_profesori[x.get_name()], -x.get_capacitate()))
    
    State.materii = materii
    State.sali = sali
    State.profesori = profesori
    State.intervale = intervale
    State.zile = zile

    _, _, _, state = hill_climbing(State())
    timetable = utils.pretty_print_timetable(state.get_orar(), input_path)
    
    print(f'Hard constraints: {state.hard_conflicts}\nSoft constraints: {state.soft_conflicts}\n')
    print(timetable)

    if not os.path.exists('my_outputs'):
        os.makedirs('my_outputs')

    output_path = input_path.replace('inputs', 'my_outputs').replace('.yaml', '.txt')
    with open(output_path, 'w') as f:
        f.write(timetable)
