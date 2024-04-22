import re

def extract_clk_domains(file_path):
    clk_domains = []
    periods = []
    modules = []

    # extract HLS pragma
    pattern = r'\s*#pragma \s*HLS \s*clkdomain \s*(\w+(?:_\w+)*)\s+(\d+(?:\s+\d+)*)'
    with open(file_path, 'r') as file:
        for line in file:
            # remove comment lines
            if line.strip().startswith("//"):
                continue
            match = re.match(pattern, line)
            if match:
                # divide clk_domain and period. It should be noted that the period is a 
                # string which might contains more than one period. If there are more 
                # than one period, it can be split into a list.
                clk_domain = match.group(1)
                period = match.group(2)
                clk_domains.append(clk_domain)
                periods.append(period)
				
                # check the function name
                next_line = file.readline()
                while next_line.strip() == "" or re.match(r"\s*#pragma \s*HLS*",next_line):
                    next_line = file.readline()
                module_match = re.search(r"\b(\w+)\s*\(", next_line)
                if module_match:
                    module = module_match.group(1)
                    modules.append(module)
                else:
                    modules.append("Unknown")

        domains, modules = clk_domains_map(clk_domains, periods, modules)

    return domains, modules

def clk_domains_map(clk_domains, periods, modules):
    num_domains = len(clk_domains)

    module_clk_map = {}
    clk_period_map = {}

    for i in range(num_domains):
        module_clk_map[modules[i]] = clk_domains[i]
        clk_period_map[clk_domains[i]] = periods[i]

    return clk_period_map, module_clk_map
        
