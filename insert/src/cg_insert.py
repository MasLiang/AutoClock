from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as ast
import os
import copy
import re
from .rtl_parser import *

def determain_cgen(top_module_ast, undf_flg):
    if undf_flg:
        # cgen = !(idle |(ap_ST_fsm_state*_blk & ap_CS_fsm_state*))
        all_wire = DFS(top_module_ast, lambda node : isinstance(node, ast.Wire))
        all_reg = DFS(top_module_ast, lambda node : isinstance(node, ast.Reg))
        state_idx_list = []
        block_state_pattern = r'ap_ST_fsm_state(\d+)_blk'
        idle_pattern = r'ap_idle'
        ap_idle_flg = 0
        for reg in all_reg:
            match = re.search(block_state_pattern, reg.name)
            if match:
                state_idx_list.append(match.group(1))
            match = re.search(idle_pattern, reg.name)
            if match:
                ap_idle_flg = 1

        cgen_n = ""
        if len(state_idx_list)>0:
            for state_idx in state_idx_list:
                if cgen_n=="":
                    cgen_n = "(ap_ST_fsm_state"+str(state_idx)+"_blk & ap_CS_fsm_state"+str(state_idx)+")"
                else:
                    cgen_n = cgen_n+" | (ap_ST_fsm_state"+str(state_idx)+"_blk & ap_CS_fsm_state"+str(state_idx)+")"
            
        if ap_idle_flg:
            cgen = "!("+cgen_n+" | ap_idle)"
        else:
            cgen = "!("+cgen_n+")"
        return cgen
    else:
        all_output = DFS(top_module_ast, lambda node : isinstance(node, ast.Output))
        for outsig in all_output:
            if outsig.name=="ap_idle":
                return "ap_idle"
        return "" 
    
#def cg_insert_single_module(inst_name, root_path, undf_flg, top_module):
#    print(inst_name)
#    file_path = root_path+"/"+inst_name+".v"
#    cgen = determain_cgen(file_path, undf_flg)
#
#    if cgen=='':
#        return
#
#    cg_list = []
#    cg_list.append("\n")
#    cg_list.append("wire        ap_clk_cg;\n")
#    cg_list.append("wire        cgen;\n")
#    cg_list.append("assign      cgen = "+cgen+";\n")
#    cg_list.append("BUFGCE "+inst_name+"_bufgce(\n")
#    cg_list.append("    .I        (ap_clk),\n")
#    cg_list.append("    .O        (ap_clk_cg),\n")
#    cg_list.append("    .CE       (cgen));\n")
#    cg_list.append("\n")
#
#    new_rtl = []
#    with open(file_path, 'r') as file:
#        var_def_flg = 0
#        insert_flg = 0
#        control_s_axi_flg = 0
#        for line in file:
#            if insert_flg==0:
#                if var_def_flg==0:
#                    if ("wire " in line or "reg " in line) and (not( "input " in line or "output " in line)):
#                        var_def_flg = 1
#                else:
#                    if not ("wire " in line or "reg " in line or line=="\n"):
#                        new_rtl += cg_list
#                        var_def_flg = 0
#                        insert_flg = 1
#                new_rtl.append(line)
#            elif "control_s_axi_U" in line or control_s_axi_flg==1:
#                if "control_s_axi_U" in line:
#                    control_s_axi_flg = 1
#                if "ACLK" in line:
#                    control_s_axi_flg = 0 
#                new_rtl.append(line)
#            elif "ap_clk" in line and (not "input " in line):
#                if "always" in line:
#                    next_line1 = file.readline()
#                    next_line2 = file.readline()
#                    if "if" in next_line2:
#                        next_line3 = file.readline()
#                        if "ap_CS_fsm" in next_line3:
#                            new_rtl.append(line)
#                            new_rtl.append(next_line1)
#                            new_rtl.append(next_line2)
#                            new_rtl.append(next_line3)
#                        else:
#                            line = line.replace("ap_clk", "ap_clk_cg")
#                            new_rtl.append(line)
#                            new_rtl.append(next_line1)
#                            new_rtl.append(next_line2)
#                            new_rtl.append(next_line3)
#                    else:
#                        if "ap_CS_fsm" in next_line2:
#                            new_rtl.append(line)
#                            new_rtl.append(next_line1)
#                            new_rtl.append(next_line2)
#                            continue
#                        else:
#                            line = line.replace("ap_clk", "ap_clk_cg")
#                            new_rtl.append(line)
#                            new_rtl.append(next_line1)
#                            new_rtl.append(next_line2)
#                elif line.count("ap_clk") == 2:
#                    # .ap_clk(ap_clk) --> .ap_clk(ap_clk_cg)
#                    parts = line.split('ap_clk')
#                    new_line = parts[0] + 'ap_clk' + parts[1] + 'ap_clk_cg' +parts[2]
#                    new_rtl.append(new_line)
#                elif "ACLK" in line:
#                    if top_module:
#                        line = line.replace("ap_clk", "ap_clk_cg")
#                    new_rtl.append(line)
#                else:
#                    line = line.replace("ap_clk", "ap_clk_cg")
#                    new_rtl.append(line)
#                    
#            else:
#                new_rtl.append(line)
#
#    with open(file_path, "w") as f:
#        for i in new_rtl:
#            f.write(i)

