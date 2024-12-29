from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as ast
import os
import sys
sys.path.append("../../")
from .rtl_parser import *
import pdb

def ap_done_mdf(file_path):
    #pdb.set_trace()
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
    out_port_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Output))
    have_port = 0
    for out_port in out_port_lst:
        if out_port.name=="ap_done":
            have_port = 1
            break
    if have_port==1:
        add_decl = []
        reg_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Reg))
        reg_def = 0
        for reg in reg_lst:
            if reg.name=="ap_done":
                reg_def = 1
                break
        if reg_def==0:
            # this "ap_done" is a wire, add reg type, then the "pre" should be wire
            # to replace "ap_done"
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done")])
            ap_done_pre_decl = ast.Decl([ast.Wire("ap_done_pre")])
            add_decl.append(ap_done_reg_decl)
            add_decl.append(ap_done_pre_decl)
            assign_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Assign))
            assign_exist = 0
            for assign in assign_lst:
                if assign.left.var.name=="ap_done":
                    assign.left.var.name = "ap_done_pre"
                    assign_exist = 1
                    break
            if assign_exist==0:
                # there is a control module
                inst_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Instance))
                for inst in inst_lst:
                    for portarg in inst.portlist:
                        if isinstance(portarg.argname, ast.Identifier):
                            if portarg.argname.name=="ap_done":
                                portarg.argname.name = "ap_done_pre"
                
        else:
            # this "ap_done" is a reg, no need to modify, then the "pre" should be 
            # reg to replace "ap_done"
            ap_done_pre_decl = ast.Decl([ast.Reg("ap_done_pre")])
            add_decl.append(ap_done_pre_decl)
            always_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Always))
            for always in always_lst:
                if always.sens_list.list[0].type=="all":
                    if isinstance(always.statement.statements[0], ast.CaseStatement):
                        continue
                    if isinstance(always.statement.statements[0], ast.IfStatement):
                        if isinstance(always.statement.statements[0].true_statement.statements[0], ast.IfStatement):
                            continue
                        if always.statement.statements[0].true_statement.statements[0].left.var.name=="ap_done":
                            always.statement.statements[0].true_statement.statements[0].left.var.name = "ap_done_pre"
                            if isinstance(always.statement.statements[0].false_statement, ast.IfStatement):
                                always.statement.statements[0].false_statement.true_statement.statements[0].left.var.name = "ap_done_pre"
                                always.statement.statements[0].false_statement.false_statement.statements[0].left.var.name = "ap_done_pre"
                            else:
                                always.statement.statements[0].false_statement.statements[0].left.var.name = "ap_done_pre"
                            break

        new_always =     ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                    ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                      ast.IntConst("1'b1")),
                                                               ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                      ast.IntConst("1'b0"))]),
                                                               ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                      ast.Identifier("ap_done_pre"))]))]))
    
        module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
        for module_def in module_defs:
            break
        item_list = list(module_def.items)
        for item_idx in range(len(item_list)):
            if isinstance(item_list[item_idx], ast.Decl):
                break

        item_list = item_list[0:item_idx] + add_decl + item_list[item_idx:]
        item_list += [new_always]
        module_def.items = tuple(item_list)
                

        rtl_generator = ASTCodeGenerator()
        new_rtl = [rtl_generator.visit(top_module_ast)]
        with open(file_path, 'w') as f:
            for line in new_rtl:
                f.write(line)

