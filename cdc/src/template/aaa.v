module aaa_wrapper(
    output        [15:0]        dout,
    output                     empty,
    input                      rd_clk,
    input                      rd_en,
    input         [15:0]        din,
    output                     full,
    input                      wr_clk,
    input                      wr_en,
    input                      rst_n
 );




wire               rd_rst_busy;
wire               wr_rst_busy;
wire               nc_almost_empty;
wire               nc_almost_full;
wire               nc_data_valid;
wire               nc_dbiterr;
wire               nc_overflow;
wire               nc_prog_empty;
wire               nc_prog_full;
wire               nc_rd_data_count;
wire               nc_sbiterr;
wire               nc_underflow;
wire               nc_wr_ack;
wire               nc_wr_data_count;
wire               empty_pre;
wire               full_pre;


assign empty = empty_pre | rd_rst_busy;
assign full  = full_pre  | wr_rst_busy;


xpm_fifo_async #(
   .CASCADE_HEIGHT      (0),
   .CDC_SYNC_STAGES     (2),
   .DOUT_RESET_VALUE    ("0"),
   .ECC_MODE            ("no_ecc"),
   .FIFO_MEMORY_TYPE    (auto),
   .FIFO_READ_LATENCY   (0),
   .FIFO_WRITE_DEPTH    (16),
   .FULL_RESET_VALUE    (0),
   .PROG_EMPTY_THRESH   (10),
   .PROG_FULL_THRESH    (10),
   .RD_DATA_COUNT_WIDTH (5),
   .READ_DATA_WIDTH     (16),
   .READ_MODE           ("fwft"),
   .RELATED_CLOCKS      (1),
   .SIM_ASSERT_CHK      (0),
   .USE_ADV_FEATURES    ("0000"),
   .WAKEUP_TIME         (0),
   .WRITE_DATA_WIDTH    (16),
   .WR_DATA_COUNT_WIDTH (5)
)xpm_fifo_async_inst (
   .almost_empty        (nc_almost_empty),
   .almost_full         (nc_almost_full),
   .data_valid          (nc_data_valid),
   .dbiterr             (nc_dbiterr),
   .dout                (dout),
   .empty               (empty_pre),
   .full                (full_pre),
   .overflow            (nc_overflow),
   .prog_empty          (nc_prog_empty),
   .prog_full           (nc_prog_full),
   .rd_data_count       (nc_rd_data_count),
   .rd_rst_busy         (nc_rd_rst_busy),
   .sbiterr             (nc_sbiterr),
   .underflow           (nc_underflow),
   .wr_ack              (nc_wr_ack),
   .wr_data_count       (nc_wr_data_count),
   .wr_rst_busy         (nc_wr_rst_busy),
   .din                 (din),
   .injectdbiterr       (),
   .injectsbiterr       (),
   .rd_clk              (rd_clk),
   .rd_en               (rd_en),
   .rst                 (rst),
   .sleep               (),
   .wr_clk              (wr_clk),
   .wr_en               (wr_en));
