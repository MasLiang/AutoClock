from crg.src.crg_gen import *
from insert.src.cdc_insert import *
from insert.src.crg_insert import *
from insert.src.cg_insert import *
import pdb
import os


#root_path = "./benchmark/L1/tests/jpegdec/"
#dut_name = "test_decoder"
#proj_name = "kernel_parser_decoder"
#cpp_path = root_path+dut_name+".cpp"
#impl_rtl_path = root_path+"test.prj/solution1/impl/verilog/"
#syn_rtl_path = root_path+"test.prj/solution1/syn/verilog/"

root_path = "./benchmark/L1/tests/jxlEnc/order_tokenize/"
dut_name = "topOrderTokenize"
proj_name = "top_order_tokenize"
cpp_path = root_path+'/kernel/'+dut_name+".cpp"
impl_rtl_path = root_path+"tokenize.prj/solution1/impl/verilog/"
syn_rtl_path = root_path+"tokenize.prj/solution1/syn/verilog/"

# back dut.cpp since after parser, it will be changed so that
# VITIS_HLS can read it. After VITIS_HLS read it, it should be restored
cur_path = os.path.dirname(os.path.abspath(__file__))
os.system("cp "+cpp_path+" "+root_path+"dut_backup.cpp")

print("*************************************")
print("*************************************")
print("step 0")
print("*************************************")
print("*************************************")
# parser HLS to generate crg
flg, module_map, fastest_clk_map = crg_gen(cpp_path)

print("*************************************")
print("*************************************")
print("step 1")
print("*************************************")
print("*************************************")
#using VITIS_HLS to generate Verilog
os.chdir(root_path)
os.system("vitis_hls -f run_hls_step1.tcl")
os.chdir(cur_path)

# insert cdc circuit and do some modification
if flg==1:
    cdc_insert(proj_name, module_map, fastest_clk_map, rtl_path)

    # insert crg
    crg_insert(proj_name, rtl_path)

# insert clock gate
print("*************************************")
print("*************************************")
print("insert clock gate")
print("*************************************")
print("*************************************")
cg_insert(proj_name, impl_rtl_path)
os.system("cp "+cur_path+"/"+impl_rtl_path+"/*.v "+cur_path+"/"+syn_rtl_path+"/")

#using VITIS_HLS to generate Verilog
print("*************************************")
print("*************************************")
print("step 2")
print("*************************************")
print("*************************************")
os.chdir(root_path)
os.system("vitis_hls -f run_hls_step2.tcl")
os.chdir(cur_path)
os.system("cp "+root_path+"dut_backup.cpp"+" "+cpp_path)
