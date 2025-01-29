class Transitions:
    """
    Handles various types of transitions between ternary digits.
    """
    
    @staticmethod
    def get_pair_transition(digit1, digit2):
        """
        Determine the transition value for a pair of digits according to the rules:
        
        Returns 0 if:
        - 0,0
        - 1,2
        - 2,1
        
        Returns 1 if:
        - 1,1
        - 0,2
        - 2,0
        
        Returns 2 if:
        - 2,2
        - 0,1
        - 1,0
        """
        transitions = {
            (0,0): '0',
            (1,2): '0',
            (2,1): '0',
            (1,1): '1',
            (0,2): '1',
            (2,0): '1',
            (2,2): '2',
            (0,1): '2',
            (1,0): '2'
        }
        return transitions.get((digit1, digit2), '')

    @staticmethod
    def get_pair_transitions(ternary1, ternary2):
        """
        Get transitions between corresponding digits of two ternary numbers.
        
        Args:
            ternary1 (str): First ternary number
            ternary2 (str): Second ternary number
            
        Returns:
            tuple: (transition_ternary, transition_decimal)
                  transition_ternary is a string of transition digits
                  transition_decimal is the decimal value of the transition
        """
        # Convert to list of integers
        digits1 = [int(d) for d in ternary1]
        digits2 = [int(d) for d in ternary2]
        
        # Get transitions between corresponding digits
        transitions = []
        for d1, d2 in zip(digits1, digits2):
            transition = Transitions.get_pair_transition(d1, d2)
            transitions.append(transition)
            
        transition_ternary = ''.join(transitions)
        
        # Convert transition to decimal
        transition_decimal = sum(int(d) * (3 ** i) for i, d in enumerate(reversed(transition_ternary)))
        
        return transition_ternary, transition_decimal 