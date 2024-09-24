import re
import sys
import os


root_path = sys.argv[1]
file_name = sys.argv[2]

file_path = root_path+"/"+file_name+".cpp"
backup_file_path = root_path+"/"+file_name+"_backup.cpp"

os.system("cp "+file_path+" "+backup_file_path)
input_clk_pattern = r'\s*#pragma \s*HLS \s*inputclk \s*(\w+(?:_\w+)*)\s*(\d+(?:\s+\d+)*)'
domain_pattern = r'\s*#pragma \s*HLS \s*clkdomain \s*(\w+(?:_\w+)*)\s*(\d+(?:\s+\d+)*)'
sel_pattern = r'\s*#pragma\s*HLS\s*clksel\s*(\w+)\s*(\w+)'
new_lines = []
with open(file_path, 'r') as file:
    for line in file:
        input_clk_match = re.match(input_clk_pattern, line)
        domain_match = re.match(domain_pattern, line)
        sel_match = re.match(sel_pattern, line)
        
        if input_clk_match or domain_match or sel_match:
            continue
        new_lines.append(line)

with open(file_path, 'w') as file:
    for line in new_lines:
        file.write(line)

