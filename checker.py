import os
import sys

def run_test(file_name, method):
    print(f"Running test for {file_name}")
    os.system(f"time python3 orar.py {method} inputs/{file_name}.yaml")
    os.system(f"python3 check_constraints.py {file_name}")
    os.system(f"rm -rf my_outputs/{file_name}.txt")

def main():
    #get the name of the file in the inputs folder
    if len(sys.argv) != 2:
        print("Usage: python3 checker.py <method>")
        exit(1)

    method = sys.argv[1]

    if method not in ["hc", "csp"]:
        print("Invalid method")
        print("The available methods are: hc and csp")
        exit(1)

    files = os.listdir("./inputs")
    for file in files:
        # print(f"Running test for {file}")
        if file.endswith(".yaml") and "bonus" not in file:
            file_name = file.split(".")[0]
            run_test(file_name, method)
    
if __name__ == "__main__":
    main()