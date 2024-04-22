def gen_rstsync(module_name):
    lst_inst = []
    lst_wire = []

    lst_wire.append("wire   "+module_name+"_dest_arst;")
    lst_wire.append("wire   "+module_name+"_src_arst;")
    lst_wire.append("wire   "+module_name+"_dest_clk;")

    lst_inst.append("xpm_cdc_async_rst #(")
    lst_inst.append("   .DEST_SYNC_FF(2),")
    lst_inst.append("   .INIT_SYNC_FF(0),")    
    lst_inst.append("   .RST_ACTIVE_HIGH(0)")
    lst_inst.append(") xpm_cdc_async_rst_"+module_name+" (")
    lst_inst.append("   .dest_arst(dest_arst),")
    lst_inst.append("   .dest_clk(dest_clk),")
    lst_inst.append("   .src_arst(src_arst)")
    lst_inst.append(");")
