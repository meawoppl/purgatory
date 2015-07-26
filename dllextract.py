import os
from io import BytesIO
import struct
from collections import OrderedDict, namedtuple

printBar = lambda : print("=" * 80)

def hexDump(flo):
	startOffset = flo.tell()
	bio = BytesIO(flo.read())
	flo.seek(startOffset)

	readBytes = 0
	printBar()

	breaks = 16
	while True:
		offset = startOffset + readBytes
		if (offset % breaks) == 0:
			print("\n%0.04i " % offset, end="")

		seg = bio.read(1)
		if len(seg) == 0:
			break

		inted = struct.unpack("B", seg)

		print("%0.02x " % inted, end="")
		if len(seg) < 1:
			break
		readBytes += len(seg)

		if offset > 100:
			break

	print()
	printBar()

class StructExtract:
	def __init__(self, nameOfStruct):
		self.n = nameOfStruct
		self.d = OrderedDict()

	def addField(self, fmt, name, count=1):
		self.d[name] = fmt, count

	def structSize(self):
		size = 0
		for fmt, cnt in self.d.values():
			if type(fmt) is str:
				size += struct.calcsize(fmt * cnt)
			elif type(fmt) is StructExtract:
				size += fmt.structSize() * cnt

		return size

	def readFromFLO(self, flo):
		units = []
		for fmt, cnt in self.d.values():
			if type(fmt) is str:
				fstr = fmt * cnt
				unitSize = struct.calcsize(fstr)
				bytez = flo.read(unitSize)
				vals = struct.unpack(fstr, bytez)
			elif type(fmt) is StructExtract:
				vals = [fmt.readFromFLO(flo) for _ in range(cnt)]
			else:
				raise RuntimeError("Derp")

			if len(vals) == 1:
				units.append(vals[0])
			else:
				units.append(vals)

		nt = namedtuple(self.n, self.d.keys())
		return nt(*units)


ms_dos_header = StructExtract("MSDOS_Header")
ms_dos_header.addField("H", "e_magic")
ms_dos_header.addField("H", "e_cblp")
ms_dos_header.addField("H", "e_cp")
ms_dos_header.addField("H", "e_crlc")
ms_dos_header.addField("H", "e_cparhdr")
ms_dos_header.addField("H", "e_minalloc")
ms_dos_header.addField("H", "e_maxalloc")
ms_dos_header.addField("H", "e_ss")
ms_dos_header.addField("H", "e_sp")
ms_dos_header.addField("H", "e_csum")
ms_dos_header.addField("H", "e_ip")
ms_dos_header.addField("H", "e_cs")
ms_dos_header.addField("H", "e_lfarlc")
ms_dos_header.addField("H", "e_ovno")
ms_dos_header.addField("H", "e_res", count=4)
ms_dos_header.addField("H", "e_oemid")
ms_dos_header.addField("H", "e_oeminfo")
ms_dos_header.addField("H", "e_res2", count=10)
ms_dos_header.addField("I", "e_lfanew")

print("MSDDOS Header size computed to be:", ms_dos_header.structSize())

image_file_header = StructExtract("IMAGE_FILE_HEADER")
image_file_header.addField("H", "Machine")
image_file_header.addField("H", "NumberOfSections")
image_file_header.addField("I", "TimeDateStamp")
image_file_header.addField("I", "PointerToSymbolTable")
image_file_header.addField("I", "NumberOfSymbols")
image_file_header.addField("H", "SizeOfOptionalHeader")
image_file_header.addField("H", "Characteristics")

image_section_header = StructExtract("IMAGE_SECTION_HEADER")
image_section_header.addField("8s", "Name")
image_section_header.addField("I", "Misc")
image_section_header.addField("I", "VirtualAddress")
image_section_header.addField("I", "SizeOfRawData")
image_section_header.addField("I", "PointerToRawData")
image_section_header.addField("I", "PointerToRelocations")
image_section_header.addField("I", "PointerToLinenumbers")
image_section_header.addField("H", "NumberOfRelocations")
image_section_header.addField("H", "NumberOfLinenumbers")
image_section_header.addField("I", "Characteristics")

image_data_directory = StructExtract("IMAGE_DATA_DIRECTORY")
image_data_directory.addField("I", "VirtualAddress")
image_data_directory.addField("I", "Size")

