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

def is_ram_1w1r_inst(inst):
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
    return is_ram_1w1r_inst(inst)

def read_file(file_path, module_map):
    # this function is used to initial module set
    fifo_module_list = []       # all FIFO between two modules
    start_fifo_module_list = [] # FIFO used to propogate start signals
    ram_module_list = []        # all BRAM between two modules
    axi_module_list = []        # axi related modules, they belongs to the phy clk
    main_module_list = []       # modules corresponding to C functions
    other_module_list = []      # others
    pose_always_list = []       # always block with posedge clock in sens_list
    all_always_list = []        # always block with all in sens_list
    top_module_ast, directives = rtl_parse([file_path])
    all_instances = DFS(top_module_ast, lambda node : isinstance(node, ast.Instance))
    all_instanceslist = DFS(top_module_ast, lambda node : isinstance(node, ast.InstanceList))
    all_always = DFS(top_module_ast, lambda node : isinstance(node, ast.Always))
    all_assign= DFS(top_module_ast, lambda node : isinstance(node, ast.Assign))
    for inst in all_instances:
        if "start" in inst.module and is_fifo_inst(inst):
            start_fifo_module_list.append(inst)
        elif is_fifo_inst(inst):
            fifo_module_list.append(inst)
        elif is_ram(inst):
            ram_module_list.append(inst)
        elif inst.name in module_map:
            main_module_list.append(inst)
        else:
            other_module_list.append(inst)

    for always in all_always:
        if len(always.sens_list.list)==1 and always.sens_list.list[0].type=="posedge":
            pose_always_list.append(always)
        elif len(always.sens_list.list)==1 and always.sens_list.list[0].type=="all":
            all_always_list.append(always)

    return_list = [fifo_module_list, start_fifo_module_list, ram_module_list, axi_module_list, main_module_list, pose_always_list, all_always_list]
    
    return return_list
    
def modify_main_module_clk(inst, module_map):
    for portarg in inst.portlist:
        if portarg.portname=="ap_clk":
            portarg.argname = module_map[inst.name]
        elif portarg.portname=="ap_rst":
            portarg.argname = "rst_"+module_map[inst.name]
  
    
def modify_fifo_clk(inst, main_module_list, module_map):
    # this function is used to determain the clock domain of rd/wr port
    for portarg in inst.portlist:
        if portarg.portname=="if_write":
            sig_wr = portarg.argname
        elif portarg.portname=="if_read":
            sig_rd = portarg.argname
    
    for module in main_module_list:
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

def modify_ram_only_clk_rst(inst, ce_clk):
    for portarg in inst.portlist:
        if portarg=="clk":
            portarg.argname = ce_clk
        elif portarg=="reset":
            portarg.argname = "rst_"+ce_clk
            break

def replace_async_ram(inst, port_dic):
    # calculate factors of async dual-port ram
    start_line = inst.lineno
    end_line = inst.children()[-1].lineno+1
    data_width = inst.
    for param in inst.parameterlist:
        if param.paramname=="DataWidth":
            data_width = int(param.argname)
        elif param.paramname=="AddressWidth":
            address_width = int(param.argname)
        elif param.paramname=="AddressRange":
            address_range = int(param.argname)
    
    memory_size = data_width*address_range   
 
    factor = [start_line, end_line, # used to find the instance to replace
              data_width,           # data width for write and read
              address_width,        # address width for write and read
              memory_size]          # memory size
    
    
    

def find_mux(sig, all_always_list):
    mux_input = []
    for always in all_always_list:
        if always.statement.statements[0].true_statement.statements[0].left.var==sig:
            for states in always.statement.statements[0]:
                for true_state in states.true_statement.statements:
                    mux_input.append(true_state.right.var)
            break

    return mux_input

def modify_ram_1w1r(inst, main_module_list, module_map, all_always_list):
    for portarg in inst.portlist:
        if portarg.portname=="ce0":
            sig_ce = portarg.argname
        elif portarg.portname=="we0":
            sig_we = portarg.argname
        elif portarg.portname=="address0":
            sig_address = portarg.argname
        elif portarg.portname=="d0":
            sig_d = portarg.argname
        elif portarg.portname=="q":
            sig_q = portarg.argname

    # 1. ram belongs to a single module
    #   a. we -> clk1, ce -> clk1: do not change
    # 2. we port ce ports are connected to muxs
    #   a. we -> clk1/clk1, ce -> clk1/clk1: do not change
    #   b. we -> clk1/clk2, ce -> clk1/clk2: change to two ports, one for wr and another for wr

    ce_clk = []
    we_clk = []
    
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
        ce_mux_input = find_mux(sig_ce, all_always_list)
        # 2. find which module connect to the mux
        module_dic = {}
        for sig_ce_mux in ce_mux_input:
            if sig_ce_mux == "1'b0":
                continue
            for module in main_module_list:
                if portarg.argname==sig_ce_mux:
                    if module_dic.get(module.name, default=True):
                        module_dic[module.name] = [sig_ce_mux]
                    else:
                        module_dic[module.name].append(sig_ce_mux)
                    break
        # analyze the clock domain
        # 3. ce from same domain, this ram belongs to a single module
        if (len(set(list(module_dic.keys())))==1):
            ce_clk = module_map[list(module_dic.keys())[0]]
            modify_ram_only_clk_rst(inst, ce_clk)
        # 4. ce from different domains, this ram should be dual-port
        #    boud other signals to each ce
        else:
            port_dic = {}
            we_mux_input = find_mux(sig_we, all_always_list)
            address_mux_input = find_mux(sig_address, all_always_list)
            d_mux_input = find_mux(sig_d, all_always_list)
            q_mux_input = find_mux(sig_q, all_always_list)
            for module in list(module_dic.keys()):
                for portarg in module.portlist:
                    for sig_we_mux_input in we_mux_input:
                        if portarg.argname==sig_we_mux_input:
                            find_flg = 1
                            break
                    if find_flg==0:
                        sig_we_mux_input = "1'b0"
                    for sig_address_mux_input in address_mux_input:
                        if portarg.argname==sig_address_mux_input:
                            break
                    for sig_d_mux_input in d_mux_input:
                        if portarg.argname==sig_d_mux_input:
                            find_flg = 1
                            break
                    if find_flg==0:
                        sig_d_mux_input = "'b0"
                    for sig_q_mux_input in q_mux_input:
                        if portarg.argname==sig_q_mux_input:
                            find_flg = 1
                            break
                    if find_flg==0:
                        sig_q_mux_input = " "
                    if portarg.portname=="ap_clk":
                        sig_clk = portarg.argname
                    elif portarg.portname=="ap_rst":
                        sig_rst = portarg.argname
                port_dic[module] = [module_dic[module], sig_we_mux_input, sig_address_mux_input, sig_d_mux_input, sig_q_mux_input, sig_clk, sig_rst]
                replace_async_ram(inst, port_dic)
    
    
def modify_bram_clk(inst, main_module_list, module_map):
    # this function is used to determain the clock domain of rd/wr port
    if is_ram_1w1r_inst(inst):
        modify_ram_1w1r(inst, main_module_list, module_map)


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
read_file("aaa.v", [])
