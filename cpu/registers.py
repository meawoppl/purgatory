import random

bitWidth = [64, 32, 16, 8]
registerNamesTable = [["rax", "eax", "ax", "al"],
                      ["rbx", "ebx", "bx", "bl"],
                      ["rcx", "ecx", "cx", "cl"],
                      ["rdx", "edx", "dx", "dl"],
                      ["rsi", "esi", "si", "sil"],
                      ["rdi", "edi", "di", "dil"],
                      ["rbp", "ebp", "bp", "bpl"],
                      ["rsp", "esp", "sp", "spl"],
                      ["r8", "r8d", "r8w", "r8b"],
                      ["r9", "r9d", "r9w", "r9b"],
                      ["r10", "r10d", "r10w", "r10b"],
                      ["r11", "r11d", "r11w", "r11b"],
                      ["r12", "r12d", "r12w", "r12b"],
                      ["r13", "r13d", "r13w", "r13b"],
                      ["r14", "r14d", "r14w", "r14b"],
                      ["r15", "r15d", "r15w", "r15b"]]


regNamesFlat = []
for rGroup in registerNamesTable:
    regNamesFlat += rGroup


# MRG TODO: Fugly
def regNameToBitCount(regName):
    assert regName in regNamesFlat

    for regGroup in registerNamesTable:
        if regName in regGroup:
            return bitWidth[regGroup.index(regName)]

print("EAX", regNameToBitCount("rax"))


def randomName(length=12):
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for r in range(length)])


class TinyLLVM:
    def __init__(self, flo):
        self.flo = flo
        self.indent = 0
        self.strings = {}
        print("INIT")

    def _emitLine(self, string):
        # Strip leadind indentation
        string = (" " * self.indent) + string.strip()

        # Add a newline if needed
        if not string.endswith("\n"):
            string += "\n"

        self.flo.write(string)

    def emitComment(self, comment):
        self._emitLine("; " + comment)

    def emitGlobalConstCString(self, string, tokenName=None):
        assert '"' not in string
        if tokenName is None:
            tokenName = randomName()

        self.strings[tokenName] = string
        stringBase = '@{0} = private unnamed_addr constant [{1} x i8] c"{2}\\00", align 1'
        self._emitLine(stringBase.format(tokenName, len(string) + 1, string))

        return tokenName

    def printCStringToken(self, tokenName):
        rtoken1 = randomName()
        stringLength = len(self.strings[tokenName])
        self._emitLine("%{} = bitcast [{} x i8]* to i8*".format(rtoken1, stringLength))

        rtoken2 = randomName()
        self._emitLine("%{} = call i32 (i8*, ...)* @printf(i8* %{})".format(rtoken2, rtoken1))

    def uglyPre(self):
        self._emitLine("""; ModuleID = 'struct.c'""")
        self._emitLine('''target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"''')
        self._emitLine('''target triple = "x86_64-unknown-linux-gnu"''')
        self._emitLine("")

    def mainStart(self):
        self._emitLine("""; Function Attrs: nounwind uwtable""")
        self._emitLine("""define i32 @main() #0 {""")
        self._emitLine("""entry:""")
        self.indent += 2

    def mainEnd(self):
        self._emitLine("""ret i32 %r""")
        self._emitLine("}")
        self.indent -= 2

        self._emitLine("""declare i32 @printf(i8*, ...) #1""")
        self._emitLine("""attributes #0 = { nounwind uwtable "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf"="true" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "unsafe-fp-math"="false" "use-soft-float"="false" }""")
        self._emitLine("""attributes #1 = { "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf"="true" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "unsafe-fp-math"="false" "use-soft-float"="false" }""")


