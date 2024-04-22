def gen_bufgmux(module_name):
	lst_inst = []
	lst_wire = []
	
	lst_wire.append("wire	"+module_name+"_clk_in_0;")
	lst_wire.append("wire	"+module_name+"_clk_in_1;")
	lst_wire.append("wire	"+module_name+"_clk_out;")
	lst_wire.append("wire	"+module_name+"_sel;")

	lst_inst.append("BUFGMUX "+module_name+"(")
	lst_inst.append("	.I0		("+module_name+"_clk_in_0),")
	lst_inst.append("	.I1		("+module_name+"_clk_in_1),")
	lst_inst.append("	.O		("+module_name+"_clk_out),")
	lst_inst.append("	.S		("+module_name+"_sel));")
	
	return [lst_wire, lst_inst]
