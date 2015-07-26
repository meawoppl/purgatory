#include <stdio.h>


int dumbCall(int a, int b)
{
	return a + b;
}


int main()
{
	int z1 = 0;

	long z2 = 5;

	int z3 = (int) z2;

	// if(z3)
	// {
	// 	printf("Yes");
	// } else {
	// 	printf("No");
	// }


	int z4 = dumbCall(1, 1);

	return 0;
}

