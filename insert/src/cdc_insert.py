from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import sys
sys.path.append("../../")
from cdc.src.template.async_dpram import *
from cdc.src.template.async_fifo import *
from cdc.src.template.async_pulse import *
from cdc.src.template.async_level import *
from .rtl_parser import *
import pyverilog.vparser.ast as ast
import os
import copy
import re
import math

   
def modify_only_module_clk(inst, clk_domain):
    for portarg in inst.portlist:
        if isinstance(portarg.argname, ast.Identifier):
            if portarg.argname.name=="ap_clk":
                portarg.argname.name = clk_domain
            elif portarg.argname.name=="ap_rst_n_inv":
                portarg.argname.name = "rst_"+clk_domain
  
    
def modify_fifo_clk(inst, main_module_list, module_map):
    # this function is used to determain the clock domain of rd/wr port
    for portarg in inst.portlist:
        if portarg.portname=="if_write":
            sig_wr = portarg.argname
        elif portarg.portname=="if_read":
            sig_rd = portarg.argname
    
    for module in main_module_list:
        for portarg in module.portlist:
            if isinstance(portarg.argname, ast.Identifier):
                if portarg.argname==sig_wr:
                    wr_clk = module_map[module.module]
                elif portarg.argname==sig_rd:
                    rd_clk = module_map[module.module]

    if wr_clk==rd_clk:
        modify_only_module_clk(inst, wr_clk)
    else:
        fifo_name = inst.module
        match = re.search(r'(\w+)_w(\d+)_d(\d+)_A(\w*)', fifo_name)
        if match:
            fifo_width = int(match.group(2))
            fifo_depth = int(match.group(3))
            async_fifo_factor = ["block", fifo_depth, fifo_depth, fifo_width, fifo_width]
        else:
            match = re.search(r'(\w+)_w(\d+)_d(\d+)_S(\w*)', fifo_name)
            fifo_width = int(match.group(2))
            fifo_depth = int(match.group(3))
            async_fifo_factor = ["distributed", fifo_depth, fifo_depth, fifo_width, fifo_width]
        gen_async_fifo_file(fifo_name, async_fifo_factor)
        for portarg in inst.portlist:
            if portarg.portname=="clk":
                portarg.argname.name = wr_clk
                portarg.portname = "if_wr_clk"
                temp_portarg = copy.deepcopy(portarg)
                temp_portarg.argname.name = rd_clk
                temp_portarg.portname = "if_rd_clk"
                port_list = list(inst.portlist)
                port_list.append(temp_portarg)
                inst.portlist = tuple(port_list)
            elif portarg.portname=="reset":
                portarg.argname.name = "rst_"+wr_clk

def modify_submodule_fifo_clk(inst, inst_list):
    # this function is used to determain the clock domain of rd/wr port
    for portarg in inst.portlist:
        if portarg.portname=="if_write":
            sig_wr = portarg.argname
        elif portarg.portname=="if_read":
            sig_rd = portarg.argname
    
    _, _, module = connect_to_module(sig_wr, inst_list)
    if is_ddr_controller(module):
        wr_clk = "axi_clk"
    else:
        wr_clk = "ap_clk"
    
    _, _, module = connect_to_module(sig_rd, inst_list)
    if is_ddr_controller(module):
        rd_clk = "axi_clk"
    else:
        rd_clk = "ap_clk"

    if wr_clk==rd_clk:

        modify_only_module_clk(inst, wr_clk)
    else:
        fifo_name = inst.module
        match = re.search(r'(\w+)_w(\d+)_d(\d+)_A(\w*)', fifo_name)
        if match:
            fifo_width = int(match.group(2))
            fifo_depth = int(match.group(3))
            async_fifo_factor = ["block", fifo_depth, fifo_depth, fifo_width, fifo_width]
        else:
            match = re.search(r'(\w+)_w(\d+)_d(\d+)_S(\w*)', fifo_name)
            fifo_width = int(match.group(2))
            fifo_depth = int(match.group(3))
            async_fifo_factor = ["distributed", fifo_depth, fifo_depth, fifo_width, fifo_width]
        gen_async_fifo_file(fifo_name, async_fifo_factor)
        for portarg in inst.portlist:
            if portarg.portname=="clk":
                portarg.argname.name = wr_clk
                portarg.portname = "if_wr_clk"
                temp_portarg = copy.deepcopy(portarg)
                temp_portarg.argname.name = rd_clk
                temp_portarg.portname = "if_rd_clk"
                port_list = list(inst.portlist)
                port_list.append(temp_portarg)
                inst.portlist = tuple(port_list)
            elif portarg.portname=="reset":
                portarg.argname.name = "rst_"+wr_clk

def find_mux_in(sig, mux_always_list):
    mux_input = []
    for always in mux_always_list:
        if always.statement.statements[0].true_statement.statements[0].left.var==sig:
            for states in always.statement.statements:
                var = states.true_statement.statements[0].right.var
                if isinstance(var, ast.IntConst) and (var.value!="'bx" or var.value!="1'b0"):
                    continue
                mux_input.append(var)
                while (isinstance(states.false_statement, ast.IfStatement)):
                    states = states.false_statement
                    var = states.true_statement.statements[0].right.var
                    if isinstance(var, ast.IntConst) and (var.value!="'bx" or var.value!="1'b0"):
                        continue
                    mux_input.append(var)
                var = states.false_statement.statements[0].right.var
                if isinstance(var, ast.IntConst) and (var.value!="'bx" or var.value!="1'b0"):
                    continue
                mux_input.append(var)
            break

    return mux_input, always

