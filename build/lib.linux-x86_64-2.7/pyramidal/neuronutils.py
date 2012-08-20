"""
"""

class NMODLWriter(object):
    def __init__(self):
        pass

class HHNMODLWriter(NMODLWriter):
    """
    """

    def __init__(self,hh_channel):
        """
        """

        import os

        self.channel = hh_channel
        self.lines = []
        filepath = os.path.join(os.curdir,hh_channel.channel_name + '.mod')
        print 'filepath:'
        print filepath
        self.file = open( filepath, 'w')

        if self.channel.x_power != 0:
            self.activation_gate = True
        else:
            self.activation_gate = False

        if self.channel.y_power != 0:
            self.inactivation_gate = True
        else:
            self.inactivation_gate = False
        
    def _whitespace(self):
        """
        """
        self.lines.append("\n")

    def _add_to_file(self,string):
        """
        """
        
        self.lines.append(string)

    def _comment(self,string):
        """
        Could be better to do this using a decorator
        """

        self._add_to_file("COMMENT")
        self._whitespace()
        self._add_to_file(string)
        self._whitespace()
        self._add_to_file("ENDCOMMENT")
        
    def _header(self):
        """
        """

        import datetime
        now = datetime.datetime.now()
        self._comment("Mod file auto-generated by pyramidal on " + str(now))

    def _neuron_block(self):
        """
        """
        self._whitespace()
        self._add_to_file("NEURON {")
        self._add_to_file("    SUFFIX " + self.channel.channel_name)
	self._add_to_file("    USEION " + self.channel.ion +" READ e" + self.channel.ion + " WRITE i" + self.channel.ion)
	self._add_to_file("    RANGE gbar")
	self._add_to_file("    RANGE g" + self.channel.ion)        

        if self.activation_gate:
            self._add_to_file("    RANGE m")
            self._add_to_file("    GLOBAL m_A_A,m_A_B,m_A_C,m_A_D,m_A_F")
            self._add_to_file("    GLOBAL m_B_A,m_B_B,m_B_C,m_B_D,m_B_F")
            self._add_to_file("    RANGE minf, mtau")

        if self.inactivation_gate:
            self._add_to_file("    RANGE h")
            self._add_to_file("    GLOBAL h_A_A,h_A_B,h_A_C,h_A_D,h_A_F")
            self._add_to_file("    GLOBAL h_B_A,h_B_B,h_B_C,h_B_D,h_B_F")
            self._add_to_file("    RANGE hinf, htau")
            
	self._add_to_file("    GLOBAL " + self.channel.ion +"_reversal_potential")
	self._add_to_file("    GLOBAL vmin, vmax")
        self._add_to_file("}")
        self._whitespace()
        
    def _independent_block(self):
        """
        """

        self._whitespace()
        self._add_to_file("INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}")
        self._whitespace()

    def _params_write(self,params,prefix = 'm'):
        self._add_to_file("    " + prefix + "_A_A    = " + str(params['A_A']) + "    (mV)")
        self._add_to_file("    " + prefix + "_A_B    = " + str(params['A_B']) + "    (ms)")
        self._add_to_file("    " + prefix + "_A_C    = " + str(params['A_C']) + "    (mV)")
        self._add_to_file("    " + prefix + "_A_D    = " + str(params['A_D']) + "    (mV)")
        self._add_to_file("    " + prefix + "_A_F    = " + str(params['A_F']) + "    (mV)")
        self._add_to_file("    " + prefix + "_B_A    = " + str(params['B_A']) + "    (mV)")
        self._add_to_file("    " + prefix + "_B_B    = " + str(params['B_B']) + "    (mV)")
        self._add_to_file("    " + prefix + "_B_C    = " + str(params['B_C']) + "        ")
        self._add_to_file("    " + prefix + "_B_D    = " + str(params['B_D']) + "    (mV)")
        self._add_to_file("    " + prefix + "_B_F    = " + str(params['B_F']) + "    (mV)")        
        
    def _parameters_block(self):
        """
        """

        self._whitespace()
        self._add_to_file("PARAMETER {")

        if self.activation_gate:
            params = self.channel.x_gating_params
            self._params_write(params, prefix = 'm')

        if self.inactivation_gate:
            params = self.channel.y_gating_params
            self._params_write(params, prefix = 'h')
            
        gbar = self.channel.specific_gbar * 100 # temporary hack because we're using ps/um2 unlike pyramidal         
        self._add_to_file("    gbar     = " + str(gbar) + "      (pS/um2)")
        self._add_to_file("    " + self.channel.ion + "_reversal_potential = " + str(self.channel.reversal_potential) + "    (mV)")
        self._add_to_file("    v                                 (mV)")
        self._add_to_file("    dt                                (ms)")
        self._add_to_file("    vmin     = " + str(self.channel.vmin) + "    (mV)")
        self._add_to_file("    vmax     = " + str(self.channel.vmax) + "    (mV)")
        self._add_to_file("}")
        self._whitespace()
        
    def _units_block(self):
        """
        """
        
        self._whitespace()
        self._add_to_file("UNITS {")
        self._add_to_file("     (mA) = (milliamp)")
	self._add_to_file("     (mV) = (millivolt)")
	self._add_to_file("     (pS) = (picosiemens)")
	self._add_to_file("     (um) = (micron)")
        self._add_to_file("}")
        self._whitespace()
        
    def _assigned_block(self):
        """
        """

        self._whitespace()
        self._add_to_file("ASSIGNED {")
        self._add_to_file("    i" + self.channel.ion + "    (mA/cm2)")
        self._add_to_file("    g" + self.channel.ion + "    (pS/um2)")
        self._add_to_file("    e" + self.channel.ion + "    (mV)")

        if self.activation_gate:
            self._add_to_file("    minf")
            self._add_to_file("    mtau (ms)")

        if self.inactivation_gate:
            self._add_to_file("    hinf")
            self._add_to_file("    htau (ms)")

        self._add_to_file("}")
        self._whitespace()
        
    def _state_block(self):
        """
        """
        
        self._whitespace()
        if self.activation_gate and self.inactivation_gate:                      
            self._add_to_file("STATE { m h }")
        elif self.activation_gate:
            self._add_to_file("STATE { m }")
        elif self.inactivation_gate:
            self._add_to_file("STATE { m h }")                                  

        self._whitespace()

    def _initial_block(self):
        """
        """
        
        self._whitespace()
        self._add_to_file("INITIAL {")
        self._add_to_file("    trates(v)")

        if self.activation_gate:
            self._add_to_file("    m = minf")

        if self.inactivation_gate:
            self._add_to_file("    h = hinf")
            
        self._add_to_file("}")
        self._whitespace()
        
    def _breakpoint_block(self):
        """
        """
        
        self._whitespace()
        self._add_to_file("BREAKPOINT {")
        self._add_to_file("    SOLVE states METHOD cnexp")

        gates_string = '*m' * int(self.channel.x_power) + '*h' * int(self.channel.y_power)

        self._add_to_file("    g" + self.channel.ion + " = gbar" + gates_string)

        self._add_to_file("    i" + self.channel.ion + " = (1e-4) * g" + self.channel.ion + " * (v - " + self.channel.ion + "_reversal_potential)")
        self._add_to_file("}")
        self._whitespace()
        
    def _local_block(self):
        """
        """
        
        self._whitespace()
        if self.activation_gate:
            self._add_to_file("LOCAL mexp")

        if self.inactivation_gate:
            self._add_to_file("LOCAL hexp")

        self._whitespace()
        
    def _derivative_block(self):
        """
        """
        
        self._whitespace()        
        self._add_to_file("DERIVATIVE states {")
        self._add_to_file("    trates(v)")

        if self.activation_gate:
            self._add_to_file("    m' =  (minf-m)/mtau")

        if self.inactivation_gate:
            self._add_to_file("    h' =  (hinf-h)/htau")

        self._add_to_file("}")
        self._whitespace()

    def _trates_block(self):
        """
        """
        
        self._whitespace()
        self._add_to_file("PROCEDURE trates(v) {")

        if self.activation_gate and self.inactivation_gate:
            self._add_to_file("    TABLE minf, mtau, hinf, htau")

        elif self.activation_gate:
            self._add_to_file("    TABLE minf, mtau")            

        elif self.inactivation_gate:
            self._add_to_file("    TABLE minf, mtau")            

	self._add_to_file("    FROM vmin TO vmax WITH 199")
	self._add_to_file("    rates(v): not consistently executed from here if usetable == 1")
        self._add_to_file("}")
        self._whitespace()        
        
    def _rates_block(self):
        """
        """

        self._whitespace()        
        self._add_to_file("PROCEDURE rates(vm) {")  
        self._add_to_file("    LOCAL  a, b")

        if self.activation_gate:
            self._add_to_file("    a = trap0(vm,m_A_A,m_A_B,m_A_C,m_A_D,m_A_F)")
            self._add_to_file("    b = trap0(vm,m_B_A,m_B_B,m_B_C,m_B_D,m_B_F)")
            self._add_to_file("    mtau = 1/(a+b)")
            self._add_to_file("    minf = a/(a+b)")

        if self.inactivation_gate:
            self._add_to_file("    a = trap0(vm,h_A_A,h_A_B,h_A_C,h_A_D,h_A_F)")
            self._add_to_file("    b = trap0(vm,h_B_A,h_B_B,h_B_C,h_B_D,h_B_F)")
            self._add_to_file("    htau = 1/(a+b)")
            self._add_to_file("    hinf = a/(a+b)")

        self._add_to_file("}")                        
        self._whitespace()
        
    def _trap0_block(self):
        """
        """
        
        self._whitespace()        
        self._add_to_file("FUNCTION trap0(v,A,B,C,D,F) {")
        self._add_to_file("	if (fabs(v/A) > 1e-6) {")
        self._add_to_file("	        trap0 = (A + B * v) / (C + exp((v + D)/F))")
        self._add_to_file("	} else {")
        self._add_to_file("	        trap0 = B * F")
        self._add_to_file(" 	}")
        self._add_to_file("}")
        self._whitespace()        
                   
    def write(self):
        """
        """

        self._header()
        self._neuron_block()
        self._parameters_block()
        self._units_block()
        self._assigned_block()
        self._state_block()
        self._initial_block()
        self._breakpoint_block()
        self._local_block()
        self._derivative_block()
        self._trates_block()
        self._rates_block()
        self._trap0_block()
        
        for line in self.lines:
            self.file.write("%s\n" % line)

        self.file.close()

        
