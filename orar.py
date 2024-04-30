import utils
import sys
import hca
import csp

if __name__ == '__main__':
    n = len(sys.argv)

    if n != 3:
        print('Usage: python3 orar.py <method> <input_file>')
        exit(1)

    method = sys.argv[1]
    input_file = sys.argv[2]

    try:
        timetable_specs = utils.read_yaml_file(input_file)
    except Exception as e:
        print(e)
        exit(1)

    if method == 'hc':
        hca.hca_main(timetable_specs, input_file)
    elif method == 'csp':
        csp.csp_main(timetable_specs, input_file)
    else:
        print('Invalid method')
        print('The available methods are: hc and csp')
        exit(1)