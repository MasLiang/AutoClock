# AutoClock

This project open-source code of AutoClock for low-power HLS design. 
Currently, only support Xilinx Ultrascale and Ultrascale+. 

CRG.pdf illustrates an example of the output of AutoCLock.

## Features (Continuously updating)
    
### generate CRG automatically. (done)
    
#### PLL/MMCM/BUFGCE_DIV selection automatically
e.g., 

       #pragma HLS inputclk clk_src 10
       void top(){
         #pragma HLS clkdomain clk1 20
         module_1();
         #pragma HLS clkdomain clk2 15
         module_2();
       };

In this example, "clk_src" is connected to clock pin. Since the frequency of "clk1"
is 1/2 of "clk_src", the BUFGCE_DIV is used to generate it. For "clk2", PLL is used.
            
#### rst_sync
Reset for each clock domain will be generated automatically.

#### output file:
- Wrapper of PLL if PLL is used
- Wrapper of MMCM if MMCM is used
- CRG module

### generate CDC circuit automatically according to INTERFACE type. (done)
        
#### insert CDC circuits between different clock domain

The CDC circuit selection depends on the INTERFACE type.

- FIFO interface: async-fifo
- BRAM interface: async-bram 
- FSM : 
  - set FSM at the fasest clock domain
  - expanding control signals
    - syncronize the edge if they are pose-sensitive
  - pipe for some states because of clock domain
           
#### original clock/reset related signals need to be updated

#### output file:

   CDC circuit

   modified modules

### clock multiplexering scheme for modules instantiated by multiple clock domains
        
#### insert clock mux to generate a new clock domain

#### generate selection signals

### insert clock gates 

#### from high to low level 
        
#### skip sub-modules of dataflow modules
     - if a dataflow modules is well optimized for streaming, sub-modules will always run with 
       father module.
        
     - based on Xilinx Power Estimator
    
### modify the interface to increase the maximum frequency

## How to run:
        - install packages:
            - pyverilog

        - cd to the path of a benchmark, modify the path of AutoClock

        - "make xclbin" to generate bitstream

        - "make host" to generate host.exe

        - "host.exe -xclbin top.xclbin" to run it on FPGA
