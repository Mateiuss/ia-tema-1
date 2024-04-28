import utils
import sys
import hca

if __name__ == '__main__':
    n = len(sys.argv)

    if n != 3:
        print('Usage: python orar.py <method> <input_file>')
        exit(1)

    print('Note: The output will be saved in my_outputs/ directory')

    method = sys.argv[1]
    input_file = sys.argv[2]

    timetable_specs = utils.read_yaml_file(input_file)

    if method == 'hc':
        hca.hca_main(timetable_specs, input_file)
    elif method == 'csp':
        pass
    else:
        print('Invalid method')
        exit(1)