class TapeLLVM(TinyLLVM):
    def regName(self, baseName):
        return "@r_{}".format(baseName)

    def emitSetReg(self, regName, rFmt, parentReg, pFmt):
        # Declare the int64 parent
        self._emitLine("define {fmt} @reg_set_{name}({fmt} %toSet)".format(fmt=rFmt, name=regName) + " {")
        self._emitLine("entry:")
        self.indent += 2
        self._emitLine("%ptr = bitcast {pFmt}* {parent} to {fmt}*".format(pFmt=pFmt, parent=parentReg, fmt=rFmt))
        self._emitLine("store {fmt} %toSet, {fmt}* %ptr".format(fmt=rFmt, parent=parentReg, pFmt=pFmt))
        self._emitLine("ret {fmt} %toSet".format(fmt=rFmt))
        self.indent -= 2
        self._emitLine("}")

    def emitGetReg(self, regName, rFmt, parentReg, pFmt):
        self._emitLine("define {fmt} @reg_get_{name}()".format(fmt=rFmt, name=regName) + " {")
        self._emitLine("entry:")
        self.indent += 2
        self._emitLine("%ptr = bitcast {pFmt}* {parent} to {fmt}*".format(pFmt=pFmt, parent=parentReg, fmt=rFmt))
        self._emitLine("%res = load {fmt}* %ptr".format(fmt=rFmt))
        self._emitLine("ret {fmt} %res".format(fmt=rFmt))
        self.indent -= 2
        self._emitLine("}")

    def emitGetSetReg(self, regName, rFmt, parentReg, pFmt):
        self._emitLine("")
        self.emitComment("Register get/set for %s" % regName)
        self.emitGetReg(regName, rFmt, parentReg, pFmt)
        self.emitSetReg(regName, rFmt, parentReg, pFmt)
        self._emitLine("")

    def emitRegisterUtil(self):
        fmts = ["i64", "i32", "i16", "i8"]
        for names in registerNamesTable:
            parentReg = names[0]
            n64 = self.regName(parentReg)
            # Declare the int64 parent
            self._emitLine("{} = global i64 0".format(n64))

            # Make getters/setters for overlapping regs
            for rn, regFmt in zip(names, fmts):
                self.emitGlobalConstCString(rn, tokenName="n_" + rn)
                self.emitGetSetReg(rn, regFmt, n64, "i64")

    def emitPrintRegname(self, registerName):
        baseString = """%res = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([{0} x i8]* @n_{1}, i32 0, i32 0))\n"""
        self._emitLine(baseString.format(len(registerName) + 1, registerName))

    def emitRegDumpFunc(self):
        for rGroup in registerNamesTable:
            parentReg = rGroup[0]
            self.emitPrintRegname(parentReg)


def emitPrintCStringToken(flo, tokenName):
    baseString = """%call = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([{0} x i8]* @.{1}, i32 0, i32 0))\n"""
    flo.write(baseString.format(tokenName))


def emitRegPointer(flo, regName):
    pass


if __name__ == "__main__":
    import os
    import subprocess

    with open("jank-test.ll", "w") as testFile:
        tl = TapeLLVM(testFile)
        tl.uglyPre()
        tl.emitRegisterUtil()
        tl.emitGlobalConstCString(" ", tokenName="space")
        tl.mainStart()
        tl._emitLine("%0 = call i32 @reg_set_eax(i32 65536)")
        tl.emitPrintRegname("eax")
        # tl._emitLine("%1 = call i32 @reg_set_eax(i32 65280)")
        tl._emitLine("%r = call i32 @reg_get_eax()")
        tl.mainEnd()

    print("Compile:")
    print()
    os.system("/usr/bin/clang --version")
    print()

    os.system('/usr/bin/clang jank-test.ll -o tokill')

    print("Run:")
    try:
        subprocess.check_call(["./tokill"])
        r = 0
    except subprocess.CalledProcessError as e:
        r = e.returncode
    print("Return Code:", r)
# MRG TODO: 8-80 bit registers (x87?)
# MRG TODO: 8-64 bit registers that overlap above?
# MRG TODO: 8/16 128-bit SSE regs
