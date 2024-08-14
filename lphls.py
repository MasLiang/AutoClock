from crg.src.crg_gen import *
from insert.src.cdc_insert import *
from insert.src.crg_insert import *
from insert.src.cg_insert import *
import pdb
import os


root_path = "./all_ab/"
cpp_path = root_path+"dut.cpp"
rtl_path = root_path+"dut/solution1/impl/verilog/"

# back dut.cpp since after parser, it will be changed so that
# VITIS_HLS can read it. After VITIS_HLS read it, it should be restored
os.system("cp "+cpp_path+" "+root_path+"dut_backup.cpp")

# parser HLS to generate crg
clk_domains, module_map, fastest_clk_map = crg_gen(cpp_path)
#print("***module map : ", module_map)
#print(clk_domains)

#using VITIS_HLS to generate 
os.chdir(root_path)
#os.system("vitis_hls -f run_hls.tcl")
os.system("cp dut_backup.cpp dut.cpp")
os.chdir("../")

# insert cdc circuit and do some modification
cdc_insert("top", module_map, fastest_clk_map, rtl_path)

# insert crg
crg_insert("top", rtl_path)

# insert clock gate
cg_insert("top", rtl_path, 0, 280, 0, 2)
