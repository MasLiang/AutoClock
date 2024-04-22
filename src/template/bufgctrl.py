def gen_bufgctrl(module_name):
	lst_inst = []
	lst_wire = []

	lst_wire.append("wire	"+module_name+"_clk_in_0;")
	lst_wire.append("wire	"+module_name+"_clk_in_1;")
	lst_wire.append("wire	"+module_name+"_clk_out;")
	lst_wire.append("wire	"+module_name+"_ce0;")
	lst_wire.append("wire	"+module_name+"_ce1;")
	lst_wire.append("wire	"+module_name+"_ignore_0;")
	lst_wire.append("wire	"+module_name+"_ignore_1;")
	lst_wire.append("wire	"+module_name+"_sel_0;")
	lst_wire.append("wire	"+module_name+"_sel_1;")
	
	lst_inst.append("BUFGCTRL +"module_name+"(")
	lst_inst.append("	.I0			("+module_name+"_clk_in_0),")
	lst_inst.append("	.I1			("+module_name+"_clk_in_1),")
	lst_inst.append("	.O			("+module_name+"_clk_out),")
	lst_inst.append("	.CE0		("+module_name+"_ce0),")
	lst_inst.append("	.CE1		("+module_name+"_ce1),")
	lst_inst.append("	.IGNORE0	("+module_name+"_ignore_0),")
	lst_inst.append("	.IGNORE1	("+module_name+"_ignore_1),")
	lst_inst.append("	.S0			("+module_name+"_sel_0),")
	lst_inst.append("	.S1			("+module_name+"_sel_1));")

	return [lst_wire, lst_inst]
