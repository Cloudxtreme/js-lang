
function calc_sum(a, b) {
    return a + b;
};

function sum_numbers(N) {
    sum = 0;
    i = 0;
    while (i < N) {
        sum = calc_sum(sum, i);
        i = i + 1;
    }
    return sum;
};

x = 3000;
x = 30000000;
print(sum_numbers(x));

