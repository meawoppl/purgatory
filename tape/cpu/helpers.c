#include <stdio.h>

void printSpace()
{
	printf(" ");
}

void printNewline()
{
	printf("\n");
}

void dumpByte(unsigned char a){
	printf("%02x", a);
}

void dumpReg(unsigned long *a){
	unsigned long r = *a;
	int i;
	for(i=3; i>=0; i--){
		unsigned char b = (r >> (i * 8)) & 0xFF;
		dumpByte(b);

		if(i != 0)
			printSpace();
	}
	printNewline();
}
