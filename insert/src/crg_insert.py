from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from .rtl_parser import *
import pyverilog.vparser.ast as ast
import os
import re

def connect_mux_sel(module_name, mux_freq, top_ast, top_path):
    # For infered TDM modules:
    # 1. find the start signal and the always block
    # 2. seperate the status in FSM for different clock frequency
    # 3. build a logic to generate sel signal
    # For configured dynamic frequency modules:
    # 1. Since they use the same name, they will be connected naturally

    # For infered TDM modules:
    # 1. find the start signal and the always block
    all_sigs = DFS(top_ast, lambda node: isinstance(node, ast.Wire))
    start_pattern = rf'(\w+)_{module_name[4:]}_(\w+)_start_reg_async_cond'
    for start_sig in all_sigs:
        start_match = re.search(start_pattern, start_sig.name)
        if start_match:
            break

    # because clock mux, this will be viewed as a seperate clock and it will be 
    # asyunc with the fastest clock. As a result, the condition should be synch.
    # So we find the condition assignment line to seperate the sattus.
    all_assigns = DFS(top_ast, lambda node: isinstance(node, ast.Assign))
    for start_assign in all_assigns:
        if start_assign.left.var.name==start_sig.name:
            break
    start_cond_lineno = start_assign.lineno
    start_assign.show()

    # 2. seperate the status in FSM for different clock frequency
    with open(top_path, 'r') as top_module:
        for cur_lineno, line in enumerate(top_module, start=1):
            if cur_lineno==start_cond_lineno:
                state_pattern = r'ap_CS_fsm_state\d+'
                state_match = re.findall(state_pattern, line)
                break
    

    # 3. build a logic to generate sel signal
    # for each module, there will be two states. For example, state4 pipe one cycle
    # and generate start signal, then the module runs during state5
    # In fact switching clock require a time slot. Because of async, the state is pipelined.
    # So there is no need to pipe again for switching clock.
    state_match.sort()
    state_mux = [[state_match[i], state_match[i+1]] for i in range(0, len(state_match), 2)]
    mux_logic = []
    mux_logic.append("reg "+module_name+"_clk_sel_reg;")
    mux_logic.append("assign    "+module_name+"_clk_sel = "+module_name+"_clk_sel_reg;")
    mux_logic.append("always @(*)")
    mux_logic.append("begin")

    for idx in range(len(state_mux)):
        if (idx==0):
            mux_logic.append("    if ("+state_mux[idx][0]+" | "+state_mux[idx][1]+")")
            mux_logic.append("    begin")
            mux_logic.append("        "+module_name+"_clk_sel_reg     =       0;")
            mux_logic.append("    end")
        else:
            mux_logic.append("    else if ("+state_mux[idx][0]+" | "+state_mux[idx][1]+")")
            mux_logic.append("    begin")
            mux_logic.append("        "+module_name+"_clk_sel_reg     =       "+str(idx)+";")
            mux_logic.append("    end")
            
    mux_logic.append("end")
    
    return mux_logic

