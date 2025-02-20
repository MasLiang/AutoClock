
#include "rwkv_top.hpp"


typedef  hls::vector<float, AVG_CHUNK_NUM> t_chunk_vector;

typedef  hls::vector<float, n_embed> t_floatVec;
typedef  hls::vector<float, stream_kernel_float_0> t_floatVec_0;
typedef  hls::vector<float, stream_kernel_float_1> t_floatVec_1;
typedef  hls::vector<int8_t, n_embed> t_int8Vec;
typedef  hls::vector<int8_t, stream_kernel_int8_0> t_int8Vec_0;
typedef  hls::vector<int8_t, stream_kernel_int_0> t_intVec_0;
typedef  hls::vector<int8_t, stream_kernel_int8_1> t_int8Vec_1;
typedef  hls::vector<int16_t, n_embed> t_int16Vec;
typedef  hls::vector<int16_t, stream_kernel_int16_0> t_int16Vec_0;
typedef  hls::vector<float, group_num> t_floatGroup;
typedef  hls::vector<float, group_num_large> t_floatGroup_l;

struct WeightLN
{
	t_floatVec weight;
	t_floatVec bias;
};

struct WeightLN_s
{
	hls::stream<t_floatVec_0> weight;
	hls::stream<t_floatVec_0> bias;
};

struct WeightFFN
{
	t_floatVec time_mix_k;
	t_floatVec time_mix_r;
	t_int8Vec r_weight[n_embed];
	t_int8Vec k_weight[n_embed];
	t_int8Vec v_weight[n_embed];
	t_floatGroup r_vec_mr[n_embed];
	t_floatGroup r_vec_mk[n_embed];
	t_floatGroup r_vec_mv[n_embed];
};

struct WeightFFN_s
{
	hls::stream<t_floatVec_0> time_mix_k;
	hls::stream<t_floatVec_0> time_mix_r;
	hls::stream<t_int8Vec_1> r_weight;
	hls::stream<t_int8Vec_1> k_weight;
	hls::stream<t_int8Vec_1> v_weight;
	hls::stream<float> r_vec_mr;
	hls::stream<float> r_vec_mk;
	hls::stream<float> r_vec_mv;
};

struct WeightATT
{
	t_floatVec time_mix_k;
	t_floatVec time_mix_v;
	t_floatVec time_mix_r;
	t_floatVec time_first;
	t_floatVec time_decay;
	t_int8Vec r_weight[n_embed];
	t_int8Vec k_weight[n_embed];
	t_int8Vec v_weight[n_embed];
	t_int8Vec o_weight[n_embed];
	t_floatGroup r_vec_mr[n_embed];
	t_floatGroup r_vec_mk[n_embed];
	t_floatGroup r_vec_mv[n_embed];
	t_floatGroup r_vec_mo[n_embed];
};

struct WeightATT_s
{
	hls::stream<t_floatVec_0> time_mix_k;
	hls::stream<t_floatVec_0> time_mix_v;
	hls::stream<t_floatVec_0> time_mix_r;
	hls::stream<t_floatVec_0> time_first;
	hls::stream<t_floatVec_0> time_decay;
	hls::stream<t_int8Vec_1> r_weight;
	hls::stream<t_int8Vec_1> k_weight;
	hls::stream<t_int8Vec_1> v_weight;
	hls::stream<t_int8Vec_1> o_weight;
	hls::stream<float> r_vec_mr;
	hls::stream<float> r_vec_mk;
	hls::stream<float> r_vec_mv;
	hls::stream<float> r_vec_mo;
};

struct WeightBlock
{
	WeightLN ln1;
	WeightLN ln2;
	WeightATT att;
	WeightFFN ffn;
};

struct WeightBlock_s
{
	WeightLN_s ln1;
	WeightLN_s ln2;
	WeightATT_s att;
	WeightFFN_s ffn;
};

struct State{
	t_floatVec xx;
	t_floatVec xx_ffn;
	t_floatVec aa;
	t_floatVec bb;
	t_floatVec pp;
};

struct State_s{
	hls::stream<t_floatVec_0> xx;
	hls::stream<t_floatVec_0> xx_ffn;
	hls::stream<t_floatVec_0> aa;
	hls::stream<t_floatVec_0> bb;
	hls::stream<t_floatVec_0> pp;
};

float abs_val(float x) {
    return x < 0 ? -x : x;
}


float find_max_abs_32(float a1, float a2, float a3, float a4, float a5, float a6, float a7, float a8,
                   float b1, float b2, float b3, float b4, float b5, float b6, float b7, float b8,
                   float c1, float c2, float c3, float c4, float c5, float c6, float c7, float c8,
                   float d1, float d2, float d3, float d4, float d5, float d6, float d7, float d8) {

	float max1 = abs_val(a1) > abs_val(a2) ? abs_val(a1) : abs_val(a2);
	float max2 = abs_val(a3) > abs_val(a4) ? abs_val(a3) : abs_val(a4);
	float max3 = abs_val(a5) > abs_val(a6) ? abs_val(a5) : abs_val(a6);
	float max4 = abs_val(a7) > abs_val(a8) ? abs_val(a7) : abs_val(a8);

	float max5 = abs_val(b1) > abs_val(b2) ? abs_val(b1) : abs_val(b2);
	float max6 = abs_val(b3) > abs_val(b4) ? abs_val(b3) : abs_val(b4);
	float max7 = abs_val(b5) > abs_val(b6) ? abs_val(b5) : abs_val(b6);
	float max8 = abs_val(b7) > abs_val(b8) ? abs_val(b7) : abs_val(b8);

	float max9 = abs_val(c1) > abs_val(c2) ? abs_val(c1) : abs_val(c2);
	float max10 = abs_val(c3) > abs_val(c4) ? abs_val(c3) : abs_val(c4);
	float max11 = abs_val(c5) > abs_val(c6) ? abs_val(c5) : abs_val(c6);
	float max12 = abs_val(c7) > abs_val(c8) ? abs_val(c7) : abs_val(c8);

	float max13 = abs_val(d1) > abs_val(d2) ? abs_val(d1) : abs_val(d2);
	float max14 = abs_val(d3) > abs_val(d4) ? abs_val(d3) : abs_val(d4);
	float max15 = abs_val(d5) > abs_val(d6) ? abs_val(d5) : abs_val(d6);
	float max16 = abs_val(d7) > abs_val(d8) ? abs_val(d7) : abs_val(d8);

    float max17 = max1 > max2 ? max1 : max2;
    float max18 = max3 > max4 ? max3 : max4;
    float max19 = max5 > max6 ? max5 : max6;
    float max20 = max7 > max8 ? max7 : max8;
    float max21 = max9 > max10 ? max9 : max10;
    float max22 = max11 > max12 ? max11 : max12;
    float max23 = max13 > max14 ? max13 : max14;
    float max24 = max15 > max16 ? max15 : max16;

    
    float max25 = max17 > max18 ? max17 : max18;
    float max26 = max19 > max20 ? max19 : max20;
    float max27 = max21 > max22 ? max21 : max22;
    float max28 = max23 > max24 ? max23 : max24;

    
    float max29 = max25 > max26 ? max25 : max26;
    float max30 = max27 > max28 ? max27 : max28;

    
    return max29 > max30 ? max29 : max30;
}






























































































void split_stream(hls::stream<t_floatVec_0>& in_stream, hls::stream<t_floatVec_0>& out_stream1, hls::stream<t_floatVec_0>& out_stream2){
	#pragma HLS inline off
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
		t_floatVec_0 in_value = in_stream.read();

		
		

		out_stream1.write(in_value);
		out_stream2.write(in_value);
	}
}


void chunk_wise_average_s(
	hls::stream<t_floatVec_0>& v_stream,
	float& var,
	float& E_v
){
	#pragma HLS inline off
   float E_v_v = 0;
   float E_v_2 = 0;
   float E_v_2_v = 0;
   t_floatVec_0 v_2_i;
   float sum_chunk;
   float sum_square_chunk;

   
   for(int i = 0; i < group_num; i++){


       	t_floatVec_0 v_i = v_stream.read();
       	sum_chunk = 0;
       	sum_square_chunk = 0;

       	for(int j = 0; j < stream_kernel_float_0; j++){

           sum_chunk += v_i[j];
           sum_square_chunk += v_i[j] * v_i[j];
       }
       E_v_v = sum_chunk / stream_kernel_float_0;
       E_v_2_v = sum_square_chunk / stream_kernel_float_0;
       E_v += E_v_v;
       E_v_2 +=  E_v_2_v;
   }



   E_v /= (group_num);
   E_v_2 /= (group_num);

	
	

   var = E_v_2 - E_v * E_v;

}

void norm_s(
	float& var,
	float& E_v,
	hls::stream<t_floatVec_0>& v_stream,
	hls::stream<t_floatVec_0>& w_stream,
	hls::stream<t_floatVec_0>& b_stream,
	hls::stream<t_floatVec_0>& output_stream
){
	#pragma HLS inline off
   
   for(int i = 0; i < group_num; i++){

       	t_floatVec_0 v_i = v_stream.read();
        t_floatVec_0 w_i = w_stream.read();
        t_floatVec_0 b_i = b_stream.read();
        t_floatVec_0 output_i;

       for(int j = 0; j < stream_kernel_float_0; j++){

           output_i[j] = (v_i[j] - E_v) / sqrt(var + epsilon);
       }
       output_i = output_i * w_i + b_i;
       output_stream.write(output_i);
   }
}

