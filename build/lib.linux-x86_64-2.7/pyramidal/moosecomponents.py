# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Vella
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are meet:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------

import moose
import math
import numpy

class IonChannel(moose.HHChannel):
    """
    Enhanced version of HHChannel with setupAlpha that takes a dict
    of parameters.

    This was taken mainly from the squid.py example file in MOOSE.
    """
    def __init__(self, name, compartment, specific_gbar, e_rev, Xpower, Ypower=0.0, Zpower=0.0):
        """Instantuate an ion channel.

        name -- name of the channel.
        
        compartment -- moose.Compartment object that contains the channel.

        specific_gbar -- specific value of maximum conductance.

        e_rev -- reversal potential of the channel.
        
        Xpower -- exponent for the first gating parameter.

        Ypower -- exponent for the second gatinmg component.
        """
        moose.HHChannel.__init__(self, '%s/%s' % (compartment.path, name))

        #Area in cm^2 when length and diameter are in um"
        compartment_area = 1e-8 * compartment.length * numpy.pi * compartment.diameter # cm^2

        self.Gbar = specific_gbar * compartment_area

        print 'self gbar is:'
        print self.Gbar

        self.Ek = e_rev
        self.Xpower = Xpower
        self.Ypower = Ypower
        self.Zpower = Zpower

        moose.connect(self, 'channel', compartment, 'channel')
        
    def setupAlpha(self, gate, params, vdivs, vmin, vmax):
        """Setup alpha and beta parameters of specified gate.

        gate -- 'X'/'Y'/'Z' string initial of the gate.

        params -- dict of parameters to compute alpha and beta, the rate constants for gates.

        vdivs -- number of divisions in the interpolation tables for alpha and beta parameters.

        vmin -- minimum voltage value for the alpha/beta lookup tables.

        vmax -- maximum voltage value for the alpha/beta lookup tables.
        """

        print "~~~"
        print "Setting up alpha in moose"
        print "self.path is:"
        print self.path
        
        if gate == 'X' and self.Xpower > 0:
            print 'gate path:'
            print self.path + '/gateX'
            gate = moose.HHGate(self.path + '/gateX')
        elif gate == 'Y' and self.Ypower > 0:
            gate = moose.HHGate(self.path + '/gateY')
        else:
            print "GATE SETUP ALPHA FAILED"
            return False
        
        gate.setupAlpha([params['A_A'],
                         params['A_B'],
                         params['A_C'],
                         params['A_D'],
                         params['A_F'],
                         params['B_A'],
                         params['B_B'],
                         params['B_C'],
                         params['B_D'],
                         params['B_F'],
                         vdivs, vmin, vmax])
        return True
