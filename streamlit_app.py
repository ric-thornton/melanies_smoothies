# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Escape single quotes for safe SQL strings
def escape_sql(value):
    if value is None:
        return ''
    return value.replace("'", "''")

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Escape inputs
        safe_ingredients = escape_sql(ingredients_string)
        safe_name = escape_sql(name_on_order)

        insert_query = f"""
            INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
            VALUES ('{safe_ingredients}', '{safe_name}')
        """

        st.write("Running SQL:", insert_query)  # Optional debug output

        try:
            session.sql(insert_query).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Order failed: {e}")
