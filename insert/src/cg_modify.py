from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast
import os
import copy
import re
from parser import *

def determain_cgen(file_path, undf_flg):
    top_module_ast, directives = rtl_parse([file_path])
    
    if undf_flg:
        # cgen = !(idle |(ap_block_state* & ap_CS_fsm_state*))
        all_wire = DFS(top_module_ast, lambda node : isinstance(node, ast.Wire))
        all_reg = DFS(top_module_ast, lambda node : isinstance(node, ast.Reg))
        cgen_n = "ap_idle"
        state_idx_list = []
        block_state_pattern = r'ap_block_state(\d+)'
        for wire in all_wire:
            match = re.search(block_state_pattern, wire.name)
            if match:
                state_idx_list.append(match.group(1))
        for reg in all_reg:
            match = re.search(block_state_pattern, reg.name)
            if match:
                state_idx_list.append(match.group(1))

        cgen_n_or = ""
        if len(state_idx_list)>0:
            for state_idx in state_idx_list:
                cgen_n_or = cgen_n_or+" | (ap_block_state"+str(state_idx)+"&ap_CS_fsm_state"+str(state_idx)+")"
            
        cgen = "!("+cgen_n+cgen_n_or+")"
        return cgen
    else:
        all_output = DFS(top_module_ast, lambda node : isinstance(node, ast.Output))
        for outsig in all_output:
            if outsig.name=="ap_idle":
                return "ap_idle"
        return "" 
    
def insert_cg(inst_name, root_path, undf_flg):
    file_path = root_path+"/"+inst_name+".v"
    cgen = determain_cgen(file_path, undf_flg)

    if cgen=='':
        return

    cg_list = []
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
            elif "ap_clk" in line and (not "input " in line):
                line = line.replace("ap_clk", "ap_clk_cg")
                
            if insert_flg==0:
                if var_def_flg==0:
                    if ("wire " in line or "reg " in line) and (not( "input " in line or "output " in line)):
                        var_def_flg = 1
                    new_rtl.append(line)
                else:
                    if not ("wire " in line or "reg " in line or line=="\n"):
                        new_rtl += cg_list
                        var_def_flg = 0
                        insert_flg = 1
                    new_rtl.append(line)
            else:
                new_rtl.append(line)


    with open(file_path, "w") as f:
        for i in new_rtl:
            f.write(i)

def cg_modify(module_list, root_path):
    for inst in module_list:
        # Why not this file?
        if not os.path.exists(root_path+"/"+inst.module+".v"):
            continue
        # read and parse this file
        _,cg_module_list, main_module_list, _, _, _, other_module_list,_, case_always_list, _, _ = read_file(inst.module, {}, root_path)
        # if there is a clock gate
        if len(cg_module_list)!=0:
            continue
        module_list = main_module_list + other_module_list
        # if there are sub-modules
        if len(module_list)!=0:
            cg_modify(module_list, root_path)
        # 1: this is a un-dataflow module
        undf_flg = 0
        if len(case_always_list)==0:
            undf_flg = 1
        insert_cg(inst.module, root_path, undf_flg)
        
#insert_cg("top", "./verilog")
root_path = "./verilog"
_, cg_module_list, main_module_list, _, _, _, other_module_list, _, _, _, _ = read_file("top", {}, root_path)
cg_modify(main_module_list+other_module_list, root_path)
