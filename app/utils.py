# app/utils.py - Utility functions for the app

def calculate_bill(default_km, extra_km):
    """
    Calculate the bill amount based on kilometers driven.
    
    Args:
        default_km (float): Default kilometers driven in a month
        extra_km (float): Extra kilometers driven in a month
        
    Returns:
        float: Calculated bill amount
    """
    # Sample rate calculation (can be adjusted as needed)
    DEFAULT_RATE = 2.50  # $2.50 per default km
    EXTRA_RATE = 3.75   # $3.75 per extra km
    BASE_FEE = 15.00    # $15 base fee per month
    
    # Calculate the bill
    default_charge = default_km * DEFAULT_RATE
    extra_charge = extra_km * EXTRA_RATE
    total = BASE_FEE + default_charge + extra_charge
    
    return round(total, 2)