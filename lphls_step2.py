from crg.src.crg_gen import *
from insert.src.cdc_insert import *
from insert.src.crg_insert import *
from insert.src.cg_insert import *
import pdb
import os
import argparse
import re
import sys

def temp_deal(file_path):
    pattern = r'\s*// synthesis translate_off'
    new_lines = []
    cnt = 0
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                cnt = 1
                continue
            elif cnt==1:
                cnt = 2
                continue
            elif cnt==2:
                cnt = 0
                continue
            new_lines.append(line)
    
    with open(file_path, 'w') as file:
        for line in new_lines:
            file.write(line)


parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--root_path", type=str, default="0")
parser.add_argument("--proj_path", type=str, default="0")
parser.add_argument("--proj_name", type=str, default="0")
parser.add_argument("--cpp_top_name", type=str, default="0")
parser.add_argument("--cpp_path", type=str, default="0")
parser.add_argument("--solution_name", type=str, default="0")
parser.add_argument("--xo_path", type=str, default="0")
parser.add_argument("--rdm", type=int, default=0)
parser.add_argument("--gate_num", type=int, default=10)
parser.add_argument("--gate_level", type=int, default=2)
parser.add_argument("--gate_enable", type=str, default="true")
args = parser.parse_args()

root_path = args.root_path
proj_path = args.proj_path
proj_name = args.proj_name
cpp_top_name = args.cpp_top_name
solution_name = args.solution_name
cpp_path = args.cpp_path
xo_path = args.xo_path
rdm = args.rdm
gate_num = args.gate_num
gate_level = args.gate_level
gate_enable = args.gate_enable

<<<<<<< HEAD
cpp_path = root_path+"kernel/"
=======
if cpp_path=="0":
    cpp_path = root_path+"kernel/"
>>>>>>> 5a7057a (release vision 0.9)
syn_rtl_path = proj_path+"/"+proj_name+"/"+solution_name+"/syn/verilog/"
rpt_root_path = proj_path+"/"+proj_name+"/"+solution_name+"/syn/report/"

# backup dut.cpp since after parser, it will be changed so that
# VITIS_HLS can read it. After VITIS_HLS read it, it should be restored
os.system("cp "+cpp_path+cpp_top_name+"_backup.cpp "+cpp_path+cpp_top_name+".cpp")

# parser HLS to generate crg
flg, module_map, fastest_clk_map = crg_gen(cpp_path+cpp_top_name+".cpp")

# temp delete "synthesis translate_off"
temp_deal(syn_rtl_path+proj_name+".v")

# insert cdc circuit and do some modification
if flg==1:
    cdc_insert(proj_name, module_map, fastest_clk_map, syn_rtl_path)

    # insert crg
    crg_insert(proj_name, syn_rtl_path)

# insert clock gate
<<<<<<< HEAD
cg_insert(proj_name, syn_rtl_path, rpt_root_path, 20, 0)
=======
if gate_enable=="true":
    if rdm:
        cg_insert_random(syn_rtl_path, gate_num, "top")
    else:
        cg_insert(proj_name, syn_rtl_path, rpt_root_path, gate_num, gate_level)
>>>>>>> 5a7057a (release vision 0.9)

# generate a tcl file 
with open(proj_path+'/run_hls.tcl', 'w') as f:
    f.write("open_project "+proj_name)
    f.write("\n")
    f.write("open_solution "+solution_name)
    f.write("\n")
<<<<<<< HEAD
    f.write("export_design -rtl verilog -format xo -output "+proj_name+".xo")
=======
    f.write("add_files "+syn_rtl_path+"/top_crg.v")
>>>>>>> 5a7057a (release vision 0.9)
    f.write("\n")
    f.write("export_design -rtl verilog -format xo -output "+proj_name+".xo")
    f.write("\n")
    f.write("exit")

#using VITIS_HLS to generate Verilog
os.chdir(proj_path)
os.system("vitis-run --mode hls --tcl run_hls.tcl")
os.chdir(root_path)
os.system("cp "+proj_path+"/"+proj_name+".xo "+root_path+"/"+xo_path)
os.system("cp "+cpp_path+cpp_top_name+"_backup.cpp "+cpp_path+cpp_top_name+".cpp")
