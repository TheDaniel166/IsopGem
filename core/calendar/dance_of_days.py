from datetime import date, timedelta

class DanceOfDays:
    """
    Calculates Dance of Days cycles (260-day) from March 20, 1904
    """
    EPOCH = date(1904, 3, 20)  # Starting date of the first cycle
    CYCLE_LENGTH = 260
    
    @classmethod
    def get_cycle_info(cls, target_date):
        """
        Calculate cycle information for a given date
        Returns: (cycle_number, day_in_cycle)
        - cycle_number: which cycle (can be negative for dates before epoch)
        - day_in_cycle: position in current cycle (1-260)
        """
        days_from_epoch = (target_date - cls.EPOCH).days
        
        if days_from_epoch >= 0:
            # For dates on or after epoch
            cycle_number = days_from_epoch // cls.CYCLE_LENGTH
            day_in_cycle = (days_from_epoch % cls.CYCLE_LENGTH) + 1
        else:
            # For dates before epoch
            cycle_number = -1 - ((-days_from_epoch - 1) // cls.CYCLE_LENGTH)
            day_in_cycle = cls.CYCLE_LENGTH - ((-days_from_epoch - 1) % cls.CYCLE_LENGTH)
            
        return (cycle_number, day_in_cycle)
    
    @classmethod
    def validate_calculation(cls, test_date):
        """Debug method to validate calculations"""
        days_from_epoch = (test_date - cls.EPOCH).days
        cycle_info = cls.get_cycle_info(test_date)
        print(f"Date: {test_date}")
        print(f"Days from epoch: {days_from_epoch}")
        print(f"Cycle info: {cycle_info}")
        print(f"Verification: {cycle_info[0]} cycles = {cycle_info[0] * cls.CYCLE_LENGTH} days")
        print(f"Plus {cycle_info[1]} days = {cycle_info[0] * cls.CYCLE_LENGTH + cycle_info[1]} total days") 