def ap_ready_mdf(file_path):
    #pdb.set_trace()
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
    out_port_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Output))
    have_port = 0
    for out_port in out_port_lst:
        if out_port.name=="ap_ready":
            have_port = 1
            break
    if have_port==1:
        add_decl = []
        reg_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Reg))
        reg_def = 0
        for reg in reg_lst:
            if reg.name=="ap_ready":
                reg_def = 1
                break
        if reg_def==0:
            # this "ap_ready" is a wire, add reg type, then the "pre" should be wire
            # to replace "ap_ready"
            ap_ready_reg_decl = ast.Decl([ast.Reg("ap_ready")])
            ap_ready_pre_decl = ast.Decl([ast.Wire("ap_ready_pre")])
            add_decl.append(ap_ready_reg_decl)
            add_decl.append(ap_ready_pre_decl)
            assign_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Assign))
            assign_exist = 0
            for assign in assign_lst:
                if assign.left.var.name=="ap_ready":
                    assign.left.var.name = "ap_ready_pre"
                    assign_exist = 1
                    break
            if assign_exist==0:
                # there is a control module
                inst_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Instance))
                for inst in inst_lst:
                    for portarg in inst.portlist:
                        if isinstance(portarg.argname, ast.Identifier):
                            if portarg.argname.name=="ap_ready":
                                portarg.argname.name = "ap_ready_pre"
                
        else:
            # this "ap_ready" is a reg, no need to modify, then the "pre" should be 
            # reg to replace "ap_ready"
            ap_ready_pre_decl = ast.Decl([ast.Reg("ap_ready_pre")])
            add_decl.append(ap_ready_pre_decl)
            always_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Always))
            for always in always_lst:
                if always.sens_list.list[0].type=="all":
                    if isinstance(always.statement.statements[0], ast.CaseStatement):
                        continue
                    if isinstance(always.statement.statements[0], ast.IfStatement):
                        if isinstance(always.statement.statements[0].true_statement.statements[0], ast.IfStatement):
                            continue
                        if always.statement.statements[0].true_statement.statements[0].left.var.name=="ap_ready":
                            always.statement.statements[0].true_statement.statements[0].left.var.name = "ap_ready_pre"
                            if isinstance(always.statement.statements[0].false_statement, ast.IfStatement):
                                always.statement.statements[0].false_statement.true_statement.statements[0].left.var.name = "ap_ready_pre"
                                always.statement.statements[0].false_statement.false_statement.statements[0].left.var.name = "ap_ready_pre"
                            else:
                                always.statement.statements[0].false_statement.statements[0].left.var.name = "ap_ready_pre"
                            break

        new_always =     ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                    ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                      ast.IntConst("1'b1")),
                                                               ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_ready"),
                                                                                                      ast.IntConst("1'b0"))]),
                                                               ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_ready"),
                                                                                                      ast.Identifier("ap_ready_pre"))]))]))
    
        module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
        for module_def in module_defs:
            break
        item_list = list(module_def.items)
        for item_idx in range(len(item_list)):
            if isinstance(item_list[item_idx], ast.Decl):
                break

        item_list = item_list[0:item_idx] + add_decl + item_list[item_idx:]
        item_list += [new_always]
        module_def.items = tuple(item_list)
                

        rtl_generator = ASTCodeGenerator()
        new_rtl = [rtl_generator.visit(top_module_ast)]
        with open(file_path, 'w') as f:
            for line in new_rtl:
                f.write(line)

def ap_start_mdf(file_path):
    #pdb.set_trace()
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]

    in_port_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Input))
    have_port = 0
    for in_port in in_port_lst:
        if in_port.name=="ap_start":
            have_port = 1
            break
    if have_port==0:
        return 

    inst_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Instance))
    last_inst_line = 0
    for inst in inst_lst:
        if inst.lineno>last_inst_line:
            last_inst_line = inst.lineno
        
    # replace ap_start with ap_start_d
    with open(file_path, "r") as f:
        lines = f.read()
    inst_done = 0
    for line in lines[last_inst_line:]:
        if inst_done==0:
            if ");" in line:
                inst_done = 1
                continue
            continue
        else:
            if "ap_start" in line:
                line.replace("ap_start", "ap_start_d")
            
    # generate ap_start_d
    # always @(posedge ap_clk)
    # begin
    #     if(ap_rst==1'b1)
    #     begin
    #         ap_start_d      <=      1'b0;
    #     end
    #     else
    #     begin
    #         if(ap_ready_pre | ap_ready)
    #         begin
    #             ap_start_d  <=      1'b0;
    #         end
    #         else
    #         begin
    #             ap_start_d  <=      ap_start;
    #         end
    #     end
    # end
        
    new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                            ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                              ast.IntConst("1'b1")),
                                                       ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d"),
                                                                                              ast.IntConst("1'b0"))]),
                                                       ast.Block([ast.IfStatement(ast.Or(ast.Identifier("ap_ready_pre"),
                                                                                         ast.Identifier("ap_ready")),
                                                                                  ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d"),
                                                                                                                         ast.IntConst("1'b0"))]),
                                                                                  ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d"),
                                                                                                                         ast.Identifier("ap_start"))]))]))]))
    new_def = ast.Decl([ast.Reg("ap_start_d")])
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    for item_idx in range(len(item_list)):
        if isinstance(item_list[item_idx], ast.Decl):
            break

    item_list = item_list[0:item_idx] + [new_def] + item_list[item_idx:]
    item_list += [new_always]
    module_def.items = tuple(item_list)
            

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)


#    
#rtl_path = "/Projects/jiawei/workspace/AutoClock_v2/benchmark/P1MC_cdc_floorplan_arst/_x_temp.hw.xilinx_u280_gen3x16_xdma_1_202211_1/top/top/top/solution/syn/verilog/"
def if_mdf(rtl_path):
    files = [os.path.join(rtl_path, file) for file in os.listdir(rtl_path)]
    for file in files:
        if file[-1]!="v":
            continue
        if "top_icmp_512ns_512ns_1_2_1.v" in file:
            continue
        if "fifo" in file:
            continue
        if "axi" in file:
            continue
        if "kernelJpegDecoder_udiv_13ns_8ns_13_17_seq_1" in file:
            continue
        print(file)
        ap_done_mdf(file)
        ap_ready_mdf(file)
        ap_start_mdf(file)