void Layer_Norm_vector_s(
	hls::stream<t_floatVec_0>& v_stream,
   hls::stream<t_floatVec_0>& w_stream,
   hls::stream<t_floatVec_0>& b_stream,
   hls::stream<t_floatVec_0>& output_stream
){
	#pragma HLS dataflow
	float var;
	hls::stream<t_floatVec_0> v1_stream;
	hls::stream<t_floatVec_0> v2_stream;
	float E_v;
	
	#pragma HLS stream variable=v1_stream depth=256
	#pragma HLS stream variable=v2_stream depth=256
	
	split_stream(v_stream,v1_stream,v2_stream);
	chunk_wise_average_s(v1_stream, var, E_v);
	norm_s(var,E_v, v2_stream, w_stream, b_stream, output_stream);
}

void dynamic_act_quant(t_floatVec& input_x, t_int8Vec& output_x, t_floatGroup& r_vec){
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		float max = find_max_abs_32(input_x[32 * i + 0], input_x[32 * i + 1], input_x[32 * i + 2], input_x[32 * i + 3], input_x[32 * i + 4], input_x[32 * i + 5], input_x[32 * i + 6], input_x[32 * i + 7], input_x[32 * i + 8], input_x[32 * i + 9], input_x[32 * i + 10], input_x[32 * i + 11], input_x[32 * i + 12], input_x[32 * i + 13], input_x[32 * i + 14], input_x[32 * i + 15], input_x[32 * i + 16], input_x[32 * i + 17], input_x[32 * i + 18], input_x[32 * i + 19], input_x[32 * i + 20], input_x[32 * i + 21], input_x[32 * i + 22], input_x[32 * i + 23], input_x[32 * i + 24], input_x[32 * i + 25], input_x[32 * i + 26], input_x[32 * i + 27], input_x[32 * i + 28], input_x[32 * i + 29], input_x[32 * i + 30], input_x[32 * i + 31]);
		const float d = max / ((1 << 7) - 1);
        const float id = d ? 1.0f/d : 0.0f;
		for(int j = 0; j < 32; j++){
			#pragma hls unroll factor=16 skip_exit_check
			output_x[32 * i + j] = static_cast<int8_t>(input_x[32 * i + j] * id);
		}
		r_vec[i] = d;
	}
}
#ifdef FLOAT_32_VEC
void dynamic_act_quant32_s(hls::stream<t_floatVec_0>& input_x, hls::stream<t_int8Vec_1>& output_x, hls::stream<float>& r_vec){
	#pragma HLS inline off
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		t_floatVec_0 input_x_i = input_x.read();
		t_int8Vec_1 output_x_i;
		float max = find_max_abs_32(input_x_i[0], input_x_i[1], input_x_i[2], input_x_i[3], input_x_i[4], input_x_i[5], input_x_i[6], input_x_i[7], input_x_i[8], input_x_i[9], input_x_i[10], input_x_i[11], input_x_i[12], input_x_i[13], input_x_i[14], input_x_i[15], input_x_i[16], input_x_i[17], input_x_i[18], input_x_i[19], input_x_i[20], input_x_i[21], input_x_i[22], input_x_i[23], input_x_i[24], input_x_i[25], input_x_i[26], input_x_i[27], input_x_i[28], input_x_i[29], input_x_i[30], input_x_i[31]);
		const float d = max / ((1 << 7) - 1);
        const float id = d ? 1.0f/d : 0.0f;
		for(int j = 0; j < 32; j++){
			output_x_i[j] = static_cast<int8_t>(input_x_i[j] * id);
		}
		output_x.write(output_x_i);
		r_vec.write(d);
	}
}

void dynamic_act_quant32_large_s(hls::stream<t_floatVec_0>& input_x, hls::stream<t_int8Vec_1>& output_x, hls::stream<float>& r_vec){
	#pragma HLS inline off
	for(int i = 0; i < group_num_large; i++){
		#pragma HLS pipeline II=10
		
		t_floatVec_0 input_x_i = input_x.read();
		t_int8Vec_1 output_x_i;
		float max = find_max_abs_32(input_x_i[0], input_x_i[1], input_x_i[2], input_x_i[3], input_x_i[4], input_x_i[5], input_x_i[6], input_x_i[7], input_x_i[8], input_x_i[9], input_x_i[10], input_x_i[11], input_x_i[12], input_x_i[13], input_x_i[14], input_x_i[15], input_x_i[16], input_x_i[17], input_x_i[18], input_x_i[19], input_x_i[20], input_x_i[21], input_x_i[22], input_x_i[23], input_x_i[24], input_x_i[25], input_x_i[26], input_x_i[27], input_x_i[28], input_x_i[29], input_x_i[30], input_x_i[31]);
		const float d = max / ((1 << 7) - 1);
        const float id = d ? 1.0f/d : 0.0f;
		for(int j = 0; j < 32; j++){
			#pragma hls unroll factor=16 skip_exit_check
			output_x_i[j] = static_cast<int8_t>(input_x_i[j] * id);
		}
		output_x.write(output_x_i);
		r_vec.write(d);
	}
}
#endif

void time_mix(t_floatVec& xk, t_floatVec& xv, t_floatVec& xr, t_floatVec& state_xx, t_floatVec xx, t_floatVec time_mix_k, t_floatVec time_mix_v, t_floatVec time_mix_r){
	xk = xx * time_mix_k + state_xx * (1 - time_mix_k);
	xv = xx * time_mix_v + state_xx * (1 - time_mix_v);
	xr = xx * time_mix_r + state_xx * (1 - time_mix_r);
	state_xx = xx;
}
void time_mix_s(
    hls::stream<t_floatVec_0>& xk_stream,
    hls::stream<t_floatVec_0>& xv_stream,
    hls::stream<t_floatVec_0>& xr_stream,
    hls::stream<t_floatVec_0>& state_xx_stream_in,
	hls::stream<t_floatVec_0>& state_xx_stream_out,
    hls::stream<t_floatVec_0>& xx_stream,
    hls::stream<t_floatVec_0>& time_mix_k_stream,
    hls::stream<t_floatVec_0>& time_mix_v_stream,
    hls::stream<t_floatVec_0>& time_mix_r_stream
){
	#pragma HLS inline off
    for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
        t_floatVec_0 xk_i;
        t_floatVec_0 xv_i;
        t_floatVec_0 xr_i;
        t_floatVec_0 state_xx_i = state_xx_stream_in.read();
        t_floatVec_0 xx_i = xx_stream.read();
        t_floatVec_0 time_mix_k_i = time_mix_k_stream.read();
        t_floatVec_0 time_mix_v_i = time_mix_v_stream.read();
        t_floatVec_0 time_mix_r_i = time_mix_r_stream.read();

        for(int j = 0; j < stream_kernel_float_0; j++){
            
            xk_i[j] = xx_i[j] * time_mix_k_i[j] + state_xx_i[j] * (1 - time_mix_k_i[j]);
            xv_i[j] = xx_i[j] * time_mix_v_i[j] + state_xx_i[j] * (1 - time_mix_v_i[j]);
            xr_i[j] = xx_i[j] * time_mix_r_i[j] + state_xx_i[j] * (1 - time_mix_r_i[j]);
            state_xx_i[j] = xx_i[j];
        }

        
        xk_stream.write(xk_i);
        xv_stream.write(xv_i);
        xr_stream.write(xr_i);
        state_xx_stream_out.write(state_xx_i);
    }
}

void time_mix_FF_s(
    hls::stream<t_floatVec_0>& xk_stream,
    
    hls::stream<t_floatVec_0>& xr_stream,
    hls::stream<t_floatVec_0>& state_xx_stream_in,
	hls::stream<t_floatVec_0>& state_xx_stream_out,
    hls::stream<t_floatVec_0>& xx_stream,
    hls::stream<t_floatVec_0>& time_mix_k_stream,
    
    hls::stream<t_floatVec_0>& time_mix_r_stream
){
	#pragma HLS inline off
    for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
        t_floatVec_0 xk_i;
        
        t_floatVec_0 xr_i;
        t_floatVec_0 state_xx_i = state_xx_stream_in.read();
        t_floatVec_0 xx_i = xx_stream.read();
        t_floatVec_0 time_mix_k_i = time_mix_k_stream.read();
        
        t_floatVec_0 time_mix_r_i = time_mix_r_stream.read();

        for(int j = 0; j < stream_kernel_float_0; j++){
            #pragma hls unroll factor=16 skip_exit_check
            xk_i[j] = xx_i[j] * time_mix_k_i[j] + state_xx_i[j] * (1 - time_mix_k_i[j]);
            
            xr_i[j] = xx_i[j] * time_mix_r_i[j] + state_xx_i[j] * (1 - time_mix_r_i[j]);
            state_xx_i[j] = xx_i[j];
        }

        
        xk_stream.write(xk_i);
        
        xr_stream.write(xr_i);
        state_xx_stream_out.write(state_xx_i);
    }
}

void MVVq_s0_s(hls::stream<t_int8Vec_1>& vec, hls::stream<t_int8Vec_1>& out_vec){
	#pragma HLS inline off
 	
 	t_int8Vec_1 input_arr[group_num];
 	
 	for(int i = 0; i < group_num; i++){

 		
 		input_arr[i] = vec.read();
 		
 	}





 	for(int i = 0; i < n_embed; i++){
 		for(int j = 0; j < group_num; j++){
 			out_vec.write(input_arr[j]);
 		}
 	}
}

void MVVq_s0_r_s(hls::stream<float>& r_vec, hls::stream<float>& out_rvec){
	#pragma HLS inline off
 	
 	float r_vec_arr[group_num];
 	
 	for(int i = 0; i < group_num; i++){

 		
 		r_vec_arr[i] = r_vec.read();
 		
 	}





 	for(int i = 0; i < n_embed; i++){
 		for(int j = 0; j < group_num; j++){
 			out_rvec.write(r_vec_arr[j]);
 		}
 	}
}
































