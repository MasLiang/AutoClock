module aaaa_wrapper(
	input		clk_in0,
	input		clk_in1,
	output		clk_out0,
	output		clk_out1,
	input		reset,
	output		locked
);


wire	clk_in0_ibuf;
wire	clk_in1_ibuf;
wire	clk_out0_pri;
wire	clk_out1_pri;
wire		clk_out0b_unused;
wire		clkfbout_clk;
wire [15:0] do_unused;
wire        drdy_unused;


IBUF clkin0_ibuf
(	.O	(clk_in0_ibuf),
	.I 	(clk_in0))
IBUF clkin1_ibuf
(	.O	(clk_in1_ibuf),
 	.I 	(clk_in1))


PLLE4_ADV#(
	.COMPENSATION         ("AUTO"),
  	.STARTUP_WAIT         ("FALSE"),
  	.DIVCLK_DIVIDE        (1),
  	.CLKFBOUT_MULT        (3),
  	.CLKFBOUT_PHASE       (0.000),
  	.CLKOUT0_DIVIDE       (6),
  	.CLKOUT0_PHASE        (0.000),
  	.CLKOUT0_DUTY_CYCLE   (0.500),
  	.CLKOUT1_DIVIDE       (10),
  	.CLKOUT1_PHASE        (0.000),
  	.CLKOUT1_DUTY_CYCLE   (0.500),
  	.CLKIN_PERIOD         (10.0),
	.CLKOUTPHY_MODE		  ("VCO_2X"),
	.IS_CLKFBIN_INVERTED  (1'b0),
	.IS_CLKIN_INVERTED    (1'b0),
	.IS_PWRDWN_INVERTED   (1'b0),
	.IS_RST_INVERTED      (1'b0),
	.REF_JITTER           (0.0))
plle4_adv_inst(
	.CLKFBOUT            (clkfbout_clk),
	.CLKOUT0             (clk_out0_pri),
	.CLKOUT0B            (clk_out0b_unused),
	.CLKOUT1             (clk_out1_pri),
	.CLKOUT1B            (clkout1b_unused),
	.CLKFBIN             (clkfbout_clk),
	.CLKIN               (clk_in1_ibuf),
	.DADDR               (7'h0),
	.DCLK                (1'b0),
	.DEN                 (1'b0),
	.DI                  (16'h0),
	.DO                  (do_unused),
	.DRDY                (drdy_unused),
	.DWE                 (1'b0),
	.CLKOUTPHYEN         (1'b0),
	.CLKOUTPHY           (),
	.LOCKED              (locked),
	.PWRDWN              (1'b0),
	.RST                 (reset));


BUFG clkout0_buf
(	.O   (clk_out0),
 	.I   (clk_out0_pri));
BUFG clkout1_buf
(	.O   (clk_out1),
 	.I   (clk_out1_pri));


endmodule
