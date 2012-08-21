COMMENT


Mod file auto-generated by pyramidal on 2012-08-21 05:08:04.227708


ENDCOMMENT


NEURON {
    SUFFIX na
    USEION na READ ena WRITE ina
    RANGE gbar
    RANGE gna
    RANGE m
    GLOBAL m_A_A,m_A_B,m_A_C,m_A_D,m_A_F
    GLOBAL m_B_A,m_B_B,m_B_C,m_B_D,m_B_F
    RANGE minf, mtau
    RANGE h
    GLOBAL h_A_A,h_A_B,h_A_C,h_A_D,h_A_F
    GLOBAL h_B_A,h_B_B,h_B_C,h_B_D,h_B_F
    RANGE hinf, htau
    GLOBAL na_reversal_potential
    GLOBAL vmin, vmax
}




PARAMETER {
    m_A_A    = 2.5    (mV)
    m_A_B    = -0.1    (ms)
    m_A_C    = -1.0    (mV)
    m_A_D    = -25.0    (mV)
    m_A_F    = -10.0    (mV)
    m_B_A    = 4.0    (mV)
    m_B_B    = 0.0    (mV)
    m_B_C    = 0.0        
    m_B_D    = 0.0    (mV)
    m_B_F    = 18.0    (mV)
    h_A_A    = 0.07    (mV)
    h_A_B    = 0.0    (ms)
    h_A_C    = 0.0    (mV)
    h_A_D    = 0.0    (mV)
    h_A_F    = 20.0    (mV)
    h_B_A    = 1.0    (mV)
    h_B_B    = 0.0    (mV)
    h_B_C    = 1.0        
    h_B_D    = -30.0    (mV)
    h_B_F    = -10.0    (mV)
    gbar     = 12000.0      (pS/um2)
    na_reversal_potential = 115.0    (mV)
    v                                 (mV)
    dt                                (ms)
    vmin     = -30    (mV)
    vmax     = 120    (mV)
}




UNITS {
     (mA) = (milliamp)
     (mV) = (millivolt)
     (pS) = (picosiemens)
     (um) = (micron)
}




ASSIGNED {
    ina    (mA/cm2)
    gna    (pS/um2)
    ena    (mV)
    minf
    mtau (ms)
    hinf
    htau (ms)
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
    ina = (1e-4) * gna * (v - na_reversal_potential)
}




LOCAL mexp
LOCAL hexp




DERIVATIVE states {
    trates(v)
    m' =  (minf-m)/mtau
    h' =  (hinf-h)/htau
}




PROCEDURE trates(v) {
    TABLE minf, mtau, hinf, htau
    FROM vmin TO vmax WITH 199
    rates(v): not consistently executed from here if usetable == 1
}




PROCEDURE rates(vm) {
    LOCAL  a, b
    a = trap0(vm,m_A_A,m_A_B,m_A_C,m_A_D,m_A_F)
    b = trap0(vm,m_B_A,m_B_B,m_B_C,m_B_D,m_B_F)
    mtau = 1/(a+b)
    minf = a/(a+b)
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


