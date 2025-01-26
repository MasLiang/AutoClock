from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as ast
import os
import sys
sys.path.append("../../")
from .rtl_parser import *
import pdb

def ap_done_mdf_nocontinue(file_path, num_cycle):
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
    wire_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Wire))
    continue_int_def = 0
    for wire in wire_lst:
        if wire.name=="ap_done":
            continue_int_def = 1
            break
    if continue_int_def==0:
        ap_done_mdf_nocontinue_no_int(top_module_ast, num_cycle)
    else:
        ap_done_mdf_continue_int(top_module_ast, num_cycle)

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)

def ap_done_mdf_nocontinue_no_int(top_module_ast, num_cycle):
    #pdb.set_trace()
    add_decl = []
    rm_decl_name = []
    reg_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Reg))
    reg_def = 0
    
    for reg in reg_lst:
        if reg.name=="ap_done":
            reg_def = 1
            break
    if reg_def==0:
        # this "ap_done" is a wire, maintain
        if num_cycle==1:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d")])
        else:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_done_pre_decl = ast.Decl([ast.Wire("ap_done_pre")])
        ap_done_pulse_decl = ast.Decl([ast.Wire("ap_done_pre_pulse")])
        ap_done_out_d_decl = ast.Decl([ast.Reg("ap_done_out_d")])
        add_decl.append(ap_done_reg_decl)
        add_decl.append(ap_done_pre_decl)
        add_decl.append(ap_done_pulse_decl)
        add_decl.append(ap_done_out_d_decl)
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
        # this "ap_done" is a reg, replace it with a wire
        if num_cycle==1:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d")])
        else:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_done_pre_decl = ast.Decl([ast.Reg("ap_done_pre")])
        ap_done_pulse_decl = ast.Decl([ast.Wire("ap_done_pre_pulse")])
        ap_done_out_d_decl = ast.Decl([ast.Reg("ap_done_out_d")])
        ap_done_decl = ast.Decl([ast.Wire("ap_done")])
        add_decl.append(ap_done_pre_decl)
        add_decl.append(ap_done_decl)
        add_decl.append(ap_done_reg_decl)
        add_decl.append(ap_done_pulse_decl)
        add_decl.append(ap_done_out_d_decl)
        rm_decl_name.append("ap_done")
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

    if num_cycle==1:
        pulse_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done_pre_pulse")), 
                                  ast.Rvalue(ast.And(ast.Identifier("ap_done_pre"),
                                                     ast.Eq(ast.Identifier("ap_done_pre_d"),
                                                            ast.IntConst("1'b0")))))

        out_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done")),
                                ast.Rvalue(ast.And(ast.Identifier("ap_done_pre_d"),
                                                   ast.Eq(ast.Identifier("ap_start"),
                                                          ast.IntConst("1'b0")))))

        dly_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
                                                                                                  ast.Identifier("ap_done_pre"))]))]))

        #always @(posedge ap_clk)
        #begin
        #    if (ap_rst==1'b1)
        #    begin
        #        ap_done_out_d     <=      1'b0;
        #    end
        #    else 
        #    begin
        #        if (ap_done_pre_pulse==1'b1)
        #            ap_done_out_d     <=      1'b1;
        #        else
        #        begin
        #            if (start)
        #            begin
        #                ap_done_out_d     <=      1'b0;
        #            end
        #            else
        #            begin
        #                ap_done_out_d     <=      ap_done_out_d;
        #            end
        #        end
        #    end
        #end
        gen_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_out_d"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_done_pre_pulse"),
                                                                                             ast.IntConst("1'b1")),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_out_d"),
                                                                                                 ast.IntConst("1'b1"))]),
                                                                                      ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_start"),
                                                                                                                        ast.IntConst("1'b1")),
                                                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_out_d"),
                                                                                                                            ast.IntConst("1'b0"))]),
                                                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_out_d"),
                                                                                                                        ast.Identifier("ap_done_out_d"))]))]))]))]))
   
    #else:
    #   new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
    #                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
    #                                                             ast.IntConst("1'b1")),
    #                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
    #                                                                                             ast.IntConst(str(num_cycle)+"'b0"))]),
    #                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
    #                                                                                             ast.Concat([ast.Partselect(ast.Identifier("ap_done_pre_d"),ast.IntConst(num_cycle-2),ast.IntConst(0)),
    #                                                                                                         ast.Identifier("ap_done_pre")]))]))]))

    #   new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done")), ast.Rvalue(ast.Pointer(ast.Identifier("ap_done_pre_d"),ast.IntConst(num_cycle-1))))
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    decl_flg = 0
    decl_start_idx = 0
    rm_decl = []
    for item_idx in range(len(item_list)):
        if decl_flg==0:
            if isinstance(item_list[item_idx], ast.Decl):
                decl_flg = 1
                decl_start_idx = item_idx
                if rm_decl_name==[]:
                    continue
                if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                    rm_decl.append(item_list[item_idx])
                    break
        else:
            if not isinstance(item_list[item_idx], ast.Decl):
                break
            if rm_decl_name==[]:
                break
            if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                rm_decl.append(item_list[item_idx])
                break

    if decl_start_idx==0:
        item_list = add_decl + item_list
    else:
        item_list = item_list[0:decl_start_idx] + add_decl + item_list[decl_start_idx:]
    item_list += [dly_always, gen_always, pulse_assign, out_assign]
            
    for rm_item in rm_decl:
        item_list.remove(rm_item)

    module_def.items = tuple(item_list)

