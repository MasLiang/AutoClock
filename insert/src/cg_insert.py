from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as ast
import os
import copy
import re
<<<<<<< HEAD
import pdb
=======
import random
>>>>>>> 5a7057a (release vision 0.9)
from .rtl_parser import *

def determain_cgen(top_module_ast, undf_flg, top_flg):
    # cgen = !ap_idle | ap_reset
    idle_pattern = r'ap_idle'
    done_pattern = r'ap_done'
    if undf_flg:
        all_reg = DFS(top_module_ast, lambda node : isinstance(node, ast.Reg))
        state_idx_list = []
        block_state_pattern = r'ap_ST_fsm_state(\d+)_blk'
        ap_idle_flg = 0
        ap_done_flg = 0
        for reg in all_reg:
            match = re.search(block_state_pattern, reg.name)
            if match:
                state_idx_list.append(match.group(1))
            match = re.search(idle_pattern, reg.name)
            if match:
                ap_idle_flg = 1
            # ap_done_reg will be triggered by "continue" outside,  and at that time, the module is idld
            # So the clock should open for "ap_done_reg"
            match = re.search(done_pattern, reg.name)
            if match:
                ap_done_flg = 1

        cgen_n = ""
        if len(state_idx_list)>0:
            for state_idx in state_idx_list:
                if cgen_n=="":
                    cgen_n = "(ap_ST_fsm_state"+str(state_idx)+"_blk & ap_CS_fsm_state"+str(state_idx)+")"
                else:
                    cgen_n = cgen_n+" | (ap_ST_fsm_state"+str(state_idx)+"_blk & ap_CS_fsm_state"+str(state_idx)+")"
            
<<<<<<< HEAD
        if ap_idle_flg:
            #cgen = "!("+cgen_n+" | ap_idle)"
            cgen = "!ap_idle"
=======
        if ap_idle_flg: 
            if top_flg:
                if ap_done_flg:
                    cgen = "!ap_idle | ap_rst_n_inv | ap_done"
                else:
                    cgen = "!ap_idle | ap_rst_n_inv"
            else:
                if ap_done_flg:
                    cgen = "!ap_idle | ap_rst | ap_done"
                else:
                    cgen = "!ap_idle | ap_rst"
>>>>>>> 5a7057a (release vision 0.9)
        else:
            #cgen = "!("+cgen_n+")"
            cgen = ""
        return cgen
    else:
        ap_idle_flg = 0
        ap_done_flg = 0
        all_wire = DFS(top_module_ast, lambda node : isinstance(node, ast.Wire))
        for wire in all_wire:
            match = re.search(idle_pattern, wire.name)
            if match:
                ap_idle_flg = 1
            match = re.search(done_pattern, wire.name)
            if match:
                ap_done_flg = 1
        if ap_idle_flg==0 and ap_done_flg==0:
            all_output = DFS(top_module_ast, lambda node : isinstance(node, ast.Output))
            for outsig in all_output:
                if outsig.name=="ap_idle":
                    ap_idle_flg = 1
                if outsig.name=="ap_done":
                    ap_done_flg = 1

        if top_flg:
            if ap_idle_flg:
                if ap_done_flg:
                    return "!ap_idle | ap_rst_n_inv | ap_done"
                else:
                    return "!ap_idle | ap_rst_n_inv"
        else:
            if ap_idle_flg:
                if ap_done_flg:
                    return "!ap_idle | ap_rst | ap_done"
                else:
                    return "!ap_idle | ap_rst"

        all_output = DFS(top_module_ast, lambda node : isinstance(node, ast.Output))
        for outsig in all_output:
            if outsig.name=="ap_idle":
                if top_flg:
                    return "!ap_idle | ap_rst_n_inv"
                else:
                    return "!ap_idle | ap_rst"
        return "" 
    
<<<<<<< HEAD
def cg_insert_single_module(module_name, top_module_ast, top_module, root_path):
    cgen = determain_cgen(top_module_ast, 1)
=======
def cg_insert_single_module(module_name, top_module_ast, root_path, undf_flg, top_flg):
    cgen = determain_cgen(top_module_ast, undf_flg, top_flg)
>>>>>>> 5a7057a (release vision 0.9)
    if cgen=="":
        return 0

    all_always = DFS(top_module_ast, lambda node : isinstance(node, ast.Always))
    all_inst = DFS(top_module_ast, lambda node : isinstance(node, ast.Instance))

    for always in all_always:
        if isinstance(always.statement.statements[0], ast.IfStatement):
            if isinstance(always.statement.statements[0].true_statement.statements[0], ast.NonblockingSubstitution):
                if isinstance(always.statement.statements[0].true_statement.statements[0].left.var, ast.Identifier):
                    var = always.statement.statements[0].true_statement.statements[0].left.var.name
                    # bind to the fastest clock
                    # FSM will control the clock gate
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

    top_module_ast.show()
    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_module_ast)
    print(root_path+"/"+module_name+".v")
    with open(root_path+"/"+module_name+".v",'w') as f:
        f.write(new_rtl)
    return 1

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
    resource_type_flg = 0
    

    latency_head_pattern = r'\s*\|\s*Latency \(cycles\)\s*\|\s*Latency \(absolute\)\s*\|\s*Interval\s*\|\s*Pipeline\s*\|'
    resource_head_pattern = '== Utilization Estimates'
    for line_idx in range(len(lines)):
        if not latency_flg:
            match = re.match(latency_head_pattern, lines[line_idx])
            if match:
                latency_flg = 1
                latency_line_idx = line_idx + 3
                latency_line = lines[latency_line_idx].replace(" ", "").split("|")
