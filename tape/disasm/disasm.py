from __future__ import print_function

# test1.py
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_MODE_32

CODE = b"\x8d\x44\x38\x02"

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

for i in md.disasm(CODE, 0):
    # print(dir(i))
    print("0x%x:\t%s\t%s" % (i.address, i.mnemonic, i.op_str))
    if len(i.regs_read) > 0:
        print("\tImplicit registers read: "),
        for r in i.regs_read:
            print("%s " % i.reg_name(r)),
        print
    if len(i.groups) > 0:
        print("\tThis instruction belongs to groups:", end="")
        for g in i.groups:
            print("%u" % g)
            # print("%u" % g, end="")
        print()


def dumpASM(flo, mode, maxAddr=1e99):
    modeRef = {32: CS_MODE_32, 64: CS_MODE_64}

    md = Cs(CS_ARCH_X86, modeRef[mode])
    md.detail = True

    for i in md.disasm(flo, 0):
        # print(dir(i))
        print("0x%x:\t%s\t%s" % (i.address, i.mnemonic, i.op_str))
        print("\tImplicit registers read: ", end="")
        for r in i.regs_read:
            print("%s " % i.reg_name(r))
        print()

        print("\tImplicit registers written: ", end="")
        for r in i.regs_write:
            print("%s " % i.reg_name(r))
        print()

        if i.address > maxAddr:
            break
