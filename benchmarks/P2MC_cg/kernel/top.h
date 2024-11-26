#include <ap_int.h>
#include <hls_stream.h>

#define min(x,y) ((x < y) ? x : y)
#define max(x,y) ((x > y) ? x : y)
#define SQRT_FUN(x) sqrt(x)

/* Data Type */
typedef float A_t1;
typedef float B_t1;
typedef float C_t1;
typedef ap_uint<512> A_t16;
typedef ap_uint<64> A_t2;
typedef ap_uint<512> B_t16;
typedef ap_uint<64> B_t2;
typedef ap_uint<512> C_t16;
typedef ap_uint<128> C_t4;
/* Data Type */

/* Helper Function */
inline void host_serialize_A_m1(float *A_to, float *A_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 3; c0 += 1)
    for (int c1 = 0; c1 <= 3; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 1; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 7; c4 += 1)
            for (int c5 = 0; c5 <= 15; c5 += 1)
              A_to[cnt++] = A_from[(16 * c0 + 8 * c3 + c4) * 64 + (16 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
inline void host_serialize_A_m2(float *A_to, float *A_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 3; c0 += 1)
    for (int c1 = 0; c1 <= 3; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 3; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 3; c4 += 1)
            for (int c5 = 0; c5 <= 15; c5 += 1)
              A_to[cnt++] = A_from[(16 * c0 + 4 * c3 + c4) * 64 + (16 * c2 + c5)];
        }
      }
}
/* Helper Function */


/* Helper Function */
inline void host_serialize_B_m1(float *B_to, float *B_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 3; c0 += 1)
    for (int c1 = 0; c1 <= 3; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 1; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 7; c4 += 1)
            for (int c5 = 0; c5 <= 15; c5 += 1)
              B_to[cnt++] = B_from[(16 * c1 + 8 * c3 + c4) * 64 + (16 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
inline void host_serialize_B_m2(float *B_to, float *B_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 3; c0 += 1)
    for (int c1 = 0; c1 <= 3; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (int c3 = 0; c3 <= 3; c3 += 1) {
          // io_L2
          for (int c4 = 0; c4 <= 3; c4 += 1)
            for (int c5 = 0; c5 <= 15; c5 += 1)
              B_to[cnt++] = B_from[(16 * c1 + 4 * c3 + c4) * 64 + (16 * c2 + c5)];
        }
      }
}
/* Helper Function */

/* Helper Function */
inline void host_deserialize_C_m1(float *C_to, float *C_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 3; c0 += 1)
    for (int c1 = 0; c1 <= 3; c1 += 1) {
      // array
      // io_L3
      for (int c3 = 0; c3 <= 1; c3 += 1) {
        // io_L2
        for (int c4 = 0; c4 <= 1; c4 += 1) {
          // io_L1
          // pe
          for (int c5 = 0; c5 <= 7; c5 += 1)
            for (int c6 = 0; c6 <= 7; c6 += 1)
              C_to[(16 * c0 + 8 * c4 + c5) * 64 + (16 * c1 + 8 * c3 + c6)] = C_from[cnt++];
        }
      }
    }
}
/* Helper Function */

/* Helper Function */
inline void host_deserialize_C_m2(float *C_to, float *C_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 3; c0 += 1)
    for (int c1 = 0; c1 <= 3; c1 += 1) {
      // array
      // io_L3
      for (int c3 = 0; c3 <= 3; c3 += 1) {
        // io_L2
        for (int c4 = 0; c4 <= 3; c4 += 1) {
          // io_L1
          // pe
          for (int c5 = 0; c5 <= 3; c5 += 1)
            for (int c6 = 0; c6 <= 3; c6 += 1)
              C_to[(16 * c0 + 4 * c4 + c5) * 64 + (16 * c1 + 4 * c3 + c6)] = C_from[cnt++];
        }
      }
    }
}
/* Helper Function */