<<<<<<< HEAD
                latency = int(latency_line[1])
=======
                if latency_line[1]=="?":
                    latency = 1
                else:
                    latency = int(latency_line[1])
>>>>>>> 5a7057a (release vision 0.9)
        elif not resource_type_flg:
            match = re.match(resource_head_pattern, lines[line_idx])
            if match:
                resource_type_flg = 1
                resource_type_line_idx =  line_idx + 4
                resource_type = lines[resource_type_line_idx].replace(" ", "").split("|")[2:-1]
        else:
            match = re.match(r"\s*\|Total\s*", lines[line_idx])
            if match:
                resource_num = lines[line_idx].replace(" ", "").split("|")[2:-1]
                break

    
    power = 0
    for resource_idx in range(len(resource_type)):
        power += power_table[resource_type[resource_idx]] * int(resource_num[resource_idx]) 
    
    if pre_latency==0:
        return latency, 0
    power_saved = power * (1- latency / pre_latency)
    
    return latency, power_saved

<<<<<<< HEAD
def cg_insert(module_name, root_path, rpt_root_path, cg_max_num, cg_max_level, top_module=1):
=======
def cg_insert(module_name, root_path, rpt_root_path, cg_max_num, cg_max_level):
>>>>>>> 5a7057a (release vision 0.9)

    module_list = [[], []]
    pi_flg = 0
    po_flg = 1
    cg_num = 0
    cg_level = 0
    top_module_name_len = len(module_name)

    tmp_latency, tmp_power_saved = rpt_parser(module_name, rpt_root_path, 0)
    # name, latency, power_saved
    module_list[pi_flg].append([module_name, tmp_latency, tmp_power_saved])
<<<<<<< HEAD

    while 1:
        pdb.set_trace()
=======
    top_flg = 1

    while 1:
>>>>>>> 5a7057a (release vision 0.9)
        curr_module_list = module_list[pi_flg]
        nxt_module_list = module_list[po_flg]
        print(curr_module_list)
        print(nxt_module_list)
        curr_module_num = len(curr_module_list)
        nxt_module_num = len(nxt_module_list)
        if curr_module_num==0 and nxt_module_num==0:
            break

        # sort
        curr_module_list.sort(key=lambda md : md[2])
        for _ in range(curr_module_num):
            curr_module = curr_module_list.pop(0)
            print(curr_module[0])
            if not os.path.exists(root_path+"/"+curr_module[0]+".v"):
                continue
            top_module_ast, _, cg_module_list, main_module_list, _, _, other_module_list, _, case_always_list, _, _, _ = read_file(curr_module[0], {}, root_path)

            # if there is not a clock gate
            # add a gate to this module
            if len(cg_module_list)==0:
                if len(case_always_list)>0:
                    for case_always in case_always_list:
                        if case_always.statement.statements[0].comp.name=="ap_CS_fsm":
<<<<<<< HEAD
                            cg_insert_result = cg_insert_single_module(curr_module[0], top_module_ast, top_module, root_path)
                            cg_num += cg_insert_result
                            break
=======
                            cg_insert_result = cg_insert_single_module(curr_module[0], top_module_ast, root_path, 1, top_flg)
                            cg_num += cg_insert_result
                            break
                else:
                    cg_insert_result = cg_insert_single_module(curr_module[0], top_module_ast, root_path, 0, top_flg)
                    cg_num += cg_insert_result
                    
>>>>>>> 5a7057a (release vision 0.9)
            
            if cg_num==cg_max_num:
                return 

            for inst in main_module_list+other_module_list:
                nxt_module_name = inst.module[top_module_name_len+1:]
                if not os.path.exists(rpt_root_path+"/"+nxt_module_name+"_csynth.rpt"):
                    continue
                tmp_latency, tmp_power_saved = rpt_parser(nxt_module_name, rpt_root_path, curr_module[1])
                nxt_module_list.append([inst.module, tmp_latency, tmp_power_saved])
    
        cg_level += 1
        if cg_level==cg_max_level or cg_num==cg_max_num:
            return 
        tmp_flg = pi_flg
        pi_flg = po_flg
        po_flg = tmp_flg
<<<<<<< HEAD
        
=======
        if top_flg==1:
            top_flg = 0
        

def cg_insert_random(root_path, cg_max_num, top_name):
    files = [f for f in os.listdir(root_path) if os.path.isfile(os.path.join(root_path, f))]
    cg_num = 0
    while 1:
        file = random.sample(files, 1)
        if file[0][-2:]!=".v":
            continue
        if file[0][:-2]==top_name:
            top_flg = 1
        else:
            top_flg = 0
        top_module_ast, _, cg_module_list, main_module_list, _, _, other_module_list, _, case_always_list, _, _, _ = read_file(file[0][:-2], {}, root_path)
        if len(cg_module_list)==0:
            if len(case_always_list)>0:
                for case_always in case_always_list:
                    if case_always.statement.statements[0].comp.name=="ap_CS_fsm":
                        cg_insert_result = cg_insert_single_module(file[0][:-2], top_module_ast, root_path, 1, top_flg)
                        cg_num += cg_insert_result
                        break
            else:
                cg_insert_result = cg_insert_single_module(file[0][:-2], top_module_ast, root_path, 0, top_flg)
                cg_num += cg_insert_result
        if cg_num==cg_max_num:
            break
    
>>>>>>> 5a7057a (release vision 0.9)
#cg_insert("top_kernel3_x0", "../../all_ab/dut/solution1/impl/verilog/")
