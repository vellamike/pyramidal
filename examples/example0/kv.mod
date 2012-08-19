COMMENT

MV trying to replicate the squid demo which comes with pymoose

ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX kv
	USEION k READ ek WRITE ik
	RANGE m, gk, gbar
	GLOBAL m_A_A,m_A_B,m_A_C,m_A_D,m_A_F
	GLOBAL m_B_A,m_B_B,m_B_C,m_B_D,m_B_F
	GLOBAL k_revpot
	RANGE minf, mtau
	GLOBAL vmin, vmax
}

PARAMETER {

	gbar = 1000   	(pS/um2)	: mho/cm2
	
	:these are the gating params:
	
	k_revpot = -12.0      (mV) :is this the right place to put it? NMODL is confusing...

        m_A_A = 0.1     (mV)
        m_A_B = -0.01   (ms)
        m_A_C = -1.0    (mV)
        m_A_D = -10.0   (mV)
        m_A_F = -10.    (mV)
        m_B_A = 0.125   (mV)
        m_B_B = 0.0     (mV)
        m_B_C = 0.0   
        m_B_D = 0.0     (mV)
        m_B_F = 80.0    (mV)

	v 		(mV)
	dt		(ms)
	vmin = -30	(mV)
	vmax = 120	(mV)
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

ASSIGNED {
	ik 		(mA/cm2)
	gk		(pS/um2)
	ek		(mV)
	minf 		hinf
	mtau (ms)	htau (ms)
}
 

STATE { m }

INITIAL { 
	trates(v)
	m = minf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
        gk = gbar*m*m*m*m
	ik = (1e-4) * gk * (v - k_revpot)
} 

LOCAL mexp:, hexp 

DERIVATIVE states {   :Computes state variables m, h, and n 
        trates(v)      :             at the current v and dt.
        m' =  (minf-m)/mtau
}

PROCEDURE trates(v) {  
        TABLE minf,  hinf, mtau, htau

	DEPEND m_A_A,m_A_B,m_A_C,m_A_D,m_A_F,m_B_A,m_B_B,m_B_C,m_B_D,m_B_F
	
	FROM vmin TO vmax WITH 199

	rates(v): not consistently executed from here if usetable == 1
}


PROCEDURE rates(vm) {  
        LOCAL  a, b

	a = trap0(vm,m_A_A,m_A_B,m_A_C,m_A_D,m_A_F)
	b = trap0(vm,m_B_A,m_B_B,m_B_C,m_B_D,m_B_F)

	mtau = 1/(a+b)
	minf = a/(a+b)
}


FUNCTION trap0(v,A,B,C,D,F) {
	if (fabs(v/A) > 1e-6) {
	        trap0 = (A + B * v) / (C + exp((v + D)/F))
	} else {
	        trap0 = B * F
 	}
}