void MVVq_s1_s(hls::stream<t_int8Vec_1>& mtx, hls::stream<t_int8Vec_1>& vec, hls::stream<float>& r_vec, hls::stream<float>& r_mtx, hls::stream<float>& out){
	#pragma HLS inline off
	for (int i = 0; i < n_embed; i++){

		for (int j = 0; j < group_num; j++){
#pragma HLS pipeline
			t_int8Vec_1 mtx_i = mtx.read();
 			float r_mtx_i = r_mtx.read();
 			t_int16Vec_0 inter;
			t_int8Vec_1 input_arr = vec.read();
			float r_vec_arr = r_vec.read();
 			int sum = 0;
 			for(int k = 0; k < stream_kernel_int8_1; k++){

 				
 				inter[k] = input_arr[k] * mtx_i[k];
 				sum += inter[k];
 			}
			out.write(r_mtx_i * r_vec_arr * static_cast<float>(sum));

		}
	}
}

























void MVVq_s2_s(hls::stream<float>& in, hls::stream<float>& output){
	#pragma HLS inline off
	
	for(int status = 0; status < n_embed; status++){
		float res = 0;
		float sum = 0;
		for(int i = 0; i < group_num; i++){
			#pragma HLS pipeline
			
			res = in.read();
			sum += res;
		}
		output.write(sum);
	}
}

void MVVq_s3_s(hls::stream<float>& in, hls::stream<t_floatVec_0>& output){
	#pragma HLS inline off
	
	t_floatVec_0 res[group_num];

	for(int cur_status = 0; cur_status < n_embed; cur_status++){
		#pragma HLS pipeline 
		
		res[cur_status / stream_kernel_float_0][cur_status % stream_kernel_float_0] = in.read();
	}
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline 
		
		output.write(res[i]);
	}
}

void MVVq_s(hls::stream<t_int8Vec_1>& mtx, hls::stream<t_int8Vec_1>& vec, hls::stream<float>& r_vec, hls::stream<float>& r_mtx, hls::stream<t_floatVec_0>& output){
	#pragma HLS dataflow
	hls::stream<float> inter1;
	#pragma HLS stream variable=inter1 depth=256
	hls::stream<float> inter2;
	#pragma HLS stream variable=inter2 depth=256
	hls::stream<t_int8Vec_1> out_vec;
	#pragma HLS stream variable=out_vec depth=2048
	hls::stream<float> out_rvec;
	#pragma HLS stream variable=out_rvec depth=2048
	MVVq_s0_s(vec, out_vec);
	MVVq_s0_r_s(r_vec, out_rvec);
	MVVq_s1_s(mtx, out_vec, out_rvec, r_mtx, inter1);
	MVVq_s2_s(inter1, inter2);
	MVVq_s3_s(inter2, output);
}

void MVVq_large_row_s0_s(hls::stream<t_int8Vec_1>& vec, hls::stream<t_int8Vec_1>& out_vec){
	#pragma HLS inline off
	t_int8Vec_1 input_arr[group_num_large];
	for (int i = 0; i < group_num_large; i++){
		input_arr[i] = vec.read();
	}
	for (int i = 0; i < n_embed; i++){
		for (int j = 0; j < group_num_large; j++){
			out_vec.write(input_arr[j]);
		}
	}
}

void MVVq_large_row_s0_r_s(hls::stream<float>& r_vec, hls::stream<float>& out_rvec){
	#pragma HLS inline off
	float r_vec_arr[group_num_large];
	for (int i = 0; i < group_num_large; i++){
		r_vec_arr[i] = r_vec.read();
	}
	for (int i = 0; i < n_embed; i++){
		for (int j = 0; j < group_num_large; j++){
			out_rvec.write(r_vec_arr[j]);
		}
	}
}

void MVVq_large_row_s1_s(hls::stream<t_int8Vec_1>& mtx, hls::stream<t_int8Vec_1>& vec, hls::stream<float>& r_vec, hls::stream<float>& r_mtx, hls::stream<float>& out){
	#pragma HLS inline off
	for (int i = 0; i < n_embed; i++){

		for (int j = 0; j < group_num_large; j++){
#pragma HLS pipeline
			t_int8Vec_1 mtx_i = mtx.read();
 			float r_mtx_i = r_mtx.read();
 			t_int16Vec_0 inter;
			t_int8Vec_1 input_arr = vec.read();
			float r_vec_arr = r_vec.read();
 			int sum = 0;
 			for(int k = 0; k < stream_kernel_int8_1; k++){

 				
 				inter[k] = input_arr[k] * mtx_i[k];
 				sum += inter[k];
 			}
			out.write(r_mtx_i * r_vec_arr * static_cast<float>(sum));

		}
	}
}

void MVVq_large_row_s2_s(hls::stream<float>& in, hls::stream<float>& output){
	#pragma HLS inline off
	for(int status = 0; status < n_embed; status++){
		float res = 0;
		float sum = 0;
		for(int i = 0; i < group_num_large; i++){
			#pragma HLS pipeline 
			
			res = in.read();
			sum += res;
		}
		output.write(sum);
	}
}

void MVVq_large_row_s(hls::stream<t_int8Vec_1>& mtx, hls::stream<t_int8Vec_1>& vec, hls::stream<float>& r_vec, hls::stream<float>& r_mtx, hls::stream<t_floatVec_0>& output){
	#pragma HLS dataflow
	hls::stream<float> inter1;
	#pragma HLS stream variable=inter1 depth=256
	hls::stream<float> inter2;
	#pragma HLS stream variable=inter2 depth=256
	hls::stream<t_int8Vec_1> out_vec;
	#pragma HLS stream variable=out_vec depth=2048
	hls::stream<float> out_rvec;
	#pragma HLS stream variable=out_rvec depth=2048
	MVVq_large_row_s0_s(vec,out_vec);
	MVVq_large_row_s0_r_s(r_vec,out_rvec);
	MVVq_large_row_s1_s(mtx, out_vec, out_rvec, r_mtx, inter1);
	MVVq_large_row_s2_s(inter1, inter2);
	MVVq_s3_s(inter2, output);
}

void MVV_large_row_s(hls::stream<t_floatVec_0>& xvec, hls::stream<t_int8Vec_1>& weight, hls::stream<float>& r_m, hls::stream<t_floatVec_0>& output){
	hls::stream<t_int8Vec_1> v8;
	#pragma HLS stream variable=v8 depth=256
	hls::stream<float> r_vec_act_v;
	#pragma HLS stream variable=r_vec_act_v depth=256
	
	dynamic_act_quant32_large_s(xvec, v8, r_vec_act_v);
	MVVq_large_row_s(weight, v8, r_vec_act_v, r_m, output);	
}

void MVVq_large_vec_s0_s(hls::stream<t_int8Vec_1>& vec, hls::stream<t_int8Vec_1>& out_vec){
	#pragma HLS inline off
	t_int8Vec_1 input_arr[group_num];
	for (int i = 0; i < group_num; i++){
		
		input_arr[i] = vec.read();
	}
	for(int i = 0; i < n_embed_large; i++){
 		for(int j = 0; j < group_num; j++){
 			out_vec.write(input_arr[j]);
 		}
 	}
}

void MVVq_large_vec_s0_r_s(hls::stream<float>& r_vec, hls::stream<float>& out_rvec){
	#pragma HLS inline off
	float r_vec_arr[group_num];
	for(int i = 0; i < group_num; i++){
		r_vec_arr[i] = r_vec.read();
	}
	for(int i = 0; i < n_embed_large; i++){
 		for(int j = 0; j < group_num; j++){
 			out_rvec.write(r_vec_arr[j]);
 		}
 	}
}

void MVVq_large_vec_s1_s(hls::stream<t_int8Vec_1>& mtx, hls::stream<t_int8Vec_1>& vec, hls::stream<float>& r_vec, hls::stream<float>& r_mtx, hls::stream<float>& out){
	#pragma HLS inline off
	for (int i = 0; i < n_embed_large; i++){

		for (int j = 0; j < group_num; j++){
#pragma HLS pipeline
			t_int8Vec_1 mtx_i = mtx.read();
 			float r_mtx_i = r_mtx.read();
 			t_int16Vec_0 inter;
			t_int8Vec_1 input_arr = vec.read();
			float r_vec_arr = r_vec.read();
 			int sum = 0;
 			for(int k = 0; k < stream_kernel_int8_1; k++){

 				
 				inter[k] = input_arr[k] * mtx_i[k];
 				sum += inter[k];
 			}
			out.write(r_mtx_i * r_vec_arr * static_cast<float>(sum));

		}
	}
}

void MVVq_large_vec_s2_s(hls::stream<float>& in, hls::stream<float>& output){
	#pragma HLS inline off
	for(int status = 0; status < n_embed_large; status++){
		float res = 0;
		float sum = 0;
		for(int i = 0; i < group_num; i++){
			#pragma HLS pipeline 
			
			res = in.read();
			sum += res;
		}
		output.write(sum);
	}
}

void MVVq_large_vec_s3_s(hls::stream<float>& in, hls::stream<t_floatVec_0>& output){
	#pragma HLS inline off
	t_floatVec_0 res[group_num_large];
	for(int cur_status = 0; cur_status < n_embed_large; cur_status++){
		#pragma HLS pipeline II=10
		
		res[cur_status / stream_kernel_float_0][cur_status % stream_kernel_float_0] = in.read();
	}
	for(int i = 0; i < group_num_large; i++){
		#pragma HLS pipeline II=10
		output.write(res[i]);
	}
}

