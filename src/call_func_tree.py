import os
import re
from collections import defaultdict

def extract_func_calls(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    
    code = re.sub(r'//.*?$|/\*[\s\S]*?\*/', '', code, flags=re.MULTILINE)

    func_def_pattern = r'\b[\w\s\*]+\b\s+\b[\w]+\b\s*\([^\)]*\)\s*\{[^}]*\}'
    func_defs = re.findall(func_def_pattern, code)
    
    for a in func_defs:
        print(a)

    func_name_pattern = r'\b[\w_]+\b\s+[\w_]+\s*(?=\()'
    func_names_list = re.findall(func_name_pattern, code)
    func_names = set()
    for name in func_names_list:
        name = name.split()
        func_names.add(name[1])

    call_map = defaultdict(list)
    for func_name in func_names:
        caller_set = set()
        for caller in func_defs:
            call_func = re.findall(rf'\b{func_name}\s*\(', caller)
            if call_func:
                caller_name = re.findall(func_name_pattern, caller)
                if caller_name:
                    caller_name = caller_name[0].split()
                    if caller_name[1] in func_names and caller_name[1]!=func_name:
                        call_map[caller_name[1]].append(func_name)
    
    return call_map

def find_file_by_func(func_name):
    file_paths = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.c'):
                file_path = os.path.join(root, file)
                if func_name in extract_func_calls(file_path):
                    file_paths.append(file_path)
    return file_paths

aaa = find_file_by_func("read_all")