def ap_done_mdf_continue_int(top_module_ast, num_cycle):
    #pdb.set_trace()
    add_decl = []
    rm_decl_name = []
    reg_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Reg))
    reg_def = 0
    for reg in reg_lst:
        if reg.name=="ap_done":
            reg_def = 1
            break
    if reg_def==0:
        # this "ap_done" is a wire, replace it with a reg
        if num_cycle==1:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d")])
        else:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_done_pre_decl = ast.Decl([ast.Wire("ap_done_pre")])
        ap_done_pulse_decl = ast.Decl([ast.Wire("ap_done_pre_pulse")])
        ap_done_decl = ast.Decl([ast.Reg("ap_done")])
        add_decl.append(ap_done_reg_decl)
        add_decl.append(ap_done_pre_decl)
        add_decl.append(ap_done_decl)
        add_decl.append(ap_done_pulse_decl)
        rm_decl_name.append("ap_done")
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
        # this "ap_done" is a reg, maintain it
        if num_cycle==1:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d")])
        else:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_done_pre_decl = ast.Decl([ast.Reg("ap_done_pre")])
        ap_done_pulse_decl = ast.Decl([ast.Wire("ap_done_pre_pulse")])
        add_decl.append(ap_done_pre_decl)
        add_decl.append(ap_done_reg_decl)
        add_decl.append(ap_done_pulse_decl)
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

    if num_cycle==1:
        new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done_pre_pulse")), 
                                ast.Rvalue(ast.And(ast.Identifier("ap_done_pre"),
                                                   ast.Eq(ast.Identifier("ap_done_pre_d"),
                                                          ast.IntConst("1'b0")))))
        dly_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
                                                                                                  ast.Identifier("ap_done_pre"))]))]))

        #always @(posedge ap_clk)
        #begin
        #    if (ap_rst==1'b1)
        #    begin
        #        ap_done     <=      1'b0;
        #    end
        #    else 
        #    begin
        #        if (ap_done_pre_pulse==1'b1)
        #            ap_done     <=      1'b1;
        #        else
        #        begin
        #            if (ap_continue_int)
        #            begin
        #                ap_done     <=      1'b0;
        #            end
        #            else
        #            begin
        #                ap_done     <=      ap_done;
        #            end
        #        end
        #    end
        #end
        gen_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_done_pre_pulse"),
                                                                                             ast.IntConst("1'b1")),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                 ast.IntConst("1'b1"))]),
                                                                                      ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_continue_int"),
                                                                                                                        ast.IntConst("1'b1")),
                                                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                                            ast.IntConst("1'b0"))]),
                                                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                                            ast.Identifier("ap_done"))]))]))]))]))
   
    #else:
    #   new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
    #                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
    #                                                             ast.IntConst("1'b1")),
    #                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
    #                                                                                             ast.IntConst(str(num_cycle)+"'b0"))]),
    #                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
    #                                                                                             ast.Concat([ast.Partselect(ast.Identifier("ap_done_pre_d"),ast.IntConst(num_cycle-2),ast.IntConst(0)),
    #                                                                                                         ast.Identifier("ap_done_pre")]))]))]))

    #   new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done")), ast.Rvalue(ast.Pointer(ast.Identifier("ap_done_pre_d"),ast.IntConst(num_cycle-1))))
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    decl_flg = 0
    decl_start_idx = 0
    rm_decl = []
    for item_idx in range(len(item_list)):
        if decl_flg==0:
            if isinstance(item_list[item_idx], ast.Decl):
                decl_flg = 1
                decl_start_idx = item_idx
                if rm_decl_name==[]:
                    continue
                if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                    rm_decl.append(item_list[item_idx])
                    break
        else:
            if not isinstance(item_list[item_idx], ast.Decl):
                break
            if rm_decl_name==[]:
                break
            if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                rm_decl.append(item_list[item_idx])
                break

    if decl_start_idx==0:
        item_list = add_decl + item_list
    else:
        item_list = item_list[0:decl_start_idx] + add_decl + item_list[decl_start_idx:]
    item_list += [dly_always, gen_always, new_assign]
            
    for rm_item in rm_decl:
        item_list.remove(rm_item)

    module_def.items = tuple(item_list)


