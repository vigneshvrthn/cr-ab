import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import psycopg2 as sql
import re
import io



connection=sql.connect(host='localhost',password='vignesh',dbname='img_to_txt',user='postgres',port=5432)
my_corsor=connection.cursor()

def img_pro(img):
    img1=Image.open(img)
    img_arr = np.array(img1)
    reader = easyocr.Reader(['en'])
    txt = reader.readtext(img_arr, detail=0)
    data=list(txt)
    extracted={'Name':[],'Designation':[],'Ph_No':[],'website':[],'Address':[],'pincode':[],'company_name':[],'mail':[]}
    extracted['Name'].append(data[0])
    data.remove(data[0])
    extracted['Designation'].append(data[0])
    data.remove(data[0])
    for i in range(6):
        try:
            for i in range (len(data)):
                if data[i].startswith("+") or (data[i].replace('-','').isdigit() and '-' in data[i]):
                    extracted['Ph_No'].append(data[i])
                    data.remove(data[i])
            for i in range (len(data)):
                if '@'in data[i] and '.com' in data[i]:
                        extracted['mail'].append(data[i])
                        (data.remove(data[i]))

            for i in range (len(data)):
                if data[i].startswith('www') or data[i].startswith('WWW') or data[i].startswith('wwW') and '.com' in data[i]:
                    extracted['website'].append(data[i])
                    data.remove(data[i])
                if  '.com' in data[i]:
                    extracted['website'].append(data[i])
                    (data.remove(data[i]))
                
            for i in range (len(data)):
                if data[i].startswith('123 ') :
                    extracted['Address'].append(data[i])
                    data.remove(data[i])
                if 'St,,' in data[i] or 'ST' in data[i] or 'St' in data[i] or 'sT' in data[i]or 'St ' in data[i] or 'St,,' in data[i]:
                        extracted['Address'].append(data[i])
                        (data.remove(data[i]))
                
                if data[i].endswith(",")or data[i].endswith(";"):
                    extracted['Address'].append(data[i])
                    data.remove(data[i])
            for i in range (len(data)):
                if 'TamilNadu' in data[i] or 'Tamil Nadu' in data[i] or data[i].isdigit():
                        extracted['pincode'].append(data[i])
                        (data.remove(data[i]))

                        
                                            
        except:
            continue
                
    if len(data)>1:
        extracted['company_name'].append(data[0])
        extracted['company_name'].append(data[1])
    else:
        extracted['company_name'].append(data[0])
    for key,value in extracted.items():
        if len(value)>0:
            concad=" ".join(value)
            extracted[key]=[concad]
        else:
            value="NA"
            extracted[key]=[value]
    def img_pro1(image_path):
        img = Image.open(image_path)  # Open the image file
        # Your image processing code goes here
        
        # Example processing: converting to grayscale
        img = img.convert('L')

        # Saving the processed image
        img_byt = io.BytesIO()
        img.save(img_byt, format="PNG")
        img_data = img_byt.getvalue()

        # Assuming 'extracted' is a dictionary where you want to store the processed image data
        extracted['IMAGE'] = img_data
        
    img_pro1(img)
    
    df=pd.DataFrame(extracted)
    df.index=(range(1,len(df)+1))
    return(df)
