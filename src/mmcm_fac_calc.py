import math

def mmcm_calc_first_factor(in_period, out_period):
    # This list is as this format: [[div_fac_all, mult_fac_all, [div_fac_clk1]]...]
    lst_fac = []
    for div_fac_all in range(1,106+1):
        for mult_fac_all in range(16,512+1): # 2~64, stride is 0.125
            for div_fac_clk in range(1,128+1):
                if((out_period * (mult_fac_all/8) / div_fac_all / div_fac_clk)==in_period):
                    lst_fac.append([div_fac_all, (mult_fac_all/8), [div_fac_clk]])
    return lst_fac

def mmcm_calc_later_factor(in_period, out_period, lst_factor):
    # This list is made of two list
    #   1. factor for all output clk: [[div_fac_all, mult_fac_all,[div_fac_clk1, div_fac_clk2, ...]]
    selected_lst_factor = []
    for fac_grp in lst_factor:
        for div_fac_clk in range(1,128+1):
            if((out_period * fac_grp[1] / fac_grp[0] / div_fac_clk)==in_period):
                selected_lst_factor.append([fac_grp[0], fac_grp[1],fac_grp[2]+[div_fac_clk]])
                continue
    
    return selected_lst_factor

def mmcm_single_calc_fac(in_period, out_period):
    # This function is used to calculate MMCM factor.
    # Mux out frequency number is 7.
    # If output is [], this mmcm can not be gen.
    lst_factor =   mmcm_calc_first_factor(in_period, out_period[0])
    if(len(lst_factor)==0):
        return []
    if(len(out_period)==1):
        return lst_factor[0]
    
    for clk_idx in range(1,len(out_period)):
        lst_factor = mmcm_calc_later_factor(in_period, out_period[clk_idx], lst_factor)
        if(len(lst_factor)==0):
            return  []

    return lst_factor[0]

def mmcm_multi_calc_fac(domains):
    # This function is used to calculate multi_mmcm factor.

    name_domains = list(domains.keys())
    num_domains = len(name_domains)
    mmcm_map = {name_domains[0]:[]}

    # calculate which clock can be generated in a single MMCM
    push_period_lst = []
    push_name_lst = []
    pop_domain_dic = {}    
    for dom_idx in range(1,num_domains):
        push_period_lst.append(domains[name_domains[dom_idx]])
        push_name_lst.append(name_domains[dom_idx])
        mmcm_fac = mmcm_single_calc_fac(domains[name_domains[0]], push_period_lst)
        if(mmcm_fac==[]):
            if(len(push_period_lst)==1):
                # TODO
                # assert Error
                return mmcm_map
            pop_domain_dic = {**pop_domain_dic, push_name_lst.pop():push_period_lst.pop()}
        if(len(push_name_lst)==7):
            mmcm_map[name_domains[0]].append(["mmcm", push_name_lst, mmcm_fac])
            push_name_lst = []
            push_period_lst = []
    
    if(len(push_name_lst)!=0):
        mmcm_map[name_domains[0]].append(["mmcm", push_name_lst, mmcm_fac])
    
    if(pop_domain_dic=={}):
        return mmcm_map    

    later_mmcm_map  = mmcm_multi_calc_fac({name_domains[0]:domains[name_domains[0]], **pop_domain_dic})
    mmcm_map[name_domains[0]] = mmcm_map[name_domains[0]]+later_mmcm_map[name_domains[0]]

    return mmcm_map 


domains = {"src_clk": 10, "clk1": 5, "clk2": 3, "clk3":19}
print(mmcm_multi_calc_fac(domains))
    