def ap_done_mdf_continue(file_path, num_cycle):
    #pdb.set_trace()
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
    add_decl = []
    rm_decl_name = []
    reg_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Reg))
    reg_def = 0
    for reg in reg_lst:
        if reg.name=="ap_done":
            reg_def = 1
            break
    if reg_def==0:
        # this "ap_done" is a wire, replace it with a reg
        if num_cycle==1:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d")])
        else:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_done_pre_decl = ast.Decl([ast.Wire("ap_done_pre")])
        ap_done_pulse_decl = ast.Decl([ast.Wire("ap_done_pre_pulse")])
        ap_done_decl = ast.Decl([ast.Reg("ap_done")])
        add_decl.append(ap_done_reg_decl)
        add_decl.append(ap_done_pre_decl)
        add_decl.append(ap_done_decl)
        add_decl.append(ap_done_pulse_decl)
        rm_decl_name.append("ap_done")
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
        # this "ap_done" is a reg, maintain it
        if num_cycle==1:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d")])
        else:
            ap_done_reg_decl = ast.Decl([ast.Reg("ap_done_pre_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_done_pre_decl = ast.Decl([ast.Reg("ap_done_pre")])
        ap_done_pulse_decl = ast.Decl([ast.Wire("ap_done_pre_pulse")])
        add_decl.append(ap_done_pre_decl)
        add_decl.append(ap_done_reg_decl)
        add_decl.append(ap_done_pulse_decl)
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

    if num_cycle==1:
        new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done_pre_pulse")), 
                                ast.Rvalue(ast.And(ast.Identifier("ap_done_pre"),
                                                   ast.Eq(ast.Identifier("ap_done_pre_d"),
                                                          ast.IntConst("1'b0")))))
        dly_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
                                                                                                  ast.Identifier("ap_done_pre"))]))]))

        #always @(posedge ap_clk)
        #begin
        #    if (ap_rst==1'b1)
        #    begin
        #        ap_done     <=      1'b0;
        #    end
        #    else 
        #    begin
        #        if (ap_done_pre_pulse==1'b1)
        #            ap_done     <=      1'b1;
        #        else
        #        begin
        #            if (ap_continue)
        #            begin
        #                ap_done     <=      1'b0;
        #            end
        #            else
        #            begin
        #                ap_done     <=      ap_done;
        #            end
        #        end
        #    end
        #end
        gen_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_done_pre_pulse"),
                                                                                             ast.IntConst("1'b1")),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                 ast.IntConst("1'b1"))]),
                                                                                      ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_continue"),
                                                                                                                        ast.IntConst("1'b1")),
                                                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                                            ast.IntConst("1'b0"))]),
                                                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done"),
                                                                                                                            ast.Identifier("ap_done"))]))]))]))]))
   
    #else:
    #   new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
    #                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
    #                                                             ast.IntConst("1'b1")),
    #                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
    #                                                                                             ast.IntConst(str(num_cycle)+"'b0"))]),
    #                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_done_pre_d"),
    #                                                                                             ast.Concat([ast.Partselect(ast.Identifier("ap_done_pre_d"),ast.IntConst(num_cycle-2),ast.IntConst(0)),
    #                                                                                                         ast.Identifier("ap_done_pre")]))]))]))

    #   new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_done")), ast.Rvalue(ast.Pointer(ast.Identifier("ap_done_pre_d"),ast.IntConst(num_cycle-1))))
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    decl_flg = 0
    decl_start_idx = 0
    rm_decl = []
    for item_idx in range(len(item_list)):
        if decl_flg==0:
            if isinstance(item_list[item_idx], ast.Decl):
                decl_flg = 1
                decl_start_idx = item_idx
                if rm_decl_name==[]:
                    continue
                if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                    rm_decl.append(item_list[item_idx])
                    break
        else:
            if not isinstance(item_list[item_idx], ast.Decl):
                break
            if rm_decl_name==[]:
                break
            if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                rm_decl.append(item_list[item_idx])
                break

    if decl_start_idx==0:
        item_list = add_decl + item_list
    else:
        item_list = item_list[0:decl_start_idx] + add_decl + item_list[decl_start_idx:]
    item_list += [dly_always, gen_always, new_assign]
            
    for rm_item in rm_decl:
        item_list.remove(rm_item)

    module_def.items = tuple(item_list)

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)


