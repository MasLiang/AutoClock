set_false_path -from [get_clocks clk_kernel_00_unbuffered_net] -to [get_clocks clk2]
set_false_path -from [get_clocks clk2] -to [get_clocks clk_kernel_00_unbuffered_net]
