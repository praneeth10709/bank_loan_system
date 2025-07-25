def calculate_interest_and_emi(principal, years, rate):
    interest = (principal * years * rate) / 100
    total = principal + interest
    emi = round(total / (years * 12), 2)
    return interest, total, emi
