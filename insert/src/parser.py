from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.vparser.parser import VerilogParser
import pyverilog.vparser.ast as ast
import os
import copy
import re

def is_fifo_inst(inst):
    port_lst = ['clk', 'reset', 'if_read_ce', 'if_write_ce', 'if_din', 'if_full_n', 'if_write', 'if_dout', 'if_empty_n', 'if_read']
    idx = 0
    for port in inst.portlist:
        if idx>=len(port_lst):
            return False
        if port.portname!=port_lst[idx]:
            return False
        idx+=1
    
    return True

def is_ram_1wr_inst(inst):
    port_lst = ["clk", "reset", "address0", "ce0", "we0", "d0", "q0"]
    idx = 0
    for port in inst.portlist:
        if idx>=len(port_lst):
            return False
        if port.portname!=port_lst[idx]:
            return False
        idx+=1
    
    return True

def is_ram_1wr2r_inst(inst):
    port_lst = ["clk", "reset", "address0", "ce0", "we0", "d0", "q0", "address1", "ce1", "q1"]
    idx = 0
    for port in inst.portlist:
        if idx>=len(port_lst):
            return False
        if port.portname!=port_lst[idx]:
            return False
        idx+=1
    
    return True

def is_ram_1r2w_inst(inst):
    port_lst = ["clk", "reset", "address0", "ce0", "q0", "address1", "ce1", "we1", "d1"]
    idx = 0
    for port in inst.portlist:
        if idx>=len(port_lst):
            return False
        if port.portname!=port_lst[idx]:
            return False
        idx+=1
    
    return True

def is_ram(inst):
    return is_ram_1wr_inst(inst) or is_ram_1wr2r_inst(inst) or is_ram_1r2w_inst(inst)

def is_main_axi_module(main_inst):
    for portarg in main_inst.portlist:
        if "axi" in portarg.portname:
            return True
    return False

def is_ddr_controller(inst):
    axi_if_flg = 0
    fifo_if_flg = 0
    for portarg in inst.portlist:
        if not(("axi" in portarg.portname) or 
               ("ap_" in portarg.portname) or
               ("_din" in portarg.portname) or
               ("_full_n" in portarg.portname) or
               ("_write" in portarg.portname) or
               ("_dout" in portarg.portname) or
               ("_empty_n" in portarg.portname) or
               ("_read" in portarg.portname)):
            return False
        elif "axi" in portarg.portname:
            axi_if_flg = 1
        elif (("ap_" in portarg.portname) or
              ("_din" in portarg.portname) or
              ("_full_n" in portarg.portname) or
              ("_write" in portarg.portname) or
              ("_dout" in portarg.portname) or
              ("_empty_n" in portarg.portname) or
              ("_read" in portarg.portname)):
            fifo_if_flg = 1
    if axi_if_flg==1 and fifo_if_flg==1:
        return True
    else:
        return False
    

def DFS(node, filter_func):
  if filter_func(node):
    try:
      logging.debug(f'visit node {node.name}')
    except:
      pass
      # logging.debug(f'node in line {node.lineno} has no name')
    yield node
  for c in node.children():
    yield from DFS(c, filter_func)

def read_file(module_name, module_map, root_path):
    file_path = root_path+"/"+module_name+".v"
    # this function is used to initial module set
    fifo_module_list = []       # all FIFO between two modules
    start_fifo_module_list = [] # FIFO used to propogate start signals
    ram_module_list = []        # all BRAM between two modules
    axi_module_list = []        # axi related modules, they belongs to the phy clk
    main_module_list = []       # modules corresponding to C functions
    cg_module_list = []        # clock gating
    other_module_list = []      # others
    pose_always_list = []       # always block with posedge clock in sens_list
    case_always_list = []       # always block equal to an case based mux
    mux_always_list = []        # always block equal to an if based mux
    assign_always_list = []     # always block equal to an assign
    top_module_ast, directives = rtl_parse([file_path])
    all_instances = DFS(top_module_ast, lambda node : isinstance(node, ast.Instance))
    all_instanceslist = DFS(top_module_ast, lambda node : isinstance(node, ast.InstanceList))
    all_always = DFS(top_module_ast, lambda node : isinstance(node, ast.Always))
    all_assign = DFS(top_module_ast, lambda node : isinstance(node, ast.Assign))
    for inst in all_instances:
        if "s_axi" in inst.module or "m_axi" in inst.module:
            axi_module_list.append(inst)
        elif "BUFG" in inst.module:
            cg_module_list.append(inst)
        elif inst.module in list(module_map.keys()):
            main_module_list.append(inst)
        elif is_fifo_inst(inst):
            fifo_module_list.append(inst)
        elif is_ram(inst):
            ram_module_list.append(inst)
        else:
            other_module_list.append(inst)

    for always in all_always:
        if len(always.sens_list.list)==1 and always.sens_list.list[0].type=="posedge":
            pose_always_list.append(always)
        elif len(always.sens_list.list)==1 and always.sens_list.list[0].type=="all":
            if isinstance(always.statement.statements[0], ast.CaseStatement):
                case_always_list.append(always)
            elif isinstance(always.statement.statements[0], ast.BlockingSubstitution):
                assign_always_list.append(always)
            else:
                mux_always_list.append(always)

    assign_list = []
    for assign in all_assign:
        assign_list.append(assign)
    
    return_list = [top_module_ast,
                   axi_module_list,
                   cg_module_list, 
                   main_module_list, 
                   fifo_module_list,  
                   ram_module_list, 
                   other_module_list, 
                   pose_always_list, 
                   case_always_list, 
                   assign_always_list, 
                   mux_always_list,
                   assign_list]

#    for inst in ram_module_list:
#        add_ram_inst, add_ram_mux, rm_ram_mux = modify_ram_common(inst, main_module_list, module_map, mux_always_list)
        # TODO, remove related mux
        #for node in top_module_ast.description.definitions[1].children():
        #    if node in always_rm:
        #        top_module_ast.description.definitions[1].children().remove(node)
        
    
    return return_list

