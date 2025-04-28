# AutoClock

This project is a extension of VITIS-HLS to manage clock automatically for 
low-power HLS design. Currently, only support Xilinx Ultrascale and Ultrascale+. 

## Features (Continuously updating)
    
### generate CRG automatically.
    
1. PLL/MMCM/BUFGCE_DIV selection automatically

    e.g., 

       #pragma HLS inputclk clk_src 10
       void top(){
         #pragma HLS clkdomain clk1 20
         module_1();
         #pragma HLS clkdomain clk2 15
         module_2();
       };

    In this example, "clk_src" is connected to ap_clock. Since the frequency of "clk1"
    is 1/2 of "clk_src", the BUFGCE_DIV is used to generate it. For "clk2", PLL is used.
            
2. rst_sync
Reset for each clock domain will be generated automatically.

### generate CDC circuit automatically according to INTERFACE type.
        
1. Insert CDC circuits between different clock domain. The CDC circuit selection depends on the INTERFACE type.

- FIFO interface: async-fifo
- BRAM interface: async-bram 
- FSM : 
  - set FSM at the fasest clock domain
  - expanding control signals
    - syncronize the edge if they are pose-sensitive
  - pipe for some states because of clock domain
           
2.  Updated original clock/reset related signals 

### clock multiplexering scheme for modules instantiated by multiple clock domains
        
1. Insert clock mux to generate a new clock domain

2. Generate selection signals

### insert clock gates 

1. From high to low level 
        
2. Skip sub-modules of dataflow modules

- if a dataflow modules is well optimized for streaming, sub-modules will always run with 
  father module.
   
- based on Xilinx Power Estimator
    
### modify the interface to increase the maximum frequency

## How to run:
- Install packages:
  - pyverilog
  - pulp

- cd to the path of a benchmark, modify the path of AutoClock

- "make xclbin" to generate bitstream

- "make host" to generate host.exe

- "host.exe -xclbin top.xclbin" to run it on FPGA

### How to apply it in your own project
- Modify the Makefile
  - Declare the path of AutoClock
  - Before V++ -c, run AutoClock_step1.py
  - After V++ -c and before V++ -l, run AutoClock_step2.py
    -- root_path: the root path of the project. In this project, the top.cpp 
                  should be in root_path/kernel/.
    -- proj_path: the path of the hardware project. Generally, the hardware 
                  hardware project will be in a temp_dir if a similar Makefile
                  is used. Then the project_path will be temp_dir/proj_name/proj_name.
    -- proj_name: the name of the hardware project. e.g., "top".
    -- cpp_top_name: the numer of the top.cpp. e.g., "top".
    -- solution_name: the hardware solution name. e.g., "solution".
    -- xo_path: the path of the .xo file.
    -- rdm/dfs/bfs: gating strategy. default, all of them are disabled and a hierarchical
                    gready based strategy is used.
    -- gate_num: the maximum number of clock gates that can be used.
    -- gate_level: the maximum number of clock gates that can be cascaded. Using larger 
                   values is not recommended as it can result in larger clock skew.
    -- gate_enable: if clock gate is used.
    -- done_reg: if use a refined ap_ctrl_chain. It is recommended to use for better timing.
    -- cg_pipe_en : if clock enable is pipelined for better timing. It is reconmmended to 
                    use when the number of modules is large.
    

    
