import pandas as pd
import streamlit as st
import psycopg2
from streamlit_option_menu import option_menu

mydb = psycopg2.connect(host="localhost", user="postgres", password="vignesh", port=5432, database="postgres")
mycursor = mydb.cursor()
st.title("Attendance calculator")
with st.sidebar:    
    select_fun=option_menu("Menu",["Insert staff","Editing satff","Deleting staff","Calculate salary"])
if select_fun=="Insert staff":

    st.subheader("INSERT STAFF DETAIL")
    name1 = st.text_input("Enter name:")
    salary1 = st.number_input("Enter salary:",step=1000)
    if st.button("insert staff details"):
        querry=('''CREATE TABLE IF NOT EXISTS staff_detail (
        name VARCHAR(50) primary key,
        salary BIGINT)''')

        mycursor.execute(querry)
        mydb.commit()
        query=("""insert into staff_detail(name,salary)
                        values(%s,%s)""")
        values=(name1,salary1)
        try:
            mycursor.execute(query,values)
            mydb.commit()
            st.success(f"Sucessfully inserted the staff detail of {name1,salary1}")
        except:
            news=f"{name1,salary1} is already exist in staff detail"
            st.success(news)

if select_fun=="Editing satff":

    a=[]
    mycursor.execute('''select * from staff_detail''')
    mydb.commit()
    tab=mycursor.fetchall()
    df=pd.DataFrame(tab,columns=["name","salary"])
    df.index = range(1, len(df) + 1)
    for i,j in df.iterrows():
        a.append(j["name"])
    st.subheader("Editing staff detail")
    a_name=st.text_input("enter the old name ")
    e_name=st.text_input("enter the new name")
    e_salary=st.number_input("enter the new salary",step=1000)

    if st.button("edit staff details"):
        if a_name in a:    
            query = f"UPDATE staff_detail SET name = '{e_name}', salary = {e_salary} WHERE name = '{a_name}'"
            mycursor.execute(query)
            mydb.commit()
            st.success(f"sucessfully modified the staff detail of {e_name,e_salary}")
        else:
            st.success(f"entered name {a_name} is not in the staff detail so please enter the correct name")

if select_fun=="Deleting staff":
    a=[]
    mycursor.execute('''select * from staff_detail''')
    mydb.commit()
    tab=mycursor.fetchall()
    df=pd.DataFrame(tab,columns=["name","salary"])
    df.index = range(1, len(df) + 1)
    for i,j in df.iterrows():
        a.append(j["name"])
    st.subheader("Deleting the staff detail")
    dele=st.text_input("enter the name to delete")
    if st.button("delete"):
        if dele in a:
            query = 'DELETE FROM staff_detail WHERE name = %s'
            mycursor.execute(query, (dele,))
            mydb.commit()
            st.success(f"sucessfully deleted the staff detail of {dele}")
        else:
            st.success(f"entered name {dele} is not in the staff detail so please enter the correct name")
show_names=st.radio("select the option to view table",("staff_detail",))
if show_names=="staff_detail":
    mycursor.execute('''select * from staff_detail''')
    mydb.commit()
    tab=mycursor.fetchall()
    df=pd.DataFrame(tab,columns=["name","salary"])
    df.index = range(1, len(df) + 1)
    st.write(df)


if select_fun=="Calculate salary":
    st.subheader("upload the excel file as excel workbook format and in the sheet the column name (Name must be in name) and (no of working days of staff must be in PRESENT)")
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    no_of_days=st.number_input("enter the no of day in the month",step=1,value=30)

    rou=st.number_input("enter the amt to round off for salary diffeence",step=1,value=19)
    if st.button("claculate the salary"): 
        df1=pd.read_excel(uploaded_file)
        df3=pd.merge(df,df1,on="name")
        df3.dropna(subset=["PRESENT"],inplace=True)
        df3["salry for worked days"]=(df3.salary/no_of_days)*df3["PRESENT"]
        df4=df3.sort_values(["salary"], ascending=False)
        df4.index = range(1, len(df4) + 1)
        df5=(df4[["name","salary","PRESENT","salry for worked days"]])
        v=[]
        for i,j in df5.iterrows():
            v.append(j["salry for worked days"])
        x=[]
        for i in range (len(v)):
            salary1=round(v[i],0)
            salary=str(int(salary1))
            salary=list(salary)
            a=[]
            for i in range(len(salary)):
                if i==len(salary)-2:
                    a.append(salary[i])
                if i==len(salary)-1:
                    a.append(salary[i])
            b=("".join(a))
            b=float(b)
            if b>rou:
                b=100-b
                salary1=salary1+b
                x.append(round(salary1,0))
            else:
                salary1=salary1-b
                x.append(round(salary1,0))
        
        df6=pd.DataFrame(x,columns=["round off salary"])
        df6.index=range(1,len(df6)+1)
        
        df7=pd.concat([df5,df6],axis=1)
        st.write(df7)


