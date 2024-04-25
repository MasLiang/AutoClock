from mmcm_fac_calc import mmcm_multi_calc_fac
def gen_mmcme4_file(module_name, factors):

    clkin_period = factors[0]
    clkout_num = factors[1]
    divclk_divide = factors[2]
    clkfbout_mult = factors[3]
    clkout0_divide = factors[4]
    clkout1_divide = factors[5]
    clkout2_divide = factors[6]
    clkout3_divide = factors[7]
    clkout4_divide = factors[8]
    clkout5_divide = factors[9]
    clkout6_divide = factors[10]
    # TODO
    # diffrential clock
    clkin_num = 1

    lst_port = []
    lst_wire = []
    lst_inst = []
    lst_ibuf = []
    lst_bufg = []
    lst_port.append("module "+module_name+"_wrapper(")
	
    # port
    lst_port.append("  output        clk_out0,")
    if(clkout_num>1):
        lst_port.append("  output        clk_out1,")
    if(clkout_num>2):
        lst_port.append("  output        clk_out2,")
    if(clkout_num>3):
        lst_port.append("  output        clk_out3,")
    if(clkout_num>4):
        lst_port.append("  output        clk_out4,")
    if(clkout_num>5):
        lst_port.append("  output        clk_out5,")
    if(clkout_num>6):
        lst_port.append("  output        clk_out6,")
    lst_port.append("  input         clk_in0")
    if(clkin_num>1):
        lst_port.append("  input         clk_in1")
    lst_port.append("  input         reset,")
    lst_port.append("  output        locked")
    lst_port.append(" );")
    
    # input initial
    lst_wire.append("wire           clk_in0_ibuf;")
    lst_ibuf.append("IBUF clkin0_ibuf")
    lst_ibuf.append("(  .O (clk_in0_ibuf),")
    lst_ibuf.append("   .I (clk_in0));")
    if(clkin_num>1):
        lst_wire.append("wire           clk_in1_ibuf;")
        lst_ibuf.append("IBUF clkin1_ibuf")
        lst_ibuf.append("(  .O (clk_in1_ibuf),")
        lst_ibuf.append("   .I (clk_in1));")

    # inter wire
    lst_wire.append("wire           clk_out0_pri;")
    if(clkout_num>1):
        lst_wire.append("wire           clk_out1_pri;")
    else:
        lst_wire.append("wire           clk_out1_unused;")
    if(clkout_num>2):
        lst_wire.append("wire           clk_out2_pri;")
    else:
        lst_wire.append("wire           clk_out2_unused;")
    if(clkout_num>3):
        lst_wire.append("wire           clk_out3_pri;")
    else:
        lst_wire.append("wire           clk_out3_unused;")
    if(clkout_num>4):
        lst_wire.append("wire           clk_out4_pri;")
    else:
        lst_wire.append("wire           clk_out4_unused;")
    if(clkout_num>5):
        lst_wire.append("wire           clk_out5_pri;")
    else:
        lst_wire.append("wire           clk_out5_unused;")
    if(clkout_num>6):
        lst_wire.append("wire           clk_out6_pri;")
    else:
        lst_wire.append("wire           clk_out6_unused;")

    lst_wire.append("wire           clkfbout_clk;")
    lst_wire.append("wire [15:0]    do_unused;")
    lst_wire.append("wire           drdy_unused;")
    lst_wire.append("wire           psdone_unused;")
    lst_wire.append("wire           clkfboutb_unused;")
    lst_wire.append("wire           clkout0b_unused;")
    lst_wire.append("wire           clkout1b_unused;")
    lst_wire.append("wire           clkout2b_unused;")
    lst_wire.append("wire           clkout3b_unused;")
    lst_wire.append("wire           clkfbstopped_unused;")
    lst_wire.append("wire           clkinstopped_unused;")

    # inst
    lst_inst.append("MMCME4_ADV #(")
    lst_inst.append("   .BANDWIDTH              (\"OPTIMIZED\"),")
    lst_inst.append("   .CLKOUT4_CASCADE        (\"FALSE\"),")
    lst_inst.append("   .COMPENSATION           (\"AUTO\"),")
    lst_inst.append("   .STARTUP_WAIT           (\"FALSE\"),")
    lst_inst.append("   .DIVCLK_DIVIDE          ("+str(divclk_divide)+"),")
    lst_inst.append("   .CLKFBOUT_MULT_F        ("+str(clkfbout_mult)+"),")
    lst_inst.append("   .CLKFBOUT_PHASE         (0.000),")
    lst_inst.append("   .CLKFBOUT_USE_FINE_PS   (\"FALSE\"),")
    lst_inst.append("   .CLKOUT0_DIVIDE_F       ("+str(clkout0_divide)+"),")
    lst_inst.append("   .CLKOUT0_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT0_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT0_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKOUT1_DIVIDE         ("+str(clkout1_divide)+"),")
    lst_inst.append("   .CLKOUT1_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT1_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT1_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKOUT2_DIVIDE         ("+str(clkout2_divide)+"),")
    lst_inst.append("   .CLKOUT2_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT2_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT2_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKOUT3_DIVIDE         ("+str(clkout3_divide)+"),")
    lst_inst.append("   .CLKOUT3_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT3_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT3_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKOUT4_DIVIDE         ("+str(clkout4_divide)+"),")
    lst_inst.append("   .CLKOUT4_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT4_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT4_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKOUT5_DIVIDE         ("+str(clkout5_divide)+"),")
    lst_inst.append("   .CLKOUT5_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT5_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT5_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKOUT6_DIVIDE         ("+str(clkout6_divide)+"),")
    lst_inst.append("   .CLKOUT6_PHASE          (0.000),")
    lst_inst.append("   .CLKOUT6_DUTY_CYCLE     (0.500),")
    lst_inst.append("   .CLKOUT6_USE_FINE_PS    (\"FALSE\"),")
    lst_inst.append("   .CLKIN1_PERIOD          ("+str(clkin_period)+"))")
    lst_inst.append("mmcme4_adv_inst(")
    lst_inst.append("   .CLKFBOUT               (clkfbout_clk),")
    lst_inst.append("   .CLKFBOUTB              (clkfboutb_unused),")
    lst_inst.append("   .CLKOUT0                (clk_out0_pri),")
    lst_inst.append("   .CLKOUT0B               (clkout0b_unused),")
    if(clkout_num>1):
        lst_inst.append("   .CLKOUT1                (clk_out1_pri),")
    else:
        lst_inst.append("   .CLKOUT1                (clk_out1_unused),")
    lst_inst.append("   .CLKOUT1B               (clkout1b_unused),")
    if(clkout_num>2):
        lst_inst.append("   .CLKOUT2                (clk_out2_pri),")
    else:
        lst_inst.append("   .CLKOUT2                (clk_out2_unused),")
    lst_inst.append("   .CLKOUT2B               (clkout2b_unused),")
    if(clkout_num>3):
        lst_inst.append("   .CLKOUT3                (clk_out3_pri),")
    else:
        lst_inst.append("   .CLKOUT3                (clk_out3_unused),")
    lst_inst.append("   .CLKOUT3B               (clkout3b_unused),")
    if(clkout_num>4):
        lst_inst.append("   .CLKOUT4                (clk_out4_pri),")
    else:
        lst_inst.append("   .CLKOUT4                (clk_out4_unused),")
    if(clkout_num>5):
        lst_inst.append("   .CLKOUT5                (clk_out5_pri),")
    else:
        lst_inst.append("   .CLKOUT5                (clk_out5_unused),")
    if(clkout_num>6):
        lst_inst.append("   .CLKOUT6                (clk_out6_pri),")
    else:
        lst_inst.append("   .CLKOUT6                (clk_out6_unused),")
    lst_inst.append("   .CLKFBIN                (clkfbout_clk),")
    lst_inst.append("   .CLKIN1                 (clk_in0_ibuf),")
    if(clkin_num>1):
        lst_inst.append("   .CLKIN2                 (clk_in1_ibuf),")
    else:
        lst_inst.append("   .CLKIN2                 (1'b0),")
    lst_inst.append("   .CLKINSEL               (1'b1),")
    lst_inst.append("   .DADDR                  (7'h0),")
    lst_inst.append("   .DCLK                   (1'b0),")
    lst_inst.append("   .DEN                    (1'b0),")
    lst_inst.append("   .DI                     (16'h0),")
    lst_inst.append("   .DO                     (do_unused),")
    lst_inst.append("   .DRDY                   (drdy_unused),")
    lst_inst.append("   .DWE                    (1'b0),")
    lst_inst.append("   .CDDCDONE               (),")
    lst_inst.append("   .CDDCREQ                (1'b0),")
    lst_inst.append("   .PSCLK                  (1'b0),")
    lst_inst.append("   .PSEN                   (1'b0),")
    lst_inst.append("   .PSINCDEC               (1'b0),")
    lst_inst.append("   .PSDONE                 (psdone_unused),")
    lst_inst.append("   .LOCKED                 (locked),")
    lst_inst.append("   .CLKINSTOPPED           (clkinstopped_unused),")
    lst_inst.append("   .CLKFBSTOPPED           (clkfbstopped_unused),")
    lst_inst.append("   .PWRDWN                 (1'b0),")
    lst_inst.append("   .RST                    (reset));")

    # bufg
    lst_bufg.append("BUFG clkout0_buf")
    lst_bufg.append("(  .O   (clk_out0),")
    lst_bufg.append("   .I   (clk_out0_pri));")
    if(clkout_num>1):
        lst_bufg.append("BUFG clkout1_buf")
        lst_bufg.append("(  .O   (clk_out1),")
        lst_bufg.append("   .I   (clk_out1_pri));")
    if(clkout_num>2):
        lst_bufg.append("BUFG clkout2_buf")
        lst_bufg.append("(  .O   (clk_out2),")
        lst_bufg.append("   .I   (clk_out2_pri));")
    if(clkout_num>3):
        lst_bufg.append("BUFG clkout3_buf")
        lst_bufg.append("(  .O   (clk_out3),")
        lst_bufg.append("   .I   (clk_out3_pri));")
    if(clkout_num>4):
        lst_bufg.append("BUFG clkout4_buf")
        lst_bufg.append("(  .O   (clk_out4),")
        lst_bufg.append("   .I   (clk_out4_pri));")
    if(clkout_num>5):
        lst_bufg.append("BUFG clkout5_buf")
        lst_bufg.append("(  .O   (clk_out5),")
        lst_bufg.append("   .I   (clk_out5_pri));")
    if(clkout_num>6):
        lst_bufg.append("BUFG clkout6_buf")
        lst_bufg.append("(  .O   (clk_out6),")
        lst_bufg.append("   .I   (clk_out6_pri));")
	
    # generate file of this module
    with open(module_name+".v", "w") as f:
        for i in (lst_port + ["\n"] + lst_wire + ["\n"] + lst_ibuf + ["\n"] + lst_inst + ["\n"] + lst_bufg):
            f.write(i)
            f.write("\n")

