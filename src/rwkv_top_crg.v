module rwkv_top_crg{
   input       clk1_sel,
   output      clk1,
   output      rst_n_clk1,
   output      clk2,
   output      rst_n_clk2,
   output      clk3,
   output      rst_n_clk3,

   input       clk_src,
   input       rst_n_sys
);



wire	pll0_clk_in0;
wire	pll0_clk_in1;
wire	pll0_clk_out0;
wire	pll0_clk_out1;
wire	pll0_reset;
wire	pll0_locked;

wire    div_clk3_o;
wire    div_clk3_ce;
wire    div_clk3_clr;
wire    div_clk3_i;

wire	mux_clk1_clk_in_0;
wire	mux_clk1_clk_in_1;
wire	mux_clk1_clk_out;
wire	mux_clk1_sel;

wire    clk1_dest_arst;
wire    clk1_src_arst;
wire    clk1_dest_clk;
wire    clk2_dest_arst;
wire    clk2_src_arst;
wire    clk2_dest_clk;
wire    clk3_dest_arst;
wire    clk3_src_arst;
wire    clk3_dest_clk;


pll0_wrapper pll0(
	.clk_in0	(pll0_clk_in0),
	.clk_in1	(pll0_clk_in1),
	.clk_out0	(pll0_clk_out0),
	.clk_out1	(pll0_clk_out1),
	.reset		(pll0_reset),
	.locked		(pll0_locked));

BUFGCE_DIV #(
   .BUFGCE_DIVIDE      (3.0),
   .IS_CE_INVERTED     (1'b0),
   .IS_CLR_INVERTED    (1'b0),
   .IS_I_INVERTED      (1'b0),
   .SIM_DEVICE("ULTRASCALE_PLUS") 
)div_clk3(
   .O                  (div_clk3_o),
   .CE                 (div_clk3_ce),
   .CLR                (div_clk3_clr),
   .I                  (div_clk3_i));

BUFGMUX mux_clk1(
	.I0		(mux_clk1_clk_in_0),
	.I1		(mux_clk1_clk_in_1),
	.O		(mux_clk1_clk_out),
	.S		(mux_clk1_sel));


xpm_cdc_async_rst #(
   .DEST_SYNC_FF       (2),
   .INIT_SYNC_FF       (0),
   .RST_ACTIVE_HIGH    (0)
) xpm_cdc_async_rst_clk1 (
   .dest_arst          (clk1_dest_arst),
   .dest_clk           (clk1_dest_clk),
   .src_arst           (clk1_src_arst)
);

xpm_cdc_async_rst #(
   .DEST_SYNC_FF       (2),
   .INIT_SYNC_FF       (0),
   .RST_ACTIVE_HIGH    (0)
) xpm_cdc_async_rst_clk2 (
   .dest_arst          (clk2_dest_arst),
   .dest_clk           (clk2_dest_clk),
   .src_arst           (clk2_src_arst)
);

xpm_cdc_async_rst #(
   .DEST_SYNC_FF       (2),
   .INIT_SYNC_FF       (0),
   .RST_ACTIVE_HIGH    (0)
) xpm_cdc_async_rst_clk3 (
   .dest_arst          (clk3_dest_arst),
   .dest_clk           (clk3_dest_clk),
   .src_arst           (clk3_src_arst)
);


assign    clk1                          =    mux_clk1_clk_out;
assign    clk1_0                        =    clk_src;
assign    clk1_dest_clk                 =    clk1;
assign    clk1_src_arst                 =    rst_n;
assign    clk2                          =    pll0_clk_out0;
assign    clk2_dest_clk                 =    clk2;
assign    clk2_src_arst                 =    rst_n;
assign    clk3                          =    div_clk3_o;
assign    clk3_dest_clk                 =    clk3;
assign    clk3_src_arst                 =    rst_n;
assign    div_clk3_i                    =    clk_src;
assign    mux_clk1_clk_in_0             =    pll0_clk_out1;
assign    mux_clk1_clk_in_1             =    clk1_0;
assign    mux_clk1_sel                  =    clk1_sel;
assign    rst_n_clk1                    =    clk1_dest_arst;
assign    rst_n_clk2                    =    clk2_dest_arst;
assign    rst_n_clk3                    =    clk3_dest_arst;