def ap_ready_mdf(file_path, num_cycle):
    #pdb.set_trace()
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
    add_decl = []
    rm_decl_name = []
    reg_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Reg))
    reg_def = 0
    for reg in reg_lst:
        if reg.name=="ap_ready":
            reg_def = 1
            break
    if reg_def==0:
        # this "ap_ready" is a wire, no need to change
        if num_cycle==1:
            ap_ready_reg_decl = ast.Decl([ast.Reg("ap_ready_d")])
        else:
            ap_ready_reg_decl = ast.Decl([ast.Reg("ap_ready_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
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
        # this "ap_ready" is a reg, replace it by a wire
        if num_cycle==1:
            ap_ready_reg_decl = ast.Decl([ast.Reg("ap_ready_d")])
        else:
            ap_ready_reg_decl = ast.Decl([ast.Reg("ap_ready_d", ast.Width(ast.IntConst(0), ast.IntConst(num_cycle-1)))])
        ap_ready_wire_decl = ast.Decl([ast.Wire("ap_ready")])
        ap_ready_pre_decl = ast.Decl([ast.Reg("ap_ready_pre")])
        add_decl.append(ap_ready_pre_decl)
        add_decl.append(ap_ready_reg_decl)
        add_decl.append(ap_ready_wire_decl)
        rm_decl_name.append("ap_ready")
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

    if num_cycle==1:
        new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_ready_d"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_ready_d"),
                                                                                                  ast.Identifier("ap_ready_pre"))]))]))

        new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_ready")), ast.Rvalue(ast.Identifier("ap_ready_d")))
    
    else:
        new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_ready_d"),
                                                                                                  ast.IntConst(str(num_cycle)+"'b0"))]),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_ready_d"),
                                                                                                  ast.Concat([ast.Partselect(ast.Identifier("ap_ready_d"),ast.IntConst(num_cycle-2),ast.IntConst(0)),
                                                                                                              ast.Identifier("ap_ready_pre")]))]))]))

        new_assign = ast.Assign(ast.Lvalue(ast.Identifier("ap_ready")), ast.Rvalue(ast.Pointer(ast.Identifier("ap_ready_d"),ast.IntConst(str(num_cycle-1)))))
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    decl_flg = 0
    decl_start_idx = 0
    #pdb.set_trace()
    rm_decl = []
    for item_idx in range(len(item_list)):
        if decl_flg==0:
            if isinstance(item_list[item_idx], ast.Decl):
                decl_flg = 1
                decl_start_idx = item_idx
                if rm_decl_name==[]:
                    continue
                if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                    rm_decl.append(item_list[item_idx])
                    break
        else:
            if not isinstance(item_list[item_idx], ast.Decl):
                break
            if rm_decl_name==[]:
                break
            if item_list[item_idx].list[0].name in rm_decl_name and isinstance(item_list[item_idx].list[0], ast.Reg):
                rm_decl.append(item_list[item_idx])
                break

    if decl_start_idx==0:
        item_list = add_decl + item_list
    else:
        item_list = item_list[0:decl_start_idx] + add_decl + item_list[decl_start_idx:]
    item_list += [new_always, new_assign]
            
    #pdb.set_trace()
    for rm_item in rm_decl:
        item_list.remove(rm_item)

    module_def.items = tuple(item_list)

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)

