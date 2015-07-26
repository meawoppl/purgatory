#include <stdio.h>

void dumpReg(unsigned long a){
	int i;
	for(i=0; i<4; i++){
		printf("%02x ", (a >> (3 - i) * 8) & 0xFF);
	}
	printf("\n");
}
