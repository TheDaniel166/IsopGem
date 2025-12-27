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
    def _sum_of_digit_squares(n: int) -> int:
        """Calculate sum of squares of digits."""
        return sum(int(d) ** 2 for d in str(abs(n)))

    @staticmethod
    def is_happy(n: int) -> bool:
        """
        Check if number is a Happy number.
        A Happy number reaches 1 after repeated sum of digit squares.
        """
        if n < 1:
            return False
        seen = set()
        current = n
        while current != 1 and current not in seen:
            seen.add(current)
            current = NumberPropertiesService._sum_of_digit_squares(current)
        return current == 1

    @staticmethod
    def get_happy_iterations(n: int) -> int:
        """
        Get the number of iterations to reach 1 for a Happy number.
        Returns -1 if the number is Sad (enters a cycle).
        """
        if n < 1:
            return -1
        seen = set()
        current = n
        iterations = 0
        while current != 1 and current not in seen:
            seen.add(current)
            current = NumberPropertiesService._sum_of_digit_squares(current)
            iterations += 1
        if current == 1:
            return iterations
        return -1  # Sad number (entered a cycle)

    @staticmethod
    def get_happy_chain(n: int) -> list:
        """
        Get the chain of numbers from n until reaching 1 or entering a cycle.
        Returns a list of numbers in the sequence.
        """
        if n < 1:
            return []
        seen = set()
        chain = [n]
        current = n
        while current != 1 and current not in seen:
            seen.add(current)
            current = NumberPropertiesService._sum_of_digit_squares(current)
            chain.append(current)
        return chain

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
            9: "Centered Nonagonal", 10: "Centered Decagonal",
            11: "Centered Hendecagonal", 12: "Star Number (Centered Dodecagonal)"
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
    def is_pronic(n: int) -> bool:
        """Check if n is a pronic number (n = k*(k+1) for some k)."""
        if n < 0:
            return False
        if n == 0:
            return True  # 0 = 0*1
        # Solve k^2 + k - n = 0 using quadratic formula
        # k = (-1 + sqrt(1 + 4n)) / 2
        discriminant = 1 + 4 * n
        sqrt_disc = int(math.isqrt(discriminant))
        if sqrt_disc * sqrt_disc != discriminant:
            return False
        k = (-1 + sqrt_disc) // 2
        return k * (k + 1) == n

    @staticmethod
    def get_pronic_index(n: int) -> int:
        """Get the index k if n is pronic (n = k*(k+1)), else return -1."""
        if n < 0:
            return -1
        if n == 0:
            return 0
        discriminant = 1 + 4 * n
        sqrt_disc = int(math.isqrt(discriminant))
        if sqrt_disc * sqrt_disc != discriminant:
            return -1
        k = (-1 + sqrt_disc) // 2
        if k * (k + 1) == n:
            return k
        return -1

    @staticmethod
    def get_figurate_3d_info(n: int) -> List[str]:
        """Check for 3D figurate numbers: tetrahedral, square pyramidal, octahedral, cubic."""
        if n < 1:
            return []
            
        results = []
        
        # Tetrahedral: T(k) = k(k+1)(k+2)/6
        max_k = int((6 * n) ** (1/3)) + 2
        for k in range(1, max_k + 1):
            val = k * (k + 1) * (k + 2) // 6
            if val == n:
                results.append(f"Tetrahedral (Index: {k})")
                break
            if val > n:
                break
        
        # Square Pyramidal: P(k) = k(k+1)(2k+1)/6
        for k in range(1, max_k + 1):
            val = k * (k + 1) * (2 * k + 1) // 6
            if val == n:
                results.append(f"Square Pyramidal (Index: {k})")
                break
            if val > n:
                break
        
        # Octahedral: O(k) = k(2k^2 + 1)/3
        for k in range(1, max_k + 1):
            val = k * (2 * k * k + 1) // 3
            if val == n:
                results.append(f"Octahedral (Index: {k})")
                break
            if val > n:
                break
        
        # Cubic (perfect cube): C(k) = k^3
        cube_root = int(round(n ** (1/3)))
        for k in [cube_root - 1, cube_root, cube_root + 1]:
            if k > 0 and k ** 3 == n:
                results.append(f"Cubic (Index: {k})")
                break
                
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
            "is_pronic": NumberPropertiesService.is_pronic(n),
            "pronic_index": NumberPropertiesService.get_pronic_index(n),
            "is_happy": NumberPropertiesService.is_happy(n),
            "happy_iterations": NumberPropertiesService.get_happy_iterations(n),
            "happy_chain": NumberPropertiesService.get_happy_chain(n),
            "digit_sum": NumberPropertiesService.digit_sum(n),
            "factors": factors,
            "sum_factors": sum_factors,
            "aliquot_sum": aliquot_sum,
            "abundance_status": abundance_status,
            "abundance_diff": abundance_diff,
            "prime_factors": NumberPropertiesService.get_prime_factorization(n),
            "polygonal_info": NumberPropertiesService.get_polygonal_info(n),
            "centered_polygonal_info": NumberPropertiesService.get_centered_polygonal_info(n),
            "figurate_3d_info": NumberPropertiesService.get_figurate_3d_info(n)
        }
        return props
