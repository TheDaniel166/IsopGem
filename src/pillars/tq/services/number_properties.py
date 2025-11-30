"""Service for calculating number properties."""
import math
from typing import List, Dict, Tuple

class NumberPropertiesService:
    """Service for calculating comprehensive number properties."""
    
    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if a number is prime."""
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    @staticmethod
    def get_factors(n: int) -> List[int]:
        """Get all factors of a number."""
        if n == 0:
            return []
        n = abs(n)
        factors = set()
        for i in range(1, int(math.sqrt(n)) + 1):
            if n % i == 0:
                factors.add(i)
                factors.add(n // i)
        return sorted(list(factors))

    @staticmethod
    def get_prime_factorization(n: int) -> List[Tuple[int, int]]:
        """
        Get prime factorization.
        Returns list of (prime, exponent) tuples.
        e.g. 12 -> [(2, 2), (3, 1)]
        """
        if n == 0:
            return []
        n = abs(n)
        factors = []
        d = 2
        temp = n
        while d * d <= temp:
            if temp % d == 0:
                count = 0
                while temp % d == 0:
                    count += 1
                    temp //= d
                factors.append((d, count))
            d += 1
        if temp > 1:
            factors.append((temp, 1))
        return factors

    @staticmethod
    def is_square(n: int) -> bool:
        """Check if number is a perfect square."""
        if n < 0:
            return False
        if n == 0:
            return True
        sqrt = int(math.sqrt(n))
        return sqrt * sqrt == n

    @staticmethod
    def is_cube(n: int) -> bool:
        """Check if number is a perfect cube."""
        if n == 0:
            return True
        cube_root = int(round(abs(n) ** (1/3)))
        return cube_root ** 3 == abs(n)

    @staticmethod
    def is_fibonacci(n: int) -> bool:
        """Check if number is in Fibonacci sequence."""
        # A number is Fibonacci if 5*n^2 + 4 or 5*n^2 - 4 is a perfect square
        if n < 0:
            return False
        x = 5 * n * n
        return NumberPropertiesService.is_square(x + 4) or NumberPropertiesService.is_square(x - 4)

    @staticmethod
    def digit_sum(n: int) -> int:
        """Calculate sum of decimal digits."""
        return sum(int(d) for d in str(abs(n)))

    @staticmethod
    def get_prime_ordinal(n: int) -> int:
        """
        Get the 1-based index of a prime number.
        Returns 0 if not prime or calculation too expensive.
        """
        if not NumberPropertiesService.is_prime(n):
            return 0
        
        # For small numbers, simple counting is fine
        if n < 2:
            return 0
            
        # Simple sieve for reasonable range
        # If n is very large, this will be slow. 
        # Assuming typical gematria usage < 1,000,000
        if n > 1000000:
            return -1 # Indicate too large to calculate quickly
            
        count = 0
        # Sieve of Eratosthenes up to n
        sieve = [True] * (n + 1)
        sieve[0] = sieve[1] = False
        
        for p in range(2, n + 1):
            if sieve[p]:
                count += 1
                if p == n:
                    return count
                for i in range(p * p, n + 1, p):
                    sieve[i] = False
        return count

    @staticmethod
    def get_polygonal_info(n: int) -> List[str]:
        """Check for polygonal numbers (3 to 12 sides)."""
        if n < 1:
            return []
            
        results = []
        # Formula for s-gonal number P(s,n) = ((s-2)n^2 - (s-4)n)/2
        # Solving for n: n = ((s-4) + sqrt((s-4)^2 + 8x(s-2))) / (2(s-2))
        
        polygons = {
            3: "Triangle", 4: "Square", 5: "Pentagonal", 6: "Hexagonal",
            7: "Heptagonal", 8: "Octagonal", 9: "Nonagonal", 10: "Decagonal",
            11: "Hendecagonal", 12: "Dodecagonal"
        }
        
        for s, name in polygons.items():
            # Calculate discriminant part: (s-4)^2 + 8n(s-2)
            discriminant = (s - 4)**2 + 8 * n * (s - 2)
            sqrt_disc = int(math.isqrt(discriminant))
            
            if sqrt_disc * sqrt_disc == discriminant:
                numerator = (s - 4) + sqrt_disc
                denominator = 2 * (s - 2)
                
                if numerator % denominator == 0:
                    index = numerator // denominator
                    results.append(f"{name} (Index: {index})")
                    
        return results

    @staticmethod
    def get_centered_polygonal_info(n: int) -> List[str]:
        """Check for centered polygonal numbers (3 to 12 sides)."""
        if n == 1:
            return ["Centered (All) (Index: 1)"]
        if n < 1:
            return []
            
        results = []
        # Formula: C(k,n) = (kn(n-1))/2 + 1
        # Solving for n: n = (k + sqrt(k^2 - 8k + 8kx)) / 2k
        # where x is the number being checked
        
        polygons = {
            3: "Centered Triangle", 4: "Centered Square", 5: "Centered Pentagonal", 
            6: "Centered Hexagonal", 7: "Centered Heptagonal", 8: "Centered Octagonal", 
            9: "Centered Nonagonal", 10: "Centered Decagonal"
        }
        
        for k, name in polygons.items():
            # Discriminant: k^2 - 8k + 8kn
            # = k^2 + 8k(n-1)
            discriminant = k**2 + 8 * k * (n - 1)
            sqrt_disc = int(math.isqrt(discriminant))
            
            if sqrt_disc * sqrt_disc == discriminant:
                numerator = k + sqrt_disc
                denominator = 2 * k
                
                if numerator % denominator == 0:
                    index = numerator // denominator
                    results.append(f"{name} (Index: {index})")
                    
        return results

    @staticmethod
    def get_properties(n: int) -> Dict:
        """Get a dictionary of all properties."""
        factors = NumberPropertiesService.get_factors(n)
        # Aliquot sum is sum of proper divisors (exclude n itself)
        # Factors list includes n, so subtract it
        sum_factors = sum(factors)
        aliquot_sum = sum_factors - abs(n) if n != 0 else 0
        
        abundance_status = "Perfect"
        abundance_diff = 0
        
        if aliquot_sum < abs(n):
            abundance_status = "Deficient"
            abundance_diff = abs(n) - aliquot_sum
        elif aliquot_sum > abs(n):
            abundance_status = "Abundant"
            abundance_diff = aliquot_sum - abs(n)
            
        props = {
            "is_prime": NumberPropertiesService.is_prime(n),
            "prime_ordinal": NumberPropertiesService.get_prime_ordinal(n) if n > 0 else 0,
            "is_square": NumberPropertiesService.is_square(n),
            "is_cube": NumberPropertiesService.is_cube(n),
            "is_fibonacci": NumberPropertiesService.is_fibonacci(n),
            "digit_sum": NumberPropertiesService.digit_sum(n),
            "factors": factors,
            "sum_factors": sum_factors,
            "aliquot_sum": aliquot_sum,
            "abundance_status": abundance_status,
            "abundance_diff": abundance_diff,
            "prime_factors": NumberPropertiesService.get_prime_factorization(n),
            "polygonal_info": NumberPropertiesService.get_polygonal_info(n),
            "centered_polygonal_info": NumberPropertiesService.get_centered_polygonal_info(n)
        }
        return props
