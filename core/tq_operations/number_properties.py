class NumberProperties:
    """
    Analyzes various mathematical properties of numbers.
    """
    
    @staticmethod
    def get_factors(n):
        """Get all factors of a number more efficiently"""
        factors = []
        # Only check up to square root
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                factors.append(i)
                if i != n // i:  # Avoid duplicating square root
                    factors.append(n // i)
        return sorted(factors)
    
    @staticmethod
    def is_prime(n):
        """Check if number is prime"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def get_prime_factors(n):
        """Get prime factorization"""
        factors = []
        d = 2
        while n > 1:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
            if d * d > n:
                if n > 1:
                    factors.append(n)
                break
        return factors
    
    @staticmethod
    def get_prime_index(n):
        """Get the index of a prime number in the sequence of primes"""
        if not NumberProperties.is_prime(n):
            return None
        count = 0
        for i in range(2, n + 1):
            if NumberProperties.is_prime(i):
                count += 1
                if i == n:
                    return count
        return count

    @staticmethod
    def is_polygonal(n):
        """Check if number is triangular, square, pentagonal, etc."""
        results = []
        # Check up to 12-gonal numbers
        for s in range(3, 13):
            # Solve quadratic equation: n = x(2 + (s-2)(x-1))/2
            a = s - 2
            b = 4 - s
            c = -2 * n
            disc = b * b - 4 * a * c
            if disc >= 0:
                x = (-b + disc ** 0.5) / (2 * a)
                if x > 0 and x.is_integer():
                    results.append((s, int(x)))
        return results

    @staticmethod
    def is_centered_polygonal(n):
        """Check if number is centered triangular, square, pentagonal, etc."""
        results = []
        # Check up to 12-gonal centered numbers
        for s in range(3, 13):
            # Solve equation: n = 1 + s(x(x-1))/2
            a = s/2
            b = -s/2
            c = 1 - n
            disc = b * b - 4 * a * c
            if disc >= 0:
                x = (-b + disc ** 0.5) / (2 * a)
                if x > 0 and x.is_integer():
                    results.append((s, int(x)))
        return results

    @staticmethod
    def is_star_number(n):
        """Check if number is a star number and its position.
        Checks for star numbers with 5 to 12 points.
        Formula for k-pointed star: n = k(m-1)m + 1, where m is position
        """
        results = []
        # Check star numbers from 5 to 12 points
        for k in range(5, 13):
            # For a k-pointed star number N:
            # N = km(m-1) + 1
            # km² - km + 1 - N = 0
            # m = (k ± √(k² - 4k(1-N))) / (2k)
            
            discriminant = k*k - 4*k*(1-n)
            if discriminant < 0:
                continue
                
            x1 = (k + (discriminant ** 0.5)) / (2*k)
            x2 = (k - (discriminant ** 0.5)) / (2*k)
            
            # Check if either solution is a positive integer
            if x1 > 0 and x1.is_integer():
                results.append((k, int(x1)))
            if x2 > 0 and x2.is_integer():
                results.append((k, int(x2)))
                
        return results if results else None

    @staticmethod
    def palindrome_iterations(n):
        """Get palindrome iterations and final number"""
        def reverse_and_add(num):
            return num + int(str(num)[::-1])
            
        iterations = 0
        current = n
        while iterations < 100:  # Limit to prevent infinite loops
            if str(current) == str(current)[::-1]:
                return iterations, current
            current = reverse_and_add(current)
            iterations += 1
        return iterations, current

    @staticmethod
    def is_fibonacci(n):
        """Check if number is in Fibonacci sequence and its position"""
        phi = (5 ** 0.5 + 1) / 2
        n5 = 5 * n * n
        if (n5 + 4).is_integer() and int((n5 + 4) ** 0.5) ** 2 == n5 + 4:
            return True
        if (n5 - 4).is_integer() and int((n5 - 4) ** 0.5) ** 2 == n5 - 4:
            return True
        return False

    @staticmethod
    def is_happy(n):
        """Check if number is happy"""
        seen = set()
        while n != 1:
            n = sum(int(i) ** 2 for i in str(n))
            if n in seen:
                return False
            seen.add(n)
        return True

    @staticmethod
    def aliquot_sum(n):
        """Calculate aliquot sum and determine abundance"""
        factors = NumberProperties.get_factors(n)[:-1]  # Exclude n itself
        sum_factors = sum(factors)
        if sum_factors == n:
            return sum_factors, "perfect", 0
        elif sum_factors < n:
            return sum_factors, "deficient", n - sum_factors
        else:
            return sum_factors, "abundant", sum_factors - n

    @staticmethod
    def gcd(a, b):
        """Calculate Greatest Common Divisor"""
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a, b):
        """Calculate Least Common Multiple"""
        return abs(a * b) // NumberProperties.gcd(a, b)

    @staticmethod
    def is_harshad(n):
        """Check if number is Harshad/Niven"""
        digit_sum = sum(int(d) for d in str(n))
        if n % digit_sum == 0:
            return digit_sum, n // digit_sum
        return None

    # Add more properties as needed 