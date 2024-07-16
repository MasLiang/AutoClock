from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast
import os
import copy
import re
from parser import *

def determain_cgen(file_path, undf_flg):
    top_module_ast, directives = rtl_parse([file_path])
    
    if undf_flg:
        # cgen = !(idle |(ap_ST_fsm_state*_blk & ap_CS_fsm_state*))
        all_wire = DFS(top_module_ast, lambda node : isinstance(node, ast.Wire))
        all_reg = DFS(top_module_ast, lambda node : isinstance(node, ast.Reg))
        cgen_n = "ap_idle"
        state_idx_list = []
        block_state_pattern = r'ap_ST_fsm_state(\d+)_blk'
        for reg in all_reg:
            print(reg.name)
            match = re.search(block_state_pattern, reg.name)
            if match:
                state_idx_list.append(match.group(1))
                print("****")
                print(match.group(0), match.group(1))

        cgen_n_or = ""
        if len(state_idx_list)>0:
            for state_idx in state_idx_list:
                cgen_n_or = cgen_n_or+" | (ap_ST_fsm_state"+str(state_idx)+"_blk & ap_CS_fsm_state"+str(state_idx)+")"
            
        cgen = "!("+cgen_n+cgen_n_or+")"
        return cgen
    else:
        all_output = DFS(top_module_ast, lambda node : isinstance(node, ast.Output))
        for outsig in all_output:
            if outsig.name=="ap_idle":
                return "ap_idle"
        return "" 
    
def cg_insert_single_module(inst_name, root_path, undf_flg):
    file_path = root_path+"/"+inst_name+".v"
    cgen = determain_cgen(file_path, undf_flg)

    if cgen=='':
        return

    cg_list = []
    cg_list.append("\n")
    cg_list.append("wire        ap_clk_cg;\n")
    cg_list.append("wire        cgen;\n")
    cg_list.append("assign      cgen = "+cgen+";\n")
    cg_list.append("BUFGCE "+inst_name+"_bufgce(\n")
    cg_list.append("    .I        (ap_clk),\n")
    cg_list.append("    .O        (ap_clk_cg),\n")
    cg_list.append("    .CE       (cgen));\n")
    cg_list.append("\n")

    new_rtl = []
    with open(file_path, 'r') as file:
        var_def_flg = 0
        insert_flg = 0
        first_apclk_flg = 0
        first_apclk_flg = 0
        for line in file:
            if "ap_clk" in line and first_apclk_flg==0:
                first_apclk_flg = 1
                new_rtl.append(line)
            elif "ap_clk" in line and (not "input " in line):
                next_line1 = file.readline()
                next_line2 = file.readline()
                if "if" in next_line2:
                    next_line3 = file.readline()
                    if "ap_CS_fsm" in next_line3:
                        new_rtl.append(line)
                        new_rtl.append(next_line1)
                        new_rtl.append(next_line2)
                        new_rtl.append(next_line3)
                    else:
                        line = line.replace("ap_clk", "ap_clk_cg")
                        new_rtl.append(line)
                        new_rtl.append(next_line1)
                        new_rtl.append(next_line2)
                        new_rtl.append(next_line3)
                else:
                    if "ap_CS_fsm" in next_line2:
                        new_rtl.append(line)
                        new_rtl.append(next_line1)
                        new_rtl.append(next_line2)
                        continue
                    else:
                        line = line.replace("ap_clk", "ap_clk_cg")
                        new_rtl.append(line)
                        new_rtl.append(next_line1)
                        new_rtl.append(next_line2)
            else:
                new_rtl.append(line)
                
            if insert_flg==0:
                if var_def_flg==0:
                    if ("wire " in line or "reg " in line) and (not( "input " in line or "output " in line)):
                        var_def_flg = 1
                else:
                    if not ("wire " in line or "reg " in line or line=="\n"):
                        new_rtl += cg_list
                        var_def_flg = 0
                        insert_flg = 1

    with open(file_path, "w") as f:
        for i in new_rtl:
            f.write(i)

def cg_insert(module_name, root_path):
    if os.path.exists(root_path+"/"+module_name+".v"):
        _, _, _, main_module_list, _, _, other_module_list, _, _, _, _, _ = read_file(module_name, {}, root_path)
        for inst in main_module_list+other_module_list:
            # Why not this file?
            if not os.path.exists(root_path+"/"+inst.module+".v"):
                continue
            # read and parse this file
            _, _, cg_module_list, main_module_list, _, _, other_module_list, _, case_always_list, _, _, _ = read_file(inst.module, {}, root_path)
            
            # if there is a clock gate
            if len(cg_module_list)!=0:
                continue
            module_list = main_module_list + other_module_list
            # if there are sub-modules
            if len(module_list)!=0:
                for sub_module in module_list:
                    cg_insert(sub_module.module, root_path)
            
            undf_flg = 0 # 1: this is a un-dataflow module with FSM
            if len(case_always_list)>0:
                for case_always in case_always_list:
                    if case_always.statement.statements[0].comp.name=="ap_CS_fsm":
                        undf_flg = 1
                        break
            cg_insert_single_module(inst.module, root_path, undf_flg)
        

cg_insert("top_kernel3_x0", "../../all_ab/dut/solution1/impl/verilog/")