void MVVq_large_vec_s(hls::stream<t_int8Vec_1>& mtx, hls::stream<t_int8Vec_1>& vec, hls::stream<float>& r_vec, hls::stream<float>& r_mtx, hls::stream<t_floatVec_0>& output){
	#pragma HLS dataflow
	hls::stream<float> inter1;
	#pragma HLS stream variable=inter1 depth=256
	hls::stream<float> inter2;
	#pragma HLS stream variable=inter2 depth=256
	hls::stream<t_int8Vec_1> out_vec;
	#pragma HLS stream variable=out_vec depth=2048
	hls::stream<float> out_rvec;
	#pragma HLS stream variable=out_rvec depth=2048
	MVVq_large_vec_s0_s(vec, out_vec);
	MVVq_large_vec_s0_r_s(r_vec, out_rvec);
	MVVq_large_vec_s1_s(mtx, out_vec, out_rvec, r_mtx, inter1);
	MVVq_large_vec_s2_s(inter1, inter2);
	MVVq_large_vec_s3_s(inter2, output);
}

void MVV_large_vec_s(hls::stream<t_floatVec_0>& xvec, hls::stream<t_int8Vec_1>& weight, hls::stream<float>& r_m, hls::stream<t_floatVec_0>& output){
	hls::stream<t_int8Vec_1> v8;
	#pragma HLS stream variable=v8 depth=256
	hls::stream<float> r_vec_act_v;
	#pragma HLS stream variable=r_vec_act_v depth=256
	
	dynamic_act_quant32_s(xvec, v8, r_vec_act_v);
	MVVq_large_vec_s(weight, v8, r_vec_act_v, r_m, output);	
}

void MVVq(t_int8Vec a[n_embed], t_int8Vec output_x, t_floatGroup r_vec, t_floatGroup r_vec_m[n_embed], t_floatVec& output){
	t_int16Vec a_[n_embed];
	for(int i = 0; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		for(int j = 0; j < n_embed; j++){
			#pragma hls unroll factor=16 skip_exit_check
			a_[i][j] = a[i][j] * output_x[j]; 
		}
	}
	t_floatGroup inter_result[n_embed];
	for(int i = 0; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		for(int j = 0; j < group_num; j++){
			#pragma hls unroll factor=16 skip_exit_check
			int inter = a_[i][j * 32 + 0] + a_[i][j * 32 + 1] + a_[i][j * 32 + 2] + a_[i][j * 32 + 3] + \
				a_[i][j * 32 + 4] + a_[i][j * 32 + 5] + a_[i][j * 32 + 6] + a_[i][j * 32 + 7] + \
				a_[i][j * 32 + 8] + a_[i][j * 32 + 9] + a_[i][j * 32 + 10] + a_[i][j * 32 + 11] + \
				a_[i][j * 32 + 12] + a_[i][j * 32 + 13] + a_[i][j * 32 + 14] + a_[i][j * 32 + 15] + \
				a_[i][j * 32 + 16] + a_[i][j * 32 + 17] + a_[i][j * 32 + 18] + a_[i][j * 32 + 19] + \
				a_[i][j * 32 + 20] + a_[i][j * 32 + 21] + a_[i][j * 32 + 22] + a_[i][j * 32 + 23] + \
				a_[i][j * 32 + 24] + a_[i][j * 32 + 25] + a_[i][j * 32 + 26] + a_[i][j * 32 + 27] + \
				a_[i][j * 32 + 28] + a_[i][j * 32 + 29] + a_[i][j * 32 + 30] + a_[i][j * 32 + 31];
			inter_result[i][j] = static_cast<float>(inter) * r_vec[j] * r_vec_m[i][j];
		}
	}
	for(int i = 0; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		output[i] = (inter_result[i]).reduce_add();
	}
}

void exp_minus(t_floatVec& a, t_floatVec& b, t_floatVec& output){
	for(int i = 0; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		output[i] = exp(a[i] - b[i]);
	}
}
void exp_minus_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b, hls::stream<t_floatVec_0>& output){
  #pragma HLS inline off
  for(int i = 0; i < group_num; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    t_floatVec_0 b_i = b.read();
    t_floatVec_0 out_i;
    for(int j = 0; j < stream_kernel_float_0; j++){
      #pragma hls unroll factor=16 skip_exit_check
      out_i[j] = exp(a_i[j] - b_i[j]); 
    }
    output.write(out_i);
  }
}

void mulVec_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b, hls::stream<t_floatVec_0>& output){
  #pragma HLS inline off
  for(int i = 0; i < group_num; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    t_floatVec_0 b_i = b.read();
    t_floatVec_0 out_i = a_i * b_i;
    output.write(out_i);
  }
}

void maximum (t_floatVec& a, t_floatVec& b, t_floatVec& result){
	for(int i = 0; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		result[i] = (a[i] > b[i]) ? a[i] : b[i];
	}
}
void maximum_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b, hls::stream<t_floatVec_0>& result){
  #pragma HLS inline off
  for(int i = 0; i < group_num; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    t_floatVec_0 b_i = b.read();
    t_floatVec_0 out_i;
    for(int j = 0; j < stream_kernel_float_0; j++){
      #pragma hls unroll factor=16 skip_exit_check
      out_i[j] = (a_i[j] > b_i[j]) ? a_i[j] : b_i[j];
    }
    result.write(out_i);
  }
}

void add_vec_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b, hls::stream<t_floatVec_0>& result){
  #pragma HLS inline off
  for(int i = 0; i < group_num; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    t_floatVec_0 b_i = b.read();
    t_floatVec_0 out_i;
    out_i = a_i + b_i;
    result.write(out_i);
  }	
}


void kernel_computation(t_floatVec& r, t_floatVec& k, t_floatVec& v, t_floatVec& state_pp, t_floatVec& state_bb, t_floatVec& state_aa, t_floatVec& time_first, t_floatVec& time_decay, t_floatVec& rwkv){
	t_floatVec pp = state_pp;
	t_floatVec aa = state_aa;
	t_floatVec bb = state_bb;
	t_floatVec ww = time_first + k;
	t_floatVec p;
	t_floatVec e1;
	t_floatVec e2;
	maximum(pp, ww, p);
	exp_minus(pp, p, e1);
	exp_minus(ww, p, e2);
	t_floatVec a = e1 * aa + e2 * v;
	t_floatVec b = e1 * bb + e2;
	ww = pp + time_decay;
	maximum(ww, k, p);
	exp_minus(ww, p, e1);
	exp_minus(k, p, e2);	
	state_aa = e1 * aa + e2 * v;
	state_bb = e1 * bb + e2;
	state_pp = p;
	rwkv = r * a / b;
}


































































