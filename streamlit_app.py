# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: My Parents New Healthy Diner :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# Insert widget 
cnx = st.connection('snowflake')
session = cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# Convert snowpark df to pandas df
pd_df = my_dataframe.to_pandas()

# --------------------- # 
# Name input            # 
# --------------------- # 

name_on_order = st.text_input('Name on Smoothie:')

# --------------------- # 
# Ingredients           # 
# --------------------- # 

ingredients_list = st.multiselect('Choose up to 5 ingredients', my_dataframe, max_selections=5)
if ingredients_list: 
    # Create empty string to store values
    ingredients_string = ''

    # Loop through the items in the list
    for item in ingredients_list: 
        # Add item to empty string + space
        ingredients_string += item + ' '

        # Search on locate in df
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == item, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        # Get information from api        
        st.subheader(f'Nutrition information for {item}')
        smoothiefroot_response = requests.get('https://my.smoothiefroot.com/api/fruit/' + search_on)
        sf_df = st.dataframe(smoothiefroot_response.json(), use_container_width=True)
 

    # Generate write statement
    my_insert_stmt = """    
    
    insert into smoothies.public.orders(ingredients, name_on_order)
    values ('""" + ingredients_string + """','""" + name_on_order + """')
    """
    
    # Insert submit button 
    time_to_insert = st.button('Submit Order')
    
    # run statement in console
    if time_to_insert: 
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}! ', icon='✅')
