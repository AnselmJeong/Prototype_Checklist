# filename: calculate_ytd_gain.py

# Replace these variables with the actual prices
beginning_of_year_price_meta = 0  # Replace 0 with the actual price for META at the beginning of the year
current_price_meta = 0  # Replace 0 with the current price for META

beginning_of_year_price_tesla = 0  # Replace 0 with the actual price for TESLA at the beginning of the year
current_price_tesla = 0  # Replace 0 with the current price for TESLA

# Ensure that the beginning of year prices are not zero to avoid division by zero
if beginning_of_year_price_meta == 0 or beginning_of_year_price_tesla == 0:
    print("Please make sure the beginning of year prices are not zero.")
else:
    # Calculate YTD gain for META
    ytd_gain_meta = ((current_price_meta - beginning_of_year_price_meta) / beginning_of_year_price_meta) * 100

    # Calculate YTD gain for TESLA
    ytd_gain_tesla = ((current_price_tesla - beginning_of_year_price_tesla) / beginning_of_year_price_tesla) * 100

    # Print the YTD gains
    print(f"META YTD Gain: {ytd_gain_meta:.2f}%")
    print(f"TESLA YTD Gain: {ytd_gain_tesla:.2f}%")