def cg_insert_single_module(module_name, top_module_ast, top_module, root_path):

    all_always = DFS(top_module_ast, lambda node : isinstance(node, ast.Always))
    all_inst = DFS(top_module_ast, lambda node : isinstance(node, ast.Instance))

    for always in all_always:
        if isinstance(always.statement.statements[0], ast.IfStatement):
            if isinstance(always.statement.statements[0].true_statement.statements[0], ast.NonblockingSubstitution):
                if isinstance(always.statement.statements[0].true_statement.statements[0].left.var, ast.Identifier):
                    var = always.statement.statements[0].true_statement.statements[0].left.var.name
                    # bind to the fastest clock
                    if var=="ap_CS_fsm":
                        continue
                    elif always.sens_list.list[0].type=="posedge":
                        if always.sens_list.list[0].sig.name=="ap_clk":
                            always.sens_list.list[0].sig.name = "ap_clk_cg"
        
    for inst in all_inst:
        if is_main_axi_module(inst):
            continue
        elif "control_s_axi" in inst.module:
            continue
        elif "m_axi" in inst.module:
            continue
        elif "crg" in inst.module:
            for portarg in inst.portlist:
                if portarg.argname.name=="ap_clk":
                    portarg.argname.name = "ap_clk_cg"
        else:
            for portarg in inst.portlist:
                if isinstance(portarg.argname, ast.Identifier):
                    if portarg.argname.name=="ap_clk":
                        portarg.argname.name = "ap_clk_cg"

    top_module_defs = DFS(top_module_ast, lambda node : isinstance(node, ast.ModuleDef))
    for top_def in top_module_defs:
        break
    cgen = determain_cgen(top_module_ast, 1)
    cg_inst_gen(module_name, cgen)
    cg_ast, _ = rtl_parse(["./"+module_name+"_inst.v"])
    os.system("rm "+module_name+"_inst.v")
    cg_module_defs = DFS(cg_ast, lambda node : isinstance(node, ast.ModuleDef))
    for cg_def in cg_module_defs:
        break
    top_items_list = list(top_def.items)
    cg_items_list = list(cg_def.items)
    top_decl_idx = 0
    cg_decl_idx = 0
    for item_idx in range(len(top_items_list)):
        if isinstance(top_items_list[item_idx], ast.Decl):
            top_decl_idx = item_idx
            break
    for item_idx in range(len(cg_items_list)):
        if not isinstance(cg_items_list[item_idx], ast.Decl):
            cg_decl_idx = item_idx
            break

    top_def.items = tuple(top_items_list[:top_decl_idx]+cg_items_list[:cg_decl_idx]+top_items_list[top_decl_idx:]+cg_items_list[cg_decl_idx:])

    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_module_ast)
    with open(root_path+"/"+module_name+".v",'w') as f:
        f.write(new_rtl)

def cg_inst_gen(inst_name, cgen):
    cg_list = []
    cg_list.append("module clk_gate(")
    cg_list.append("    input clk);")
    cg_list.append("wire        ap_clk_cg;")
    cg_list.append("wire        cgen;")
    cg_list.append("assign      cgen = "+cgen+";\n")
    cg_list.append("(* dont_touch = \"yes\" *)")
    cg_list.append("BUFGCE "+inst_name+"_bufgce(")
    cg_list.append("    .I        (ap_clk),")
    cg_list.append("    .O        (ap_clk_cg),")
    cg_list.append("    .CE       (cgen));")
    cg_list.append("endmodule")
    with open(inst_name+"_inst.v", "w") as f:
        for i in cg_list:
            f.write(i)
            f.write("\n")