def find_mux_out(sig, mux_always_list):
    mux_output = []
    for always in mux_always_list:
        if always.statement.statements[0].true_statement.statements[0].right.var==sig:
            for states in always.statement.statements:
                var = states.true_statement.statements[0].left.var
                mux_output.append(var)
                while (isinstance(states.false_statement, ast.IfStatement)):
                    states = states.false_statement
                    var = states.true_statement.statements[0].right.var
                    mux_output.append(var)
                var = states.false_statement.statements[0].right.var
                mux_output.append(var)
            break

    return mux_output, always

                   
def extrace_always_naming_rule(always, naming_rules, clk_domain, direction):
    # find not needed true_statement of a statement, using the false_statement to replace 
    #  the statement
    temp_always = copy.deepcopy(always)
    mux_in = []
    for states_idx in range(len(always.statement.statements)):
        states = always.statement.statements[states_idx]
        temp_states = temp_always.statement.statements[states_idx]
        while(True):
            if direction=="in":
                var = states.true_statement.statements[0].right.var
            elif direction=="out":
                var = states.true_statement.statements[0].left.var
            for naming_rule in naming_rules:
                name_match = re.search(naming_rule, var.name)
                if name_match:
                    break
            if name_match:
                temp_states.true_statement.statements[0].left.var.name += "_"+clk_domain
                mux_in.append(var.name)
                if isinstance(states.false_statement, ast.IfStatement):
                    states = states.false_statement
                    parent_states = temp_states
                    temp_states = temp_states.false_statement
                else:
                    temp_states.false_statement.statements[0].left.var.name += "_"+clk_domain
                    break
            else:
                if isinstance(states.false_statement, ast.IfStatement):
                    states = states.false_statement
                    temp_states.cond = temp_states.false_statement.cond
                    temp_states.true_statement = temp_states.false_statement.true_statement
                    temp_states.false_statement = temp_states.false_statement.false_statement
                else:
                    temp_states.false_statement.statements[0].left.var.name += "_"+clk_domain
                    parent_states.false_statement = temp_states.false_statement
                    break
    return temp_always, mux_in
    
def extrace_always_full_name(always, full_name, clk_domain):
    # find not needed true_statement of a statement, using the false_statement to replace 
    #  the statement
    temp_always = copy.deepcopy(always)
    for states_idx in range(len(always.statement.statements)):
        states = always.statement.statements[states_idx]
        temp_states = temp_always.statement.statements[states_idx]
        while(True):
            var = states.true_statement.statements[0].right.var
            if var.name in full_name:
                temp_states.true_statement.statements[0].left.var.name += "_"+clk_domain
                if isinstance(states.false_statement, ast.IfStatement):
                    states = states.false_statement
                    parent_states = temp_states
                    temp_states = temp_states.false_statement
                else:
                    temp_states.false_statement.statements[0].left.var.name += "_"+clk_domain
                    break
            else:
                if isinstance(states.false_statement, ast.IfStatement):
                    states = states.false_statement
                    temp_states.cond = temp_states.false_statement.cond
                    temp_states.true_statement = temp_states.false_statement.true_statement
                    temp_states.false_statement = temp_states.false_statement.false_statement
                else:
                    parent_states.false_statement = temp_states.false_statement
                    temp_states.false_statement.statements[0].left.var.name += "_"+clk_domain
                    break
    return temp_always

def connect_to_module(sig, main_module_list):
    for module in main_module_list:
        for portarg in module.portlist:
            if isinstance(sig, ast.Identifier):
                if portarg.argname==sig:
                    return True, portarg, module
            elif isinstance(portarg.argname, ast.IntConst):
                continue
            else:
                if portarg.argname.name==sig:
                    return True, portarg, module

    return False,'',''
       
def find_reg_wire_def(var_name, def_list):
    for item in def_list:
        if item.list[0].name==var_name:
            return item

