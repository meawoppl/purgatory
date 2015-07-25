from binascii import hexlify
from io import BytesIO
import xml.etree.ElementTree as ET

opCodeData = ET.fromstring(open("linted.xml").read())

bytesToName = {}
prefixes = []


def extactOpCodes(superHeading):
    ocs = {}
    superGroup = opCodeData.find(superHeading)

    for ocXML in superGroup.findall(".//pri_opcd"):
        vStr = ocXML.get("value")

        group = ocXML.find(".//grp1") 
        if (group is not None) and (group.text == "prefix"):
            prefixes.append(vStr)
            continue

        ocs[vStr] = ocXML.find(".//mnem").text
    return ocs


oneByteCodes = extactOpCodes(".//one-byte")
twoByteCodes = extactOpCodes(".//two-byte")
twoByteCodes = {"0F" + code: nm for code, nm in twoByteCodes.items()}

allCodes = {}
allCodes.update(oneByteCodes)
allCodes.update(twoByteCodes)

for code, nm in sorted(allCodes.items()):
    print(code, nm)


_qryResult = {}
def queryCodeByBytes(bytez, extInt=None):
    assert len(bytez) in [1, 2]

    if bytez in _qryResult:
        return _qryResult

    if len(bytez) == 1:
        sg = opCodeData.find(".//one-byte")
    if len(bytez) == 2:
        sg = opCodeData.find(".//two-byte")

    # MRG NOTE: Stupid and slow
    for ocXML in sg.findall(".//pri_opcd"):
        rightOC = int(ocXML.get("value"), base=16) == bytez[-1]
        for ent in ocXML.findall(".//entry"):
            if extInt is None:
                return ent
            entryExt = int(ent.find(".//opcd_ext").text)
            if entryExt == extInt:
                return ent

    return None


def ocBytesToName(bytez):
    ocXML = queryCodeByBytes(bytez)
    return ocXML.find(".//mnem").text



possiblePrefixes = {0xF0: "LOCK", 0xF2: "REP/REPE", 0xF3: "REPNE", 
                    0x2E: "CS", 0x36: "SS", 0x3E: "DS", 
                    0x26:"ES", 0x64:"FS", 0x65:"GS",
                    0x66: "DATA", 0x67: "ADDR"}

for i in range(16):
    possiblePrefixes[0x40 + i ] = "REX?"



def readOpCode(flo):
    oc1 = flo.read(1)

    if oc1[0] == 0x0F:
        return oc1 + flo.read(1)
    else:
        return oc1




def floPeek(flo):
    before = flo.tell()
    b = flo.read(1)
    flo.seek(before)
    return b

def detectPrefixes(flo):
    """
    Given a FLO, read it forward until there are no prefixes remaining.  
    Return a list of single byte prefix codes.
    """

    pfx = []
    while True:
        # Inspect the byte, and decide if it is a possible prefix
        byte = floPeek(flo)
        if byte[0] not in possiblePrefixes:
            break

        # If it is, add it to the list
        pfx.append(flo.read(1)[0])

        # Sanity check!
        assert len(pfx) <= 4

    return pfx



# [['40',  . . .  '4f']]
rexPrefixes = ["%x" % i for i in range(0x40, 0x50)]

# Vex prefixes
vexPrefixes = [0xC4, 0xC5]

def processPrefixes(flo):
    pfxs =  detectPrefixes(flo)

    # Check if this of is "locked"
    lock = 0xf0 in pfxs

    # Decode all rex bytes. Use only the last
    rexByte = REXByte(0x40)
    vex = None
    for pfx in pfxs:
        if pfx in rexPrefixes:        
            rexByte = REXByte(pfx)
            continue

        # Barf on VEX, NotImplemented
        if pfx in vexPrefixes:
            raise RuntimeError("VEX NOT IMPLEMENTED")

    # Decode the address/register sizes
    aSize = 32
    dSize = 32
    if 0x67 in nonRexPrefixes:
        aSize = 64

    if rexByte and rexByte.w:
        dSize = 64
    else:
        if 0x66 in nonRexPrefixes:
            dSize = 16
        else:
            dSize = 32

    return lock, rexByte, vex, dSize, aSize


def decodeOpCodeName(ocBytes):
    pass


def readMODRM(flo, rexByte):
    modrmByte = flo.read(1)[0]

    # MRG TODO:
    rex_r = 0

    mod = (modrm >> 6) & 3;
    reg = ((modrm >> 3) & 7) | rex_r;






def decodeML(bytez):
    bio = BytesIO(bytez)
    pfxs = processPrefixes(bio)

    print(len(pfxs), "prefixes detected" , repr(pfxs))

    opCode = readOpCode(bio)
    print(opCode, ocBytesToName(opCode))

    needsMODRM(opcode)



if __name__ == "__main__":

    decodeML(b"\x55")  # PUSH EBP
    decodeML(b"\x8B\xEC") # MOV EBP, ESP

    decodeML(b"\x66\x00")
    decodeML(b"\x0F\x58")