#include <stdio.h>
#include <iostream>
#include "omp.h"
#include <time.h>
#include <stdlib.h>
#include <ctime>

//Ejecutar como ./a.out n
//n:Tamaño de Matriz

using namespace std;

int main(int argc, char const *argv[])
{
	int i, j;
	srand(time(NULL));
	int n = atoi(argv[1]);
	int vector__1[n][n], vector__2[n][n], vector__res[n][n];
	for(i = 0; i < n; i++)
	{
		for(j = 0; j < n; j++)
		{
			vector__1[i][j] = (rand()%4)+1;
			vector__2[i][j] = (rand()%4)+1;
		}
	}
	/* vector 1 */
	for(i = 0; i < n; i++)
	{
		for(j = 0; j < n; j++)
		{
			printf("%d ", vector__1[i][j]);
		}
		printf("\n");
	}
	printf("\n");
	/* vector 2 */
	for(i = 0; i < n; i++)
	{
		for(j = 0; j < n; j++)
		{
			printf("%d ", vector__2[i][j]);
		}
		printf("\n");
	}

	printf("\n");

	unsigned t0,t1;	/* realizar la multiplicación en paralelo */

	t0=clock();

	#pragma omp parallel
	{
		int i, j, k, suma = 0;
		#pragma omp for 
		for(i = 0; i < n; i++)
		{
			for(j = 0; j < n; j++)
			{
				for(k = 0; k < n; k++)
				{
					suma += (vector__1[i][k] * vector__2[j][k]);
				}
				vector__res[i][j] = suma;
				suma = 0;
			}
		}
	}

	t1=clock();


	for(i = 0; i < n; i++){
		for(j = 0; j < n; j++){
			printf("%d ", vector__res[i][j]);
		}
		printf("\n");
	}
//	return 0;

	cout<<endl;

	double time = (double(t1-t0)/CLOCKS_PER_SEC);
	cout << "Execution Time: " << time << endl;


}

