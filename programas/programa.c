#include <stdio.h>
int soma(int x, int y);

int main() {
    int a = 5;
    int b = 10;

    int result = soma(a, b);

    printf("%d\n", result);

    return 0;
}

int soma(int x, int y) {
    return x + y;
}
