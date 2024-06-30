#pragma HLS inputclk  clk_src 20
void example(){
	
	#pragma HLS clkdomain clk1 4 5
	#pragma HLS clksel clk1 sel 
	module_1(int* in1, int* in2, int* out, int sel);
	#pragma HLS clkdomain clk3 30
	module_2();
}

void module_1(int* in1, int* in2, int* out, int sel)
{
    #pragma HLS INTERFACE ap_none port=sel
    out = int1*int2;
    if out==0:
        sel = 1;
    else:
        sel = 0;
};

void module_2(int cen)
{
    #pragma HLS INTERFACE ap_none port=cen
};
