

class OpCodeTransmutator:
    def __init__(self, prefixes, ocvalue, binFlo):
        # Store the prefixes, and oc bytes
        self.pfxs = prefixes
        self.ocBytes = ocvalue
        self.ocInt = ocBytes[0] if len(ocBytes) == 1 else (ocBytes[0] << 8) + ocBytes[1]

    	# run some general, and OC specific sanity checks
        assert ocvalue in self.ocs, "Opcode {} not associated with this class".format(ocvalue) 
        self.universalAssertions()
        self.assertions()

        # Read the rest of the bytes necessary to decode this op
        self.readOC(binFlo)

    def readModRM(self, binFlo):
    	"""Read the Mod/RM byte from the binFLo, and apply the logics
    	associated with my prefixes to influence register/memory address
    	computations"""

    	return ModRMByte(binFlo.read(1))


    def universalAssertions(self):
    	"""TODO: Sanity check the opcode/prefix combinations"""
    	
    def assertions(self):
    	"""OC Prefix combinations particular to this group of codes"""
    	pass

    def readOC(ocvalue, binFlo):
        raise NotImplemented("Subcasses must implement this method")

    def emitBC(self):
        raise NotImplemented("Subcasses must implement this method")


# These are all the register-register operations.  Pretty easy to work with.
#                   ADD,  OR,   ADC,  SBB,  AND,  SUB,  XOR,  CMP 
# Their 3 LSB dictate some special things.
_groupAops = []
for startOffset in [0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38]:
    for x in range(5):
        _groupAops.append(startOffset + x)

class GroupATransmutor:
	def readOC(self):
		# This group of opcodes packs register information into the bottom 3 bits of the OC
        op = (self.ocInt >> 3) & 7;
        f = (self.ocInt >> 1) & 3;

		
