def gen_async_level_inst(module_name, in_sig, in_clk, out_sig, out_clk):
    
    lst_inst = []
    lst_inst.append("module "+module_name+"(")
    lst_inst.append("    input clk);")

    lst_inst.append("xpm_cdc_single #(")
    lst_inst.append("   .DEST_SYNC_FF(2),")
    lst_inst.append("   .INIT_SYNC_FF(0),")
    lst_inst.append("   .SIM_ASSERT_CHK(0),")
    lst_inst.append("   .SRC_INPUT_REG(1)")
    lst_inst.append(") "+module_name+"  (")
    lst_inst.append("   .dest_out("+out_sig+"),")
    lst_inst.append("   .dest_clk("+out_clk+"),")
    lst_inst.append("   .src_clk("+in_clk+"),")
    lst_inst.append("   .src_in("+in_sig+"));")

    lst_inst.append("endmodule")
    with open(module_name+"_inst.v", "w") as f:
        for i in lst_inst:
            f.write(i)
            f.write("\n")

