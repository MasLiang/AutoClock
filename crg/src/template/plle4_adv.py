def gen_plle4_file(module_name, factors):

    clkin_period = factors[0]
    clkout_num = factors[1]
    divclk_divide = factors[2]
    clkfbout_mult = factors[3]
    clkout0_divide = factors[4]
    clkout1_divide = factors[5]
    if clkout1_divide==0:
        clkout1_divide = 1
    # TODO
    # diffriencial clock
    clkin_num = 1

    lst_port = []
    lst_wire = []
    lst_inst = []
    lst_bufg = []
    lst_port.append("module "+module_name+"_wrapper(")

    # port
    #   input clk
    lst_port.append("	input		clk_in0,")
    if(clkin_num>1):
        lst_port.append("	input		clk_in1,")
    #   output clk
    lst_port.append("	output		clk_out0,")
    if(clkout_num>1):
        lst_port.append("	output		clk_out1,")
    #	input rst
    lst_port.append("	input		reset,")
    #	output locked
    lst_port.append("	output		locked")

    lst_port.append(");")

    # inter wire
    lst_wire.append("wire	clk_out0_pri;")	
    if(clkout_num>1):
        lst_wire.append("wire	clk_out1_pri;")	
    else:
        lst_wire.append("wire	clk_out1_unused;")
    lst_wire.append("wire		clk_out0b_unused;")
    lst_wire.append("wire		clkfbout_clk;")
    lst_wire.append("wire [15:0] do_unused;")
    lst_wire.append("wire        drdy_unused;")

    # bufg
    lst_bufg.append("BUFG clkout0_buf")
    lst_bufg.append("(	.O   (clk_out0),")
    lst_bufg.append(" 	.I   (clk_out0_pri));")
    if(clkout_num>1):
        lst_bufg.append("BUFG clkout1_buf")
        lst_bufg.append("(	.O   (clk_out1),")
        lst_bufg.append(" 	.I   (clk_out1_pri));")

    # inst
    lst_inst.append("PLLE4_ADV#(")
    lst_inst.append("	.COMPENSATION         (\"AUTO\"),")
    lst_inst.append("  	.STARTUP_WAIT         (\"FALSE\"),")
    lst_inst.append("  	.DIVCLK_DIVIDE        ("+str(divclk_divide)+"),")
    lst_inst.append("  	.CLKFBOUT_MULT        ("+str(clkfbout_mult)+"),")
    lst_inst.append("  	.CLKFBOUT_PHASE       (0.000),")
    lst_inst.append("  	.CLKOUT0_DIVIDE       ("+str(clkout0_divide)+"),")
    lst_inst.append("  	.CLKOUT0_PHASE        (0.000),")
    lst_inst.append("  	.CLKOUT0_DUTY_CYCLE   (0.500),")
    lst_inst.append("  	.CLKOUT1_DIVIDE       ("+str(clkout1_divide)+"),")
    lst_inst.append("  	.CLKOUT1_PHASE        (0.000),")	
    lst_inst.append("  	.CLKOUT1_DUTY_CYCLE   (0.500),")
    lst_inst.append("  	.CLKIN_PERIOD         ("+str(clkin_period)+"),")
    lst_inst.append("	.CLKOUTPHY_MODE		  (\"VCO_2X\"),")
    lst_inst.append("	.IS_CLKFBIN_INVERTED  (1'b0),")
    lst_inst.append("	.IS_CLKIN_INVERTED    (1'b0),")
    lst_inst.append("	.IS_PWRDWN_INVERTED   (1'b0),")
    lst_inst.append("	.IS_RST_INVERTED      (1'b0),")
    lst_inst.append("	.REF_JITTER           (0.0))")
    lst_inst.append("plle4_adv_inst(")
    lst_inst.append("	.CLKFBOUT            (clkfbout_clk),")	
    lst_inst.append("	.CLKOUT0             (clk_out0_pri),")
    lst_inst.append("	.CLKOUT0B            (clk_out0b_unused),")
    if(clkout_num>1):
        lst_inst.append("	.CLKOUT1             (clk_out1_pri),")
    else:
        lst_inst.append("	.CLKOUT1             (clk_out1_unused),")
    lst_inst.append("	.CLKOUT1B            (clkout1b_unused),")
    lst_inst.append("	.CLKFBIN             (clkfbout_clk),")
    lst_inst.append("	.CLKIN               (clk_in0),")
    lst_inst.append("	.DADDR               (7'h0),")
    lst_inst.append("	.DCLK                (1'b0),")
    lst_inst.append("	.DEN                 (1'b0),")
    lst_inst.append("	.DI                  (16'h0),")
    lst_inst.append("	.DO                  (do_unused),")
    lst_inst.append("	.DRDY                (drdy_unused),")
    lst_inst.append("	.DWE                 (1'b0),")
    lst_inst.append("	.CLKOUTPHYEN         (1'b0),")
    lst_inst.append("	.CLKOUTPHY           (),")
    lst_inst.append("	.LOCKED              (locked),")
    lst_inst.append("	.PWRDWN              (1'b0),")
    lst_inst.append("	.RST                 (reset));")

    lst_bufg.append("\n")
    lst_bufg.append("endmodule")

    # generate file of this module
    with open(module_name+".v", "w") as f:
        for i in (lst_port + ["\n"] + lst_wire + ["\n"] + ["\n"] + lst_inst + ["\n"] + lst_bufg):
            f.write(i)
            f.write("\n")

def gen_plle4_inst(module_name, factors):
    gen_plle4_file(module_name, factors)
    clkout_num = factors[1]
    clkin_num = 1
	
    lst_inst = []
    lst_wire = []
	
    lst_inst.append(module_name+"_wrapper "+module_name+"(")
    lst_inst.append("	.clk_in0	("+module_name+"_clk_in0),")
    lst_wire.append("wire	"+module_name+"_clk_in0;")
    if(clkin_num>1):
        lst_inst.append("	.clk_in1	("+module_name+"_clk_in1),")
        lst_wire.append("wire	"+module_name+"_clk_in1;")
    lst_inst.append("	.clk_out0	("+module_name+"_clk_out0),")
    lst_wire.append("wire	"+module_name+"_clk_out0;")
    if(clkout_num>1):
        lst_inst.append("	.clk_out1	("+module_name+"_clk_out1),")
        lst_wire.append("wire	"+module_name+"_clk_out1;")
    lst_inst.append("	.reset		("+module_name+"_reset),")
    lst_wire.append("wire	"+module_name+"_reset;")
    lst_inst.append("	.locked		("+module_name+"_locked));")
    lst_wire.append("wire	"+module_name+"_locked;")

    return [lst_wire, lst_inst]
		