def ap_start_mdf(file_path, num_cycle):
    #pdb.set_trace()
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]

    decl_list = DFS(top_module_ast, lambda node: isinstance(node, ast.Decl))
    last_decl_line = 0
    for decl in decl_list:
        if decl.lineno>last_decl_line:
            last_decl_line = decl.lineno

    # replace ap_start with ap_start_d
    with open(file_path, "r") as f:
        lines = f.readlines()
    inst_done = 0
    new_lines = lines[:last_decl_line]
    for line in lines[last_decl_line:]:
        if " ap_start " in line:
            line = line.replace(" ap_start ", " ap_start_d_"+str(num_cycle-1)+" ")
            new_lines.append(line)
        elif " ap_start;" in line:
            line = line.replace(" ap_start;", " ap_start_d_"+str(num_cycle-1)+";")
            new_lines.append(line)
        elif " ap_start)" in line:
            line = line.replace(" ap_start)", " ap_start_d_"+str(num_cycle-1)+")")
            new_lines.append(line)
        elif "(ap_start)" in line:
            line = line.replace("(ap_start)", "(ap_start_d_"+str(num_cycle-1)+")")
            new_lines.append(line)
        elif "(ap_start" in line:
            line = line.replace("(ap_start ", "(ap_start_d_"+str(num_cycle-1)+" ")
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)
            

    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
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
    add_always = []
    add_def = []
        
    if num_cycle==1:
        new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_0"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.IfStatement(ast.Or(ast.Identifier("ap_ready_pre"),
                                                                                             ast.Identifier("ap_ready_d")),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_0"),
                                                                                                                             ast.IntConst("1'b0"))]),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_0"),
                                                                                                                             ast.Identifier("ap_start"))]))]))]))
    else:
        new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_0"),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.IfStatement(ast.Or(ast.Identifier("ap_ready_pre"),
                                                                                             ast.Identifier("ap_ready_d[0]")),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_0"),
                                                                                                                             ast.IntConst("1'b0"))]),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_0"),
                                                                                                                             ast.Identifier("ap_start"))]))]))]))
    new_def = ast.Decl([ast.Reg("ap_start_d_0")])
    add_always.append(new_always)
    add_def.append(new_def)
    for idx_cycle in range(1,num_cycle):
        new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                                ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                                  ast.IntConst("1'b1")),
                                                           ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_"+str(idx_cycle)),
                                                                                                  ast.IntConst("1'b0"))]),
                                                           ast.Block([ast.IfStatement(ast.Or(ast.Identifier("ap_ready_d["+str(idx_cycle-1)+"]"),
                                                                                             ast.Identifier("ap_ready_d["+str(idx_cycle)+"]")),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_"+str(idx_cycle)),
                                                                                                                             ast.IntConst("1'b0"))]),
                                                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_start_d_"+str(idx_cycle)),
                                                                                                                             ast.Identifier("ap_start_"+str(idx_cycle-1)))]))]))]))
        new_def = ast.Decl([ast.Reg("ap_start_d_"+str(idx_cycle))])
        add_always.append(new_always)
        add_def.append(new_def)       
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    for item_idx in range(len(item_list)):
        if isinstance(item_list[item_idx], ast.Decl):
            break

    item_list = item_list[0:item_idx] + add_def + item_list[item_idx:] + add_always
    module_def.items = tuple(item_list)
            

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)

