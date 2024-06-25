import os
import shutil
import string
import sys
import time
from subprocess import PIPE, STDOUT, run


def replace_umlauts(line):
    new_line = line.replace("ä", "ae")
    new_line = new_line.replace("ü", "ue")
    new_line = new_line.replace("ö", "oe")
    new_line = new_line.replace("Ä", "Ae")
    new_line = new_line.replace("Ü", "Ue")
    new_line = new_line.replace("Ö", "Oe")
    return new_line

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
    #print(input_file)
    
    for line in f:
        if check_line_skip(line) == False:
            new_line = replace_umlauts(line)
            input_string = input_string + new_line
            #print(line + "\n")
            
    f.close()
    return [input_file, input_string.encode('ascii')] # encode string as binary ascii code, so it can be used as an input with subprocess.run()


# parse the directories to get all relevant files 
def get_all_files(file_location):
    all_files = []
    print("hey")
    for subdir, dir, files in os.walk(file_location):
        for file in files:
            #print(os.path.join(subdir,file))
            all_files.append(os.path.join(subdir,file))
    return all_files


# get all relevant .smt2 benchmark files for testing 
def get_test_files(file_location):
    print("hi")
    potential_test_files = get_all_files(file_location=file_location)
            
    test_files = []
    directory = file_location
    
    for file in potential_test_files:
        #print(str(file[-4:]))
        if file[-4:] == "smt2":
            test_files.append(file)
    
    test_files.sort()
    #print(test_files)
    with open('test_files.txt', 'w') as f:
        for line in test_files:
            f.write(f"{line}\n")
    return test_files 


# runs our parser 
def run_antlr_subprocess(test_inputs, test_location, test_file):
    i = 0
    for file, input in test_inputs:
        # only run the desired test input
        path, file_name = os.path.split(file)
        #file_name = file.replace("/", "_")
        #print(file_name[: -5])
        if test_file != None:
            if file == test_location + test_file:
                
                with open("outputs/" + test_location + file[:-5] + ".o", 'w') as outfile:
                    run(["antlr4-parse",
                            "smtlibv2/SMTLIBv2.g4",
                            "start_",
                            "-tree",
                            #"outputs/"+ file_name[: -5] +".csv"
                            ], 
                                    stdout=outfile,  
                                    stderr=STDOUT,
                                    input=input 
                                    )
                    i = i+1
        # run all test inputs that we have in our given folder
        elif test_file == None: 
            with open("outputs/" + test_location + file_name[:-5] + ".o", 'w') as outfile:
                run(["antlr4-parse",
                    "smtlibv2/SMTLIBv2.g4",
                    "start_",
                    "-tree",
                    #"-profile",
                    #"outputs/"+ file_name[: -5] +".csv"
                    ], 
                                    stdout=outfile,  
                                    stderr=STDOUT,
                                    input=input 
                                    )
                i = i+1


def what_kinds_of_errors(test_location):
    errors = []
    #outputs = get_all_files('outputs/')
    
    with open("error_files/categories.txt", "a+") as error_categorization:
        for line in error_categorization:
            errors.append(line)
        
        with open("error_files" + test_location[10:-1] + "_error_files.txt", "r") as error_files:
            for file in error_files:
                #print(file)
                cur_file = open('outputs/'+ file[:-5] + 'o', "r")
                #print(cur_file)
                for line in cur_file:
                    if line[:-33] in errors:
                        continue
                    elif line[-33:] not in errors and "line" in line[:4]:
                        errors.append(line[-33:])
                        error_categorization.write(line)
        error_files.close()
    error_categorization.close()
    #print(errors)
                
    
def check_for_syntax_errors(file_name, test_location):
    
    syntax_error_files = open("error_files/" + file_name + "error_files.txt", "w")
    #print(syntax_error_files)
    outputs = get_all_files('outputs/' + test_location)
    
    for file in outputs:
        #print(file)
        
        with open(file, "r") as output:
            for line in output:
                if "line" in line:
                    syntax_error_files.write(file[8:-2] +".smt2\n")
                    break
                    # TODO add dictionary so that i can track back to the file name and add the error warning to it. 
                    # TODO we will have outputs, which include the error lines and derivation trees
                    # TODO we can also link the outputs to the og files by using the file names (they are named the same with a different suffix)
                    # TODO separate instances with error/no error and save them in separate files. 
                    # TODO double check that they have no overlap 
    syntax_error_files.close()

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
    # # maybe improve this later on
    # if len(sys.argv) >= 3:
    #     test_file = sys.argv[2]
    
    # # get all test files from benchmark
    test_files = get_test_files(test_location)
    #test_files = open("test_files.txt", "r")
    # input_strings = []
    # for file in test_files:
    #     f = open(file[:-1], "r")
    #     input_string=""
            
    #     for line in f:
    #         if check_line_skip(line) == False:
    #             new_line = replace_umlauts(line)
    #             input_string = input_string + new_line
    #             #print(line + "\n")
        
    #     input_strings.append(input_string)
    
    #for string in input_strings:
        #print(string)
        
    # if os.path.exists("outputs/"):
    #     shutil.rmtree("outputs/")
    # os.mkdir("outputs/")
    
    test_inputs = []
    for file in test_files:
        test_inputs.append(parse_input_file(file))
    run_antlr_subprocess(test_inputs=test_inputs, test_location=test_location, test_file=test_file)
    
    test_folder = test_location.replace("benchmarks/", "")
    test_folder = test_folder.replace("/", "_")
    #print(test_folder)
    check_for_syntax_errors(file_name=test_folder, test_location=test_location)
    what_kinds_of_errors(test_location=test_location)
    if len(sys.argv) >= 3:
        if sys.argv[2] == "-r":
            shutil.rmtree("outputs/")
            
        
        
    
           
            
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(end - start)