#include <stdio.h>

int main() {
    // 1. Erro semântico de tipo: atribuindo texto (string) a uma variável inteira
    int idade = "oi"; 

    float nota1 = 8.0;
    float nota2 = 6.0;
    float media;

    // 2. Erro semântico de lógica: falta de parênteses altera o resultado esperado
    media = nota1 + nota2 / 2;

    printf("A media final e: %.2f\n", media);

    return 0;
}