def ap_continue_mdf(file_path):
    #always @(posedge ap_clk)
    #begin
    #    if (ap_rst==1'b1)
    #    begin
    #        ap_continue_d <= 1'b0;
    #    end
    #    else
    #    begin
    #        if (ap_continue_d)
    #        begin
    #            ap_continue_d   <=  1'b0;
    #        end
    #        else
    #        begin
    #            if(ap_done & ap_continue)
    #                ap_continue_d       <=      1'b1;
    #        end
    #    end
    #end
    
    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]

    in_port_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Input))
    have_port = 0
    for in_port in in_port_lst:
        if in_port.name=="ap_continue":
            have_port = 1
            break
    if have_port==0:
        return 

    decl_list = DFS(top_module_ast, lambda node: isinstance(node, ast.Decl))
    last_decl_line = 0
    for decl in decl_list:
        if decl.lineno>last_decl_line:
            last_decl_line = decl.lineno

    # replace ap_continue with ap_continue_d
    with open(file_path, "r") as f:
        lines = f.readlines()
    inst_done = 0
    new_lines = lines[:last_decl_line]
    for line in lines[last_decl_line:]:
        if " ap_continue;" in line:
            line = line.replace(" ap_continue;", " ap_continue_d;")
            new_lines.append(line)
        elif "(ap_continue)" in line:
            line = line.replace("(ap_continue)", "(ap_continue_d)")
            new_lines.append(line)
        elif "(ap_continue" in line:
            line = line.replace("(ap_continue ", "(ap_continue_d ")
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)
            

    top_module_ast = rtl_parse([file_path])
    top_module_ast = top_module_ast[0]
    add_always = []
    add_def = []
        
    new_always = ast.Always(ast.SensList([ast.Sens(ast.Identifier("ap_clk"))]),
                           ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_rst"),
                                                             ast.IntConst("1'b1")),
                                                      ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_continue_d"),
                                                                                             ast.IntConst("1'b0"))]),
                                                      ast.Block([ast.IfStatement(ast.Eq(ast.Identifier("ap_continue_d"),
                                                                                        ast.IntConst("1'b1")),
                                                                                 ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_continue_d"),
                                                                                                                        ast.IntConst("1'b0"))]),
                                                                                 ast.Block([ast.IfStatement(ast.And(ast.Identifier("ap_continue"),
                                                                                                                    ast.Identifier("ap_done")),
                                                                                                            ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_continue_d"),
                                                                                                                                                   ast.IntConst("1'b1"))]),
                                                                                                            ast.Block([ast.NonblockingSubstitution(ast.Identifier("ap_continue_d"),
                                                                                                                                                   ast.IntConst("1'b0"))]))]))]))]))

    new_def = ast.Decl([ast.Reg("ap_continue_d")])
    add_always.append(new_always)
    add_def.append(new_def)
    
    module_defs = DFS(top_module_ast, lambda node: isinstance(node, ast.ModuleDef))
    for module_def in module_defs:
        break
    item_list = list(module_def.items)
    for item_idx in range(len(item_list)):
        if isinstance(item_list[item_idx], ast.Decl):
            break

    item_list = item_list[0:item_idx] + add_def + item_list[item_idx:] + add_always
    module_def.items = tuple(item_list)
            

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)

