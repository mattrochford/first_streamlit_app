import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError

# Global variable for snowflake connection
my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])

def main():
  streamlit.title("My Mom's New Healthy Diner")

  streamlit.header('Breakfast Favorites')

  streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
  streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
  streamlit.text('🐔 Hard-Boiled Free-Range Egg')
  streamlit.text('🥑🍞 Avocado Toast')

  streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

  # Import fruit data with pandas
  my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
  my_fruit_list = my_fruit_list.set_index('Fruit')

  # Let's put a pick list here so they can pick the fruit they want to include 
  fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Avocado','Strawberries'])
  fruits_to_show = my_fruit_list.loc[fruits_selected]

  # Display the table on the page.
  streamlit.dataframe(fruits_to_show)

  # New section for fruityvice API requests
  streamlit.header("Fruityvice Fruit Advice!")

  try:

    # Prompt for user input
    fruit_choice = streamlit.text_input('What fruit would you like information about?')

    if not fruit_choice:
      streamlit.error("Please select a fruit to get information.")

    else:  
      fruityvice_data = get_fruityvice_data(fruit_choice)
      streamlit.dataframe(fruityvice_data)

  except URLError as e:
    streamlit.error()

  #streamlit.stop()

  # Do Snowflake stuff
  if streamlit.button('Get Fruit Load List'): 
    #streamlit.header("The fruit load list contains:")
    my_data_rows = get_fruit_load_list()
    streamlit.dataframe(my_data_rows)

  add_my_fruit = streamlit.text_input('What fruit would you like to add?')
  streamlit.write('Thanks for adding ', add_my_fruit)

  # Add row to table
  my_cur.execute("INSERT INTO FRUIT_LOAD_LIST VALUES ('from streamlit')")

def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+this_fruit_choice)

  # Convert the response to a dataframe
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  
  return fruityvice_normalized
  
def get_fruit_load_list():
  
  with my_cnx.cursor() as my_cur:
    my_cur.execute("SELECT * FROM FRUIT_LOAD_LIST")
    return my_cur.fetchall()


if __name__ == '__main__':
  main()
