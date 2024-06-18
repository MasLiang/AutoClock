from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import sys
sys.path.append("../../")
from cdc.src.template.async_dpram import *
from cdc.src.template.async_fifo import *
from parser import *
import pyverilog.vparser.ast as ast
import os
import copy
import re

   
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

'''
def modify_ram_only_clk_rst(inst, ce_clk):
    for portarg in inst.portlist:
        if portarg=="clk":
            portarg.argname = ce_clk
        elif portarg=="reset":
            portarg.argname = "rst_"+ce_clk
            break

def replace_async_ram(inst, port_dic):
    # calculate factors of async dual-port ram
    for param in inst.parameterlist:
        if param.paramname=="DataWidth":
            data_width = int(param.argname.value)
        elif param.paramname=="AddressWidth":
            address_width = int(param.argname.value)
        elif param.paramname=="AddressRange":
            address_range = int(param.argname.value)
    
    factors = [data_width, address_width, address_range]    
    gen_async_bram_inst(inst.module, inst.name, port_dic, factors)
    new_ram_ast, _ = rtl_parse(["./"+inst.module+"_inst.v"])
    os.system("rm ./"+inst.module+"_inst.v")
    
    new_instances = DFS(new_ram_ast, lambda node : isinstance(node, ast.Instance))
    for new_inst in new_instances:
        inst = new_inst

def modify_ram_1w1r(inst, main_module_list, module_map, mux_always_list):
    for portarg in inst.portlist:
        if portarg.portname=="ce0":
            sig_ce = portarg.argname
        elif portarg.portname=="we0":
            sig_we = portarg.argname
        elif portarg.portname=="address0":
            sig_address = portarg.argname
        elif portarg.portname=="d0":
            sig_d = portarg.argname
        elif portarg.portname=="q0":
            sig_q = portarg.argname

    # 1. ram belongs to a single module
    #   a. we -> clk1, ce -> clk1: do not change
    # 2. we port ce ports are connected to muxs
    #   a. we -> clk1/clk1, ce -> clk1/clk1: do not change
    #   b. we -> clk1/clk2, ce -> clk1/clk2: change to two ports, one for wr and another for wr

    ce_clk = ''
    we_clk = ''
    
    # check if connected to a module
    for module in main_module_list:
        for portarg in module.portlist:
            if portarg.argname==sig_ce:
                ce_clk = module_map[module.name]
            elif portarg.argname==sig_we:
                we_clk = module_map[module_name]
            if ce_clk!='' and we_clk!='':
                break
        if ce_clk!='' and we_clk!='':
            break
    
    if ce_clk!='' and we_clk==ce_clk:
        # this ram belongs to a single module
        modify_ram_only_clk_rst(inst, ce_clk)
    elif ce_clk=='' and we_clk==ce_clk:
        # there are mux so that the bram will be TDM, extrace the mux
        # 1. find the mux of ce
        ce_mux_input, ce_mux_always = find_mux_in(sig_ce, mux_always_list)
        # 2. find which module connect to the mux
        module_dic = {}
        for sig_ce_mux in ce_mux_input:
            flag, _, module = connect_to_module(sig_ce_mux, main_module_list)
            if flag:
                if module in list(module_dic.keys()):
                    module_dic[module].append(sig_ce_mux.name)
                else:
                    module_dic[module] = [sig_ce_mux.name]
        # analyze the clock domain
        # 3. ce from same domain, this ram belongs to a single module
        if (len(set(list(module_dic.keys())))==1):
            ce_clk = module_map[list(module_dic.keys())[0]]
            modify_ram_only_clk_rst(inst, ce_clk)
        # 4. ce from different domains, this ram should be dual-port
        #    boud other signals to each ce
        else:
            port_dic = {}
            we_mux_input, we_mux_always = find_mux_in(sig_we, mux_always_list)
            address_mux_input, address_mux_always = find_mux_in(sig_address, mux_always_list)
            d_mux_input, d_mux_always = find_mux_in(sig_d, mux_always_list)
            q_mux_input, q_mux_always = find_mux_in(sig_q, mux_always_list)
            for module in list(module_dic.keys()):
                for portarg in module.portlist:
                    find_flg = 0
                    for sig_we_mux_input in we_mux_input:
                        if portarg.argname==sig_we_mux_input:
                            find_flg = 1
                            break
                    if find_flg==0:
                        sig_we_mux_input = "1'b0"
                    else:
                        if(isinstance(sig_we_mux_input, ast.Identifier)):
                            sig_we_mux_input = sig_we_mux_input.name
                        elif(isinstance(sig_we_mux_input, ast.IntConst)):
                            sig_we_mux_input = sig_we_mux_input.value
                    for sig_address_mux_input in address_mux_input:
                        if portarg.argname==sig_address_mux_input:
                            break
                    sig_address_mux_input = sig_address_mux_input.name
                    for sig_d_mux_input in d_mux_input:
                        if portarg.argname==sig_d_mux_input:
                            find_flg = 1
                            break
                    if find_flg==0:
                        sig_d_mux_input = "'b0"
                    else:
                        if(isinstance(sig_d_mux_input, ast.Identifier)):
                            sig_d_mux_input = sig_d_mux_input.name
                        elif(isinstance(sig_d_mux_input, ast.IntConst)):
                            sig_d_mux_input = sig_d_mux_input.value
                    for sig_q_mux_input in q_mux_input:
                        if portarg.argname==sig_q_mux_input:
                            find_flg = 1
                            break
                    if find_flg==0:
                        sig_q_mux_input = " "
                    else:
                        if(isinstance(sig_q_mux_input, ast.Identifier)):
                            sig_q_mux_input = sig_q_mux_input.name
                        elif(isinstance(sig_q_mux_input, ast.IntConst)):
                            sig_q_mux_input = sig_q_mux_input.value
                    if portarg.portname=="ap_clk":
                        sig_clk = portarg.argname.name
                    elif portarg.portname=="ap_rst":
                        sig_rst = portarg.argname.name
                port_dic[module] = module_dic[module]+[sig_we_mux_input, sig_address_mux_input, sig_d_mux_input, sig_q_mux_input, sig_clk, sig_rst]
            replace_async_ram(inst, port_dic)

            return [we_mux_always, address_mux_always, d_mux_always, q_mux_always]
'''
 
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
            port[0] = port[0].name+"_"+port[8]
            new_port_list_ce.append(port)
            continue
        # connect to mux, but only a data gate
        if len(port[7])==1:
            flag, _, module = connect_to_module(port[7][0], main_module_list)
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
                    port[sig_idx] = sig+"_"+clk_domain
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
    
    # TODO merge a w port and a r port from the same clock domain. Can it do?
    
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
            port_dic["w"] = port0[0:5]+[port0[-1]]+[port0[-1]+"_rst"]
            port_dic["r"] = port1[0:5]+[port1[-1]]+[port1[-1]+"_rst"]
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
        break
    item_list = list(module_def.items)
    
    for item_idx in range(len(item_list)):
        if isinstance(item_list[item_idx], ast.Decl):
            if isinstance(item_list[item_idx].list[0], ast.Input):
                if item_list[item_idx].list[0].name=="ap_clk":
                    break
    
    temp_clk = copy.deepcopy(item_list[item_idx])
    temp_clk.list[0].name = "axi_clk"
    item_list = item_list[0:item_idx]+[temp_clk]+item_list[item_idx:]
    temp_rst = copy.deepcopy(item_list[item_idx])
    temp_rst.list[0].name = "rst_axi"
    item_list = item_list[0:item_idx]+[temp_rst]+item_list[item_idx:]

    port_list = list(module_def.portlist.ports)

    for portarg_idx in range(len(port_list)):
        if port_list[portarg_idx].name=="ap_clk":
            break
    
    temp_clk_port = copy.deepcopy(port_list[portarg_idx])
    temp_clk_port.name = "axi_clk"
    port_list = port_list[0:portarg_idx]+[temp_clk_port]+port_list[portarg_idx:]
    temp_rst_port = copy.deepcopy(port_list[portarg_idx])
    temp_rst_port.name = "rst_axi"
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
            main_axi_module_clk_bound(inst, "ap_clk", root_path)

    if end_flg==1:
        for inst in inst_list:
            if is_fifo_inst(inst):
                modify_submodule_fifo_clk(inst, inst_list)

    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_module_ast)
    with open(module_name+".v", "w") as f:
        f.write(new_rtl)
    