void kernel_computation_s(
    hls::stream<t_floatVec_0>& r, 
    hls::stream<t_floatVec_0>& k, 
    hls::stream<t_floatVec_0>& v, 
	hls::stream<t_floatVec_0>& state_pp_in,
	hls::stream<t_floatVec_0>& state_bb_in,
	hls::stream<t_floatVec_0>& state_aa_in,  
    hls::stream<t_floatVec_0>& state_pp_out,
	hls::stream<t_floatVec_0>& state_bb_out,
	hls::stream<t_floatVec_0>& state_aa_out,
    hls::stream<t_floatVec_0>& time_first, 
    hls::stream<t_floatVec_0>& time_decay, 
    hls::stream<t_floatVec_0>& rwkv
){
	#pragma HLS inline off
    for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
        t_floatVec_0 r_i = r.read();
        t_floatVec_0 k_i = k.read();
        t_floatVec_0 v_i = v.read();
        t_floatVec_0 state_pp_i = state_pp_in.read();
        t_floatVec_0 state_bb_i = state_bb_in.read();
        t_floatVec_0 state_aa_i = state_aa_in.read();
        t_floatVec_0 time_first_i = time_first.read();
        t_floatVec_0 time_decay_i = time_decay.read();
        t_floatVec_0 rwkv_i;

        t_floatVec_0 pp_i = state_pp_i;
        t_floatVec_0 aa_i = state_aa_i;
        t_floatVec_0 bb_i = state_bb_i;
        t_floatVec_0 ww_i = time_first_i + k_i;
        t_floatVec_0 p_i;
        t_floatVec_0 e1_i;
        t_floatVec_0 e2_i;

        for(int j = 0; j < stream_kernel_float_0; j++){
            #pragma hls unroll factor=16 skip_exit_check
            p_i[j] = (pp_i[j] > ww_i[j]) ? pp_i[j] : ww_i[j];
            e1_i[j] = exp(pp_i[j] - p_i[j]);
            e2_i[j] = exp(ww_i[j] - p_i[j]);
        }

        t_floatVec_0 a_i = e1_i * aa_i + e2_i * v_i;
        t_floatVec_0 b_i = e1_i * bb_i + e2_i;
        ww_i = pp_i + time_decay_i;

        for(int j = 0; j < stream_kernel_float_0; j++){
            #pragma hls unroll factor=16 skip_exit_check
            p_i[j] = (ww_i[j] > k_i[j]) ? ww_i[j] : k_i[j];
            e1_i[j] = exp(ww_i[j] - p_i[j]);
            e2_i[j] = exp(k_i[j] - p_i[j]);
        }

        state_aa_i = e1_i * aa_i + e2_i * v_i;
        state_bb_i = e1_i * bb_i + e2_i;
        state_pp_i = p_i;
        rwkv_i = r_i * a_i / b_i;

        
        state_pp_out.write(state_pp_i);
        state_bb_out.write(state_bb_i);
        state_aa_out.write(state_aa_i);
        rwkv.write(rwkv_i);
    }
}
void convert_float32_to_float8_s(hls::stream<t_floatVec_0>& input, hls::stream<t_floatVec_1>& output){
	#pragma HLS inline off
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
		t_floatVec_0 input_i = input.read();
		t_floatVec_1 output_i_1;
		t_floatVec_1 output_i_2;
		t_floatVec_1 output_i_3;
		t_floatVec_1 output_i_4;
		for(int j = 0; j < stream_kernel_float_1; j++){
			#pragma hls unroll factor=16 skip_exit_check
			output_i_1[j] = input_i[j + 0 * stream_kernel_float_1];
			output_i_2[j] = input_i[j + 1 * stream_kernel_float_1];
			output_i_3[j] = input_i[j + 2 * stream_kernel_float_1];
			output_i_4[j] = input_i[j + 3 * stream_kernel_float_1];
		}
		output.write(output_i_1);
		output.write(output_i_2);
		output.write(output_i_3);
		output.write(output_i_4);
	}
}
void convert_float8_to_float32_s(hls::stream<t_floatVec_1>& input, hls::stream<t_floatVec_0>& output){
	#pragma HLS inline off
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		t_floatVec_1 input_i_1 = input.read();
		t_floatVec_1 input_i_2 = input.read();
		t_floatVec_1 input_i_3 = input.read();
		t_floatVec_1 input_i_4 = input.read();
		t_floatVec_0 output_i;
		for(int j = 0; j < stream_kernel_float_1; j++){
			#pragma hls unroll factor=16 skip_exit_check
			output_i[j + 0 * stream_kernel_float_1] = input_i_1[j];
			output_i[j + 1 * stream_kernel_float_1] = input_i_2[j];
			output_i[j + 2 * stream_kernel_float_1] = input_i_3[j];
			output_i[j + 3 * stream_kernel_float_1] = input_i_4[j];
		}
		output.write(output_i);
	}
}
void kernel_computation_8_s(
    hls::stream<t_floatVec_1>& r, 
    hls::stream<t_floatVec_1>& k, 
    hls::stream<t_floatVec_1>& v, 
	hls::stream<t_floatVec_1>& state_pp_in,
	hls::stream<t_floatVec_1>& state_bb_in,
	hls::stream<t_floatVec_1>& state_aa_in,  
    hls::stream<t_floatVec_1>& state_pp_out,
	hls::stream<t_floatVec_1>& state_bb_out,
	hls::stream<t_floatVec_1>& state_aa_out,
    hls::stream<t_floatVec_1>& time_first, 
    hls::stream<t_floatVec_1>& time_decay, 
    hls::stream<t_floatVec_1>& rwkv
){
	#pragma HLS inline off
    for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
        t_floatVec_1 r_i = r.read();
        t_floatVec_1 k_i = k.read();
        t_floatVec_1 v_i = v.read();
        t_floatVec_1 state_pp_i = state_pp_in.read();
        t_floatVec_1 state_bb_i = state_bb_in.read();
        t_floatVec_1 state_aa_i = state_aa_in.read();
        t_floatVec_1 time_first_i = time_first.read();
        t_floatVec_1 time_decay_i = time_decay.read();
        t_floatVec_1 rwkv_i;

        t_floatVec_1 pp_i = state_pp_i;
        t_floatVec_1 aa_i = state_aa_i;
        t_floatVec_1 bb_i = state_bb_i;
        t_floatVec_1 ww_i = time_first_i + k_i;
        t_floatVec_1 p_i;
        t_floatVec_1 e1_i;
        t_floatVec_1 e2_i;

        for(int j = 0; j < stream_kernel_float_0; j++){
            #pragma hls unroll factor=16 skip_exit_check
            p_i[j] = (pp_i[j] > ww_i[j]) ? pp_i[j] : ww_i[j];
            e1_i[j] = exp(pp_i[j] - p_i[j]);
            e2_i[j] = exp(ww_i[j] - p_i[j]);
        }

        t_floatVec_1 a_i = e1_i * aa_i + e2_i * v_i;
        t_floatVec_1 b_i = e1_i * bb_i + e2_i;
        ww_i = pp_i + time_decay_i;

        for(int j = 0; j < stream_kernel_float_0; j++){
            #pragma hls unroll factor=16 skip_exit_check
            p_i[j] = (ww_i[j] > k_i[j]) ? ww_i[j] : k_i[j];
            e1_i[j] = exp(ww_i[j] - p_i[j]);
            e2_i[j] = exp(k_i[j] - p_i[j]);
        }

        state_aa_i = e1_i * aa_i + e2_i * v_i;
        state_bb_i = e1_i * bb_i + e2_i;
        state_pp_i = p_i;
        rwkv_i = r_i * a_i / b_i;

        
        state_pp_out.write(state_pp_i);
        state_bb_out.write(state_bb_i);
        state_aa_out.write(state_aa_i);
        rwkv.write(rwkv_i);
    }
}

void kernel_computation_32to8_s(
    hls::stream<t_floatVec_0>& r, 
    hls::stream<t_floatVec_0>& k, 
    hls::stream<t_floatVec_0>& v, 
	hls::stream<t_floatVec_0>& state_pp_in,
	hls::stream<t_floatVec_0>& state_bb_in,
	hls::stream<t_floatVec_0>& state_aa_in,  
    hls::stream<t_floatVec_0>& state_pp_out,
	hls::stream<t_floatVec_0>& state_bb_out,
	hls::stream<t_floatVec_0>& state_aa_out,
    hls::stream<t_floatVec_0>& time_first, 
    hls::stream<t_floatVec_0>& time_decay, 
    hls::stream<t_floatVec_0>& rwkv
){
	#pragma HLS dataflow
	hls::stream<t_floatVec_1> r_8;
	hls::stream<t_floatVec_1> k_8;
	hls::stream<t_floatVec_1> v_8;
	hls::stream<t_floatVec_1> state_pp_in_8;
	hls::stream<t_floatVec_1> state_bb_in_8;
	hls::stream<t_floatVec_1> state_aa_in_8;
	hls::stream<t_floatVec_1> state_pp_out_8;
	hls::stream<t_floatVec_1> state_bb_out_8;
	hls::stream<t_floatVec_1> state_aa_out_8;
	hls::stream<t_floatVec_1> time_first_8;
	hls::stream<t_floatVec_1> time_decay_8;
	hls::stream<t_floatVec_1> rwkv_8;
	convert_float32_to_float8_s(r, r_8);
	convert_float32_to_float8_s(k, k_8);
	convert_float32_to_float8_s(v, v_8);
	convert_float32_to_float8_s(state_pp_in, state_pp_in_8);
	convert_float32_to_float8_s(state_bb_in, state_bb_in_8);
	convert_float32_to_float8_s(state_aa_in, state_aa_in_8);
	convert_float32_to_float8_s(time_first, time_first_8);
	convert_float32_to_float8_s(time_decay, time_decay_8);
	kernel_computation_8_s(r_8, k_8, v_8, state_pp_in_8, state_bb_in_8, state_aa_in_8, state_pp_out_8, state_bb_out_8, state_aa_out_8, time_first_8, time_decay_8, rwkv_8);
	convert_float8_to_float32_s(state_pp_out_8, state_pp_out);
	convert_float8_to_float32_s(state_bb_out_8, state_bb_out);
	convert_float8_to_float32_s(state_aa_out_8, state_aa_out);
	convert_float8_to_float32_s(rwkv_8, rwkv);
}

void mulVec(t_floatVec& a, t_floatVec& b, t_floatVec& c){
	c = a * b;
}

void sigmoid(t_floatVec& a, t_floatVec& b){
	for (int i = 1; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		if(a[i] < -8){
			b[i] = 0.0;
		}
		else if(a[i] <= -2){
			b[i] = 0.01511 * a[i] + 0.09783;
		}
		else if(a[i] <= 2){
			b[i] = 0.21619 * a[i]+ 0.5;
		}
		else if(a[i] <= 8){
			b[i] = 0.01511 * a[i] + 0.90217;
		}
		else{
			b[i] = 1.0;
		}
	}
}
void sigmoid_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b){
	#pragma HLS inline off
  for(int i = 0; i < group_num; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    for(int j = 0; j < stream_kernel_float_0; j++){
      #pragma hls unroll factor=16 skip_exit_check
      if(a_i[j] < -8){
        a_i[j] = 0.0; 
      }
      else if(a_i[j] <= -2){
        a_i[j] = 0.01511 * a_i[j] + 0.09783;
      }
      else if(a_i[j] <= 2){
        a_i[j] = 0.21619 * a_i[j]+ 0.5;
      }
      else if(a_i[j] <= 8){
        a_i[j] = 0.01511 * a_i[j] + 0.90217;
      }
      else{
        a_i[j] = 1.0;
      }
    }
    b.write(a_i);
  }
}

void relu(t_floatVec& a, t_floatVec& b){
	for (int i = 1; i < n_embed; i++){
		#pragma hls unroll factor=16 skip_exit_check
		if(a[i] < 0){
			b[i] = 0;
		}
		else{
			b[i] = a[i];
		}
	}
}

void relu_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b){
	#pragma HLS inline off
	for(int i = 0; i < group_num; i++){
		#pragma HLS pipeline II=10
		
		t_floatVec_0 a_i = a.read();
		for(int j = 0; j < stream_kernel_float_0; j++){
			#pragma hls unroll factor=16 skip_exit_check
			if(a_i[j] < 0){
				a_i[j] = 0;
			}
		}
		b.write(a_i);
	}
}

void relu_large_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b){
	#pragma HLS inline off
	for(int i = 0; i < group_num_large; i++){
		#pragma HLS pipeline II=10
		
		t_floatVec_0 a_i = a.read();
		for(int j = 0; j < stream_kernel_float_0; j++){
			#pragma hls unroll factor=16 skip_exit_check
			if(a_i[j] < 0){
				a_i[j] = 0;
			}
		}
		b.write(a_i);
	}
}