image_optional_header32 = StructExtract("IMAGE_OPTIONAL_HEADER32")
image_optional_header32.addField("H", "Magic")
image_optional_header32.addField("B", "MajorLinkerVersion")
image_optional_header32.addField("B", "MinorLinkerVersion")
image_optional_header32.addField("I", "SizeOfCode")
image_optional_header32.addField("I", "SizeOfInitializedData")
image_optional_header32.addField("I", "SizeOfUninitializedData")
image_optional_header32.addField("I", "AddressOfEntryPoint")
image_optional_header32.addField("I", "BaseOfCode")
image_optional_header32.addField("I", "BaseOfData")
image_optional_header32.addField("I", "ImageBase")
image_optional_header32.addField("I", "SectionAlignment")
image_optional_header32.addField("I", "FileAlignment")
image_optional_header32.addField("H", "MajorOperatingSystemVersion")
image_optional_header32.addField("H", "MinorOperatingSystemVersion")
image_optional_header32.addField("H", "MajorImageVersion")
image_optional_header32.addField("H", "MinorImageVersion")
image_optional_header32.addField("H", "MajorSubsystemVersion")
image_optional_header32.addField("H", "MinorSubsystemVersion")
image_optional_header32.addField("I", "Win32VersionValue")
image_optional_header32.addField("I", "SizeOfImage")
image_optional_header32.addField("I", "SizeOfHeaders")
image_optional_header32.addField("I", "CheckSum")
image_optional_header32.addField("H", "Subsystem")
image_optional_header32.addField("H", "DllCharacteristics")
image_optional_header32.addField("I", "SizeOfStackReserve")
image_optional_header32.addField("I", "SizeOfStackCommit")
image_optional_header32.addField("I", "SizeOfHeapReserve")
image_optional_header32.addField("I", "SizeOfHeapCommit")
image_optional_header32.addField("I", "LoaderFlags")
image_optional_header32.addField("I", "NumberOfRvaAndSizes")
image_optional_header32.addField(image_data_directory, "DataDirectory", count=16)

image_optional_header64 = StructExtract("IMAGE_OPTIONAL_HEADER64")
image_optional_header64.addField("H", "Magic")
image_optional_header64.addField("B", "MajorLinkerVersion")
image_optional_header64.addField("B", "MinorLinkerVersion")
image_optional_header64.addField("I", "SizeOfCode")
image_optional_header64.addField("I", "SizeOfInitializedData")
image_optional_header64.addField("I", "SizeOfUninitializedData")
image_optional_header64.addField("I", "AddressOfEntryPoint")
image_optional_header64.addField("I", "BaseOfCode")
image_optional_header64.addField("Q", "ImageBase")
image_optional_header64.addField("I", "SectionAlignment")
image_optional_header64.addField("I", "FileAlignment")
image_optional_header64.addField("H", "MajorOperatingSystemVersion")
image_optional_header64.addField("H", "MinorOperatingSystemVersion")
image_optional_header64.addField("H", "MajorImageVersion")
image_optional_header64.addField("H", "MinorImageVersion")
image_optional_header64.addField("H", "MajorSubsystemVersion")
image_optional_header64.addField("H", "MinorSubsystemVersion")
image_optional_header64.addField("I", "Win32VersionValue")
image_optional_header64.addField("I", "SizeOfImage")
image_optional_header64.addField("I", "SizeOfHeaders")
image_optional_header64.addField("I", "CheckSum")
image_optional_header64.addField("H", "Subsystem")
image_optional_header64.addField("H", "DllCharacteristics")
image_optional_header64.addField("I", "SizeOfStackReserve")
image_optional_header64.addField("I", "SizeOfStackCommit")
image_optional_header64.addField("I", "SizeOfHeapReserve")
image_optional_header64.addField("I", "SizeOfHeapCommit")
image_optional_header64.addField("I", "LoaderFlags")
image_optional_header64.addField("I", "NumberOfRvaAndSizes")
image_optional_header64.addField(image_data_directory, "DataDirectory", count=16)


print("32", image_optional_header32.structSize())
print("64", image_optional_header64.structSize())

image_export_directory = StructExtract("IMAGE_EXPORT_DIRECTORY")
image_export_directory.addField("I", "Characteristics")
image_export_directory.addField("I", "TimeDateStamp")
image_export_directory.addField("H", "MajorVersion")
image_export_directory.addField("H", "MinorVersion")
image_export_directory.addField("I", "Name")
image_export_directory.addField("I", "Base")
image_export_directory.addField("I", "NumberOfFunctions")
image_export_directory.addField("I", "NumberOfNames")
image_export_directory.addField("I", "AddressOfFunctions")
image_export_directory.addField("I", "AddressOfNames")
image_export_directory.addField("I", "AddressOfNameOrdinals")



