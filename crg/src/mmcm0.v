module mmcm0_wrapper(
  output        clk_out0,
  output        clk_out1,
  output        clk_out2,
  input         clk_in0
  input         reset,
  output        locked
 );


wire           clk_out0_pri;
wire           clk_out1_pri;
wire           clk_out2_pri;
wire           clk_out3_unused;
wire           clk_out4_unused;
wire           clk_out5_unused;
wire           clk_out6_unused;
wire           clkfbout_clk;
wire [15:0]    do_unused;
wire           drdy_unused;
wire           psdone_unused;
wire           clkfboutb_unused;
wire           clkout0b_unused;
wire           clkout1b_unused;
wire           clkout2b_unused;
wire           clkout3b_unused;
wire           clkfbstopped_unused;
wire           clkinstopped_unused;


MMCME4_ADV #(
   .BANDWIDTH              ("OPTIMIZED"),
   .CLKOUT4_CASCADE        ("FALSE"),
   .COMPENSATION           ("AUTO"),
   .STARTUP_WAIT           ("FALSE"),
   .DIVCLK_DIVIDE          (1),
   .CLKFBOUT_MULT_F        (10.0),
   .CLKFBOUT_PHASE         (0.000),
   .CLKFBOUT_USE_FINE_PS   ("FALSE"),
   .CLKOUT0_DIVIDE_F       (2),
   .CLKOUT0_PHASE          (0.000),
   .CLKOUT0_DUTY_CYCLE     (0.500),
   .CLKOUT0_USE_FINE_PS    ("FALSE"),
   .CLKOUT1_DIVIDE         (5),
   .CLKOUT1_PHASE          (0.000),
   .CLKOUT1_DUTY_CYCLE     (0.500),
   .CLKOUT1_USE_FINE_PS    ("FALSE"),
   .CLKOUT2_DIVIDE         (3),
   .CLKOUT2_PHASE          (0.000),
   .CLKOUT2_DUTY_CYCLE     (0.500),
   .CLKOUT2_USE_FINE_PS    ("FALSE"),
   .CLKOUT3_DIVIDE         (0),
   .CLKOUT3_PHASE          (0.000),
   .CLKOUT3_DUTY_CYCLE     (0.500),
   .CLKOUT3_USE_FINE_PS    ("FALSE"),
   .CLKOUT4_DIVIDE         (0),
   .CLKOUT4_PHASE          (0.000),
   .CLKOUT4_DUTY_CYCLE     (0.500),
   .CLKOUT4_USE_FINE_PS    ("FALSE"),
   .CLKOUT5_DIVIDE         (0),
   .CLKOUT5_PHASE          (0.000),
   .CLKOUT5_DUTY_CYCLE     (0.500),
   .CLKOUT5_USE_FINE_PS    ("FALSE"),
   .CLKOUT6_DIVIDE         (0),
   .CLKOUT6_PHASE          (0.000),
   .CLKOUT6_DUTY_CYCLE     (0.500),
   .CLKOUT6_USE_FINE_PS    ("FALSE"),
   .CLKIN1_PERIOD          (10))
mmcme4_adv_inst(
   .CLKFBOUT               (clkfbout_clk),
   .CLKFBOUTB              (clkfboutb_unused),
   .CLKOUT0                (clk_out0_pri),
   .CLKOUT0B               (clkout0b_unused),
   .CLKOUT1                (clk_out1_pri),
   .CLKOUT1B               (clkout1b_unused),
   .CLKOUT2                (clk_out2_pri),
   .CLKOUT2B               (clkout2b_unused),
   .CLKOUT3                (clk_out3_unused),
   .CLKOUT3B               (clkout3b_unused),
   .CLKOUT4                (clk_out4_unused),
   .CLKOUT5                (clk_out5_unused),
   .CLKOUT6                (clk_out6_unused),
   .CLKFBIN                (clkfbout_clk),
   .CLKIN1                 (clk_in0),
   .CLKIN2                 (1'b0),
   .CLKINSEL               (1'b1),
   .DADDR                  (7'h0),
   .DCLK                   (1'b0),
   .DEN                    (1'b0),
   .DI                     (16'h0),
   .DO                     (do_unused),
   .DRDY                   (drdy_unused),
   .DWE                    (1'b0),
   .CDDCDONE               (),
   .CDDCREQ                (1'b0),
   .PSCLK                  (1'b0),
   .PSEN                   (1'b0),
   .PSINCDEC               (1'b0),
   .PSDONE                 (psdone_unused),
   .LOCKED                 (locked),
   .CLKINSTOPPED           (clkinstopped_unused),
   .CLKFBSTOPPED           (clkfbstopped_unused),
   .PWRDWN                 (1'b0),
   .RST                    (reset));


BUFG clkout0_buf
(  .O   (clk_out0),
   .I   (clk_out0_pri));
BUFG clkout1_buf
(  .O   (clk_out1),
   .I   (clk_out1_pri));
BUFG clkout2_buf
(  .O   (clk_out2),
   .I   (clk_out2_pri));
