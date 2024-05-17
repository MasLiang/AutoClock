import math 

def gen_async_fifo_file(module_name, factors):

    memory_type = factor[0] # "auto", "block", "distributed", default "auto"
    write_depth = factor[1]
    rd_data_width = factor[2]
    wr_data_width = factor[3]
    read_depth = write_depth*wr_data_width/rd_data_width
    
    lst_port = []
    lst_wire = []
    lst_inst = []

    lst_port.append("module "+module_name+"_wrapper(")
    lst_port.append("    output        ["+str(rd_data_width-1)+":0]        dout,")
    lst_port.append("    output                     empty,")
    lst_port.append("    input                      rd_clk,")
    lst_port.append("    input                      rd_en,")
    lst_port.append("    input         ["+str(wr_data_width-1)+":0]        din,")
    lst_port.append("    output                     full,")
    lst_port.append("    input                      wr_clk,")
    lst_port.append("    input                      wr_en,")
    lst_port.append("    input                      rst_n"),                     
    lst_port.append(" );")
    lst_port.append("\n")

    lst_wire.append("wire               rd_rst_busy;")
    lst_wire.append("wire               wr_rst_busy;")
    lst_wire.append("wire               nc_almost_empty;")
    lst_wire.append("wire               nc_almost_full;") 
    lst_wire.append("wire               nc_data_valid;") 
    lst_wire.append("wire               nc_dbiterr;")   
    lst_wire.append("wire               nc_overflow;")
    lst_wire.append("wire               nc_prog_empty;")
    lst_wire.append("wire               nc_prog_full;")
    lst_wire.append("wire               nc_rd_data_count;")
    lst_wire.append("wire               nc_sbiterr;") 
    lst_wire.append("wire               nc_underflow;") 
    lst_wire.append("wire               nc_wr_ack;") 
    lst_wire.append("wire               nc_wr_data_count;")
    lst_wire.append("wire               empty_pre;")
    lst_wire.append("wire               full_pre;")
    lst_wire.append("\n")
    lst_wire.append("assign empty = empty_pre | rd_rst_busy;")
    lst_wire.append("assign full  = full_pre  | wr_rst_busy;")

    lst_inst.append("xpm_fifo_async #(")
    lst_inst.append("   .CASCADE_HEIGHT      (0),")
    lst_inst.append("   .CDC_SYNC_STAGES     (2),")
    lst_inst.append("   .DOUT_RESET_VALUE    (\"0\"),")
    lst_inst.append("   .ECC_MODE            (\"no_ecc\"),")
    lst_inst.append("   .FIFO_MEMORY_TYPE    ("+memory_type+"),")
    lst_inst.append("   .FIFO_READ_LATENCY   (0),")
    lst_inst.append("   .FIFO_WRITE_DEPTH    ("+str(write_depth)+"),")
    lst_inst.append("   .FULL_RESET_VALUE    (0),")
    lst_inst.append("   .PROG_EMPTY_THRESH   (10),")
    lst_inst.append("   .PROG_FULL_THRESH    (10),")
    lst_inst.append("   .RD_DATA_COUNT_WIDTH ("+str(round(math.log2(read_depth))+1)+"),")
    lst_inst.append("   .READ_DATA_WIDTH     ("+str(rd_data_width)+"),")
    lst_inst.append("   .READ_MODE           (\"fwft\"),")
    lst_inst.append("   .RELATED_CLOCKS      (1),")
    lst_inst.append("   .SIM_ASSERT_CHK      (0),");
    lst_inst.append("   .USE_ADV_FEATURES    (\"0000\"),")
    lst_inst.append("   .WAKEUP_TIME         (0),")
    lst_inst.append("   .WRITE_DATA_WIDTH    ("+str(wr_data_width)+"),")
    lst_inst.append("   .WR_DATA_COUNT_WIDTH ("+str(round(math.log2(write_depth))+1)+")")
    lst_inst.append(")xpm_fifo_async_inst (")
    lst_inst.append("   .almost_empty        (nc_almost_empty),")
    lst_inst.append("   .almost_full         (nc_almost_full),")
    lst_inst.append("   .data_valid          (nc_data_valid),")
    lst_inst.append("   .dbiterr             (nc_dbiterr),")
    lst_inst.append("   .dout                (dout),")
    lst_inst.append("   .empty               (empty_pre),")
    lst_inst.append("   .full                (full_pre),")
    lst_inst.append("   .overflow            (nc_overflow),")
    lst_inst.append("   .prog_empty          (nc_prog_empty),")
    lst_inst.append("   .prog_full           (nc_prog_full),")
    lst_inst.append("   .rd_data_count       (nc_rd_data_count),")
    lst_inst.append("   .rd_rst_busy         (nc_rd_rst_busy),")
    lst_inst.append("   .sbiterr             (nc_sbiterr),")
    lst_inst.append("   .underflow           (nc_underflow),")
    lst_inst.append("   .wr_ack              (nc_wr_ack),")
    lst_inst.append("   .wr_data_count       (nc_wr_data_count),")
    lst_inst.append("   .wr_rst_busy         (nc_wr_rst_busy),")
    lst_inst.append("   .din                 (din),")
    lst_inst.append("   .injectdbiterr       (),")
    lst_inst.append("   .injectsbiterr       (),")
    lst_inst.append("   .rd_clk              (rd_clk),")
    lst_inst.append("   .rd_en               (rd_en),")
    lst_inst.append("   .rst                 (rst),")
    lst_inst.append("   .sleep               (),")
    lst_inst.append("   .wr_clk              (wr_clk),")
    lst_inst.append("   .wr_en               (wr_en));")

    with open(module_name+".v", "w") as f:
        for i in (lst_port + ["\n"] + lst_wire + ["\n"] + lst_inst):
            f.write(i)
            f.write("\n")

def gen_async_fifo_inst(module_name, factors):
    gen_async_fifo_file(module_name, factors)
    
    rd_data_width = factor[2]
    wr_data_width = factor[3]

    lst_inst = []
    lst_wire = []

    lst_inst.append("wire           ["+str(wr_data_width-1)+":0]"+module_name+"_dout;")
    lst_inst.append("wire           "+module_name+"_empty,")
    lst_inst.append("wire           "+module_name+"_rd_clk;")
    lst_inst.append("wire           "+module_name+"_rd_en,")
    lst_inst.append("wire           ["+str(rd_data_width-1)+":0]"+module_name+"_din;")
    lst_inst.append("wire           "+module_name+"_full;")
    lst_inst.append("wire           "+module_name+"_wr_clk;")
    lst_inst.append("wire           "+module_name+"_wr_en;")
    lst_inst.append("wire           "+module_name+"_rst_n));")

    lst_inst.append(module_name+"_wrapper "+module_name+"(")
    lst_inst.append("    .dout          ("+module_name+"_dout),")
    lst_inst.append("    .empty         ("+module_name+"_empty,")
    lst_inst.append("    .rd_clk        ("+module_name+"_rd_clk),")
    lst_inst.append("    .rd_en         ("+module_name+"_rd_en,")
    lst_inst.append("    .din           ("+module_name+"_din),")
    lst_inst.append("    .full          ("+module_name+"_full),")
    lst_inst.append("    .wr_clk        ("+module_name+"_wr_clk),")
    lst_inst.append("    .wr_en         ("+module_name+"_wr_en),")
    lst_inst.append("    .rst_n         ("+module_name+"_rst_n));")

    return [lst_wire, lst_inst]

#factor = ["auto", 16, 16, 16, 16]
#bbb = gen_async_fifo_inst("aaa", factor)
#for i in bbb:
#    for j in i:
#        print(j)