void kernel_sep(A_t16 *A, B_t16 *B, C_t16 *C_temp1, C_t16 *C_temp2);
void kernel_m1_0(A_t16 *A, B_t16 *B, C_t16 *C);
void kernel_m1_1(A_t16 *A, B_t16 *B, C_t16 *C);
void kernel_m1_2(A_t16 *A, B_t16 *B, C_t16 *C);
void kernel_m2_0(A_t16 *A, B_t16 *B, C_t16 *C);
void kernel_m2_1(A_t16 *A, B_t16 *B, C_t16 *C);
void A_IO_L2_in_intra_trans_m1(int idx, int c0, int c1, int c2, A_t16 local_A[8][1], hls::stream<A_t2> &fifo_A_local_out, bool intra_trans_en);
void A_IO_L2_in_inter_trans_m1(int idx, int c0, int c1, int c2, A_t16 local_A[8][1], hls::stream<A_t16> &fifo_A_in, hls::stream<A_t16> &fifo_A_out, bool inter_trans_en);
void A_IO_L2_in_inter_trans_boundary_m1(int idx, int c0, int c1, int c2, A_t16 local_A[8][1], hls::stream<A_t16> &fifo_A_in, bool inter_trans_en);
void B_IO_L2_in_intra_trans_m1(int idx, int c0, int c1, int c2, B_t16 local_B[8][1], hls::stream<B_t2> &fifo_B_local_out, bool intra_trans_en);
void B_IO_L2_in_inter_trans_m1(int idx, int c0, int c1, int c2, B_t16 local_B[8][1], hls::stream<B_t16> &fifo_B_in, hls::stream<B_t16> &fifo_B_out, bool inter_trans_en);
void B_IO_L2_in_inter_trans_boundary_m1(int idx, int c0, int c1, int c2, B_t16 local_B[8][1], hls::stream<B_t16> &fifo_B_in, bool inter_trans_en);
void PE_wrapper_m1(int idx, int idy, hls::stream<A_t2> &fifo_A_in, hls::stream<A_t2> &fifo_A_out, hls::stream<B_t2> &fifo_B_in, hls::stream<B_t2> &fifo_B_out, hls::stream<float> &fifo_C_drain_out);
void C_drain_IO_L1_out_intra_trans_m1(int idx, int idy, int c0, int c1, C_t4 local_C[8][2], hls::stream<float> &fifo_C_drain_local_in);
void C_drain_IO_L1_out_inter_trans_m1(int idx, int idy, int c0, int c1, C_t4 local_C[8][2], hls::stream<C_t4> &fifo_C_drain_in, hls::stream<C_t4> &fifo_C_drain_out);
void C_drain_IO_L1_out_inter_trans_boundary_m1(int idx, int idy, int c0, int c1, C_t4 local_C[8][2], hls::stream<C_t4> &fifo_C_drain_out);
void C_drain_IO_L1_out_wrapper_m1(int idx, int idy, hls::stream<C_t4> &fifo_C_drain_in, hls::stream<C_t4> &fifo_C_drain_out, hls::stream<float> &fifo_C_drain_local_in);
void C_drain_IO_L1_out_boundary_wrapper_m1(int idx, int idy, hls::stream<C_t4> &fifo_C_drain_out, hls::stream<float> &fifo_C_drain_local_in);
void A_IO_L2_in_intra_trans_m2(int idx, int c0, int c1, int c2, A_t16 local_A[4][1], hls::stream<A_t2> &fifo_A_local_out, bool intra_trans_en);
void A_IO_L2_in_inter_trans_m2(int idx, int c0, int c1, int c2, A_t16 local_A[4][1], hls::stream<A_t16> &fifo_A_in, hls::stream<A_t16> &fifo_A_out, bool inter_trans_en);
void A_IO_L2_in_inter_trans_boundary_m2(int idx, int c0, int c1, int c2, A_t16 local_A[4][1], hls::stream<A_t16> &fifo_A_in, bool inter_trans_en);
void B_IO_L2_in_intra_trans_m2(int idx, int c0, int c1, int c2, B_t16 local_B[4][1], hls::stream<B_t2> &fifo_B_local_out, bool intra_trans_en);
void B_IO_L2_in_inter_trans_m2(int idx, int c0, int c1, int c2, B_t16 local_B[4][1], hls::stream<B_t16> &fifo_B_in, hls::stream<B_t16> &fifo_B_out, bool inter_trans_en);
void B_IO_L2_in_inter_trans_boundary_m2(int idx, int c0, int c1, int c2, B_t16 local_B[4][1], hls::stream<B_t16> &fifo_B_in, bool inter_trans_en);
void PE_wrapper_m2(int idx, int idy, hls::stream<A_t2> &fifo_A_in, hls::stream<A_t2> &fifo_A_out, hls::stream<B_t2> &fifo_B_in, hls::stream<B_t2> &fifo_B_out, hls::stream<float> &fifo_C_drain_out);
void C_drain_IO_L1_out_intra_trans_m2(int idx, int idy, int c0, int c1, C_t4 local_C[4][1], hls::stream<float> &fifo_C_drain_local_in);
void C_drain_IO_L1_out_inter_trans_m2(int idx, int idy, int c0, int c1, C_t4 local_C[4][1], hls::stream<C_t4> &fifo_C_drain_in, hls::stream<C_t4> &fifo_C_drain_out);
void C_drain_IO_L1_out_inter_trans_boundary_m2(int idx, int idy, int c0, int c1, C_t4 local_C[4][1], hls::stream<C_t4> &fifo_C_drain_out);
void C_drain_IO_L1_out_wrapper_m2(int idx, int idy, hls::stream<C_t4> &fifo_C_drain_in, hls::stream<C_t4> &fifo_C_drain_out, hls::stream<float> &fifo_C_drain_local_in);
void C_drain_IO_L1_out_boundary_wrapper_m2(int idx, int idy, hls::stream<C_t4> &fifo_C_drain_out, hls::stream<float> &fifo_C_drain_local_in);
