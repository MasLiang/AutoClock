import clk_domain_check
from template import *
from clk_domain_analyze import clk_resource_cal
from clk_domain_check import extract_clk_domains

def crg_gen(file):
    domains, modules = extract_clk_domains(file)
    clk_map_mux, clk_map_bypass, clk_map_div, clk_map_mmcm = clk_resource_cal(domains)
    
    print("clk_map_mux" , clk_map_mux)
    print("clk_map_bypass" , clk_map_bypass)
    print("clk_map_div" , clk_map_div)
    print("clk_map_mmcm" , clk_map_mmcm)
    # generate pll to generate clks in domains
    
    
    
    # gen BUFXXX according to clk_map
    # gen div
    
    # gen bypass
    
    # gen mux

crg_gen("a.txt")
