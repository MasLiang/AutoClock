import math

def pll_calc_fac(in_period, out_period):
    # This function is used to calculate factor of a single PLL.
    # Mux out frequency number is 2.
    # If output is [], this PLL can not be gen.

    # a = f_in * fac_mult_all
    # b = a / fac_div_all
    # for each k, fk = b / fac_div_k
    #
    # however, input is period rather than freq, so:
    # a = 1 / p_in * fac_mult_all
    # b = a / fac_div_all
    # for each k, pk = fac_div_k / b 

    # b = fac_div_k / pk
    # for max pk, max b is 128/pk_max
    # for min pk, min b is 1/pk_min
    # 1/pk_min shoud < 128/pk_max
    # 128 pk_min > pk_max
    min_period = min(out_period)
    min_128period = 128 * min_period 
    max_period = max(out_period) 

    if min_128period < max_period:
       return [] 

    b_1_lst = [max_period/_ for _ in range(1,128+1) if (max_period/_ <= min_period and all(out_p%(max_period/_)==0 for out_p in out_period))]
    
    # 1/a = 1/b / fac_div_all
    # for a given 1/b, 1/b/15 < 1/a < 1/b
    # 1/a = p_in / fac_mult_all
    # for a given p_in, p_in / 20 < 1/a < p_pin
    for b_1 in b_1_lst:
        a_1_low_from_p = in_period / 20
        a_1_high_from_p = in_period
        a_1_lst = [b_1/_ for _ in range(1,15+1) if (b_1/_<a_1_high_from_p and b_1/_>a_1_low_from_p and in_period%(b_1/_)==0)]
        # This list is made of two list
        #   1. factor for all output clk: [[div_fac_all, mult_fac_all,[div_fac_clk1, div_fac_clk2, ...]]
        if len(a_1_lst)!=0:
            a_1 = a_1_lst[0]
            lst_fac = [b_1//a_1, in_period//a_1, [_/b_1 for _ in out_period]]
            return lst_fac

    if len(out_period)==1:
        assert "aaaa"
    # this two freq can not be generated from one PLL
    return []
    
def partition_in_order(domains, n):
    # group clock domains to n groups, n is the number of PLLs
    m = len(domains)
    results = []

    def backtrack(index, groups):
        if index == m:
            if len(groups) == n:
                results.append([g[:] for g in groups])
            return
        num = domains[index]

        for group in groups:
            if len(group) < 2:
                group.append(num)
                backtrack(index + 1, groups)
                group.pop()

        if len(groups) < n:
            groups.append([num])
            backtrack(index + 1, groups)
            groups.pop()

    backtrack(0, [])
    
    return results

        
def pll_multi_calc_fac(domains, num_pll):
    # This function is used to calculate factor of all PLL

    # group clock domains
    # [[[a,b], [c], [d,e],...]
    #  [[a], [b,c], [d,e],...]
    #  ...]
    groups = partition_in_order(domains[1:], num_pll)
    
    pll_map = {}
    for group in groups:
        #pll_map = {domains[0][0]:[]}
        pll_map_lst = []
        for pll_item in group:
            pll_fac = pll_calc_fac(domains[0][1], [_[1] for _ in pll_item])
            if pll_fac==[]:
                break
            pll_map_lst.append(["pll", [_[0] for _ in pll_item], pll_fac])
        if len(pll_map_lst)==num_pll:
            pll_map[domains[0][0]] = pll_map_lst
            break

    return pll_map
