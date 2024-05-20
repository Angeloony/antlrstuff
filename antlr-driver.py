import os
import sys
import time
from subprocess import PIPE, STDOUT, run


# check for commented out lines and remove them from out inputs!
# comments start with ; in smtlib apparently 
def check_line_skip(line):
    
     for character in line:
        if character == ';':
            return True    
        if character != ';' and character != ' ':
            return False
        if character == ' ':
            continue
        

# extracts relevant inputs of our smtlibv2 example files for input into antlr parsing later
def parse_input_file(input_file):
    f = open(input_file, "r")
    input_string=""
    
    for line in f:
        if check_line_skip(line) == False:
            input_string = input_string + line
            #print(line)
            
    f.close()
    
    return [input_file, input_string.encode('ascii')] # encode string as binary ascii code, so it can be used as an input with subprocess.run()


# get file names from our example file location
def get_test_files(file_location):
    test_file_names = []
    directory = os.fsencode(file_location)
    
    for file in os.listdir(directory):
        test_file_names.append(os.fsdecode(file))
    
    test_file_names.sort()
    
    return test_file_names 
    
    

"""
    Driver for running smtlibv2 test files using antlr
    
    Run command:
                                arg1           arg2 (optional)
        python3 antlr-driver.py file_location/ file_name
    Example: 
        python antlr-driver.py examples/ test01.smt2
"""
def main():
    # file information
    test_location = sys.argv[1]
    test_file = None
    # only init filename is its given, makes it optional
    # maybe improve this later on
    if len(sys.argv) >= 3:
        test_file = sys.argv[2]
    
    # if file is given, get only that file back
    test_files = get_test_files(test_location)
    
    test_inputs = []
    for file in test_files:
        test_inputs.append(parse_input_file(test_location + file))
    
    i = 0
    for file, input in test_inputs:
        # only run the desired test input
        path, file_name = os.path.split(file)
        #print(file_name[: -5])
        if test_file != None:
            if file == test_location + test_file:
                #with open("output" + str(i).zfill(3), 'w') as outfile:
                run(["antlr4-parse",
                        "smtlibv2/SMTLIBv2.g4",
                        "start_",
                        "-profile",
                        "outputs/"+ file_name[: -5] +".csv"
                        ], 
                                stdout=PIPE,  
                                stderr=STDOUT,
                                input=input 
                                )
                i = i+1
        # run all test inputs that we have in our given folder
        elif test_file == None: 
            #with open("output" + str(i).zfill(3), 'w') as outfile:
            run(["antlr4-parse",
                "smtlibv2/SMTLIBv2.g4",
                "start_",
                #"-tree",
                "-profile",
                "outputs/"+ file_name[: -5] +".csv"
                ], 
                                stdout=PIPE,  
                                stderr=STDOUT,
                                input=input 
                                )
            i = i+1
                
            
            
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(end - start)