def modify_bram_clk(top_module_ast, inst, main_module_list, module_map, mux_always_list):
    # extrace ports
    sig_ce0 = ''
    sig_we0 = ''
    sig_address0 = ''
    sig_d0 = ''
    sig_q0 = ''
    sig_ce1 = ''
    sig_we1 = ''
    sig_address1 = ''
    sig_d1 = ''
    sig_q1 = ''
    
    for portarg in inst.portlist:
        if portarg.portname=="ce0":
            sig_ce0 = portarg.argname
        elif portarg.portname=="we0":
            sig_we0 = portarg.argname
        elif portarg.portname=="address0":
            sig_address0 = portarg.argname
        elif portarg.portname=="d0":
            sig_d0 = portarg.argname
        elif portarg.portname=="q0":
            sig_q0 = portarg.argname
        elif portarg.portname=="ce1":
            sig_ce1 = portarg.argname
        elif portarg.portname=="we1":
            sig_we1 = portarg.argname
        elif portarg.portname=="address1":
            sig_address1 = portarg.argname
        elif portarg.portname=="d1":
            sig_d1 = portarg.argname
        elif portarg.portname=="q1":
            sig_q1 = portarg.argname
    
    # number of ports
    num_ports = (sig_ce0!='')+(sig_ce1!='')
    port_list = [[sig_ce0, sig_we0, sig_address0, sig_d0, sig_q0]]
    if num_ports==2:
        port_list.append([sig_ce1, sig_we1, sig_address1, sig_d1, sig_q1])
    
    # check connections of ce
    
    for port in port_list:
        # check which module port connect directly, this port should nor be touched
        flag, portarg, _ = connect_to_module(port[0], main_module_list)
        if flag:
            port.append("bypass")
            port.append([])
            port.append([portarg.argname]) # it means there is no mux
            port.append(module_map[module.module])
        # check the mux
        if len(port)<9:
            ce_mux_inputs, ce_mux_always = find_mux_in(port[0], mux_always_list)
            port.append("mux")
            port.append(ce_mux_always)
            port.append(ce_mux_inputs)
            port.append([]) # it means connect to mux currently. later it will be filled in
    
    # analyze connections, if a mux connects to multiple clock domain, it will be
    # divided to two ports
    new_port_list_ce = []
    rm_ram_mux = set()
    rm_reg_def = []
    add_reg_def = []
    for port in port_list:
        # connect to module directly, no need to change
        if port[5]=="bypass":
            port[0] = port[0].name
            #port[0] = port[0].name+"_"+port[8]
            #new_port_list_ce.append(port)
            continue
        # connect to mux, but only a data gate
        if len(port[7])==1:
            flag, _, module = connect_to_module(port[7][0], main_module_list)
            port[8] = module
            if flag:
                port[8] = module_map[module.module]
            port[7] = [port[7][0].name]
            decl_reg = find_reg_wire_def(port[0].name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
            port[0] = port[0].name+"_"+port[8]
            decl_reg_add = copy.deepcopy(decl_reg)
            decl_reg_add.list[0].name = port[0]
            add_reg_def.append(decl_reg_add)
            new_port_list_ce.append(port)
            ce_mux_always = port[6]
            rm_ram_mux.add(ce_mux_always)
            decl_reg_name = ce_mux_always.statement.statements[0].true_statement.statements[0].left.var.name
            decl_reg = find_reg_wire_def(decl_reg_name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
            rm_reg_def.append(decl_reg)
            new_ce_mux_always =  copy.deepcopy(ce_mux_always)
            new_ce_mux_always.statement.statements[0].true_statement.statements[0].left.var.name = port[0]
            new_ce_mux_always.statement.statements[0].false_statement.statements[0].left.var.name = port[0]
            port[6] = new_ce_mux_always
            continue
        # find modules connected to the mux input
        clk_dic = {}
        for ce_mux_input in port[7]:
            flag, _, module = connect_to_module(ce_mux_input, main_module_list)
            if flag:
                clk_domain = module_map[module.module]
                if clk_domain in list(clk_dic.keys()):
                    clk_dic[clk_domain].append(ce_mux_input.name)
                else:
                    clk_dic[clk_domain] = [ce_mux_input.name]
        # all from the same clk domain, no need to change 
        # TODO need to verify
        if len(list(clk_dic.keys()))==1:
            continue
        # extract the ce always mux
        ce_mux_always = port[6]
        rm_ram_mux.add(ce_mux_always)
        decl_reg_name = ce_mux_always.statement.statements[0].true_statement.statements[0].left.var.name
        decl_reg = find_reg_wire_def(decl_reg_name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
        rm_reg_def.append(decl_reg)
        for clk_domain in list(clk_dic.keys()):
            ce_signals = clk_dic[clk_domain]
            temp_ce_always = extrace_always_full_name(ce_mux_always, ce_signals, clk_domain)
            temp_port = port[0:6]+[temp_ce_always, ce_signals, clk_domain]
            decl_reg = find_reg_wire_def(temp_port[0].name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
            temp_port[0] = temp_port[0].name+"_"+clk_domain
            decl_reg_add = copy.deepcopy(decl_reg)
            decl_reg_add.list[0].name = temp_port[0]
            add_reg_def.append(decl_reg_add)
            new_port_list_ce.append(temp_port)

    # analyze other ports
    wr_port_list = [] 
    w_port_list = [] 
    r_port_list = [] 
    for port in new_port_list_ce:
        clk_domain = port[8]
        port = port[0:8]
        naming_rules = []
        # using naming rule to match other ports
        for ce_sig in port[7]:
            _, portarg, _ = connect_to_module(ce_sig, main_module_list)
            ce_pattern = f'(\w+)_(\w+)(\d+)'
            ce_match = re.search(ce_pattern, portarg.portname)
            naming_rules.append(rf'{ce_match.group(1)}_(\w+){ce_match.group(3)}')
        for sig_idx in range(1,5):
            # there is not a signal of this port
            if port[sig_idx]=='':
                temp_sig_type = "none"
                temp_sig_always = []
                temp_sig_mux_in = []
                port.append(temp_sig_type)
                port.append(temp_sig_always)
                port.append(temp_sig_mux_in)
                continue

            sig = port[sig_idx].name
            # must connect to a module directly
            flag, portarg, _ = connect_to_module(port[sig_idx], main_module_list)
            if flag:
                for naming_rule in naming_rules:
                    sig_match = re.search(naming_rule, portarg.portname)
                    if sig_match:
                        break
                if sig_match:
                    port[sig_idx] = sig
                    temp_sig_type = "bypass"
                    temp_sig_mux_in = []
                    temp_sig_always = []
                # can not find a signals because of clock domain
                else:
                    port[sig_idx] = ''
                    temp_sig_type = "none"
                    temp_sig_mux_in = []
                    temp_sig_always = []
                port.append(temp_sig_type)
                port.append(temp_sig_always)
                port.append(temp_sig_mux_in)
            # connect to a mux
            else:
                # 4 is output of the bram, others are input
                if sig_idx==4:
                    sig_mux_out, sig_mux_always = find_mux_out(port[sig_idx], mux_always_list)
                    rm_ram_mux.add(sig_mux_always)
                    decl_reg_name = sig_mux_always.statement.statements[0].true_statement.statements[0].left.var.name
                    decl_reg = find_reg_wire_def(decl_reg_name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
                    rm_reg_def.append(decl_reg)
                    temp_sig_always, temp_sig_mux_in = extrace_always_naming_rule(sig_mux_always, naming_rules, clk_domain, "out")
                    port.append(temp_sig_type)
                    port.append(temp_sig_always)
                    port.append(temp_sig_mux_out)
                    decl_reg = find_reg_wire_def(port[sig_idx].name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
                    port[sig_idx]=port[sig_idx].name+"_"+clk_domain
                    decl_reg_add = copy.deepcopy(decl_reg)
                    decl_reg_add.list[0].name = port[sig_idx]
                    add_reg_def.append(decl_reg_add)
                else:
                    sig_mux_in, sig_mux_always = find_mux_in(port[sig_idx], mux_always_list)
                    rm_ram_mux.add(sig_mux_always)
                    decl_reg_name = sig_mux_always.statement.statements[0].true_statement.statements[0].left.var.name
                    decl_reg = find_reg_wire_def(decl_reg_name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
                    rm_reg_def.append(decl_reg)
                    # this is a data gate
                    if len(sig_mux_in)==1:
                        for naming_rule in naming_rules:
                            sig_match = re.search(naming_rule, sig_mux_in[0].name)
                            if sig_match:
                                temp_sig_type = "mux"
                                temp_sig_always = copy.deepcopy(sig_mux_always)
                                temp_sig_always.statement.statements[0].true_statement.statements[0].left.var.name  += "_"+clk_domain
                                temp_sig_always.statement.statements[0].false_statement.statements[0].left.var.name += "_"+clk_domain
                                temp_sig_mux_in = sig_mux_in[0].name
                                decl_reg = find_reg_wire_def(port[sig_idx].name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
                                port[sig_idx] = port[sig_idx].name+"_"+clk_domain
                                decl_reg_add = copy.deepcopy(decl_reg)
                                decl_reg_add.list[0].name = port[sig_idx]
                                add_reg_def.append(decl_reg_add)
                                break
                        if not sig_match:
                            temp_sig_type = "none"
                            temp_sig_always = []
                            temp_sig_mux_in = []
                            port[sig_idx] = ""
                    # this is a real mux
                    else:
                        temp_sig_type = "mux"
                        temp_sig_always, temp_sig_mux_in = extrace_always_naming_rule(sig_mux_always, naming_rules, clk_domain, "in")
                        decl_reg = find_reg_wire_def(port[sig_idx].name, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
                        port[sig_idx]=port[sig_idx].name+"_"+clk_domain
                        decl_reg_add = copy.deepcopy(decl_reg)
                        decl_reg_add.list[0].name = port[sig_idx]
                        add_reg_def.append(decl_reg_add)
                    port.append(temp_sig_type)
                    port.append(temp_sig_always)
                    port.append(temp_sig_mux_in)
        port.append(clk_domain)
        if port[1]!='' and port[4]!='':
            wr_port_list.append(port)
        elif port[1]!='':
            w_port_list.append(port)
        else:
            r_port_list.append(port)
    
    # TODO merge a w port and a r port from the same clock domain. Can it?
    
    # build bram instance for each port
    num_w = len(w_port_list)
    num_r = len(r_port_list)
    num_wr = len(wr_port_list)
    num_new_inst = (num_w+num_wr)*(num_r+num_wr)

    for param in inst.parameterlist:
        if param.paramname=="DataWidth":
            data_width = int(param.argname.value)
        elif param.paramname=="AddressWidth":
            address_width = int(param.argname.value)
        elif param.paramname=="AddressRange":
            address_range = int(param.argname.value)
            
    # TODO can only deal with 1wNr condition.
    factors = [data_width, address_width, address_range]    
    add_ram_inst = []
    inst_idx = 0
    for port0 in w_port_list:
        for port1 in r_port_list + wr_port_list:
            port_dic = {}
            port_dic["w"] = port0[0:5]+[port0[-1]]+["rst_"+port0[-1]]
            port_dic["r"] = port1[0:5]+[port1[-1]]+["rst_"+port1[-1]]
            gen_async_bram_inst(inst.module+"_"+port0[-1]+"_"+port1[-1]+"_"+str(inst_idx), 
                                inst.name+"_"+port0[-1]+"_"+port1[-1]+"_"+str(inst_idx),  
                                port_dic, factors)
            new_ram_ast, _ = rtl_parse(["./"+inst.module+"_"+port0[-1]+"_"+port1[-1]+"_"+str(inst_idx)+"_inst.v"])
            os.system("rm ./"+inst.module+"_"+port0[-1]+"_"+port1[-1]+"_"+str(inst_idx)+"_inst.v")
            new_instances = DFS(new_ram_ast, lambda node : isinstance(node, ast.Instance))
            for new_inst in new_instances:
                break # only one inst in this file
            add_ram_inst.append(new_inst)
            inst_idx += 1

    add_ram_mux = []
    for port in w_port_list+r_port_list+wr_port_list:
        if port[6]!=[]:
            add_ram_mux.append(port[6])
        if port[9]!=[]:
            add_ram_mux.append(port[9])
        if port[12]!=[]:
            add_ram_mux.append(port[12])
        
    return add_ram_inst, add_ram_mux, list(rm_ram_mux), list(set(add_reg_def)), list(set(rm_reg_def))
    
def main_axi_module_process(module_name, root_path):
    file_path = root_path+"/"+module_name+".v"
    top_module_ast, directives = rtl_parse([file_path])
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        # there is only one module
        break
    item_list = list(module_def.items)
    
    # add a "input axi_clk;"
    # add a "input axi_rst;"
    for item_idx in range(len(item_list)):
        if isinstance(item_list[item_idx], ast.Decl):
            if isinstance(item_list[item_idx].list[0], ast.Input):
                if item_list[item_idx].list[0].name=="ap_clk":
                    break
    
    temp_clk = copy.deepcopy(item_list[item_idx])
    temp_clk.list[0].name = "axi_clk"
    item_list = item_list[0:item_idx]+[temp_clk]+item_list[item_idx:]
    temp_rst = copy.deepcopy(item_list[item_idx])
    temp_rst.list[0].name = "axi_rst"
    item_list = item_list[0:item_idx]+[temp_rst]+item_list[item_idx:]

    module_def.items = tuple(item_list)

    # add a ".axi_clk,"
    # add a ".axi_rst,"
    port_list = list(module_def.portlist.ports)

    for portarg_idx in range(len(port_list)):
        if port_list[portarg_idx].name=="ap_clk":
            break
    
    temp_clk_port = copy.deepcopy(port_list[portarg_idx])
    temp_clk_port.name = "axi_clk"
    port_list = port_list[0:portarg_idx]+[temp_clk_port]+port_list[portarg_idx:]
    temp_rst_port = copy.deepcopy(port_list[portarg_idx])
    temp_rst_port.name = "axi_rst"
    port_list = port_list[0:portarg_idx]+[temp_rst_port]+port_list[portarg_idx:]

    module_def.portlist.ports = tuple(port_list)

    all_instances = DFS(top_module_ast, lambda node :  isinstance(node, ast.Instance))
    inst_list = [inst for inst in all_instances]

    end_flg = 0
    for inst in inst_list:
        if is_ddr_controller(inst):
            end_flg = 1
            for portarg in inst.portlist:
                if portarg.portname == "ap_clk":
                    portarg.portname = "axi_clk"
            break
        elif is_main_axi_module(inst):
            sub_axi_module_clk_bind(inst, root_path)

    if end_flg==1:
        for inst in inst_list:
            if is_fifo_inst(inst):
                modify_submodule_fifo_clk(inst, inst_list)

    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_module_ast)
    with open(module_name+".v", "w") as f:
        f.write(new_rtl)
 
def sub_axi_module_clk_bind(inst, root_path):
    for portarg in inst.portlist:
        if isinstance(portarg.argname, ast.Identifier):
            if portarg.argname.name=="axi_clk":
                portarg.argname.name = clk_domain
            elif portarg.argname.name=="ap_rst":
                portarg.argname.name = "axi_rst"
 
   

def main_axi_module_clk_bind(inst, clk_domain, root_path):
    for portarg in inst.portlist:
        if isinstance(portarg.argname, ast.Identifier):
            if portarg.argname.name=="ap_clk":
                portarg.argname.name = clk_domain
                temp_portarg = copy.deepcopy(portarg)
                temp_portarg.argname.name = "ap_clk"
                temp_portarg.portname = "axi_clk"
                port_list = list(inst.portlist)
                port_list.append(temp_portarg)
                inst.portlist = tuple(port_list)
            elif portarg.argname.name=="ap_rst_n_inv":
                portarg.argname.name = "rst_"+clk_domain
                temp_portarg = copy.deepcopy(portarg)
                temp_portarg.argname.name = "ap_rst_n_inv"
                temp_portarg.portname = "axi_rst"
                port_list = list(inst.portlist)
                port_list.append(temp_portarg)
                inst.portlist = tuple(port_list)

    main_axi_module_process(inst.module, root_path)
 
def axi_module_clk_bind(axi_module_list, clk_domain):
    for axi_inst in axi_module_list:
        modify_only_module_clk(axi_inst, clk_domain)

def main_module_clk_bind(main_module_list, module_map, root_path):
    for main_inst in main_module_list:
        if is_ddr_controller(main_inst):
            # TODO, assert that user's config is wrong. It should be in ap_clk domain
            continue
        if is_main_axi_module(main_inst):
            main_axi_module_clk_bind(main_inst, module_map[main_inst.module], root_path)
        else:
            modify_only_module_clk(main_inst, module_map[main_inst.module])

def fifo_module_clk_bind(fifo_module_list, main_module_list, module_map):
    for fifo_inst in fifo_module_list:
        modify_fifo_clk(fifo_inst, main_module_list, module_map)

def ram_module_clk_bind(top_module_ast, ram_module_list, main_module_list, module_map, mux_always_list):
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)

    add_ram_inst_all = []
    add_ram_mux_all = []
    rm_ram_mux_all = []
    rm_instlist_all = []
    rm_reg_def_all = []
    add_reg_def_all = []
    for ram_inst in ram_module_list:
        add_ram_inst, add_ram_mux, rm_ram_mux, add_reg_def, rm_reg_def = modify_bram_clk(top_module_ast, ram_inst, main_module_list, module_map, mux_always_list)
        add_ram_inst_all += add_ram_inst
        add_ram_mux_all += add_ram_mux
        rm_ram_mux_all += rm_ram_mux
        rm_reg_def_all += rm_reg_def
        add_reg_def_all += add_reg_def

    for item in item_list:
        if isinstance(item, ast.InstanceList):
            for rm_item in ram_module_list:
                if item.instances[0]==rm_item:
                    rm_instlist_all.append(item)
                    break

    for rm_mux in rm_ram_mux_all:
        item_list.remove(rm_mux)
        
    for rm_reg in rm_reg_def_all:
        item_list.remove(rm_reg)
    
    for rm_item in rm_instlist_all:
        item_list.remove(rm_item)
            
    for add_instance in add_ram_inst_all:
        add_instance_list = ast.InstanceList(add_instance.module, add_instance.parameterlist, [add_instance])
        item_list.append(add_instance_list)

    # when adding mux, those new signals need to be added
    item_list += add_ram_mux_all

    start_reg_def = 0
    for item_idx in range(len(item_list)):
        if start_reg_def==0:
            if isinstance(item_list[item_idx], ast.Decl):
                if isinstance(item_list[item_idx].list[0], ast.Reg):
                    start_reg_def = 1
        else:
            if isinstance(item_list[item_idx], ast.Decl) or isinstance(item_list[item_idx], ast.Pragma):
                continue
            break
    item_list = item_list[0:item_idx]+add_reg_def_all+item_list[item_idx:]

    module_def.items = tuple(item_list)
    
def org_rst_rm(top_module_ast):
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)

    rm_list = []
    for item in item_list:
        if isinstance(item, ast.Always):
            if isinstance(item.statement.statements[0], ast.NonblockingSubstitution):
                if "ap_rst" in item.statement.statements[0].left.var.name:
                    rm_list.append(item)
    for rm_always in rm_list:
        item_list.remove(rm_always)
    
    module_def.items = tuple(item_list)

def gen_cnt(state_name, cnt_value, fastest_clk):
    '''
    always @(posedge clk) begin
        if(rst==1'b1)
            state_cnt <= 1'b0;
        else if(state==1 & state_cnt!=max)
            state_cnt <= state_cnt +1;
        else
            state_cnt <= 1'b0;
    end
    '''
    bit_width = math.ceil(math.log2(cnt_value-1))
    cnt_name = state_name+"_cnt"
    new_decl = ast.Reg(cnt_name, ast.Width(ast.IntConst("0"), ast.IntConst(str(bit_width))))
    new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier(fastest_clk))]),
                            ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("rst_"+fastest_clk), 
                                                              ast.IntConst("1'b1")),
                                                       ast.Block([ast.NonblockingSubstitution(ast.Identifier(cnt_name), 
                                                                                              ast.IntConst("1'b0"))]),
                                                       ast.Block([ast.IfStatement(ast.And(ast.Eq(ast.Identifier(state_name), 
                                                                                                 ast.IntConst("1'b1")),
                                                                                          ast.NotEq(ast.Identifier(cnt_name), 
                                                                                                    ast.IntConst(str(cnt_value-1)))),
                                                                                  ast.Block([ast.NonblockingSubstitution(ast.Identifier(cnt_name), 
                                                                                                                         ast.Plus(ast.Identifier(cnt_name),
                                                                                                                                  ast.IntConst("1'b1")))]),
                                                                                  ast.Block([ast.NonblockingSubstitution(ast.Identifier(cnt_name),
                                                                                                                         ast.IntConst("1'b1"))]))]))]))
    return new_decl, new_always
    

