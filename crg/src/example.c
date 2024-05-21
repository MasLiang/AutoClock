#pragma HLS clkdomain clk_src 10
void example(){
	
	#pragma HLS clkdomain clk1 10 5 3
	#pragma HLS clksel clk1 sel 
	module_1(sel);
	#pragma HLS clkdomain clk2 2
	#pragma HLS clken clk2 cen
	module_2(cen);
	#pragma HLS clkdomain clk3 30
	module_3();
}

void module_1(int sel)
{
    #pragma HLS INTERFACE ap_none port=sel
};

void module_2(int cen)
{
    #pragma HLS INTERFACE ap_none port=cen
};
