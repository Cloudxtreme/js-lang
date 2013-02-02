function sum_numbers(N) {
    sum = 0;
    i = 0;
    while (i < N) {
        sum = sum + i;
        i = i + 1;
    }
    return sum;
};

print(sum_numbers(7000000));

