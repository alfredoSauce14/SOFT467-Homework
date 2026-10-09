// hello1.c: program to be reduced
#include <stdio.h>
int main(int argc, char **argv) {
    int a = 0;
    printf("Hello, World!\n");
    a++;
    a--;
    a+=2;
    a++;
    a--;
    a++;
    if (a >= 3){
      printf("correct\n");
    }
    return 0;

}
