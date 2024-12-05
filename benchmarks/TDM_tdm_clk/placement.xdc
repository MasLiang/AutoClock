set_false_path -from [get_clocks clk_kernel_00_unbuffered_net] -to [get_clocks *clk2*]
set_false_path -from [get_clocks *clk2*] -to [get_clocks clk_kernel_00_unbuffered_net]
set_false_path -from [get_pins level0_i/ulp/top/inst/u_crg/xpm_cdc_async_rst_top_kernel_m2_0_clk/arststages_ff_reg[1]/C]