void square(t_floatVec& a, t_floatVec& b){
	for (int i = 1; i < n_embed; i++){
		
		b[i] = a[i] * a[i];
	}
}

void square_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b){
	#pragma HLS inline off
  for(int i = 0; i < group_num; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    for(int j = 0; j < stream_kernel_float_0; j++){
      #pragma hls unroll factor=16 skip_exit_check  
      a_i[j] = a_i[j] * a_i[j];
    }
    b.write(a_i);
  }
}

void square_large_s(hls::stream<t_floatVec_0>& a, hls::stream<t_floatVec_0>& b){
	#pragma HLS inline off
  for(int i = 0; i < group_num_large; i++){
	#pragma HLS pipeline II=10
	
    t_floatVec_0 a_i = a.read();
    for(int j = 0; j < stream_kernel_float_0; j++){
      #pragma hls unroll factor=16 skip_exit_check  
      a_i[j] = a_i[j] * a_i[j];
    }
    b.write(a_i);
  }
}

void MVV_for_test(t_floatVec& xvec, t_int8Vec weight[n_embed], t_floatGroup r_m[n_embed], t_floatVec& output){
	t_int8Vec v8;
	t_floatGroup r_vec_act_v;
	dynamic_act_quant(xvec, v8, r_vec_act_v);
	MVVq(weight, v8, r_vec_act_v, r_m, output);	
}

void MVV_s(hls::stream<t_floatVec_0>& xvec, hls::stream<t_int8Vec_1>& weight, hls::stream<float>& r_m, hls::stream<t_floatVec_0>& output){
	#pragma HLS dataflow
	
	hls::stream<t_int8Vec_1> v8;
	#pragma HLS stream variable=v8 depth=256
	hls::stream<float> r_vec_act_v;
	#pragma HLS stream variable=r_vec_act_v depth=256
	
	dynamic_act_quant32_s(xvec, v8, r_vec_act_v);
	MVVq_s(weight, v8, r_vec_act_v, r_m, output);	
}


void FF(t_floatVec& xx, t_floatVec& time_mix_k, t_floatVec& time_mix_r, t_int8Vec r_weight[n_embed], t_int8Vec k_weight[n_embed], t_int8Vec v_weight[n_embed], t_floatGroup r_vec_mr[n_embed], t_floatGroup r_vec_mk[n_embed], t_floatGroup r_vec_mv[n_embed], t_floatVec& state_xx, t_floatVec& result){
	t_floatVec xk; 
	t_floatVec xr;
	xk = xx * time_mix_k + state_xx * (1 - time_mix_k);
	xr = xx * time_mix_r + state_xx * (1 - time_mix_r);
	state_xx = xx;

	t_int8Vec r8;
	t_floatGroup r_vec_act_r;
	dynamic_act_quant(xr, r8, r_vec_act_r);
	
	t_floatVec rw_xr;
	MVVq(r_weight, r8, r_vec_act_r, r_vec_mr, rw_xr);
	t_floatVec r;
	sigmoid(rw_xr, r);

	t_int8Vec k8;
	t_floatGroup r_vec_act_k;
	dynamic_act_quant(xk, k8, r_vec_act_k);
	t_floatVec kw_xk;
	MVVq(k_weight, k8, r_vec_act_k, r_vec_mk, kw_xk);

	t_floatVec k_relu;
	t_floatVec k;
	relu(kw_xk, k_relu);
	square(k_relu, k);

	t_int8Vec v8;
	t_floatGroup r_vec_act_v;
	dynamic_act_quant(k, v8, r_vec_act_v);
	t_floatVec kv;
	MVVq(v_weight, v8, r_vec_act_v, r_vec_mv, kv);	

	result = r * kv;
}

void FF_s(
hls::stream<t_floatVec_0>& xx_stream,
hls::stream<t_floatVec_0>& time_mix_k_stream,
hls::stream<t_floatVec_0>& time_mix_r_stream,
hls::stream<t_int8Vec_1>& r_weight_stream,
hls::stream<t_int8Vec_1>& k_weight_stream,
hls::stream<t_int8Vec_1>& v_weight_stream,
hls::stream<float>& r_vec_mr_stream,
hls::stream<float>& r_vec_mk_stream,
hls::stream<float>& r_vec_mv_stream,
hls::stream<t_floatVec_0>& state_xx_stream_in,
hls::stream<t_floatVec_0>& state_xx_stream_out, 
hls::stream<t_floatVec_0>& result_stream
){
	#pragma HLS dataflow
    
    hls::stream<t_floatVec_0> xk_stream, xr_stream, kv_stream;
    hls::stream<t_floatVec_0> r_stream;
	hls::stream<t_floatVec_0> rw_xr_stream;
	hls::stream<t_floatVec_0> kw_xk_stream, k_relu_stream, k_square_stream;
	#pragma HLS stream variable=xk_stream depth=256
	#pragma HLS stream variable=xr_stream depth=256
	#pragma HLS stream variable=kv_stream depth=256
	#pragma HLS stream variable=r_stream depth=256
	#pragma HLS stream variable=rw_xr_stream depth=256
	#pragma HLS stream variable=kw_xk_stream depth=256
	#pragma HLS stream variable=k_relu_stream depth=256
	#pragma HLS stream variable=k_square_stream depth=256

    
    time_mix_FF_s(xk_stream, xr_stream, state_xx_stream_in, state_xx_stream_out, xx_stream, time_mix_k_stream, time_mix_r_stream);
    
    
    MVV_s(xr_stream, r_weight_stream, r_vec_mr_stream, rw_xr_stream);

    
    sigmoid_s(rw_xr_stream, r_stream);

    
    MVV_large_vec_s(xk_stream, k_weight_stream, r_vec_mk_stream, kw_xk_stream);

    
    relu_large_s(kw_xk_stream, k_relu_stream);

    
    square_large_s(k_relu_stream, k_square_stream);

    
    MVV_large_row_s(k_square_stream, v_weight_stream, r_vec_mv_stream, kv_stream);

    
	mulVec_s(r_stream, kv_stream, result_stream);
}

void SA(t_floatVec& xx, t_floatVec& time_first, t_floatVec& time_decay, t_floatVec& time_mix_k, t_floatVec& time_mix_v, t_floatVec& time_mix_r, t_int8Vec r_weight[n_embed], t_int8Vec k_weight[n_embed], t_int8Vec v_weight[n_embed], t_int8Vec o_weight[n_embed], t_floatGroup r_vec_mr[n_embed], t_floatGroup r_vec_mk[n_embed], t_floatGroup r_vec_mv[n_embed], t_floatGroup r_vec_mo[n_embed], t_floatVec& state_aa, t_floatVec& state_bb, t_floatVec& state_pp, t_floatVec& state_xx, t_floatVec& result){
	
	t_floatVec xk; 
	t_floatVec xv; 
	t_floatVec xr;
	time_mix(xk, xv, xr, state_xx, xx, time_mix_k, time_mix_v, time_mix_r);
	
	t_int8Vec r8;
	t_floatGroup r_vec_act_r;
	dynamic_act_quant(xr, r8, r_vec_act_r);
	
	t_floatVec rw_xr;
	MVVq(r_weight, r8, r_vec_act_r, r_vec_mr, rw_xr);
	t_floatVec r;
	sigmoid(rw_xr, r);

	t_int8Vec k8;
	t_floatGroup r_vec_act_k;
	dynamic_act_quant(xk, k8, r_vec_act_k);
	t_floatVec kw_xk;
	MVVq(k_weight, k8, r_vec_act_k, r_vec_mk, kw_xk);

	t_int8Vec v8;
	t_floatGroup r_vec_act_v;
	dynamic_act_quant(xv, v8, r_vec_act_v);
	t_floatVec vw_xv;
	MVVq(v_weight, v8, r_vec_act_v, r_vec_mv, vw_xv);

	t_floatVec rwkv;

	kernel_computation(r, kw_xk, vw_xv, state_pp, state_bb, state_aa, time_first, time_decay, rwkv);

	t_int8Vec rwkv8;
	t_floatGroup r_vec_act_rwkv;
	dynamic_act_quant(rwkv, rwkv8, r_vec_act_rwkv);
	MVVq(o_weight, rwkv8, r_vec_act_rwkv, r_vec_mo, result);
}

