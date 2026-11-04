#include <stdio.h>

int main() {
    int a = 10;
    int b = 20;
    int c = a @ b;      // erro léxico: @ não é permitido em C
    int d = 5 $ 2;      // erro léxico: $ não é permitido em C

    printf("Resultado: %d\\n", c);
    return 0;
}
