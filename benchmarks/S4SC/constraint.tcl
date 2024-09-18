#create_pblock debug
#resize_pblock debug -add CLOCKREGION_X0Y4:CLOCKREGION_X6Y7
#add_cells_to_pblock debug [ get_cells -regexp {
#    level0_i/ulp/rwkv_top/inst/.*/grp_Layer_Norm_vector_s.*
#    level0_i/ulp/rwkv_top/inst/.*/.*/grp_MVV_large_fusion_s.*
#    level0_i/ulp/rwkv_top/inst/.*/.*/grp_dynamic_act_quant32_s_5_fu.*
#    level0_i/ulp/rwkv_top/inst/.*/grp_MVV_int4_s_fu.*
#} ]

# level0_i/ulp/rwkv_top/inst/.*/.*/.*/MVVq_large_vec_s0_s.*
# level0_i/ulp/rwkv_top/inst/.*/.*/.*/MVVq_large_vec_s0_r_s.*
# level0_i/ulp/rwkv_top/inst/.*/.*/.*/MVVq_large_vec_s1_s.*
# level0_i/ulp/rwkv_top/inst/.*/.*/.*/MVVq_large_vec_s2_s.*
# level0_i/ulp/rwkv_top/inst/.*/.*/.*/MVV_large_fusion_s2.*