def rm_initial_sig(top_module_ast, sig):
    ini_blks = DFS(top_module_ast, lambda node: isinstance(node, ast.Initial))
    for ini_blk in ini_blks:
        break # only one initial block
    
    new_statements = []
    for item in list(ini_blk.statement.statements):
        if item.left.var.name == sig.list[0].name:
            continue
        new_statements.append(item)
    ini_blk.statement.statements = tuple(new_statements)    
    

def fsm_clk_bind(top_module_ast, assign_list, pose_always_list, mux_always_list, case_always_list, main_module_list, fastest_clk_map, module_map):
    fastest_clk = fastest_clk_map[0]
    # sync ready and done signals 
    rm_sig = []
    rm_always = []
    mdfy_always = []
    rm_assign = []
    rm_decl = []
    add_async_inst = []
    add_assign = []
    add_decl = []
    add_always = []
    for assign in assign_list:
        match_sync = re.search(r'ap_sync_(\w+)', assign.left.var.name)
        if match_sync:
            in_sig = match_sync.group(1)
            _, _, module = connect_to_module(in_sig, main_module_list)
            in_clk = module_map[module.module]
            if in_clk==fastest_clk:
                mdfy_always.append("ap_sync_reg_"+match_sync.group(1))
                continue
            out_sig = assign.left.var.name
            out_clk = fastest_clk 
            if "ap_done" in in_sig:
                gen_async_level_inst("async_inst_"+in_sig, in_sig, in_clk, out_sig, out_clk)
            else:
                gen_async_pulse_inst("async_inst_"+in_sig, in_sig, in_clk, out_sig, out_clk)
            async_inst_ast, _ = rtl_parse(["./async_inst_"+in_sig+"_inst.v"])
            os.system("rm async_inst_"+in_sig+"_inst.v")
            new_instance_list = DFS(async_inst_ast, lambda node : isinstance(node, ast.InstanceList))
            for new_inst_list in new_instance_list:
                break # only one inst in this file
            add_async_inst.append(new_inst_list)
            rm_sig.append("ap_sync_reg_"+match_sync.group(1))
            decl_reg = find_reg_wire_def(rm_sig[-1], DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
            rm_decl.append(decl_reg)
            rm_initial_sig(top_module_ast, decl_reg)
            rm_assign.append(assign)
            continue
 
    state_to_pipe = []
    for always in pose_always_list:
        if isinstance(always.statement.statements[0], ast.IfStatement):
            var = always.statement.statements[0].true_statement.statements[0].left.var.name
            # bind to the fastest clock
            if (var=="ap_CS_fsm") or (var=="ap_done_reg") or (var in mdfy_always):
                always.sens_list.list[0].sig.name = fastest_clk
                # TODO: is there a bug?
                #always.sens_list.list[0].sig = fastest_clk
                always.statement.statements[0].cond.left.name = "rst_"+fastest_clk
            # remove those unused always for async
            elif var in rm_sig:
                rm_always.append(always)

            # deal with start signals 
            # 1. for FSM_states related condition, sync them
            # 2. pipe FSM
            # 3. add "ap_done" to the condition for aux
            elif "_ap_start_reg" in var:
                # 1. for FSM_states, sync them
                eq_async = copy.deepcopy(always.statement.statements[0].false_statement.statements[0].cond)
                eq_sync_assign = ast.Assign(ast.Lvalue(ast.Identifier(var+"_async_cond")), ast.Rvalue(eq_async))
                add_assign.append(eq_sync_assign)
                in_sig = var+"_async_cond"
                in_clk = fastest_clk
                out_sig = var+"_sync_cond"
                _, _, module = connect_to_module(var.replace("_reg",""), main_module_list)
                out_clk = module_map[module.module]
                if in_clk==out_clk:
                    always.sens_list.list[0].sig.name = in_clk
                    # TODO: is there a bug?
                    #always.sens_list.list[0].sig = in_clk
                    always.statement.statements[0].cond.left.name = "rst_"+in_clk
                    continue
                gen_async_level_inst("async_inst_"+in_sig, in_sig, in_clk, out_sig, out_clk)
                async_inst_ast, _ = rtl_parse(["./async_inst_"+in_sig+"_inst.v"])
                os.system("rm async_inst_"+in_sig+"_inst.v")
                new_instance_list = DFS(async_inst_ast, lambda node : isinstance(node, ast.InstanceList))
                for new_inst_list in new_instance_list:
                    break # only one inst in this file
                add_async_inst.append(new_inst_list)
                decl_reg = find_reg_wire_def(in_sig, DFS(top_module_ast, lambda node : isinstance(node, ast.Decl)))
                sync_decl_reg_start = ast.Decl([ast.Wire(out_sig)])
                sync_decl_wire_start = ast.Decl([ast.Wire(in_sig)])
                add_decl.append(sync_decl_reg_start)
                add_decl.append(sync_decl_wire_start)
                # 2. pipe FSM, here only colect all states need to pipe. 
                #    pipe will be implemented after the for loop
                if isinstance(eq_async, ast.Eq):
                    state_to_pipe.append([eq_async.right.name, out_clk])
                elif isinstance(eq_async, ast.Or):
                    if isinstance(eq_async.left, ast.Eq):
                        state_to_pipe.append([eq_async.left.right.name, out_clk])
                    
                # 3. add "ap_done" to the condition for aux
                eq_sync = ast.And(ast.Lvalue(ast.Identifier(out_sig)), 
                                  ast.Rvalue(ast.Eq(ast.Lvalue(ast.Identifier(var.replace("start_reg", "done"))), 
                                                    ast.Rvalue(ast.Identifier("1'b0")))))
                always.statement.statements[0].false_statement.statements[0].cond = eq_sync
                always.sens_list.list[0].sig.name = out_clk
                #always.sens_list.list[0].sig = out_clk
                always.statement.statements[0].cond.left.name = "rst_"+out_clk

    for case_item in case_always_list[0].statement.statements[0].caselist:
        if case_item.cond==None:
            continue
        for pipe_item in state_to_pipe:
            if case_item.cond[0].name[9:] == pipe_item[0][9:]:
                # add a counter
                state_name = pipe_item[0]
                for fastest_clk_map_idx in range(1,len(fastest_clk_map)):
                    if fastest_clk_map[fastest_clk_map_idx][0]==pipe_item[1]:
                        cnt_value = fastest_clk_map[fastest_clk_map_idx][1]
                cnt_decl, cnt_always = gen_cnt(state_name, cnt_value, fastest_clk)
                add_decl.append(cnt_decl)
                add_always.append(cnt_always)
                # TODO change the fsm
                temp_statement =ast.Block([ast.IfStatement(ast.Eq(ast.Lvalue(ast.Identifier(state_name+"_cnt")),
                                                                                      ast.Rvalue(ast.Identifier(str(cnt_value-1)))),
                                                                               ast.Block([case_item.statement.statements[0]]),
                                                                               ast.Block([ast.BlockingSubstitution(ast.Identifier("ap_NS_fsm"),
                                                                                                                   ast.Identifier(case_item.cond[0].name))]))]) 
                case_item.statement.statements = tuple([temp_statement])
                
                
    # deal with ap_continue
    # since ap_continue is a pulst, it need to be delayed to longer
    for always in mux_always_list:
        var = always.statement.statements[0].true_statement.statements[0].left.var.name
        if "ap_continue" in var:
            in_sig = var
            _, _, module = connect_to_module(in_sig, main_module_list)
            out_clk = module_map[module.module]
            in_clk = fastest_clk
            if in_clk==out_clk:
                continue
            # add sync inst 
            out_sig = in_sig+"_sync"
            gen_async_pulse_inst("async_inst_"+in_sig, in_sig, in_clk, out_sig, out_clk)
            async_inst_ast, _ = rtl_parse(["./async_inst_"+in_sig+"_inst.v"])
            os.system("rm async_inst_"+in_sig+"_inst.v")
            new_instance_list = DFS(async_inst_ast, lambda node : isinstance(node, ast.InstanceList))
            for new_inst_list in new_instance_list:
                break # only one inst in this file
            add_async_inst.append(new_inst_list)
            sync_decl_wire_continue = ast.Decl([ast.Wire(out_sig)])
            add_decl.append(sync_decl_wire_continue)
            for portarg in module.portlist:
                if isinstance(portarg.argname, ast.Identifier):
                    if portarg.argname.name==in_sig:
                        portarg.argname.name = out_sig
            # *** since it has been considered in the CDC, there is no need to change ***
            # change the always so that the pulse will be longer
            # always.statement.statements[0].false_statement = ast.IfStatement(ast.Eq(ast.Identifier(out_sig),
            #                                                                         ast.IntConst("1'b1")),
            #                                                                  ast.Block([ast.BlockingSubstitution(ast.Identifier(in_sig),
            #                                                                                                      ast.IntConst("1'b0"))]), 
            #                                                                  ast.Block([ast.BlockingSubstitution(ast.Identifier(in_sig),
            #                                                                                                      ast.Identifier(in_sig))])) 
 

    # update the ast
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    for rm_item in rm_decl+rm_always+rm_assign:
        item_list.remove(rm_item)
    item_list += add_async_inst + add_assign + add_always
    for item_idx in range(len(item_list)):
        if isinstance(item_list[item_idx], ast.Decl):
            if isinstance(item_list[item_idx].list[0], ast.Reg):
                break
    item_list = item_list[0:item_idx] + add_decl + item_list[item_idx:]
    module_def.items = tuple(item_list)
        
def cdc_insert(module_name, module_map, fastest_clk_map, root_path):
    top_module_ast, axi_module_list, cg_module_list, main_module_list, fifo_module_list, ram_module_list, other_module_list, pose_always_list, case_always_list, assign_always_list, mux_always_list, assign_list = read_file(module_name, module_map, root_path)
    ram_module_clk_bind(top_module_ast, ram_module_list, main_module_list, module_map, mux_always_list)
    #axi_module_clk_bind(axi_module_list, module_map[module_name]) #maintain the clock
    main_module_clk_bind(main_module_list, module_map, root_path)
    fifo_module_clk_bind(fifo_module_list, main_module_list, module_map)
    #org_rst_rm(top_module_ast) # reserve for axi
    fsm_clk_bind(top_module_ast, assign_list, pose_always_list, mux_always_list, case_always_list, main_module_list, fastest_clk_map, module_map)
    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_module_ast)
    with open(module_name+".v", 'w') as f:
        f.write(new_rtl) 
    os.system("mv *.v "+root_path)
    
 
#clk_domains = {"clk1": '10', 'clk2': '2 5', 'clk3': '30'}
#module_map = {"top": "clk_phy", "top_nondf_kernel_2mm": "clk1", "top_kernel3_x1": "clk2", "top_kernel3_x0": "clk3"}
#fastest_clk_map = ["clk3", ["clk2", 15], ["clk1", 2]]
#cdc_insert("top", module_map, fastest_clk_map, "./verilog/")
