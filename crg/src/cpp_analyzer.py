import re
import os
import networkx as nx
import matplotlib.pyplot as plt

class CPPFunctionAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.functions = self._extract_functions()
        self.function_calls_cache = {}
        
    def _extract_functions(self):
        content = ""
        
        if self.file_path:
            try:
                with open(self.file_path, 'r') as f:
                    content = f.read()
                print(f"Read code from file: {self.file_path}")
            except Exception as e:
                print(f"Error reading file: {e}")
                return {}
        elif self.code_string:
            content = self.code_string
            print("Using provided code string")
        else:
            print("No code source provided")
            return {}
        
        content = re.sub(r'//.*?\n|/\*.*?\*/', '', content, flags=re.DOTALL)
        function_pattern = r'([\w\s\*]+)\s+(\w+)\s*\(([^)]*)\)\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\})'
        matches = re.finditer(function_pattern, content)
        functions = {}
        for match in matches:
            return_type = match.group(1).strip()
            function_name = match.group(2).strip()
            params = match.group(3).strip()
            body = match.group(4)
            if function_name in ['if', 'for', 'while', 'switch', 'else', 'do']:
                continue
            
            functions[function_name] = {
                'return_type': return_type,
                'params': params,
                'body': body,
                'calls': []
            }
        
        cpp_keywords = [
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'goto', 'sizeof', 'typedef',
            'struct', 'class', 'enum', 'union', 'const', 'static', 'extern',
            'volatile', 'register', 'auto', 'inline', 'virtual', 'explicit',
            'new', 'delete', 'try', 'catch', 'throw', 'template', 'namespace',
            'using', 'public', 'private', 'protected', 'friend', 'operator'
        ]
        
        for func_name, func_info in functions.items():
            body = func_info['body']
            
            call_pattern = r'\b(\w+)\s*\('
            
            for match in re.finditer(call_pattern, body):
                potential_call = match.group(1).strip()
                
                if (potential_call not in cpp_keywords and
                    potential_call != func_name):
                    
                    start_pos = match.end() - 1
                    end_pos = start_pos + 1
                    bracket_level = 1
                    
                    while end_pos < len(body) and bracket_level > 0:
                        if body[end_pos] == '(':
                            bracket_level += 1
                        elif body[end_pos] == ')':
                            bracket_level -= 1
                        end_pos += 1
                    
                    if bracket_level == 0:
                        args = body[start_pos+1:end_pos-1].strip()
                        
                        signal_width = 0
                        if args:
                            bracket_level = 0
                            current_arg = ""
                            arg_list = []
                            
                            for char in args:
                                if char == '(':
                                    bracket_level += 1
                                elif char == ')':
                                    bracket_level -= 1
                                
                                if char == ',' and bracket_level == 0:
                                    arg_list.append(current_arg.strip())
                                    current_arg = ""
                                else:
                                    current_arg += char
                            
                            if current_arg.strip():
                                arg_list.append(current_arg.strip())
                            
                            signal_width = len(arg_list)
                        
                        context_before = body[:match.start()].strip()
                        last_relevant_chars = re.findall(r'[=;{]', context_before[-20:] if len(context_before) > 20 else context_before)
                        
                        is_likely_function = True
                        if last_relevant_chars:
                            last_char = last_relevant_chars[-1]
                            if last_char == '=':
                                is_likely_function = False
                        
                        if is_likely_function:
                            func_info['calls'].append({
                                'function': potential_call,
                                'args': args,
                                'signal_width': signal_width
                            })
        
        all_called_functions = set()
        for func_info in functions.values():
            for call in func_info['calls']:
                all_called_functions.add(call['function'])
        
        for func_name in all_called_functions:
            if func_name not in functions:
                functions[func_name] = {
                    'return_type': 'unknown',
                    'params': '',
                    'body': '',
                    'calls': [],
                    'is_external': True
                }
        
        print(f"Extracted {len(functions)} functions")
        return functions
    
    def get_all_function_names(self):
        return list(self.functions.keys())
    
    def analyze_function_calls(self, target_function):
        if target_function not in self.functions:
            print(f"Function '{target_function}' not found in the file.")
            return None
        
        if target_function in self.function_calls_cache:
            return self.function_calls_cache[target_function]
        
        call_graph = nx.DiGraph()
        call_graph.add_node(target_function)
        
        analyzed = set()
        subfunctions_map = {}
        
        def analyze_recursive(func_name):
            if func_name in analyzed:
                return
            
            analyzed.add(func_name)
            direct_subfunctions = []
            
            if func_name not in self.functions:
                subfunctions_map[func_name] = []
                return
            
            body = self.functions[func_name]['body']
            
            for potential_call in self.functions.keys():
                if potential_call == func_name:
                    continue
                    
                call_pattern = rf'\b{potential_call}\s*\(([^)]*)\)'
                matches = list(re.finditer(call_pattern, body))
                
                if matches:
                    direct_subfunctions.append(potential_call)
                    
                    total_signal_width = 0
                    for match in matches:
                        args = match.group(1).strip()
                        signal_width = len(args.split(',')) if args else 0
                        total_signal_width += signal_width
                    
                    call_graph.add_edge(func_name, potential_call, weight=total_signal_width)
            
            subfunctions_map[func_name] = direct_subfunctions
            
            for subfunc in direct_subfunctions:
                analyze_recursive(subfunc)
        
        analyze_recursive(target_function)
        
        all_subfunctions = list(call_graph.nodes())
        all_subfunctions.remove(target_function)
        
        result = {
            'direct_subfunctions': subfunctions_map[target_function],
            'all_subfunctions': all_subfunctions,
            'subfunctions_map': subfunctions_map,
            'graph': call_graph
        }
        
        self.function_calls_cache[target_function] = result
        
        return result
    
    def visualize_call_graph(self, graph, output_file=None, highlight_function=None):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph)
        edge_weights = [graph[u][v]['weight'] for u, v in graph.edges()]
        max_weight = max(edge_weights) if edge_weights else 1
        node_colors = []
        for node in graph.nodes():
            if node == highlight_function:
                node_colors.append('red')
            elif node in graph.predecessors(highlight_function) if highlight_function else []:
                node_colors.append('orange')
            elif highlight_function and node in graph.successors(highlight_function):
                node_colors.append('green')
            else:
                node_colors.append('lightblue')
        
        nx.draw_networkx_nodes(graph, pos, node_size=700, node_color=node_colors)
        nx.draw_networkx_labels(graph, pos)
        nx.draw_networkx_edges(
            graph, 
            pos, 
            width=[1 + (w/max_weight)*5 for w in edge_weights],
            alpha=0.7,
            edge_color='gray',
            arrows=True
        )
        
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in graph.edges(data=True)}
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        
        plt.title("Function Call Graph with Signal Width")
        plt.axis('off')
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
            print(f"Graph saved to {output_file}")
