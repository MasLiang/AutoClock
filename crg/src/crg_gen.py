from .template.mmcme4_adv import *
from .template.plle4_adv import *
from .template.bufgmux import *
from .template.bufgce_div import *
from .template.rst_sync import *
from .template.bufgce import *
from .clk_domain_analyze import clk_resource_cal
from .clk_domain_extract import extract_clk_domains

def crg_gen(file):
    modules, domains, domains_sel_if, fastest_clk_map= extract_clk_domains(file)
    clk_map_mux, clk_map_bypass, clk_map_div, clk_map_mmcm, domains = clk_resource_cal(domains)
    
    lst_port = []
    lst_assign = []    
    lst_mmcm_wire = []
    lst_mmcm_inst = []
    lst_pll_wire = []
    lst_pll_inst = []
    lst_bufgdiv_wire = []
    lst_bufgdiv_inst = []
    lst_bufgmux_wire = []
    lst_bufgmux_inst = []
    lst_rst_sync_wire = []
    lst_rst_sync_inst = []
    lst_bufgce_wire = []
    lst_bufgce_inst = []
    lst_bufi_wire = []
    lst_bufi_inst = []
    lst_crg_inst = []
    lst_crg_wire = []

    top_module = list(modules.keys())[0]
    lst_clk = list(domains.keys())
    src_clk = lst_clk[0]
    
    lst_bufi_wire.append("wire    "+src_clk+"_ibuf;")
    lst_bufi_inst.append("IBUF clkin_ibuf")
    lst_bufi_inst.append("(    .o    ("+src_clk+"_ibuf),")
    lst_bufi_inst.append("     .I    ("+src_clk+"));")

    #print("clk_map_mux" , clk_map_mux)
    #print("clk_map_bypass" , clk_map_bypass)
    #print("clk_map_div" , clk_map_div)
    #print("clk_map_mmcm" , clk_map_mmcm)
    #print("sel_if:", domains_sel_if)
    #print("module:", modules)
    #print("domains:", domains)
    
    # generate mmcm or pll to generate clks in domains
    for unit_idx in range(len(clk_map_mmcm[src_clk])):
        unit = clk_map_mmcm[src_clk][unit_idx]
        clkin_period = domains[src_clk]
        clkout_num = len(unit[1])
        if unit[0] == "mmcm":
            lst_mmcm = gen_mmcme4_inst("mmcm"+str(unit_idx),[clkin_period, clkout_num]+unit[2]+[0 for _ in range(7-clkout_num)])
            lst_mmcm_wire += lst_mmcm[0]
            lst_mmcm_inst += lst_mmcm[1]
            lst_assign.append(f'''{'assign    mmcm'+str(unit_idx)+'_clk_in0':<40}=    {src_clk}_ibuf;''')
            lst_assign.append(f'''{'assign    mmcm'+str(unit_idx)+'_reset':<40}=    ~rst_n_sys;''')
        elif unit[0]=="pll":
            lst_pll = gen_plle4_inst("pll"+str(unit_idx),[clkin_period, clkout_num]+unit[2]+[0 for _ in range(2-clkout_num)])
            lst_pll_wire += lst_pll[0]
            lst_pll_inst += lst_pll[1]
            
            
    # gen BUFXXX according to clk_map
    # gen div
    for unit in list(clk_map_div.keys()):
        lst_bufgdiv = gen_bufgce_div("div_"+unit, clk_map_div[unit][2])
        lst_bufgdiv_wire += lst_bufgdiv[0]
        lst_bufgdiv_inst += lst_bufgdiv[1]
        # connect input of div to src_clk
        if clk_map_div[unit][1] == src_clk:
            lst_assign.append(f'''{'assign    div_'+unit+'_i':<40}=    {src_clk}_ibuf;''')
        # connect input of div to output of mux
        elif clk_map_div[unit][1] in clk_map_mux:
            lst_assign.append(f'''{'assign    div_'+unit+'_i':<40}=    mux_{clk_map_div[unit][1]}_clk_out;''')
        # connect input of div to output of bypass
        elif clk_map_div[unit][1] in clk_map_bypass:
            lst_assign.append(f'''{'assign    div_'+unit+'_i':<40}=    {clk_map_div[unit]};''')
        # connect input of div to output of mmcm or pll
        else:
            for pll_mmcm_idx in range(len(clk_map_mmcm[src_clk])):
                # connect input of div to output of mmcm
                if clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="mmcm": 
                    outlst_mmcm = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                    for clk_idx in range(len(outlst_mmcm)):
                        if clk_map_div[unit][1] ==outlst_mmcm[clk_idx]:
                            lst_assign.append(f'''{'assign    div_'+unit+'_i':<40}=    mmcm{str(pll_mmcm_idx)}_clk_out{str(clk_idx)}''')
                            continue
                # connect input of div to output of pll
                elif clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="pll":
                    outlst_pll = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                    for clk_idx in range(len(outlst_pll)):
                        if clk_map_div[unit][1] ==outlst_pll[clk_idx]:
                            lst_assign.append(f'''{'assign    div_'+unit+'_i':<40}=    pll{str(pll_mmcm_idx)}_clk_out{str(clk_idx)}''')
                            continue

    
    # gen bypass
    for unit in list(clk_map_bypass.keys()):
        if clk_map_bypass[unit][1] == src_clk:
            lst_assign.append(f'''{'assign    '+unit:<40}=    {clk_map_bypass[unit][1]}_ibuf;''')
        # connect input of bypass to output of mux
        elif clk_map_bypass[unit][1] in clk_map_mux:
            lst_assign.append(f'''{'assign    '+unit:<40}=    mux_{clk_map_bypass[unit][1]}_clk_out;''')
        # connect input of bypass to output of div
        elif clk_map_bypass[unit][1] in clk_map_div:
            lst_assign.append(f'''{'assign    '+unit:<40}=    div_{clk_map_bypass[unit][1]}_o;''')
        # connect input of bypass to output of mmcm or pll
        else:
            for pll_mmcm_idx in range(len(clk_map_mmcm[src_clk])):
                # connect input of div to output of mmcm
                if clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="mmcm": 
                    outlst_mmcm = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                    for clk_idx in range(len(outlst_mmcm)):
                        if clk_map_bypass[unit][1] ==outlst_mmcm[clk_idx]:
                            lst_assign.append(f'''{'assign    '+unit:<40}=    mmcm{str(pll_mmcm_idx)}_clk_out{str(clk_idx)};''')
                            continue
                # connect input of div to output of pll
                elif clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="pll":
                    outlst_pll = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                    for clk_idx in range(len(outlst_pll)):
                        if clk_map_bypass[unit][1] ==outlst_pll[clk_idx]:
                            lst_assign.append(f'''{'assign    '+unit:<40}=    pll{str(pll_mmcm_idx)}_clk_out{str(clk_idx)};''')
                            continue

    # gen mux
    for unit in list(clk_map_mux.keys()):
        lst_bufgmux = gen_bufgmux("mux_"+unit)
        lst_bufgmux_wire += lst_bufgmux[0]
        lst_bufgmux_inst += lst_bufgmux[1]
        lst_bufgmux_inst += ["\n"]
        # connect input of mux to others
        for mux_in_idx in range(2):
            # connect input of mux to src_clk
            if clk_map_mux[unit][1][mux_in_idx] == src_clk:
                lst_assign.append(f'''{'assign    mux_'+unit+'_clk_in_'+str(mux_in_idx):<40}=    {src_clk}_ibuf;''')
            # connect input of mux to output of div
            elif clk_map_mux[unit][1][mux_in_idx] in clk_map_div:
                lst_assign.append(f'''{'assign    mux_'+unit+'_clk_in_'+str(mux_in_idx):<40}=    div_{unit}_o;''')
            # connect input of mux to output of bypass
            elif clk_map_mux[unit][1][mux_in_idx] in clk_map_bypass:
                lst_assign.append(f'''{'assign    mux_'+unit+'_clk_in_'+str(mux_in_idx):<40}=    {clk_map_mux[unit][1][mux_in_idx]};''')
            # connect input of mux to output of other mux
            elif clk_map_mux[unit][1][mux_in_idx] in clk_map_mux:
                lst_assign.append(f'''{'assign    mux_'+unit+'_clk_in_'+str(mux_in_idx):<40}=    mux_{clk_map_mux[unit][1][mux_in_idx]}_clk_out;''')
            # connect input of mux to output of mmcm or pll
            else:
                for pll_mmcm_idx in range(len(clk_map_mmcm[src_clk])):
                    # connect input of div to output of mmcm
                    if clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="mmcm": 
                        outlst_mmcm = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                        for clk_idx in range(len(outlst_mmcm)):
                            if clk_map_mux[unit][1][mux_in_idx] == outlst_mmcm[clk_idx]:
                                lst_assign.append(f'''{'assign    mux_'+unit+'_clk_in_'+str(mux_in_idx):<40}=    mmcm{str(pll_mmcm_idx)}_clk_out{str(clk_idx)};''')
                                continue
                    # connect input of div to output of pll
                    elif clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="pll":
                        outlst_pll = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                        for clk_idx in range(len(outlst_pll)):
                            if clk_map_mux[unit][1][mux_in_idx] == outlst_pll[clk_idx]:
                                lst_assign.append(f'''{'assign    mux_'+unit+'_clk_in_'+str(mux_in_idx):<40}=    pll{str(pll_mmcm_idx)}_clk_out{str(clk_idx)};''')
                                continue
    
    # gen port
    lst_port.append(f'''module {top_module}_crg{'{'}''')
    lst_crg_inst.append(f'''{top_module}_crg u_crg(''')
    for clk in lst_clk[1:]:
        if clk in domains_sel_if :
            lst_port.append("   input       "+clk+"_"+domains_sel_if[clk][0]+",")
            lst_crg_inst.append(f'''{'    .'+clk+'_'+domains_sel_if[clk][0]:<40}({clk+'_'+domains_sel_if[clk][0]}),''')
            lst_crg_wire.append("wire    "+clk+'_'+domains_sel_if[clk][0]+";")
            lst_assign.append(f'''{'assign    mux_'+clk+'_sel':<40}=    {clk}_{domains_sel_if[clk][0]};''')
        lst_port.append("   input       "+clk+"_en,")
        lst_crg_inst.append(f'''{'    .'+clk+'_en':<40}({clk+'_en'}),''')
        lst_crg_wire.append("wire    "+clk+"_en;")
        lst_assign.append(f'''{'assign    bufgce_'+clk+'_gce':<40}=    {clk}_en;''')
        lst_port.append("   output      "+clk+",")
        lst_crg_inst.append(f'''{'   .'+clk:<40}({clk}),''')
        lst_crg_wire.append("wire    "+clk+";")
        lst_port.append("   output      rst_"+clk+",")
        lst_crg_inst.append(f'''{'   .rst_'+clk:<40}({'rst_'+clk}),''')
        lst_crg_wire.append("wire    rst_"+clk+";")
    lst_port.append("\n")
    lst_port.append("   input       "+src_clk+",")
    lst_crg_inst.append(f'''{'   .'+src_clk:<40}(ap_clk),''')
    lst_port.append("   input       rst_n_sys")
    lst_crg_inst.append(f'''{'   .rst_n_sys':<40}(ap_rst_n));''')
    lst_port.append(");")
    lst_port.append("\n")
    
    # assign output of each macro to port
    for clk in lst_clk:
        if(clk==src_clk):
            continue
        elif clk in clk_map_mux:
            lst_assign.append(f'''{'assign    '+clk:<40}=    bufgce_{clk}_clk_out;''')
            lst_assign.append(f'''{'assign    bufgce_'+clk+"_clk_in":<40}=    mux_{clk}_clk_out;''')
            lst_bufgce = gen_bufgce("bufgce_"+clk)
            lst_bufgce_wire += lst_bufgce[0]
            lst_bufgce_inst += lst_bufgce[1]
                
        elif clk in clk_map_div:
            lst_assign.append(f'''{'assign    '+clk:<40}=    bufgce_{clk}_clk_out;''')
            lst_assign.append(f'''{'assign    bufgce_'+clk+'_clk_in':<40}=    div_{clk}_o;''')
            lst_bufgce = gen_bufgce("bufgce_"+clk)
            lst_bufgce_wire += lst_bufgce[0]
            lst_bufgce_inst += lst_bufgce[1]
        else:
            for pll_mmcm_idx in range(len(clk_map_mmcm[src_clk])):
                if(clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="mmcm"):
                    outlst_mmcm = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                    for clk_idx in range(len(outlst_mmcm)):
                        if outlst_mmcm[clk_idx]==clk:
                            lst_assign.append(f'''{'assign    '+clk:<40}=    bufgce_{clk}_clk_out;''')
                            lst_assign.append(f'''{'assign    bufgce_'+clk+'_clk_in':<40}=    mmcm{str(pll_mmcm_idx)}_clk_out{str(clk_idx)};''')
                            lst_bufgce = gen_bufgce("bufgce_"+clk)
                            lst_bufgce_wire += lst_bufgce[0]
                            lst_bufgce_inst += lst_bufgce[1]
                elif(clk_map_mmcm[src_clk][pll_mmcm_idx][0]=="pll"):
                    outlst_pll = clk_map_mmcm[src_clk][pll_mmcm_idx][1]
                    for clk_idx in range(len(outlst_pll)):
                        if outlst_pll[clk_idx]==clk:
                            lst_assign.append(f'''{'assign    '+clk:<40}=    bufgce_{clk}_clk_out;''')
                            lst_assign.append(f'''{'assign    bufgce_'+clk+'_clk_in':<40}=    pll{str(pll_mmcm_idx)}_clk_out{str(clk_idx)};''')
                            lst_bufgce = gen_bufgce("bufgce_"+clk)
                            lst_bufgce_wire += lst_bufgce[0]
                            lst_bufgce_inst += lst_bufgce[1]
        # rst sync gen
        lst_rst_sync = gen_rstsync(clk)
        lst_rst_sync_wire += lst_rst_sync[0]
        lst_rst_sync_inst += lst_rst_sync[1]
        lst_rst_sync_inst += ["\n"]
        for unit_idx in range(len(clk_map_mmcm[src_clk])):
            if clk in clk_map_mmcm[src_clk][unit_idx][1]:
                if clk_map_mmcm[src_clk][unit_idx][0]=="pll":
                    lst_assign.append(f'''{'assign    '+clk+'_src_arst':<40}=    ~(rst_n_sys & pll{unit_idx}_locked);''')
                else:
                    lst_assign.append(f'''{'assign    '+clk+'_src_arst':<40}=    ~(rst_n_sys & mmcm{unit_idx}_locked);''')
            else:
                lst_assign.append(f'''{'assign    '+clk+'_src_arst':<40}=    ~rst_n_sys;''')
        lst_assign.append(f'''{'assign    rst_'+clk:<40}=    {clk}_dest_arst;''')
        lst_assign.append(f'''{'assign    '+clk+'_dest_clk':<40}=    {clk};''')

    lst_assign.sort()
            


    lst_wire = lst_bufi_wire + ["\n"] + lst_mmcm_wire + ["\n"] + lst_pll_wire + ["\n"] +lst_bufgdiv_wire + ["\n"] +lst_bufgmux_wire + ["\n"] + lst_bufgce_wire + ["\n"] + lst_rst_sync_wire 
    lst_inst = lst_bufi_inst + ["\n"] + lst_mmcm_inst + ["\n"] + lst_pll_inst + ["\n"] +lst_bufgdiv_inst + ["\n"] +lst_bufgmux_inst + ["\n"] + lst_bufgce_inst + ["\n"] + lst_rst_sync_inst
    lst_wfile = lst_port + ["\n"] + lst_wire + ["\n"] + lst_inst + ["\n"] + lst_assign

    with open(top_module+"_crg.v", "w") as f:
        for line in lst_wfile:
            f.write(line)
            if(line!="\n"):
                f.write("\n")

    with open(top_module+"_crg_inst.v", "w") as f:
        f.write("module "+top_module+"_crg_inst(\n")
        f.write("input clk,\n")
        f.write("input rst_n);\n")
        for line in lst_crg_wire:
            f.write(line)
            f.write("\n")        
        for line in lst_crg_inst:
            f.write(line)
            f.write("\n")        
        f.write("endmodule")

    return domains, modules, fastest_clk_map
