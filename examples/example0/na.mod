COMMENT

MV trying to replicate the squid demo which comes with pymoose

ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX na
	USEION na READ ena WRITE ina
	RANGE m, h, gna, gbar
	GLOBAL m_A_A,m_A_B,m_A_C,m_A_D,m_A_F
	GLOBAL m_B_A,m_B_B,m_B_C,m_B_D,m_B_F
	GLOBAL h_A_A,h_A_B,h_A_C,h_A_D,h_A_F
	GLOBAL h_B_A,h_B_B,h_B_C,h_B_D,h_B_F
	GLOBAL na_revpot
	RANGE minf, hinf, mtau, htau
	GLOBAL vmin, vmax
}

PARAMETER {

	gbar = 1000   	(pS/um2)	: mho/cm2
	
	:these are the gating params:
	
	na_revpot = 115      (mV) :is this the right place to put it? NMODL is confusing...

        m_A_A = 2.50   (mV)
        m_A_B = -0.1   (ms)
        m_A_C = -1.0   (mV)
        m_A_D = -25.0  (mV)
        m_A_F =-10.0   (mV)
        m_B_A = 4.0    (mV)
        m_B_B = 0.0    (mV)
        m_B_C = 0.0    
        m_B_D = 0.0    (mV)
        m_B_F = 18.0   (mV)

        h_A_A =  0.07  (mV)
        h_A_B =  0.0   (ms)
        h_A_C =  0.0   (mV)
        h_A_D =	 0.0   (mV)
        h_A_F =	 20.0  (mV)
        h_B_A =	 1.0   (mV)
        h_B_B =	 0.0   (mV)
        h_B_C =	 1.0   
        h_B_D =	 -30.0 (mV)
        h_B_F =	 -10.0 (mV)
							
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
	ina 		(mA/cm2)
	gna		(pS/um2)
	ena		(mV)
	minf 		hinf
	mtau (ms)	htau (ms)
}
 

STATE { m h }

INITIAL { 
	trates(v)
	m = minf
	h = hinf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
        gna = gbar*m*m*m*h
	ina = (1e-4) * gna * (v - na_revpot)
} 

LOCAL mexp, hexp 

DERIVATIVE states {   :Computes state variables m, h, and n 
        trates(v)      :             at the current v and dt.
        m' =  (minf-m)/mtau
        h' =  (hinf-h)/htau
}

PROCEDURE trates(v) {  
        TABLE minf,  hinf, mtau, htau

	DEPEND m_A_A,m_A_B,m_A_C,m_A_D,m_A_F,m_B_A,m_B_B,m_B_C,m_B_D,m_B_F,h_A_A,h_A_B,h_A_C,h_A_D,h_A_F
	
	FROM vmin TO vmax WITH 199

	rates(v): not consistently executed from here if usetable == 1
}


PROCEDURE rates(vm) {  
        LOCAL  a, b

	a = trap0(vm,m_A_A,m_A_B,m_A_C,m_A_D,m_A_F)
	b = trap0(vm,m_B_A,m_B_B,m_B_C,m_B_D,m_B_F)

	mtau = 1/(a+b)
	minf = a/(a+b)

	:"h" inactivation 

	a = trap0(vm,h_A_A,h_A_B,h_A_C,h_A_D,h_A_F)
	b = trap0(vm,h_B_A,h_B_B,h_B_C,h_B_D,h_B_F)

	htau = 1/(a+b)
	hinf = a/(a+b)
}


FUNCTION trap0(v,A,B,C,D,F) {
	if (fabs(v/A) > 1e-6) {
	        trap0 = (A + B * v) / (C + exp((v + D)/F))
	} else {
	        trap0 = B * F
 	}
}