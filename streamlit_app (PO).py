# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title("Pending Smoothie Orders")
st.write("Orders that need to be filled.")

# Get the current Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Load unfilled smoothie orders
my_dataframe = session.table("smoothies.public.orders") \
    .filter(col("ORDER_FILLED") == False) \
    .select(
        col("ORDER_FILLED"),
        col("ORDER_UID"),
        col("NAME_ON_ORDER"),
        col("INGREDIENTS"),
        col("ORDER_TS")
    )

# Show the table if not empty
if my_dataframe.count() > 0:
    editable_df = st.data_editor(my_dataframe, use_container_width=True)
    
    if st.button("Submit"):
        try:
            og_dataset = session.table("smoothies.public.orders")
            edited_dataset = session.create_dataframe(editable_df)

            og_dataset.merge(
                edited_dataset,
                og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"],
                [
                    when_matched().update({
                        "ORDER_FILLED": edited_dataset["ORDER_FILLED"]
                    })
                ]
            )
            st.success("Order(s) Updated!", icon="ðŸ‘")
        
        except Exception as e:
            st.error("Something went wrong.")
            st.exception(e)

else:
    st.success("There are no pending orders right now", icon="ðŸ‘")
