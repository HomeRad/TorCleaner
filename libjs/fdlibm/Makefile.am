SRC = fdlibm.h e_acos.c e_asin.c e_atan2.c e_exp.c e_fmod.c e_log.c e_pow.c \
e_rem_pio2.c e_sqrt.c k_cos.c k_sin.c k_rem_pio2.c k_standard.c k_tan.c \
s_atan.c s_ceil.c s_copysign.c s_cos.c s_fabs.c s_finite.c s_floor.c \
s_isnan.c s_lib_version.c s_matherr.c s_rint.c s_scalbn.c s_sin.c s_tan.c \
w_acos.c w_asin.c w_atan2.c w_exp.c w_fmod.c w_log.c w_pow.c w_sqrt.c


DEFS			= @DEFS@ -DIEEE_LIBM
CFLAGS += -fPIC
noinst_LTLIBRARIES	= libfdm.la
libfdm_la_SOURCES	= $(SRC)
