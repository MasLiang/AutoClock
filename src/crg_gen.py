import clk_domain_check
import template
from clk_domain_analyze import clk_resource_cal
from clk_domain_check import extract_clk_domains

def crg_gen(file)
    domains, modules = extract_clk_domains(file)
    clk_map, domains = clk_resource_cal(domains)
    
    # generate pll to generate clks in domains
    
    
    # gen BUFXXX according to clk_map
    # gen div
    
    # gen bypass
    
    # gen mux


