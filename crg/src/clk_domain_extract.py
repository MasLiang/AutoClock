import re
import math

def extract_clk_domains(file_path):
    clk_domains = []
    periods = []
    modules = []
    domains_sel_if = {}

    # extract HLS pragma
    input_clk_pattern = r'\s*#pragma \s*HLS \s*inputclk \s*(\w+(?:_\w+)*)\s*(\d+(?:\s+\d+)*)'
    domain_pattern = r'\s*#pragma \s*HLS \s*clkdomain \s*(\w+(?:_\w+)*)\s*(\d+(?:\s+\d+)*)'
    sel_pattern = r'\s*#pragma\s*HLS\s*clksel\s*(\w+)\s*(\w+)'
    new_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            input_clk_match = re.match(input_clk_pattern, line)
            if input_clk_match:
                clk_domain = input_clk_match.group(1)
                period = input_clk_match.group(2)
                clk_domains = [clk_domain] + clk_domains
                periods = [period] + periods
                # check the function name
                next_line = file.readline()
                while next_line.strip() == "" or re.match(r"\s*#pragma \s*HLS*",next_line):
                    next_line = file.readline()
                module_match = re.search(r"\b(\w+)\s*\(", next_line)
                if module_match:
                    module = module_match.group(1)
                    modules = [module]+modules
                    new_lines.append(next_line)
                else:
                    modules = ["Unknown"]+modules
                continue

            # remove comment lines
            if line.strip().startswith("//"):
                new_lines.append(line)
                continue
            domain_match = re.match(domain_pattern, line)
            if domain_match:
                # divide clk_domain and period. It should be noted that the period is a 
                # string which might contains more than one period. If there are more 
                # than one period, it can be split into a list.
                clk_domain = domain_match.group(1)
                period = domain_match.group(2)
                clk_domains.append(clk_domain)
                periods.append(period)
				
                next_line = file.readline()
                # extract the interface signel used for clk mux
                match_mux = re.match(sel_pattern, next_line)
                if match_mux:
                    domains_sel_if[match_mux.group(1)] = [match_mux.group(2)]
                # check the function name
                while next_line.strip() == "" or re.match(r"\s*#pragma \s*HLS*",next_line):
                    new_lines.append(next_line)
                    next_line = file.readline()
                module_match = re.search(r"\b(\w+)\s*\(", next_line)
                if module_match:
                    module = module_match.group(1)
                    modules.append(modules[0]+"_"+module)
                    if match_mux:
                        domains_sel_if[match_mux.group(1)].append(module)
                    new_lines.append(next_line)
                else:
                    modules.append("Unknown")
                continue
            new_lines.append(line)

        domains, modules = clk_domains_map(clk_domains, periods, modules)

    with open(file_path, 'w') as file:
        for line in new_lines:
            file.write(line)
    
    check_mux_if(domains_sel_if, file_path)
    domains, fastest_clk_map = cal_fastest_clk_map(domains)

    return modules, domains, domains_sel_if, fastest_clk_map

def clk_domains_map(clk_domains, periods, modules):
    num_domains = len(clk_domains)

    module_clk_map = {}
    clk_period_map = {}

    for i in range(num_domains):
        module_clk_map[modules[i]] = clk_domains[i]
        clk_period_map[clk_domains[i]] = periods[i]

    return clk_period_map, module_clk_map
        
def check_mux_if(domains_if, file_path):
    # This function is to check the clk mux interface signals
    #   the type must by ap_none, no matter what the user defined
    #   type is. If user defined other type, change it.
    #   find the clk domain -> 
    #   find the interface ->
    #   find the pragma -> 
    #   if not true, change, if no, add
    
    with open(file_path, 'r') as f:
        code = f.read()

    # code = re.sub(r'//.*?$|/\*[\s\S]*?\*/', '', code, flags=re.MULTILINE)
    
    lst_domain_sel = list(domains_if.keys())

    for domain in lst_domain_sel:
        module = domains_if[domain][1] 
        signal = domains_if[domain][0] 
        func_def_pattern = r'\b[\w\s*]+\b\s+'+re.escape(module)+r'\b\s*\([^\)]*\)\s*\{[^}]*\}'
        func = re.search(func_def_pattern, code, re.DOTALL)
        # replace incorrect pragma
        func_content = func.group(0)
        replacement = "\n    #pragma HLS INTERFACE ap_none port={}".format(re.escape(signal))
        if_pragma_pattern = r"\s*#pragma\s+HLS\s+INTERFACE\s+(\w+)\s+port\s*=\s*{}\b".format(re.escape(signal))
        new_func_content = re.sub(if_pragma_pattern, replacement, func_content)
        pragma = re.search(if_pragma_pattern, func_content, re.DOTALL)
        if pragma:
            # replace new function
            code = code.replace(func_content, new_func_content)
        else:
            # if no this pragma, insert a new line into it.
            func_name_pattern = r'\b[\w\s*]+\b\s+'+re.escape(module)+r'\b\s*\([^\)]*\)\s*\{'
            func_name_match = re.search(func_name_pattern, new_func_content)
            func_name_loc = func_name_match.end()
            new_func_content = new_func_content[:func_name_loc]+replacement+"\n"+new_func_content[func_name_loc:]
            # replace new function
            code = code.replace(func_content, new_func_content)
        
                
        
    with open(file_path, 'w') as file:
        file.write(code)
               
def cal_fastest_clk_map(domains):
    # this function is to find the fastest clk and the relationship with other clock
    fastest_clk = 0
    fastest_clk_map = []

    for domain in list(domains.keys()):
        periods = domains[domain].split()
        periods = [int(x) for x in periods]
        min_period = min(periods)
        max_period = max(periods)
        if fastest_clk==0:
            fastest_clk = min_period
        elif min_period<fastest_clk:
            fastest_clk = min_period
        fastest_clk_map.append([domain, max_period])

    fastest_clk_domain = "fastest_clk"
    for mapping_idx in range(len(fastest_clk_map)):
        mapping = fastest_clk_map[mapping_idx]
        if mapping[1]==fastest_clk:
            fastest_clk_domain = mapping[0]
            mapping[1] = 1
            rm_mapping_idx = mapping_idx
        else:
            mapping[1] = int(math.ceil(mapping[1]/fastest_clk))

    if fastest_clk_domain=="fastest_clk":
        domains = {**domains, "fastest_clk":str(fastest_clk)}
    else:
        del fastest_clk_map[rm_mapping_idx]
    fastest_clk_map = [fastest_clk_domain] + fastest_clk_map
    
    return domains, fastest_clk_map 
         