def in_sql(df):
    # Establish a connection to the database
    connection = sql.connect(host='localhost', password='vignesh', dbname='img_to_txt', user='postgres', port=5432)
    
    # Create a cursor object
    my_cursor = connection.cursor()

    # Create the table if it doesn't exist
    cr_query = '''CREATE TABLE IF NOT EXISTS img (Name VARCHAR(50) primary, Designation VARCHAR(50), Ph_No VARCHAR(50), 
                   website text, Address text, pincode VARCHAR, 
                   company_name VARCHAR, mail VARCHAR, image_byte text)'''
    my_cursor.execute(cr_query)
    # Insert data from the DataFrame into the table
    for i, j in df.iterrows():
        try:
            in_query = '''INSERT INTO img 
                          (Name, Designation, Ph_No, website, Address, pincode, company_name, mail, image_byte) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            values = (j['Name'], j['Designation'], j['Ph_No'][:25], j['website'], j['Address'], j['pincode'],
                      j['company_name'], j['mail'],str( j['IMAGE']))
            my_cursor.execute(in_query, values)
        except sql.Error as e:
            st.write('duplicate dit not alowed you have already uploaded this image', e)
            connection.rollback()  # Rollback the transaction in case of an error

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    my_cursor.close()
    connection.close()

    

st.set_page_config(page_title="img to txt",layout="wide")


st.markdown(
    """
    <style>
        .title-text {
            color: #e7feff; /* Change to your desired color */
        }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 class='title-text'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

with st.sidebar:    
    select_fun=option_menu("Menu",["Home","Upload img & and modify txt","Delete"],icons=["house","upload","trash"])


if select_fun=='Home':
    page_bg_img = '''
    <style>
    [data-testid=stAppViewContainer] {
        background-image: url("https://raw.githubusercontent.com/vigneshvrthn/BizCardX-Extracting-Business-Card-Data-with-OCR/main/Image-To-Text-Converter-Online.jpg");
        background-size: 100% 100%; /* Cover the entire container */
        background-repeat: no-repeat; /* Ensure background image doesn't repeat */
    }
    </style>
    '''
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.markdown("### <span style='color:#e7feff  ;'>Technologies Used:</span> <span style='color:#e7feff;'>Python  ,   easy OCR  ,   Streamlit  ,   SQL  ,   Pandas</span>", unsafe_allow_html=True)
    
    
    st.markdown("### <span style='color:#e7feff  ;'><br><br>About:</span> <span style='color:#e7feff;'>  Bizcard is a Python application designed to extract information from business cards.</span>", unsafe_allow_html=True)
    
    
    st.markdown("### <span style='color:#e7feff  ;'>The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.</span>", unsafe_allow_html=True)


    
    
elif select_fun=='Upload img & and modify txt':
    page_bg_img = '''
    <style>
    [data-testid=stAppViewContainer] {
        background-image: url("https://tse1.mm.bing.net/th?id=OIP.h_jfW1d7_fa8UTM0rMnhYgHaE7&pid=Api&P=0&h=220");
        background-size: 100% 100%; /* Cover the entire container */
        background-repeat: no-repeat; /* Ensure background image doesn't repeat */
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    img = st.file_uploader("upload an image", type=["png", "jpg", "jpeg"])

    if img is not None:
        df=img_pro(img)
        st.image(img)
        st.markdown("""<style>.stButton > button {display: block; margin: 0 auto;}</style> """, unsafe_allow_html=True)
        if st.button('Insert into sql DB',use_container_width=True):        
            if in_sql(df):
                st.write("### <span style='color:#00ffef   ;'>Extracted Text is Sucessfully entred at sql db</span>", unsafe_allow_html=True)
            else:
                st.write("you have already saved this data in sql")
               
    else :
        st.write('Please uplod the image')
    
    radio=st.radio("Select the option",["Preview","Modify"])

    if radio=="Preview":
        df=pd.read_sql_query('select * from img',connection)
        df.index=range(1,len(df)+1)        
        st.write(df)
    
    if radio=='Modify':
        df=pd.read_sql_query("select * from img",connection)
        name=st.selectbox("Select the name to modify",df["name"])
        df2=df[df['name']==name].head(1)
        st.write(df2)
        col1,col2=st.columns(2)
        with col1:
            name=st.text_input("Name",df2.iloc[0]['name'])
            ph_no=st.text_input("Ph_No",df2.iloc[0]["ph_no"])
            address=st.text_input("Address",df2.iloc[0]["address"])
            company_name=st.text_input("Company_name",df2.iloc[0]["company_name"])
        with col2:
            designation=st.text_input("Designation",df2.iloc[0]["designation"])
            website=st.text_input("website",df2.iloc[0]['website'])
            pincode=st.text_input("Pincode",df2.iloc[0]["pincode"])
            mailid=st.text_input("Mail_id",df2.iloc[0]["mail"])
        image_byte=st.text_input("Image",df2.iloc[0]["image_byte"])   

        if st.button("Modify"):
            query = '''UPDATE img SET designation=%s, ph_no=%s, address=%s, company_name=%s, website=%s,pincode=%s, mail=%s, image_byte=%s WHERE name=%s'''
            values = (designation, ph_no, address, company_name, website, pincode, mailid, image_byte, name)
            my_corsor.execute(query, values)
            connection.commit()
            st.write("### <span style='color:#00ffef   ;'>Modifed Sucessfully</span>", unsafe_allow_html=True)
elif select_fun=='Delete':
    page_bg_img = '''
    <style>
    [data-testid=stAppViewContainer] {
        background-image: url("https://www.financialfortunemedia.com/wp-content/uploads/2021/06/Image-to-Text.png");
        background-size: 100% 100%; /* Cover the entire container */
        background-repeat: no-repeat; /* Ensure background image doesn't repeat */
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    radio=st.radio("Select the option",["Preview","Delete"])
    if radio=="Preview":
        df=pd.read_sql_query('select * from img',connection)
        df.index=range(1,len(df)+1)        
        st.write(df)
    
    if radio == 'Delete':
        df = pd.read_sql_query("SELECT * FROM img", connection)
        name = st.selectbox("Select the name to delete", df["name"])
        if st.button("Delete"):
            query = "DELETE FROM img WHERE name = %s"
            my_corsor.execute(query, (name,))
            connection.commit()
            st.write("### <span style='color:#00ffef   ;'>Successfully deleted the selected name</span>", unsafe_allow_html=True)