def gen_mmcme4_inst(module_name, factors):
    gen_mmcme4_file(module_name, factors)
    clkout_num = factors[1]
    clkin_num = 1
	
    lst_inst = []
    lst_wire = []
    lst_inst.append(module_name+"_wrapper "+module_name+"(")
    lst_wire.append("wire	"+module_name+"_clk_out0;")
    lst_inst.append("   .clk_out0   ("+module_name+"_clk_out0),")
    if(clkout_num>1):
        lst_inst.append("   .clk_out1   ("+module_name+"_clk_out1),")
        lst_wire.append("wire	"+module_name+"_clk_out1;")
    if(clkout_num>2):
        lst_inst.append("   .clk_out2   ("+module_name+"_clk_out2),")
        lst_wire.append("wire	"+module_name+"_clk_out2;")
    if(clkout_num>3):
        lst_inst.append("   .clk_out3   ("+module_name+"_clk_out3),")
        lst_wire.append("wire	"+module_name+"_clk_out3;")
    if(clkout_num>4):
        lst_inst.append("   .clk_out4   ("+module_name+"_clk_out4),")
        lst_wire.append("wire	"+module_name+"_clk_out4;")
    if(clkout_num>5):
        lst_inst.append("   .clk_out5   ("+module_name+"_clk_out5),")
        lst_wire.append("wire	"+module_name+"_clk_out5;")
    if(clkout_num>6):
        lst_inst.append("   .clk_out6   ("+module_name+"_clk_out6),")
        lst_wire.append("wire	"+module_name+"_clk_out6;")
    lst_wire.append("wire	"+module_name+"_clk_in0;")
    lst_inst.append("   .clk_in0    ("+module_name+"_clk_in0)")
    if(clkin_num>1):
        lst_wire.append("wire	"+module_name+"_clk_in1;")
        lst_inst.append("   .clk_in1    (clk_in1)")
    lst_wire.append("wire	"+module_name+"_reset;")
    lst_inst.append("   .reset      ("+module_name+"_reset),")
    lst_wire.append("wire	"+module_name+"_locked;")
    lst_inst.append("   .locked     ("+module_name+"_locked));")
    
    return [lst_wire, lst_inst]
		
