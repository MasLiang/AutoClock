module example_crg{
   input       clk1_sel,
   input       clk1_en,
   output      clk1,
   output      rst_n_clk1,
   input       clk2_en,
   output      clk2,
   output      rst_n_clk2,
   input       clk3_en,
   output      clk3,
   output      rst_n_clk3,

   input       clk_src,
   input       rst_n_sys
);


wire    clk_src_ibuf;

wire	mmcm0_clk_out0;
wire	mmcm0_clk_out1;
wire	mmcm0_clk_out2;
wire	mmcm0_clk_in0;
wire	mmcm0_reset;
wire	mmcm0_locked;


wire    div_clk3_o;
wire    div_clk3_ce;
wire    div_clk3_clr;
wire    div_clk3_i;

wire	mux_clk1_clk_in_0;
wire	mux_clk1_clk_in_1;
wire	mux_clk1_clk_out;
wire	mux_clk1_sel;
wire	mux_clk1_1_temp_clk_in_0;
wire	mux_clk1_1_temp_clk_in_1;
wire	mux_clk1_1_temp_clk_out;
wire	mux_clk1_1_temp_sel;

wire	bufgce_clk1_clk_in;
wire	bufgce_clk1_clk_out;
wire	bufgce_clk1_gce;
wire	bufgce_clk2_clk_in;
wire	bufgce_clk2_clk_out;
wire	bufgce_clk2_gce;
wire	bufgce_clk3_clk_in;
wire	bufgce_clk3_clk_out;
wire	bufgce_clk3_gce;

wire    clk1_dest_arst;
wire    clk1_src_arst;
wire    clk1_dest_clk;
wire    clk2_dest_arst;
wire    clk2_src_arst;
wire    clk2_dest_clk;
wire    clk3_dest_arst;
wire    clk3_src_arst;
wire    clk3_dest_clk;

IBUF clkin_ibuf
(    .o    (clk_src_ibuf),
     .I    (clk_src))

mmcm0_wrapper mmcm0(
   .clk_out0   (mmcm0_clk_out0),
   .clk_out1   (mmcm0_clk_out1),
   .clk_out2   (mmcm0_clk_out2),
   .clk_in0    (mmcm0_clk_in0)
   .reset      (mmcm0_reset),
   .locked     (mmcm0_locked));


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

BUFGMUX mux_clk1_1_temp(
	.I0		(mux_clk1_1_temp_clk_in_0),
	.I1		(mux_clk1_1_temp_clk_in_1),
	.O		(mux_clk1_1_temp_clk_out),
	.S		(mux_clk1_1_temp_sel));


BUFGCE bufgce_clk1(
	.I			(bufgce_clk1_clk_in),
	.O			(bufgce_clk1_clk_out),
	.CE			(bufgce_clk1_gce));
BUFGCE bufgce_clk2(
	.I			(bufgce_clk2_clk_in),
	.O			(bufgce_clk2_clk_out),
	.CE			(bufgce_clk2_gce));
BUFGCE bufgce_clk3(
	.I			(bufgce_clk3_clk_in),
	.O			(bufgce_clk3_clk_out),
	.CE			(bufgce_clk3_gce));

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


assign    bufgce_clk1_clk_in            =    mux_clk1_clk_out;
assign    bufgce_clk1_gce               =    clk1_en;
assign    bufgce_clk2_clk_in            =    mmcm0_clk_out0;
assign    bufgce_clk2_gce               =    clk2_en;
assign    bufgce_clk3_clk_in            =    div_clk3_o;
assign    bufgce_clk3_gce               =    clk3_en;
assign    clk1                          =    bufgce_clk1_clk_out;
assign    clk1_0                        =    clk_src_ibuf;
assign    clk1_dest_clk                 =    clk1;
assign    clk1_src_arst                 =    rst_n;
assign    clk2                          =    bufgce_clk2_clk_out;
assign    clk2_dest_clk                 =    clk2;
assign    clk2_src_arst                 =    rst_n & mmcm0_locked;
assign    clk3                          =    bufgce_clk3_clk_out;
assign    clk3_dest_clk                 =    clk3;
assign    clk3_src_arst                 =    rst_n;
assign    div_clk3_i                    =    clk_src_ibuf;
assign    mmcm0_clk_in0                 =    clk_src_ibuf;
assign    mmcm0_reset                   =    !rst_n_sys;
assign    mux_clk1_1_temp_clk_in_0      =    mmcm0_clk_out2;
assign    mux_clk1_1_temp_clk_in_1      =    mmcm0_clk_out1;
assign    mux_clk1_clk_in_0             =    mux_clk1_1_temp_clk_out;
assign    mux_clk1_clk_in_1             =    clk1_0;
assign    mux_clk1_sel                  =    clk1_sel;
assign    rst_n_clk1                    =    clk1_dest_arst;
assign    rst_n_clk2                    =    clk2_dest_arst;
assign    rst_n_clk3                    =    clk3_dest_arst;
