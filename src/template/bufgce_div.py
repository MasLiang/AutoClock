def gen_bufgce_div(module_name, div_fac):
	lst_wire = []
	lst_inst = []
	
	lst_inst.append("wire	"+module_name+"_o;")
	lst_inst.append("wire	"+module_name+"_ce;")
	lst_inst.append("wire	"+module_name+"_clr;")
	lst_inst.append("wire	"+module_name+"_i;")

	lst_inst.append("BUFGCE_DIV #(")
	lst_inst.append("   .BUFGCE_DIVIDE("+str(div_fac)+"),")
	lst_inst.append("   .IS_CE_INVERTED(1'b0),")
	lst_inst.append("   .IS_CLR_INVERTED(1'b0),")
	lst_inst.append("   .IS_I_INVERTED(1'b0),")
	lst_inst.append("   .SIM_DEVICE("ULTRASCALE_PLUS") ")
	lst_inst.append(")"+module_name+"(")
	lst_inst.append("   .O("+module_name+"_o),")
	lst_inst.append("   .CE("+module_name+"_ce),")
	lst_inst.append("   .CLR("+module_name+"_clr),")
	lst_inst.append("   .I("+module_name+"_i));")

	return [lst_wire, lst_inst]
