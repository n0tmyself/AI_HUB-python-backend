import math
from typing import List

def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    return math.factorial(n)

def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    
    a, b = 0, 1
    for _ in range(n):
         a, b = b, a + b
    
    return b

def mean(data: List[int] | List[float]) -> float:
    if not data:
        raise ValueError("Input list cannot be empty")
    return sum(data) / len(data)