def rpt_parser(module_name, rpt_root_path, pre_latency):
    # TODO: this should be input as device info
    power_table = {"BRAM_18K": 1, "DSP": 1, "FF": 1, "LUT" : 1, "URAM" : 1}
    rpt_path = rpt_root_path+"/"+module_name+"_csynth.rpt"

    with open(rpt_path, 'r') as file:
        lines = file.readlines()
    
    latency_flg = 0
    resrouce_type_flg = 0
    

    latency_head_pattern = r'\s*\|\s*Latency \(cycles\)\s*\|\s*Latency \(absolute\)\s*\|\s*Interval\s*\|\s*Pipeline\s*\|'
    resource_head_pattern = '== Utilization Estimates'
    for line in lines:
        if not latency_flg:
            match = re.match(latency_head_pattern, line)
            if match:
                latency_flg = 1
                latency_head_line = line
                latency_line_idx = lines.index(latency_head_line) + 3
                latency_line = lines[latency_line_idx].replace(" ", "").split("|")
                latency = latency_line[1]
        elif not resource_type_flg:
            match = re.match(resource_head_pattern, line)
            if match:
                resource_type_flg = 1
                resource_head_line = line
                resource_type_line_idx = lines.index(resource_head_line, line) + 4
                resource_type = lines[latency_line_idx].replace(" ", "").split("|")[2:]
        else:
            match = re.match("|Total", line)
            if match:
                resource_num = line.replace(" ", "").splie("|")[2:]
                break

    
        power = 0
        for resource_idx in range(len(resource_type)):
            power += power_table[resource_type[resource_idx]] * int(resource_num[resource_idx]) 
    
        if pre_latency==0:
            return latency, 0
        power_saved = power * (1- latency / pre_latency)
        
        return latency, power_saved

def cg_insert(module_name, root_path, rpt_root_path, cg_max_num, cg_max_level, top_module=1):

    module_list = [[], []]
    pi_flg = 0
    po_flg = 1
    cg_num = 0
    level_num = 0

    tmp_latency, tmp_power_saved = rpt_parser(module_name, rpt_root_path, 0)
    # name, latency, power_saved
    module_list[pi_flg].append([module_name, tmp_latency, tmp_power_saved])

    while 1:
        curr_module_list = module_list[pi_flg]
        nxt_module_list = module_list[po_flg]
        curr_module_num = len(curr_module_list)
        nxt_module_num = len(nxt_module_list)
        if curr_module_num==0 and nxt_module_num==0:
            break

        # sort
        curr_module_list.sort(key=lambda md : md[2])
        for _ in range(curr_module_num):
            curr_module = curr_module_list.pop(0)
            if os.path.exists(root_path+"/"+curr_module[0]+".v"):
                top_module_ast, _, cg_module_list, main_module_list, _, _, other_module_list, _, case_always_list, _, _, _ = read_file(curr_module, {}, root_path)

            # if there is not a clock gate
            # add a gate to this module
            if len(cg_module_list)==0:
                undf_flg = 0 # 1: this is a un-dataflow module with FSM
                if len(case_always_list)>0:
                    for case_always in case_always_list:
                        if case_always.statement.statements[0].comp.name=="ap_CS_fsm":
                            undf_flg = 1
                            cg_insert_single_module(module_name, top_module_ast, top_module, root_path)
                            cg_num += 1
                            break
            
            if cg_num==cg_max_num:
                return 

            for inst in main_module_list+other_module_list:
                tmp_latency, tmp_power_saved = rpt_parser(inst.module, rpt_root_path, curr_module[1])
                nxt_module_list.append([inst.module, tmp_latency, tmp_power_saved])
    
        cg_level += 1
        if cg_level==cg_max_level or cg_num==cg_max_num:
            return 
        tmp_flg = pi_flg
        pi_flg = po_flg
        po_flg = tmp_flg
        
#cg_insert("top_kernel3_x0", "../../all_ab/dut/solution1/impl/verilog/")
