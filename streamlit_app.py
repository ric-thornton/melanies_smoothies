# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import sqlite3  # For escaping special characters in strings

# Write directly to the app
st.title( f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!  
    """)

# Text input for the name on the order
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Query to get the list of fruits from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multi-select for fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),  # Ensure it's in list form
    max_selections=5
)

if ingredients_list:
    # Join the selected fruits into a single string
    ingredients_string = ' '.join(ingredients_list)

    # Escape special characters in name_on_order and ingredients_string
    name_on_order = sqlite3.escape_string(name_on_order)
    ingredients_string = sqlite3.escape_string(ingredients_string)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Dynamically format the SQL query
        insert_query = f"""
            INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        
        # Log the query to debug
        st.write("SQL Query:", insert_query)

        try:
            # Execute the SQL query directly
            session.sql(insert_query).collect()
            # Display success message
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            # Catch and display any errors during query execution
            st.error(f"Error executing the query: {e}")
