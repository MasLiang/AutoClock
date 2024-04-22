def gen_bufgce(module_name):
	lst_inst = []
	lst_wire = []
	
	lst_wire.append("wire	"+module_name+"_clk_in;")
	lst_wire.append("wire	"+module_name+"_clk_out;")
	lst_wire.append("wire	"+module_name+"_ce;")

	lst_inst.append("BUFGCE "+module_name+"(")
	lst_inst.append("	.I			("+module_name+"_clk_in),")
	lst_inst.append("	.O			("+module_name+"_clk_out),")
	lst_inst.append("	.CE			("+module_name+"_ce));")
	
	return [lst_wire, lst_inst]
