function sum_numbers(N) {
    sum = 0;
    i = 0;
    while (i < N) {
        if (i < N / 2) {
            sum = sum + i;
        }
        i = i + 1;
    }
    return sum;
};


function sum_numbers_bridge(N) {
    sum = 0;
    i = 0;
    while (i < N) {
        if (i % 3) {
            sum = sum + i;
        }
        i = i + 1;
    }
    return sum;
};


function sum_numbers_bridge_2(N) {
    sum = 0;
    i = 0;
    while (i < N) {
        if (i < N / 2) {
            sum = sum + i;
        }
        i = i + 1;
    }
    return sum;
};


x = 3000;
x = 30000000;
print(sum_numbers_bridge(x));

