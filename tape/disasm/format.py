def singleByteToInt(byteOrInt):
    if type(byteOrInt) == bytes:
        assert len(byteOrInt) == 1
        return byteOrInt[0]
    return byteOrInt


class REXByte:
    def __init__(self, byte):
        byte = singleByteToInt(byte)

        assert bool(byte & 0x40), "Invalid REX byte"
        self.w = (byte >> 3) & 1
        self.r = (byte >> 2) & 1
        self.x = (byte >> 1) & 1
        self.b = (byte >> 0) & 1


class ModRMByte:
    def __init__(self, modrmByte, rex):
        modrm = singleByteToInt(modrmByte)
        self.reg = ((modrm >> 3) & 7) | rex.r
        self.mod = (modrm >> 6) & 3
        self.rm = (modrm & 7) | rex.b
