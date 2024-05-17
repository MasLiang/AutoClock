import math

def pll_calc_first_factor(in_period, out_period):
    # This list is as this format: [[div_fac_all, mult_fac_all, [div_fac_clk1]]...]
    lst_fac = []
    for div_fac_all in range(1,15+1):
        for mult_fac_all in range(1,19+1):
            for div_fac_clk in range(1,128+1):
                if((out_period * mult_fac_all / div_fac_all / div_fac_clk)==in_period):
                    lst_fac.append([div_fac_all, mult_fac_all, div_fac_clk])
    return lst_fac

def pll_calc_later_factor(in_period, out_period, lst_factor):
    # This list is made of two list
    #   1. factor for all output clk: [[div_fac_all, mult_fac_all,[div_fac_clk1, div_fac_clk2, ...]]
    selected_lst_factor = []
    for fac_grp in lst_factor:
        for div_fac_clk in range(1,128+1):
            if((out_period * fac_grp[1] / fac_grp[0] / div_fac_clk)==in_period):
                selected_lst_factor.append(fac_grp+[div_fac_clk])
                continue
    
    return selected_lst_factor

def pll_calc_fac(in_period, out_period, clkout_num):
    # This function is used to calculate PLL factor.
    # Mux out frequency number is 2.
    # If output is [], this PLL can not be gen.
    lst_factor =   pll_calc_first_factor(in_period, out_period[0])
    if(len(lst_factor)==0):
        # TODO
        # assert warnning
        return []
    if(clkout_num==1):
        return lst_factor[0]

    lst_factor = pll_calc_later_factor(in_period, out_period[1], lst_factor)
    if(len(lst_factor)==0):
        # TODO
        # assert warnning
        return  []

    return lst_factor[0]
