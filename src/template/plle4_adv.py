import math
from pll_fac_calc import calc_fac

def gen_plle4_file(module_name, clkin_period, clkout_num, divclk_divide, clkfbout_mult, clkout0_divide, clkout1_divide):
	lst_port = []
	lst_wire = []
	lst_pll = []
	lst_ibuf = []
	lst_bufg = []
	lst_port.append("module "+module_name+"_wrapper(")
	
	# port
	#   input clk
	lst_port.append("	input		clk_in0,")
	if(clkout_num>1):
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

    # input initial
	lst_wire.append("wire	clk_in0_ibuf;")
	lst_ibuf.append("IBUF clkin0_ibuf")
	lst_ibuf.append("(	.O	(clk_in0_ibuf),")
	lst_ibuf.append("	.I 	(clk_in0))")
	if(clkout_num>1):
		lst_wire.append("wire	clk_in1_ibuf;")
		lst_ibuf.append("IBUF clkin1_ibuf")
		lst_ibuf.append("(	.O	(clk_in1_ibuf),")
		lst_ibuf.append(" 	.I 	(clk_in1))")
  
	# inter wire
	lst_wire.append("wire	clk_out0_pri;")	
	if(clkout_num>1):
		lst_wire.append("wire	clk_out1_pri;")	
	else:
		lst_wire.append("wire	clk_out1_unused;")
	
	# bufg
	lst_bufg.append("BUFG clkout0_buf")
	lst_bufg.append("(	.O   (clk_out0),")
	lst_bufg.append(" 	.I   (clk_out0_pri));")
	if(clkout_num>1):
		lst_bufg.append("BUFG clkout1_buf")
		lst_bufg.append("(	.O   (clk_out1),")
		lst_bufg.append(" 	.I   (clk_out1_pri));")

	# inter wire
	lst_wire.append("wire		clk_out0b_unused;")
	lst_wire.append("wire		clkfbout_clk;")
	lst_wire.append("wire [15:0] do_unused;")
	lst_wire.append("wire        drdy_unused;")
	
	# calculate parameters
	# clkin_period = 1000000/in_freq[0]
	# divclk_divide, clkfbout_mult, clkout0_divide, clkout1_divide = calc_fac(in_freq[0], out_freq)
					
	lst_pll.append("PLLE4_ADV#(")
	lst_pll.append("	.COMPENSATION         (\"AUTO\"),")
	lst_pll.append("  	.STARTUP_WAIT         (\"FALSE\"),")
	lst_pll.append("  	.DIVCLK_DIVIDE        ("+str(divclk_divide)+"),")
	lst_pll.append("  	.CLKFBOUT_MULT        ("+str(clkfbout_mult)+"),")
	lst_pll.append("  	.CLKFBOUT_PHASE       (0.000),")
	lst_pll.append("  	.CLKOUT0_DIVIDE       ("+str(clkout0_divide)+"),")
	lst_pll.append("  	.CLKOUT0_PHASE        (0.000),")
	lst_pll.append("  	.CLKOUT0_DUTY_CYCLE   (0.500),")
	lst_pll.append("  	.CLKOUT1_DIVIDE       ("+str(clkout1_divide)+"),")
	lst_pll.append("  	.CLKOUT1_PHASE        (0.000),")	
	lst_pll.append("  	.CLKOUT1_DUTY_CYCLE   (0.500),")
	lst_pll.append("  	.CLKIN_PERIOD         ("+str(clkin_period)+"),")
	lst_pll.append("	.CLKOUTPHY_MODE		  (\"VCO_2X\"),")
	lst_pll.append("	.IS_CLKFBIN_INVERTED  (1'b0),")
	lst_pll.append("	.IS_CLKIN_INVERTED    (1'b0),")
	lst_pll.append("	.IS_PWRDWN_INVERTED   (1'b0),")
	lst_pll.append("	.IS_RST_INVERTED      (1'b0),")
	lst_pll.append("	.REF_JITTER           (0.0))")
	lst_pll.append("plle4_adv_inst(")
	lst_pll.append("	.CLKFBOUT            (clkfbout_clk),")	
	lst_pll.append("	.CLKOUT0             (clk_out0_pri),")
	lst_pll.append("	.CLKOUT0B            (clk_out0b_unused),")
	if(clkout_num>1):
		lst_pll.append("	.CLKOUT1             (clk_out1_pri),")
	else:
		lst_pll.append("	.CLKOUT1             (clk_out1_unused),")
	lst_pll.append("	.CLKOUT1B            (clkout1b_unused),")
	lst_pll.append("	.CLKFBIN             (clkfbout_clk),")
	lst_pll.append("	.CLKIN               (clk_in1_ibuf),")
	lst_pll.append("	.DADDR               (7'h0),")
	lst_pll.append("	.DCLK                (1'b0),")
	lst_pll.append("	.DEN                 (1'b0),")
	lst_pll.append("	.DI                  (16'h0),")
	lst_pll.append("	.DO                  (do_unused),")
	lst_pll.append("	.DRDY                (drdy_unused),")
	lst_pll.append("	.DWE                 (1'b0),")
	lst_pll.append("	.CLKOUTPHYEN         (1'b0),")
	lst_pll.append("	.CLKOUTPHY           (),")
	lst_pll.append("	.LOCKED              (locked),")
	lst_pll.append("	.PWRDWN              (1'b0),")
	lst_pll.append("	.RST                 (reset));")

	lst_bufg.append("\n")
	lst_bufg.append("endmodule")
	
	# generate file of this module
	with open(module_name+".v", "w") as f:
		for i in (lst_port + ["\n"] + lst_wire + ["\n"] + lst_ibuf + ["\n"] + lst_pll + ["\n"] + lst_bufg):
			f.write(i)
			f.write("\n")

def gen_plle4_inst(module_name, clkin_period, clkout_num, divclk_divide, clkfbout_mult, clkout0_divide, clkout1_divide):
	gen_plle4_file(module_name, clkin_period, clkout_num, divclk_divide, clkfbout_mult, clkout0_divide, clkout1_divide)
	
	lst_inst = []
	lst_wire = []
	
	lst_inst.append(module_name+"_wrapper "+module_name+"(")
	lst_inst.append("	.clk_in0	("+module_name+"_clk_in0),")
	lst_wire.append("wire	"+module_name+"_clk_in0;")
	if(clkout_num>1):
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
		
# test
lst_factor = calc_fac(100000, [50000, 30000], 2)
clkin_period = 1000000/100000
print(lst_factor)

lst_inst = gen_plle4_inst("aaaa", clkin_period, 2, lst_factor[0], lst_factor[1], lst_factor[2][0], lst_factor[2][1])
for i in lst_inst:
	print(i)