void SA_s(
hls::stream<t_floatVec_0>& xx_stream,
hls::stream<t_floatVec_0>& time_first_stream,
hls::stream<t_floatVec_0>& time_decay_stream,
hls::stream<t_floatVec_0>& time_mix_k_stream,
hls::stream<t_floatVec_0>& time_mix_v_stream,
hls::stream<t_floatVec_0>& time_mix_r_stream,
hls::stream<t_int8Vec_1>& r_weight_stream,
hls::stream<t_int8Vec_1>& k_weight_stream,
hls::stream<t_int8Vec_1>& v_weight_stream,
hls::stream<t_int8Vec_1>& o_weight_stream,
hls::stream<float>& r_vec_mr_stream,
hls::stream<float>& r_vec_mk_stream,
hls::stream<float>& r_vec_mv_stream,
hls::stream<float>& r_vec_mo_stream,
hls::stream<t_floatVec_0>& state_aa_stream_in,
hls::stream<t_floatVec_0>& state_bb_stream_in,
hls::stream<t_floatVec_0>& state_pp_stream_in,
hls::stream<t_floatVec_0>& state_xx_stream_in,
hls::stream<t_floatVec_0>& state_aa_stream_out,
hls::stream<t_floatVec_0>& state_bb_stream_out,
hls::stream<t_floatVec_0>& state_pp_stream_out,
hls::stream<t_floatVec_0>& state_xx_stream_out,
hls::stream<t_floatVec_0>& result_stream
){
	#pragma HLS dataflow
    
    hls::stream<t_floatVec_0> xk_stream, xv_stream, xr_stream,  rwkv_stream;
	hls::stream<t_floatVec_0> rw_xr_stream, r_stream;
    hls::stream<t_floatVec_0> kw_xk_stream, vw_xv_stream;
	#pragma HLS stream variable=xk_stream depth=256
	#pragma HLS stream variable=xv_stream depth=256
	#pragma HLS stream variable=xr_stream depth=256
	#pragma HLS stream variable=rwkv_stream depth=256
	#pragma HLS stream variable=rw_xr_stream depth=256
	#pragma HLS stream variable=r_stream depth=256
	#pragma HLS stream variable=kw_xk_stream depth=256
	#pragma HLS stream variable=vw_xv_stream depth=256

    
    time_mix_s(xk_stream, xv_stream, xr_stream, state_xx_stream_in, state_xx_stream_out, xx_stream, time_mix_k_stream, time_mix_v_stream, time_mix_r_stream);
    
    
    MVV_s(xr_stream, r_weight_stream, r_vec_mr_stream, rw_xr_stream);

    
    sigmoid_s(rw_xr_stream, r_stream);

    
    MVV_s(xk_stream, k_weight_stream, r_vec_mk_stream, kw_xk_stream);

    
    MVV_s(xv_stream, v_weight_stream, r_vec_mv_stream, vw_xv_stream);

    
    kernel_computation_s(r_stream, kw_xk_stream, vw_xv_stream, state_pp_stream_in, state_bb_stream_in, state_aa_stream_in,
                         state_pp_stream_out, state_bb_stream_out, state_aa_stream_out,
                         time_first_stream, time_decay_stream, rwkv_stream);

    
    MVV_s(rwkv_stream, o_weight_stream, r_vec_mo_stream, result_stream);
}















void read_matrix(int8_t* input, hls::stream<t_int8Vec_1>& output, int size){
	#pragma HLS inline off
	#pragma HLS ARRAY_PARTITION variable=input type=cyclic factor=16 dim=1
	for(int i = 0; i < size; i++){
		#pragma HLS unroll factor=16 skip_exit_check
		#pragma hls pipeline
		t_int8Vec_1 output_i;
		for(int j = 0; j < stream_kernel_int8_1; j++){
			
			output_i[j] = input[i * stream_kernel_int8_1 + j];
		}
		output << output_i;
	}
}

void read_matrix_large(int8_t* input, hls::stream<t_int8Vec_1>& output, int size){
	#pragma HLS inline off
	for(int i = 0; i < size; i++){
		#pragma hls pipeline
		t_int8Vec_1 output_i;
		for(int j = 0; j < stream_kernel_int8_1; j++){
			
			output_i[j] = input[i * stream_kernel_int8_1 + j];
		}
		output << output_i;
	}
}

void read_vectors(float* input, hls::stream<t_floatVec_0>& output, int size){
	#pragma HLS inline off
	for(int i = 0; i < size; i++){
		#pragma hls pipeline
		t_floatVec_0 output_i;
		for(int j = 0; j < stream_kernel_float_0; j++){
			
			output_i[j] = input[i * stream_kernel_float_0 + j];
		}
		output << output_i;
	}
}

void read_vectors_rvec(float* input, hls::stream<float>& output, int size){
	#pragma HLS inline off
	#pragma HLS ARRAY_PARTITION variable=input type=cyclic factor=8 dim=1
	for(int i = 0; i < size; i++){
		#pragma HLS UNROLL factor=8 skip_exit_check
		#pragma hls pipeline
		output << input[i];
	}
}

void read_vectors_rvec_large(float* input, hls::stream<float>& output, int size){
	#pragma HLS inline off
	for(int i = 0; i < size; i++){
		#pragma hls pipeline
		output << input[i];
	}
}

void write_vectors(hls::stream<t_floatVec_0>& output, float* input, int size){
	#pragma HLS inline off
	for(int i = 0; i < size; i++){
		
		t_floatVec_0 output_i = output.read();
		for(int j = 0; j < stream_kernel_float_0; j++){
			#pragma hls pipeline
			
			input[i * stream_kernel_float_0 + j] = output_i[j];
		}
	}
}

void read_all(State_s& state_in, WeightBlock_s& weight_block, hls::stream<t_floatVec_0>& x, float* x_, float* xx, float* xx_ffn, float* aa, float* bb, float* pp, float* ln1_weight, float* ln1_bias, float* ln2_weight, float* ln2_bias, int8_t* att_r_weight, int8_t* att_k_weight, int8_t* att_v_weight, int8_t* att_o_weight, float* att_time_mix_k, float* att_time_mix_v, float* att_time_mix_r, float* att_time_first, float* att_time_decay, float* att_r_vec_mr, float* att_r_vec_mk, float* att_r_vec_mv, float* att_r_vec_mo, int8_t* ffn_r_weight, int8_t* ffn_k_weight, int8_t* ffn_v_weight, float* ffn_time_mix_k, float* ffn_time_mix_r, float* ffn_r_vec_mr, float* ffn_r_vec_mk, float* ffn_r_vec_mv, int sel){
    #pragma HLS INTERFACE ap_none port=sel
    read_vectors(x_, x, n_embed/32);
	
    read_vectors(xx, state_in.xx, n_embed/32);
    read_vectors(xx_ffn, state_in.xx_ffn, n_embed/32);
    read_vectors(aa, state_in.aa, n_embed/32);
    read_vectors(bb, state_in.bb, n_embed/32);
    read_vectors(pp, state_in.pp, n_embed/32);
    
    
    read_vectors(ln1_weight, weight_block.ln1.weight, n_embed/32);
    read_vectors(ln1_bias, weight_block.ln1.bias, n_embed/32);
    read_vectors(ln2_weight, weight_block.ln2.weight, n_embed/32);
    read_vectors(ln2_bias, weight_block.ln2.bias, n_embed/32);
    
    
    read_matrix(att_r_weight, weight_block.att.r_weight, n_embed*n_embed/32);
    read_matrix(att_k_weight, weight_block.att.k_weight, n_embed*n_embed/32);
    read_matrix(att_v_weight, weight_block.att.v_weight, n_embed*n_embed/32);
    read_matrix(att_o_weight, weight_block.att.o_weight, n_embed*n_embed/32);
    read_vectors(att_time_mix_k, weight_block.att.time_mix_k, n_embed/32);
    read_vectors(att_time_mix_v, weight_block.att.time_mix_v, n_embed/32);
    read_vectors(att_time_mix_r, weight_block.att.time_mix_r, n_embed/32);
    read_vectors(att_time_first, weight_block.att.time_first, n_embed/32);
    read_vectors(att_time_decay, weight_block.att.time_decay, n_embed/32);
    read_vectors_rvec(att_r_vec_mr, weight_block.att.r_vec_mr, n_embed*group_num);
	read_vectors_rvec(att_r_vec_mk, weight_block.att.r_vec_mk, n_embed*group_num);
	read_vectors_rvec(att_r_vec_mv, weight_block.att.r_vec_mv, n_embed*group_num);
	read_vectors_rvec(att_r_vec_mo, weight_block.att.r_vec_mo, n_embed*group_num);
    
    
    read_matrix(ffn_r_weight, weight_block.ffn.r_weight, n_embed*n_embed/32);
    read_matrix(ffn_k_weight, weight_block.ffn.k_weight, n_embed*n_embed_large/32);
    read_matrix(ffn_v_weight, weight_block.ffn.v_weight, n_embed*n_embed_large/32);
    read_vectors(ffn_time_mix_k, weight_block.ffn.time_mix_k, n_embed/32);
    read_vectors(ffn_time_mix_r, weight_block.ffn.time_mix_r, n_embed/32);
	read_vectors_rvec(ffn_r_vec_mr, weight_block.ffn.r_vec_mr, n_embed*group_num);
	read_vectors_rvec(ffn_r_vec_mk, weight_block.ffn.r_vec_mk, n_embed*group_num_large);
	read_vectors_rvec(ffn_r_vec_mv, weight_block.ffn.r_vec_mv, n_embed*group_num_large);
}

void write_all(State_s& state_out,hls::stream<t_floatVec_0>& output_,float* output, float* xx, float* xx_ffn, float* aa, float* bb, float* pp){
	
	write_vectors(state_out.xx, xx, n_embed/32);
	write_vectors(state_out.xx_ffn, xx_ffn, n_embed/32);
	write_vectors(state_out.aa, aa, n_embed/32);
	write_vectors(state_out.bb, bb, n_embed/32);
	write_vectors(state_out.pp, pp, n_embed/32);
	
	
	write_vectors(output_, output, n_embed/32);
}

void weight_consume(WeightBlock_s& weight_block, State_s& state_in, State_s& state_out){
	
	
	t_floatVec_0 ln2_weight = weight_block.ln2.weight.read();
	t_floatVec_0 ln2_bias = weight_block.ln2.bias.read();
	
	
	
	
	
	
	
	
	
	
	
	
	
	t_floatVec_0 tmk_f = weight_block.ffn.time_mix_k.read();
	t_floatVec_0 tmr_f = weight_block.ffn.time_mix_r.read();
	t_int8Vec_1	r_w_f = weight_block.ffn.r_weight.read();
	t_int8Vec_1	k_w_f = weight_block.ffn.k_weight.read();
	t_int8Vec_1 v_w_f = weight_block.ffn.v_weight.read();
	float	mr_f = weight_block.ffn.r_vec_mr.read();
	float	mk_f = weight_block.ffn.r_vec_mk.read();
	float	mv_f = weight_block.ffn.r_vec_mv.read();
	t_floatVec_0	xx_ffn = state_in.xx_ffn.read();
	state_out.xx_ffn.write(0);
	
}

