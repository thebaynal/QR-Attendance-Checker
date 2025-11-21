# basic_calculator.py
# CCCS 106 - Week 1 Lab Exercise
# Simple Interactive Calculator

print("=" * 40)
print("BASIC CALCULATOR")
print("=" * 40)

# Get user input
print("Enter two numbers for calculation:")
try:
    num1 = float(input("First number: "))
    num2 = float(input("Second number: "))
    
    # Perform calculations
    addition = num1 + num2
    subtraction = num1 - num2
    multiplication = num1 * num2
    
    # Handle division by zero
    if num2 != 0:
        division = num1 / num2
    else:
        division = "Cannot divide by zero"
    
    # Display results
    print("\n" + "=" * 40)
    print("RESULTS:")
    print("=" * 40)
    print(f"{num1} + {num2} = {addition}")
    print(f"{num1} - {num2} = {subtraction}")
    print(f"{num1} * {num2} = {multiplication}")
    print(f"{num1} / {num2} = {division}")
    
    # Additional information
    print(f"\nLarger number: {max(num1, num2)}")
    print(f"Smaller number: {min(num1, num2)}")
    
except ValueError:
    print("Error: Please enter valid numbers only!")
except Exception as e:
    print(f"An error occurred: {e}")

print("\nThank you for using Basic Calculator!")