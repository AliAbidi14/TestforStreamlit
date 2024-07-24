import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import distance
import pandas as pd
import webbrowser

st.title('SHEFA')
st.subheader('Search for free/low-cost healthcare near you')

DISTANCE_OPTIONS = [5, 10, 25, 50, 100]

def geocode_address(address):
    geolocator = Nominatim(user_agent="syedinamabidi@gmail.com")
    location = geolocator.geocode(address, addressdetails=True, country_codes='US')
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def calculate_distance(coords1, coords2):
    return distance(coords1, coords2).miles

def filter_by_service_type(row, medical, dental, behavioral):
    service_type = row['Service Type'].lower()
    
    if medical and 'medical' in service_type:
        return True
    if dental and 'dental' in service_type:
        return True
    if behavioral and 'behavioral' in service_type:
        return True
    
    return False

def hyperlink(url):
    return f'<a href="{url}" target="_blank">{url}</a>'

def main():
    #st.title("Location Search")
    counter = 0
    # Input section
    user_address = st.text_input("Enter your zip code:")

    distance_limit = st.selectbox("Select distance limit (miles):", DISTANCE_OPTIONS)

    st.markdown("Select service types to search:")
    medical = st.checkbox("Medical")
    dental = st.checkbox("Dental")
    behavioral = st.checkbox("Behavioral Health")

    if st.button("Search"):
        try:
            if not user_address:
                st.error("Please enter an address.")
                return

            user_lat, user_lon = geocode_address(user_address)

            if user_lat is None or user_lon is None:
                st.error(f"Could not geocode address '{user_address}'")
                return

            # Read location coordinates from the CSV file
            csv_file = r'Addresses.csv'  # Replace with your CSV file path
            df = pd.read_csv(csv_file)

            # Initialize an empty list to store matching rows
            matching_rows = []

            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                # Extract latitude and longitude from the row
                lat = row['Latitude']
                lon = row['Longitude']

                # Calculate distance between user's address coordinates and row coordinates
                row_coords = (lat, lon)
                dist = calculate_distance((user_lat, user_lon), row_coords)

                # Check if row matches distance and service type criteria
                if dist <= distance_limit and filter_by_service_type(row, medical, dental, behavioral):
                    matching_rows.append(row)
                    counter += 1

            # Display the matching rows
            if matching_rows:
                st.markdown(f"{counter} locations within {distance_limit} miles of your address '{user_address}' for selected service types:")
                st.write('\n')
                for row in matching_rows:
                    for col in df.columns:
                        if col == 'Website':
                            url = row[col]
                            st.write(f"{col}: {hyperlink(url)}", unsafe_allow_html=True)
                        elif col not in ['Latitude', 'Longitude']:
                            st.write(f"{col}: {row[col]}")
                    st.write("-" * 30)
            else:
                st.write(f"No locations found within {distance_limit} miles of your address '{user_address}' for selected service types.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