void layer_common_s(State_s& state_in, State_s& state_out,WeightBlock_s& weight_block, hls::stream<t_floatVec_0>& x, hls::stream<t_floatVec_0>& output){
	
	
	
	
	
	#pragma HLS dataflow
	hls::stream<t_floatVec_0> output1;
	hls::stream<t_floatVec_0> output2;
	hls::stream<t_floatVec_0> output2_n;
	hls::stream<t_floatVec_0> output2_n2;
	hls::stream<t_floatVec_0> output2_n1;
	hls::stream<t_floatVec_0> output_o;
	hls::stream<t_floatVec_0> x1;
	hls::stream<t_floatVec_0> x2;
	#pragma HLS stream variable=output1 depth=256
	#pragma HLS stream variable=output2 depth=256
	#pragma HLS stream variable=output2_n depth=256
	#pragma HLS stream variable=output2_n2 depth=256
	#pragma HLS stream variable=output2_n1 depth=256
	#pragma HLS stream variable=output_o depth=256
	#pragma HLS stream variable=x1 depth=256
	#pragma HLS stream variable=x2 depth=256
	split_stream(x, x1, x2);

	hls::stream<t_floatVec_0> output3;
	#pragma HLS stream variable=output3 depth=256
	Layer_Norm_vector_s(x1, weight_block.ln1.weight, weight_block.ln1.bias, output1);
	SA_s(output1, weight_block.att.time_first, weight_block.att.time_decay, weight_block.att.time_mix_k, weight_block.att.time_mix_v, weight_block.att.time_mix_r, weight_block.att.r_weight, weight_block.att.k_weight, weight_block.att.v_weight, weight_block.att.o_weight, weight_block.att.r_vec_mr, weight_block.att.r_vec_mk, weight_block.att.r_vec_mv, weight_block.att.r_vec_mo, state_in.aa, state_in.bb, state_in.pp, state_in.xx, state_out.aa, state_out.bb, state_out.pp, state_out.xx, output2);
	add_vec_s(x2, output2, output2_n);
	split_stream(output2_n, output2_n1, output2_n2);
	Layer_Norm_vector_s(output2_n1, weight_block.ln2.weight, weight_block.ln2.bias, output3);
	FF_s(output3, weight_block.ffn.time_mix_k, weight_block.ffn.time_mix_r, weight_block.ffn.r_weight, weight_block.ffn.k_weight, weight_block.ffn.v_weight, weight_block.ffn.r_vec_mr, weight_block.ffn.r_vec_mk, weight_block.ffn.r_vec_mv, state_in.xx_ffn, state_out.xx_ffn, output_o);
	add_vec_s(output_o, output2_n2, output);
}
extern "C" {
	#pragma HLS clkdomain clk_src 10
void rwkv_top(float* x_, float* xx, float* xx_ffn, float* aa, float* bb, float* pp, float* ln1_weight, float* ln1_bias, float* ln2_weight, float* ln2_bias, int8_t* att_r_weight, int8_t* att_k_weight, int8_t* att_v_weight, int8_t* att_o_weight, float* att_time_mix_k, float* att_time_mix_v, float* att_time_mix_r, float* att_time_first, float* att_time_decay, float* att_r_vec_mr, float* att_r_vec_mk, float* att_r_vec_mv, float* att_r_vec_mo, int8_t* ffn_r_weight, int8_t* ffn_k_weight, int8_t* ffn_v_weight, float* ffn_time_mix_k, float* ffn_time_mix_r, float* ffn_r_vec_mr, float* ffn_r_vec_mk, float* ffn_r_vec_mv,float* output, float* xx_o, float* xx_ffn_o, float* aa_o, float* bb_o, float* pp_o){
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem0 port=x_
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem1 port=xx
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem2 port=xx_ffn
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem3 port=aa
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem4 port=bb
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem5 port=pp
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem6 port=ln1_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem7 port=ln1_bias
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem8 port=ln2_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem9 port=ln2_bias
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem10 port=att_r_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem11 port=att_k_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem12 port=att_v_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem13 port=att_o_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem14 port=att_time_mix_k
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem15 port=att_time_mix_v
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem16 port=att_time_mix_r
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem17 port=att_time_first
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem18 port=att_time_decay
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem19 port=att_r_vec_mr
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem20 port=att_r_vec_mk
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem21 port=att_r_vec_mv
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem22 port=att_r_vec_mo
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem23 port=ffn_r_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem24 port=ffn_k_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem25 port=ffn_v_weight
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem26 port=ffn_time_mix_k
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem27 port=ffn_time_mix_r
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem28 port=ffn_r_vec_mr
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem29 port=ffn_r_vec_mk
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem30 port=ffn_r_vec_mv
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem31 port=output
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem32 port=xx_o
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem33 port=xx_ffn_o
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem34 port=aa_o
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem35 port=bb_o
	#pragma HLS INTERFACE m_axi offset=slave latency=32 num_write_outstanding=8 num_read_outstanding=8 max_write_burst_length=64 max_read_burst_length=64 bundle=gmem36 port=pp_o
	
	State_s state_in;
	#pragma HLS stream variable=state_in.xx depth=256
	#pragma HLS stream variable=state_in.xx_ffn depth=256
	#pragma HLS stream variable=state_in.aa depth=256
	#pragma HLS stream variable=state_in.bb depth=256
	#pragma HLS stream variable=state_in.pp depth=256
	State_s state_out;
	#pragma HLS stream variable=state_out.xx depth=256
	#pragma HLS stream variable=state_out.xx_ffn depth=256
	#pragma HLS stream variable=state_out.aa depth=256
	#pragma HLS stream variable=state_out.bb depth=256
	#pragma HLS stream variable=state_out.pp depth=256
	WeightBlock_s weight_block;
	#pragma HLS stream variable=weight_block.ln1.weight depth=256
	#pragma HLS stream variable=weight_block.ln1.bias depth=256
	#pragma HLS stream variable=weight_block.ln2.weight depth=256
	#pragma HLS stream variable=weight_block.ln2.bias depth=256
	#pragma HLS stream variable=weight_block.att.time_mix_k depth=256
	#pragma HLS stream variable=weight_block.att.time_mix_v depth=256
	#pragma HLS stream variable=weight_block.att.time_mix_r depth=256
	#pragma HLS stream variable=weight_block.att.time_first depth=256
	#pragma HLS stream variable=weight_block.att.time_decay depth=256
	#pragma HLS stream variable=weight_block.att.r_weight depth=256
	#pragma HLS stream variable=weight_block.att.k_weight depth=256
	#pragma HLS stream variable=weight_block.att.v_weight depth=256
	#pragma HLS stream variable=weight_block.att.o_weight depth=256	
	#pragma HLS stream variable=weight_block.att.r_vec_mr depth=2048
	#pragma HLS stream variable=weight_block.att.r_vec_mk depth=2048
	#pragma HLS stream variable=weight_block.att.r_vec_mv depth=2048
	#pragma HLS stream variable=weight_block.att.r_vec_mo depth=2048	
	#pragma HLS stream variable=weight_block.ffn.time_mix_k depth=256
	#pragma HLS stream variable=weight_block.ffn.time_mix_r depth=256	
	#pragma HLS stream variable=weight_block.ffn.r_weight depth=256
	#pragma HLS stream variable=weight_block.ffn.k_weight depth=256
	#pragma HLS stream variable=weight_block.ffn.v_weight depth=256
	#pragma HLS stream variable=weight_block.ffn.r_vec_mr depth=2048
	#pragma HLS stream variable=weight_block.ffn.r_vec_mk depth=2048
	#pragma HLS stream variable=weight_block.ffn.r_vec_mv depth=2048	

	hls::stream<t_floatVec_0> x;
	#pragma HLS stream variable=x depth=256
	hls::stream<t_floatVec_0> output_;
	#pragma HLS stream variable=output_ depth=256
	#pragma HLS dataflow
	#pragma HLS clkdomain clk1 10 5
	#pragma HLS clksel clk1 sel 
	read_all(state_in, weight_block, x, x_, xx, xx_ffn, aa, bb, pp, ln1_weight, ln1_bias, ln2_weight, ln2_bias, att_r_weight, att_k_weight, att_v_weight, att_o_weight, att_time_mix_k, att_time_mix_v, att_time_mix_r, att_time_first, att_time_decay, att_r_vec_mr, att_r_vec_mk, att_r_vec_mv, att_r_vec_mo, ffn_r_weight, ffn_k_weight, ffn_v_weight, ffn_time_mix_k, ffn_time_mix_r, ffn_r_vec_mr, ffn_r_vec_mk, ffn_r_vec_mv);
	#pragma HLS clkdomain clk2 2
	layer_common_s(state_in,state_out, weight_block, x, output_);
	#pragma HLS clkdomain clk3 30
	
	
	write_all(state_out,output_, output, xx_o, xx_ffn_o, aa_o, bb_o, pp_o);
}
}

void example(char *a, char *b, char *c)
{
#pragma HLS INTERFACE s_axilite port=a bundle=BUS_A
#pragma HLS INTERFACE s_axilite port=b bundle=BUS_A
#pragma HLS INTERFACE s_axilite port=c bundle=BUS_A
#pragma HLS INTERFACE s_axilite port=return bundle=BUS_A

  *c += *a + *b;
}

