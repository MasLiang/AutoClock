#In this file, the connection between different instances are determained

from pyverilog.vparser.parser import parse as rtl_parse
import pyverilog.vparser.ast as ast

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

def is_ram_1w1r(inst):
    port_lst = ["clk", "reset", "address0", "ce0", "we0", "d0", "q0"]
    idx = 0
    for port in inst.portlist:
        if idx>=len(port_lst):
            return False
        if port.portname!=port_lst[idx]:
            return False
        idx+=1
    
    return True

def is_ram(inst):
    return is_ram_1w1r(inst)

def read_file(file_path):
    # this function is used to initial module set
    fifo_module_list = []       # all FIFO between two modules
    start_fifo_module_list = [] # FIFO used to propogate start signals
    ram_module_list = []        # all BRAM between two modules
    axi_module_list = []        # axi related modules, they belongs to the phy clk
    other_module_list = []      # other modules corresponding to C functions
    top_module_ast, directives = rtl_parse([file_path])
    all_instances = DFS(top_module_ast, lambda node : isinstance(node, ast.Instance))
    for inst in all_instances:
        if "start" in inst.module and is_fifo(inst):
            start_fifo_module_list.append(inst)
        elif is_fifo(inst):
            fifo_module_list.append(inst)
        elif "axi" in inst.module:
            axi_module_list.append(inst)
        elif is_ram(inst):
            ram_module_list.append(inst)
        else:
            other_module_list.append(inst)
    
    return fifo_module_list, start_fifo_module_list, ram_module_list, axi_module_list, other_module_list
    
def modify_main_module_clk(inst, module_map)
    for portarg in inst.portlist:
        if portarg.portname=="ap_clk":
            portarg.argname = module_map[inst.name]
        elif portarg.portname=="ap_rst":
            portarg.argname = "rst_"+module_map[inst.name]
  
    
def modify_fifo_clk(inst, other_module_list, module_map):
    # this function is used to determain the clock domain of rd/wr port
    for portarg in inst.portlist:
        if portarg.portname=="if_write":
            sig_wr = portarg.argname
        elif portarg.portname=="if_read":
            sig_rd = portarg.argname
    
    for module in other_module_list:
        for portarg in module.portlist:
            if portarg.argname==sig_wr:
                wr_clk = module_map[module.name]
            elif portarg.argname==sig_rd:
                rd_clk = module_map[module_name]

    if wr_clk==rd_clk:
        for portarg in inst.portlist:
            if portarg.portname=="clk":
                portarg.argname = wr_clk
            elif portarg.portname=="reset":
                portarg.argname = "rst_"+wr_clk
    else:
        fifo_name = inst.name
        match = re.search(r'(\w+)_w(\d+)_d(\d+)_A(\w+)', fifo_name)
        if match:
            fifo_width = match.group(1)
            fifo_depth = match.group(2)
            async_fifo_factor = ["block", fifo_depth, fifo_depth, fifo_width, fifo_width]
        else:
            match = re.search(r'(\w+)_w(\d+)_d(\d+)_S(\w+)', fifo_name)
            fifo_width = match.group(1)
            fifo_depth = match.group(2)
            async_fifo_factor = ["distributed", fifo_depth, fifo_depth, fifo_width, fifo_width]
        gen_async_fifo_file(fifo_name, async_fifo_factor)
        for portarg in inst.portlist:
            if portarg.portname=="clk":
                portarg.argname = wr_clk
                portarg.portname = "if_wr_clk"
            temp_portarg = portarg
            temp_portarg.argname = rd_clk
            temp_portarg.portname = "if_rd_clk"
            inst.portlist.append(temp_portarg)
            break

def modify_ram_1w1r(inst, other_module_list, module_map):
    for portarg in inst.portlist:
        if portarg.portname=="ce0":
            sig_ce = portarg.argname
        elif portarg.portname=="we0":
            sig_we = portarg.argname

    # 1. w and r ports are connected to modules directly
    #   a. w -> clk1, r -> clk1: do not change
    #   b. w -> clk1, r -> clk2: change to two ports, one for w and another for r
    # 2. w port is connected to a module, while r port is connected to a mux
    #   a. w -> clk1, r -> clk1/clk1: do not change
    #   b. w -> clk1, r -> clk1/clk2: change to two ports, one for wr and another for r, also change mux
    #   c. w -> clk2, r -> clk1/clk1: change to two ports, one for w and another for r, do not change mux
    # 3. w port is connected to a mux, while r port is connected to a module
    #   a. w -> clk1/clk1, r -> clk1: do not change
    #   b. w -> clk1/clk2, r -> clk1: change to two ports, one for wr and another for w, also change mux
    #   c. w -> clk1/clk1, r -> clk2: change to two ports, one for w and another for r, do not change mux
    # 4. w port r ports are connected to muxs
    #   a. w -> clk1/clk1, r -> clk1/clk1: do not change
    #   b. w -> clk1/clk2, r -> clk1/clk1: change to two ports, one for wr and another for w
    #   c. w -> clk1/clk1, r -> clk1/clk2: change to two ports, one for wr and another for r
    #   d. w -> clk1/clk2, r -> clk1/clk2: change to two ports, one for wr and another for wr

    # 1a,2a,3a,4a do not change
    # others, change to two ports
    #   1b, 2c, 3c one for w and another for r
    #   2b, 4c one for wr and another for r
    #   3b, 4b one for wr and another for w
    #   2c, 3c one for w and another for r
    #   4d one for wr and another for wr
    ce_clk = ''
    we_clk = ''
    for module in other_module_list:
        for portarg in module.portlist:
            if portarg.argname==sig_ce:
                ce_clk = module_map[module.name]
            elif portarg.argname==sig_we:
                we_clk = module_map[module_name]


    
    
    
def modify_bram_clk(inst, other_module_list, module_map):
    # this function is used to determain the clock domain of rd/wr port
    if is_ram_1w1r(inst):
        modify_ram_1w1r(inst, other_module_list, module_map)


#def find_bram_conn
#    # this function is used to determain the clock domain of two ports
#
#
## for these three function, it is not sure.
## We might need DMUX to sync all these signals if they are from 
## a clock domain being different from phy clock.
#
## how to do that
#
#def find_alwpos_conn
#
#def find_alwcmp_conn
#
#def find_assign_conn

#def verilog_parser(file_path, module_map):
#    # clk domain map of main modules from crg_gen
#    modules_map

read_file("aaa.v")