#rtl_path = "/Projects/jiawei/workspace/AutoClock_v2/benchmark/P1MC_cdc_floorplan_arst/_x_temp.hw.xilinx_u280_gen3x16_xdma_1_202211_1/top/top/top/solution/syn/verilog/"
def if_mdf(rtl_path, top_module, num_cycle, max_level):
    #files = [os.path.join(rtl_path, file) for file in os.listdir(rtl_path)]
    #for file in files:
    #    if file[-1]!="v":
    #        continue
    #    if "top_icmp_512ns_512ns_1_2_1.v" in file:
    #        continue
    #    if "fifo" in file:
    #        continue
    #    if "axi" in file:
    #        continue
    #    if "kernelJpegDecoder_udiv_13ns_8ns_13_17_seq_1" in file:
    #        continue
    #    print(file)
    #    ap_done_mdf(file,num_cycle)
    #    ap_ready_mdf(file,num_cycle)
    #    ap_start_mdf(file,num_cycle)
    #    ap_continue_mdf(file)

    module_list = [[], []]
    pi_flg = 0
    po_flg = 1
    level = 0
    top_module_name_len = len(top_module)
    
    top_module_path = rtl_path+"/"+top_module+".v"
    top_module_ast = rtl_parse([top_module_path])
    top_module_ast = top_module_ast[0]
    out_port_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Output))
    have_done_port = 0
    have_start_port = 0
    have_ready_port = 0
    have_continue_port = 0
    for out_port in out_port_lst:
        if out_port.name=="ap_done":
            have_done_port = 1
        elif out_port.name=="ap_start":
            have_start_port = 1
        elif out_port.name=="ap_continue":
            have_continue_port = 1
        elif out_port.name=="ap_ready":
            have_ready_port = 1
        
    module_list[pi_flg].append([top_module, have_done_port, have_start_port, have_ready_port, have_continue_port])  
    
    module_dealed = []
    while 1:
        curr_module_list = module_list[pi_flg]
        nxt_module_list = module_list[po_flg]
        curr_module_num = len(curr_module_list)
        nxt_module_num = len(nxt_module_list)
        if curr_module_num ==0 and nxt_module_num==0:
            break

        for _ in range(curr_module_num):
            curr_module = curr_module_list.pop(0)
            if curr_module in module_dealed:
                continue
            module_dealed.append(curr_module)
            curr_module_path = rtl_path+"/"+curr_module[0]+".v"
            if not os.path.exists(curr_module_path):
                continue
            if curr_module[4]:
                ap_continue_mdf(curr_module_path)
            if curr_module[3]:
                ap_ready_mdf(curr_module_path, num_cycle)
            if curr_module[2]:
                ap_start_mdf(curr_module_path, num_cycle)
            if curr_module[1]:
                if curr_module[4]:
                    ap_done_mdf_continue(curr_module_path, num_cycle)
                else:       
                    ap_done_mdf_nocontinue(curr_module_path, num_cycle)
            curr_module_ast = rtl_parse([curr_module_path])
            curr_module_ast = curr_module_ast[0]
 
            for inst in DFS(curr_module_ast, lambda node :  isinstance(node, ast.Instance)):
                have_done_port = 0
                have_start_port = 0
                have_ready_port = 0
                have_continue_port = 0
                for portarg in inst.portlist:
                    if portarg.portname=="ap_start":
                        have_start_port = 1
                    elif portarg.portname=="ap_ready":
                        have_ready_port = 1
                    elif portarg.portname=="ap_done":
                        have_done_port = 1
                    elif portarg.portname=="ap_continue":
                        have_continue_port = 1
                        # skip those modules that ap_continue=1
                        argname = portarg.argname.name
                        for assign in DFS(curr_module_ast, lambda node: isinstance(node, ast.Assign)):
                            if assign.left.var.name==portarg.argname.name:
                                if isinstance(assign.left, ast.IntConst):
                                    have_continue_port = 0
                    if portarg.portname=="ap_start_int":
                        # this module is a ctrl module, used to deal with ap_ctrl interface
                        have_done_port = 0
                        have_start_port = 0
                        have_ready_port = 0
                        have_continue_port = 0
                        break
                        

                if "top_icmp_512ns_512ns_1_2_1.v" in inst.module:
                    continue
                if "fifo" in inst.module:
                    continue
                if "axi" in inst.module:
                    continue
                if "kernelJpegDecoder_udiv_13ns_8ns_13_17_seq_1" in inst.module:
                    continue
                if have_start_port==0 and have_ready_port==0 and have_ready_port==0 and have_continue_port==0:
                    continue
                nxt_module_list.append([inst.module, have_done_port, have_start_port, have_ready_port, have_continue_port])
    
        level += 1
        if level==max_level:
            return
        tmp_flg = pi_flg
        pi_flg = po_flg
        po_flg = tmp_flg
    
    
