import os
def run_test(file_name):
    print(f"Running test for {file_name}")
    os.system(f"python3 orar.py hc inputs/{file_name}.yaml")
    os.system(f"python3 check_constraints.py {file_name}")

def main():
    #get the name of the file in the inputs folder
    files = os.listdir("./inputs")
    for file in files:
        # print(f"Running test for {file}")
        if file.endswith(".yaml") and "bonus" not in file:
            file_name = file.split(".")[0]
            run_test(file_name)
    
if __name__ == "__main__":
    main()