def readNTHeader(flo):
	startOffset = flo.tell()
	image_nt_headers = StructExtract("IMAGE_NT_HEADERS")
	image_nt_headers.addField("4s", "Signature") # Actully DWORD, but this makes checking easier
	image_nt_headers.addField(image_file_header, "FileHeader")

	# Read the next two bytes to compute the "magic"
	flo.seek(startOffset + image_nt_headers.structSize())
	magic = struct.unpack("H", flo.read(2))[0]
	decoder = {0x10b: image_optional_header32, 0x20b: image_optional_header64}[magic]
	flo.seek(startOffset)

	# Use that magic to determin which header formatting to use, and read it
	image_nt_headers.addField(decoder, "OptionalHeader")	
	return image_nt_headers.readFromFLO(flo)


def imageCharacteristicsDecode(char):
	sectionHeaderFlags = {"CODE": 0x20, "IDATA": 0x40, "UDATA": 0x80,
	                      "NOCACHE": 0x04000000, "NOPAGE": 0x08000000,
	                      "SHARED": 0x10000000, "EXE": 0x20000000,
	                      "READ": 0x40000000, "WRITE": 0x80000000}	
	tags = []
	for k, v in sorted(sectionHeaderFlags.items()):
		if char & v:
			tags.append(k)

	return " ".join(tags)

def analyzeExports(flo, imageSectionHeader):
	# Jump to my syection header
	sectionAddress = imageSectionHeader.PointerToRawData
	flo.seek(sectionAddress)
	offsetAddress = imageSectionHeader.VirtualAddress - sectionAddress

	vaToFA = lambda va: va - offsetAddress

	ied = image_export_directory.readFromFLO(flo)

	print("     >Exports Details: %i functions %i names" % (ied.NumberOfFunctions, ied.NumberOfNames))
	# print(ied.AddressOfNames)
	# print(ied.AddressOfFunctions)

	fileAddress = vaToFA(ied.AddressOfNames)
	flo.seek(fileAddress)

	stringStarts = []
	for i in range(ied.NumberOfNames):
		stringPtr = struct.unpack("I", flo.read(4))[0]
		fa = vaToFA(stringPtr)
		stringStarts.append(fa)

	names = []
	for startOffset in stringStarts:
		flo.seek(startOffset)

		n = b""
		while True:
		 	n += flo.read(1)
		 	if n[-1] == 0:
		 		break

		names.append(n[:-1].decode("ascii"))


	for idee, name in enumerate(names):
		functionAddressAddress = vaToFA(ied.AddressOfFunctions + (4*idee))
		flo.seek(functionAddressAddress)
		adr = struct.unpack("I", flo.read(4))[0]
		print("      > " + name, adr)




	1/0

def extractDLL(pathToDLL):	
	# Open the file
	f = open(pathToDLL, "rb")

	# Skip over the msdos header
	msdosHeader = ms_dos_header.readFromFLO(f)
	dosHeaderEnd = msdosHeader.e_lfanew
	f.seek(dosHeaderEnd)

	# Read the "optional" header
	inth = readNTHeader(f)
	assert inth.Signature == b"PE\x00\x00", "NT Header Magic (Should be PE00)"

	print(inth.Signature)

	sectionCount = inth.FileHeader.NumberOfSections

	sectionNames = []
	print("Sections:")
	print("=========")
	for sectionHeaderNumber in range(sectionCount):
		imageSection = image_section_header.readFromFLO(f)
		sectionName = imageSection.Name.decode("ascii")
		print(sectionName)
		print("   > Start: ", imageSection.PointerToRawData)
		print("   > Size: ", imageSection.SizeOfRawData)
		print("   > Virtual Address", imageSection.VirtualAddress)
		print("   > Flags: " + imageCharacteristicsDecode(imageSection.Characteristics))

		if sectionName.startswith(".edata"):
			cursor = f.tell()
			analyzeExports(f, imageSection)
			f.seek(cursor)

		sectionNames.append(sectionName)
	return sectionNames




print("Scanning Program Files:")
files = []
sectionAccure = []
folder = "/media/meawoppl/Blade/Program Files (x86)/"
for root, dirs, fis in os.walk(folder):
	for f in fis:
		if f.endswith(".dll"):
			fullPath = os.path.join(folder, root, f)
			if os.path.islink(fullPath):
				continue
			files.append(fullPath)

print("%i dll's found" % len(files))


for n, fPath in enumerate(files):
	print()
	print("*" * 77)
	print(fPath)
	print("*" * 77)
	print()
	sectionAccure += extractDLL(fPath)
	# if n > 5:
	# 	break
