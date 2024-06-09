module top_nondf_kernel_2mm_A_V(
    address0,
    ce0,
    d0,
    we0,
    q0,
    reset0,
    clk0,
    address1,
    ce1,
    d1,
    we1,
    q1,
    reset1,
    clk1
    );

parameter DataWidth = 32;
parameter AddressWidth = 8;
parameter AddressRange = 256;
 
input[AddressWidth-1:0] address0;
input ce0;
input[DataWidth-1:0] d0;
input we0;
output reg[DataWidth-1:0] q0;
input reset0;
input clk0;
input[AddressWidth-1:0] address1;
input ce1;
input[DataWidth-1:0] d1;
input we1;
output reg[DataWidth-1:0] q1;
input reset1;
input clk1;


wire           nc_dbiterra;
wire           nc_dbiterrb;
wire           nc_sbiterra;
wire           nc_sbiterrb;


xpm_memory_tdpram #(
      .ADDR_WIDTH_A(AddressWidth),
      .ADDR_WIDTH_B(AddressWidth),
      .AUTO_SLEEP_TIME(0),
      .BYTE_WRITE_WIDTH_A(DataWidth),
      .BYTE_WRITE_WIDTH_B(DataWidth),
      .CASCADE_HEIGHT(0),
      .CLOCKING_MODE("independent"),
      .ECC_BIT_RANGE("7:0"),
      .ECC_MODE("no_ecc"),
      .ECC_TYPE("none"),
      .IGNORE_INIT_SYNTH(0),
      .MEMORY_INIT_FILE("none"),
      .MEMORY_INIT_PARAM("0"),
      .MEMORY_OPTIMIZATION("true"),
      .MEMORY_PRIMITIVE("auto"),
      .MEMORY_SIZE(address_range),
      .MESSAGE_CONTROL(0),
      .RAM_DECOMP("auto"),
      .READ_DATA_WIDTH_A(DataWidth),
      .READ_DATA_WIDTH_B(DataWidth),
      .READ_LATENCY_A(1),
      .READ_LATENCY_B(1),
      .READ_RESET_VALUE_A("0"),
      .READ_RESET_VALUE_B("0"),
      .RST_MODE_A("SYNC"),
      .RST_MODE_B("SYNC"),
      .SIM_ASSERT_CHK(0),
      .USE_EMBEDDED_CONSTRAINT(0),
      .USE_MEM_INIT(1),
      .USE_MEM_INIT_MMI(0),
      .WAKEUP_TIME("disable_sleep"),
      .WRITE_DATA_WIDTH_A(DataWidth),
      .WRITE_DATA_WIDTH_B(DataWidth),
      .WRITE_MODE_A("no_change"),
      .WRITE_MODE_B("no_change"),
      .WRITE_PROTECT(1)
   ) xpm_memory_tdpram_inst (
      .dbiterra         (nc_dbiterra),
      .dbiterrb         (nc_dbiterrb),
      .douta            (q0),
      .doutb            (q1),
      .sbiterra         (nc_sbiterra),
      .sbiterrb         (nc_sbiterrb),
      .addra            (address0),
      .addrb            (address1),
      .clka             (clk0),
      .clkb             (clk1),
      .dina             (d0),
      .dinb             (d1),
      .ena              (ena),
      .enb              (enb),
      .injectdbiterra   (),
      .injectdbiterrb   (),
      .injectsbiterra   (),
      .injectsbiterrb   (),
      .regcea           (regcea),
      .regceb           (regceb),
      .rsta             (reset0),
      .rstb             (reset1),
      .sleep            (sleep),
      .wea              (wea),
      .web              (web)
   );
endmodule