def main_axi_module_clk_bound(inst, clk_domain, root_path):
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
                temp_portarg.portname = "rst_axi"
                port_list = list(inst.portlist)
                port_list.append(temp_portarg)
                inst.portlist = tuple(port_list)

    main_axi_module_process(inst.module, root_path)
 
def axi_module_clk_bound(axi_module_list, clk_domain):
    for axi_inst in axi_module_list:
        modify_only_module_clk(axi_inst, clk_domain)

def main_module_clk_bound(main_module_list, module_map, root_path):
    for main_inst in main_module_list:
        if is_ddr_controller(main_inst):
            # TODO, assert that user's config is wrong. It should be in ap_clk domain
            continue
        if is_main_axi_module(main_inst):
            main_axi_module_clk_bound(main_inst, module_map[main_inst.module], root_path)
        else:
            modify_only_module_clk(main_inst, module_map[main_inst.module])

def fifo_module_clk_bound(fifo_module_list, main_module_list, module_map):
    for fifo_inst in fifo_module_list:
        modify_fifo_clk(fifo_inst, main_module_list, module_map)

def ram_module_clk_bound(top_module_ast, ram_module_list, main_module_list, module_map, mux_always_list):
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
        add_instance_list = ast.InstanceList(module=add_instance.module, parameterlist = add_instance.parameterlist, instances =[add_instance])
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

def fsm_clk_bound(always_list, clk_domain):
    for always in always_list:
        if isinstance(always.statement.statements[0], ast.IfStatement):
            var = always.statement.statements[0].true_statement.statements[0].left.var.name
            if var=="ap_CS_fsm" or var=="ap_done_reg":
                always.sens_list.list[0].sig.name = clk_domain
        
def cdc_insert(module_name, module_map, fastest_clk, root_path):
    top_module_ast, axi_module_list, cg_module_list, main_module_list, fifo_module_list, ram_module_list, other_module_list, pose_always_list, case_always_list, assign_always_list, mux_always_list = read_file(module_name, module_map, root_path)
    ram_module_clk_bound(top_module_ast, ram_module_list, main_module_list, module_map, mux_always_list)
    #axi_module_clk_bound(axi_module_list, module_map[module_name])
    main_module_clk_bound(main_module_list, module_map, root_path)
    fifo_module_clk_bound(fifo_module_list, main_module_list, module_map)
    #org_rst_rm(top_module_ast) # reserve for axi
    fsm_clk_bound(pose_always_list, fastest_clk)
    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_module_ast)
    with open(module_name+".v", 'w') as f:
        f.write(new_rtl) 
 
cdc_insert("top", {"top": "clk_phy", "top_nondf_kernel_2mm": "clk1", "top_kernel3_x1": "clk2", "top_kernel3_x0": "clk3"}, "clk3", "./verilog/")
#cdc_insert("rwkv_top", {"rwkv_top": "clk_phy", "rwkv_top_read_all115": "clk1", "rwkv_top_layer_common_s": "clk2", "rwkv_top_write_all": "clk3"}, "../../../rwkv_src/verilog/")
