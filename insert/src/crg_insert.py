from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from parser import *
import pyverilog.vparser.ast as ast
import os

def crg_insert(module_name, root_path):
    # read crg
    os.system("cp ../../crg/src/"+module_name+"_crg_inst.v .")
    crg_ast, _ = rtl_parse(["./"+module_name+"_crg_inst.v"])
    #os.system("rm ./"+module_name+"_crg_inst.v")
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
    top_ast, _ = rtl_parse([root_path+"/"+module_name+".v"])
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
    print(top_item_idx)
    print(top_item_list[top_item_idx])
    # fuse wires
    top_item_list = top_item_list[0:top_item_idx]+crg_item_list[0:crg_item_idx]+top_item_list[top_item_idx:]
    for iii in top_item_list:
        print("1: ", iii)
    for top_item_idx in range(len(top_item_list)):
        if isinstance(top_item_list[top_item_idx], ast.InstanceList):
            break
    # fuse instance
    top_item_list = top_item_list[0:top_item_idx]+crg_item_list[crg_item_idx:]+top_item_list[top_item_idx:]
    for iii in top_item_list:
        print("2: ", iii)
    top_module_def.items = tuple(top_item_list)
    
    # generate new rtl
    rtl_generator = ASTCodeGenerator()
    new_rtl = rtl_generator.visit(top_ast)
    with open(module_name+".v", 'w') as f:
        f.write(new_rtl) 

crg_insert("top", "./verilog/")
#cdc_insert("rwkv_top", {"rwkv_top": "clk_phy", "rwkv_top_read_all115": "clk1", "rwkv_top_layer_common_s": "clk2", "rwkv_top_write_all": "clk3"}, "../../../rwkv_src/verilog/")
