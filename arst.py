from pyverilog.vparser.parser import parse as rtl_parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as ast
import os
import sys
sys.path.append("../../")
import pdb

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

def arst_mdf(file_path):
    print(file_path)
    top_module_ast = rtl_parse([file_path])
    if len(list(top_module_ast))!=1:
        return
    always_lst = DFS(top_module_ast, lambda node: isinstance(node, ast.Always))
    for always in always_lst:
        if isinstance(always.statement.statements[0].cond.left, ast.Identifier):
            if "rst_" in always.statement.statements[0].cond.left.name:
                always.sens_list.list.append(always.sens_list.list[0])
                always.sens_list.list[1].sig.name = always.statement.statements[0].cond.left.name

    rtl_generator = ASTCodeGenerator()
    new_rtl = [rtl_generator.visit(top_module_ast)]
    with open(file_path, 'w') as f:
        for line in new_rtl:
            f.write(line)
    
rtl_path = "/Projects/jiawei/workspace/AutoClock_v2/benchmark/P1MC_cdc_floorplan_arst/_x_temp.hw.xilinx_u280_gen3x16_xdma_1_202211_1/top/top/top/solution/syn/verilog/"
files = [os.path.join(rtl_path, file) for file in os.listdir(rtl_path)]
for file in files:
    if file[-1]!="v":
        continue
    if "axi" in file:
        continue
    arst_mdf(file)
