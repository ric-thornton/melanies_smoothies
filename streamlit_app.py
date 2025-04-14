# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Helper function to escape single quotes for safe SQL
def escape_sql(value):
    if value is None:
        return ''
    return value.replace("'", "''")

# App title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input field for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load available fruits from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert to list for use in multiselect
fruit_options = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()

# Let the user select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# Handle form submission
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    
    # Show submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Escape inputs for SQL safety
        safe_ingredients = escape_sql(ingredients_string)
        safe_name = escape_sql(name_on_order)

        # Prepare the SQL query
        insert_query = f"""
            INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
            VALUES ('{safe_ingredients}', '{safe_name}')
        """

        # Optional: show query for debugging (can be removed in prod)
        # st.write("Running SQL:", insert_query)

        try:
            session.sql(insert_query).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Order failed: {e}")