def crg_insert(module_name, root_path, lst_new_module, tdm_modules):
    # read crg
    crg_ast, _ = rtl_parse([root_path+"/"+module_name+"_crg_inst.v"])
    os.system("rm "+root_path+"/"+module_name+"_crg_inst.v")
    crg_instances = DFS(crg_ast, lambda node : isinstance(node, ast.Instance))
    for crg_inst in crg_instances:
        break
    crg_module_defs = DFS(crg_ast, lambda node: isinstance(node, ast.ModuleDef))
    for crg_module_def in crg_module_defs:
        break
    crg_item_list = list(crg_module_def.items)
    for crg_item_idx in range(len(crg_item_list)):
        if isinstance(crg_item_list[crg_item_idx], ast.InstanceList):
            break

    # read top module
    top_path = root_path+"/"+module_name+".v"
    top_ast, _ = rtl_parse([top_path])
    top_instances = DFS(top_ast, lambda node : isinstance(node, ast.Instance))
    for top_inst in top_instances:
        break
    top_module_defs = DFS(top_ast, lambda node: isinstance(node, ast.ModuleDef))
    for top_module_def in top_module_defs:
        break
    top_item_list = list(top_module_def.items)
    def_start_flg = 0
    for top_item_idx in range(len(top_item_list)):
        if def_start_flg==0:
            if isinstance(top_item_list[top_item_idx], ast.Decl) or isinstance(top_item_list[top_item_idx], ast.Pragma):
                def_start_flg = 1
        elif not (isinstance(top_item_list[top_item_idx], ast.Decl) or isinstance(top_item_list[top_item_idx], ast.Pragma)):
            break

    # connect mux selection signals
    # 1. user configure
    # 2. infered tdm
    mux_logic = []
    for tdm_module in list(tdm_modules.keys()):
        mux_freq = tdm_modules[tdm_module] 
        mux_logic += connect_mux_sel(tdm_module, mux_freq, top_ast, top_path)

    mux_sig_path = root_path+"/sel_mux.v"
    with open(mux_sig_path, "w") as f:
        f.write("module "+module_name+"_sel_mux(\n")
        f.write("input clk,\n")
        f.write("input rst_n);\n")
        for line in mux_logic:
            f.write(line)
            f.write("\n")
        f.write("endmodule")
    mux_sig_ast, _ = rtl_parse([mux_sig_path])
    mux_sig_instances = DFS(mux_sig_ast, lambda node : isinstance(node, ast.Instance))
    for mux_sig_inst in mux_sig_instances:
        break
    mux_sig_module_defs = DFS(mux_sig_ast, lambda node: isinstance(node, ast.ModuleDef))
    for mux_sig_module_def in mux_sig_module_defs:
        break
    mux_sig_item_list = list(mux_sig_module_def.items)
    def_start_flg = 0
    for mux_sig_item_idx in range(len(mux_sig_item_list)):
        if def_start_flg==0:
            if isinstance(mux_sig_item_list[mux_sig_item_idx], ast.Decl) or isinstance(mux_sig_item_list[mux_sig_item_idx], ast.Pragma):
                def_start_flg = 1
        elif not (isinstance(mux_sig_item_list[mux_sig_item_idx], ast.Decl) or isinstance(mux_sig_item_list[mux_sig_item_idx], ast.Pragma)):
            break



    # fuse wires
    top_item_list = top_item_list[0:top_item_idx]+crg_item_list[0:crg_item_idx]+mux_sig_item_list[0:mux_sig_item_idx]+top_item_list[top_item_idx:]
    for top_item_idx in range(len(top_item_list)):
        if isinstance(top_item_list[top_item_idx], ast.InstanceList):
            break
    # fuse instance
    top_item_list = top_item_list[0:top_item_idx]+crg_item_list[crg_item_idx:]+mux_sig_item_list[mux_sig_item_idx:]+top_item_list[top_item_idx:]
    top_module_def.items = tuple(top_item_list)
    
    # generate new rtl
    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_ast)]

    with open(root_path+"/"+module_name+"_crg.v", "r") as f:
        new_rtl += f.readlines()
    new_rtl+="\n"
    os.system("rm "+root_path+"/"+module_name+"_crg.v")

    for new_module in lst_new_module:
        with open(root_path+"/"+new_module, "r") as f:
            new_rtl += f.readlines()
        new_rtl+="\n"
        os.system("rm "+root_path+"/"+new_module)
        
    with open(module_name+".v", 'w') as f:
        for line in new_rtl:
            f.write(line) 
    os.system("mv *.v "+root_path)
    os.system("rm "+mux_sig_path)

#crg_insert("top", "./verilog/")
#cdc_insert("rwkv_top", {"rwkv_top": "clk_phy", "rwkv_top_read_all115": "clk1", "rwkv_top_layer_common_s": "clk2", "rwkv_top_write_all": "clk3"}, "../../../rwkv_src/verilog/")
