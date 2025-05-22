# import streamlit as st
# import pandas as pd
# import os
# import time
# from datetime import datetime
# import uuid
# import sqlite3
# import bcrypt
# import requests
# from recommender import recommend_jobs

# # ---------- Constants ----------
# INTERACTION_LOG = "/tmp/user_interactions.csv"
# BASE_API_URL = "http://127.0.0.1:7860"
# FLOW_ID = "1a520f57-f6b0-46b3-aa50-9041f4d83e60"

# # ---------- Load Jobs Data ----------
# jobs_df = pd.read_csv("jobs.csv")
# available_skills = sorted(jobs_df["Job type"].dropna().unique().tolist())
# indian_states = [
#     'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
#     'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
#     'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
#     'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
#     'Dadra and Nagar Haveli and Daman and Diu', 'Lakshadweep', 'Delhi', 'Puducherry'
# ]

# # ---------- Session State Initialization ----------
# def init_session():
#     keys = {
#         'authenticated': False, 'page': 'login', 'login_trigger': 0, 'user_data': {},
#         'recommendations': None, 'interaction_trigger': 0, 'generated_otp': None,
#         'user_id': None, 'user_name': None, 'session_id': None, 'messages': [],
#         'confirm_delete': False
#     }
#     for k, v in keys.items():
#         if k not in st.session_state:
#             st.session_state[k] = v

# init_session()

# # ---------- Chatbot Helper ----------
# def run_flow(user_message, session_id, user_name, tweaks=None, api_key=None):
#     api_url = f"{BASE_API_URL}/api/v1/run/{FLOW_ID}"
#     payload = {
#         "session_id": session_id,
#         "input_value": user_message,
#         "input_type": "chat",
#         "output_type": "chat",
#         "tweaks": tweaks or {}
#     }
#     payload["tweaks"].update({
#         "ChatInput-voquK": {"session_id": session_id},
#         "TextInput-s26mJ": {"input_value": user_name},
#         "Memory-rRETL": {"session_id": session_id},
#         "ChatOutput-GFauW": {"session_id": session_id}
#     })
#     headers = {"x-api-key": api_key} if api_key else None
#     response = requests.post(api_url, json=payload, headers=headers)
#     response.raise_for_status()
#     return response.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"]

# # ---------- Chatbot Database ----------
# conn = sqlite3.connect("users.db", check_same_thread=False)
# cursor = conn.cursor()

# # ---------- Routing ----------
# if st.session_state.page == 'login':
#     st.title("🔐 Login")
#     phone_number = st.text_input("Enter your phone number")
#     if phone_number and (not phone_number.isdigit() or len(phone_number) != 10):
#         st.error("Please enter a valid 10-digit phone number.")
#     valid_phone = phone_number.isdigit() and len(phone_number) == 10
#     if st.button("Send OTP", disabled=not valid_phone):
#         st.session_state.generated_otp = "123456"
#         st.success("OTP sent! Use 123456 for demo.")
#     if st.session_state.generated_otp:
#         entered_otp = st.text_input("Enter OTP", key="entered_otp")
#         if st.button("Verify OTP"):
#             if entered_otp == st.session_state.generated_otp:
#                 st.session_state.authenticated = True
#                 st.session_state.page = 'main'
#                 st.session_state.session_id = phone_number
#                 st.rerun()
#             else:
#                 st.error("Incorrect OTP")

# elif st.session_state.page == 'main' and st.session_state.authenticated:
#     st.title("🧠 AI Job Recommender")
#     if st.button("Logout"):
#         for k in ('authenticated', 'generated_otp', 'recommendations', 'user_data'):
#             st.session_state[k] = None
#         st.session_state.page = 'login'
#         st.rerun()
#     if st.button("💬 Go to Chatbot"):
#         st.session_state.page = 'chatbot'
#         st.rerun()

#     with st.form("user_input_form"):
#         name = st.text_input("Name")
#         age = st.number_input("Age", min_value=18, max_value=70, value=25)
#         location = st.selectbox("Select Your Location (State)", indian_states)
#         skills = st.multiselect("Select Skills (Job Types)", available_skills)
#         salary = st.number_input("Expected Monthly Salary (INR)", min_value=0)
#         top_n = st.slider("Number of Job Recommendations", 1, 10, 3)
#         submitted = st.form_submit_button("Get Recommendations")

#     if submitted:
#         if not name.strip():
#             st.error("Please enter your name.")
#         elif not skills:
#             st.error("Please select at least one skill.")
#         else:
#             with st.spinner('Generating recommendations...'):
#                 session_id = str(uuid.uuid4())
#                 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 skills_str = ", ".join(skills)
#                 st.session_state.user_data = {
#                     "name": name, "age": age, "location": location,
#                     "skills": skills_str, "salary": salary, "top_n": top_n,
#                     "session_id": session_id, "timestamp": timestamp
#                 }
#                 st.session_state.recommendations = recommend_jobs(
#                     user_name=name, user_age=age, user_location=location,
#                     user_skills=skills_str, expected_salary=salary, top_n=top_n
#                 )

#     if st.session_state.recommendations is not None:
#         if not st.session_state.recommendations.empty:
#             st.write(f"🔍 Recommendations for **{st.session_state.user_data['name']}**:")
#             recs = st.session_state.recommendations[['Company', 'Job type', 'State', 'match_score']].sort_values(by="match_score", ascending=False)
#             for index, row in recs.iterrows():
#                 job_key = f"expander_{index}"
#                 with st.expander(f"📌 {row['Company']}"):
#                     st.write(f"**Job Type**: {row['Job type']}")
#                     st.write(f"**Location**: {row['State']}")
#                     st.write(f"**Match Score**: {row['match_score']}")
#                     if st.button(f"I'm interested in {row['Company']}", key=f"button_{job_key}"):
#                         interaction_data = {
#                             "Timestamp": st.session_state.user_data['timestamp'],
#                             "Session ID": st.session_state.user_data['session_id'],
#                             "Name": st.session_state.user_data['name'],
#                             "Age": st.session_state.user_data['age'],
#                             "Location": st.session_state.user_data['location'],
#                             "Skills": st.session_state.user_data['skills'],
#                             "Expected Salary": st.session_state.user_data['salary'],
#                             "Top N": st.session_state.user_data['top_n'],
#                             "Jobs Recommended": "|".join(st.session_state.recommendations["Company"].astype(str).tolist()),
#                             "Jobs Clicked": row['Company'],
#                             "Match Scores": "|".join(st.session_state.recommendations["match_score"].astype(str).tolist())
#                         }
#                         if os.path.exists(INTERACTION_LOG):
#                             df_log = pd.read_csv(INTERACTION_LOG)
#                             df_log = pd.concat([df_log, pd.DataFrame([interaction_data])], ignore_index=True)
#                         else:
#                             df_log = pd.DataFrame([interaction_data])
#                         df_log.to_csv(INTERACTION_LOG, index=False)
#                         st.success(f"Your interest in {row['Company']} has been logged!")
#         else:
#             st.warning("⚠️ No jobs found matching your profile.")

# elif st.session_state.page == 'chatbot':
#     st.set_page_config(page_title="InnoDatatics Chat", layout="wide")
#     st.title("🔐 InnoDatatics Chat — Register, Login, and Chat")

#     action = st.sidebar.selectbox("Action", ["Register", "Login"])

#     if action == "Register":
#         st.header("📝 Register New Account")
#         name = st.text_input("Name", key="reg_name")
#         phone = st.text_input("Phone Number", key="reg_phone")
#         pwd = st.text_input("Password", type="password", key="reg_pwd")
#         if st.button("Sign Up"):
#             if not (name and phone and pwd):
#                 st.error("All fields are required.")
#             else:
#                 pwd_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
#                 try:
#                     cursor.execute("INSERT INTO users (name, phone, password_hash) VALUES (?,?,?)", (name, phone, pwd_hash))
#                     conn.commit()
#                     st.success("Registration successful! Now switch to Login.")
#                 except sqlite3.IntegrityError:
#                     st.error("That phone number is already registered.")

#     elif action == "Login":
#         st.header("🔐 Login to Your Account")
#         phone = st.text_input("Phone Number", key="login_phone")
#         pwd = st.text_input("Password", type="password", key="login_pwd")
#         if st.button("Log In"):
#             cursor.execute("SELECT id, name, password_hash FROM users WHERE phone = ?", (phone,))
#             row = cursor.fetchone()
#             if row and bcrypt.checkpw(pwd.encode(), row[2]):
#                 st.session_state.user_id = row[0]
#                 st.session_state.user_name = row[1]
#                 st.session_state.session_id = phone
#                 st.session_state.messages = []
#                 st.session_state.confirm_delete = False
#                 st.success(f"🎉 Welcome back, {row[1]}!")
#             else:
#                 st.error("🚫 Invalid phone number or password.")

#     if st.session_state.user_id:
#         st.header(f"💬 Welcome, {st.session_state.user_name}!")
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Sign Out"):
#                 for k in ("user_id", "user_name", "session_id", "messages", "confirm_delete"):
#                     st.session_state.pop(k, None)
#                 st.experimental_rerun()
#         with col2:
#             if not st.session_state.confirm_delete:
#                 if st.button("Delete Account"):
#                     st.session_state.confirm_delete = True
#             else:
#                 st.warning("Are you sure you want to delete your account and chat history?")
#                 if st.button("Yes, delete my account"):
#                     cursor.execute("DELETE FROM users WHERE id = ?", (st.session_state.user_id,))
#                     conn.commit()
#                     for k in ("user_id", "user_name", "session_id", "messages", "confirm_delete"):
#                         st.session_state.pop(k, None)
#                     st.success("Your account and chat history have been deleted.")
#                     st.experimental_rerun()
#                 if st.button("Cancel"):
#                     st.session_state.confirm_delete = False

#         for msg in st.session_state.messages:
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])

#         if prompt := st.chat_input("Type your message…"):
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             with st.chat_message("assistant"):
#                 reply = run_flow(
#                     user_message=prompt,
#                     session_id=st.session_state.session_id,
#                     user_name=st.session_state.user_name
#                 )
#                 st.markdown(reply)
#                 st.session_state.messages.append({"role": "assistant", "content": reply})

#         if st.button("🔙 Back to Recommender"):
#             st.session_state.page = 'main'
#             st.rerun()
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import uuid
import sqlite3
import bcrypt
import requests
from recommender import recommend_jobs

# ---------- Constants ----------
INTERACTION_LOG = "/tmp/user_interactions.csv"
BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "1a520f57-f6b0-46b3-aa50-9041f4d83e60"

# ---------- Load Jobs Data ----------
jobs_df = pd.read_csv("jobs.csv")
available_skills = sorted(jobs_df["Job type"].dropna().unique().tolist())
indian_states = [
     'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
     'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
     'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
     'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
     'Dadra and Nagar Haveli and Daman and Diu', 'Lakshadweep', 'Delhi', 'Puducherry'
 ]

# ---------- Session State Initialization ----------
def init_session():
    keys = {
        'authenticated': False,
        'page': 'login',
        'login_trigger': 0,
        'user_data': {},
        'recommendations': None,
        'interaction_trigger': 0,
        'generated_otp': None,
        'user_id': None,
        'user_name': None,
        'session_id': None,
        'messages': []
    }
    for k, v in keys.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ---------- Chatbot Helper ----------
def run_flow(user_message, session_id, user_name, tweaks=None, api_key=None):
    api_url = f"{BASE_API_URL}/api/v1/run/{FLOW_ID}"
    payload = {
        "session_id": session_id,
        "input_value": user_message,
        "input_type": "chat",
        "output_type": "chat",
        "tweaks": tweaks or {}
    }
    payload["tweaks"].update({
        "ChatInput-voquK": {"session_id": session_id},
        "TextInput-s26mJ": {"input_value": user_name},
        "Memory-rRETL": {"session_id": session_id},
        "ChatOutput-GFauW": {"session_id": session_id}
    })
    headers = {"x-api-key": api_key} if api_key else None
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"]

# ---------- Routing ----------
if st.session_state.page == 'login':
    st.title("🔐 Login")
    phone_number = st.text_input("Enter your phone number")
    if phone_number and (not phone_number.isdigit() or len(phone_number) != 10):
        st.error("Please enter a valid 10-digit phone number.")
    valid_phone = phone_number.isdigit() and len(phone_number) == 10
    if st.button("Send OTP", disabled=not valid_phone):
        st.session_state.generated_otp = "123456"
        st.success("OTP sent! Use 123456 for demo.")
    if st.session_state.generated_otp:
        entered_otp = st.text_input("Enter OTP", key="entered_otp")
        if st.button("Verify OTP"):
            if entered_otp == st.session_state.generated_otp:
                st.session_state.authenticated = True
                st.session_state.page = 'main'
                st.session_state.session_id = phone_number
                # Set user_name and clear chat history for new user session
                st.session_state.user_name = phone_number
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("Incorrect OTP")

elif st.session_state.page == 'main' and st.session_state.authenticated:
    st.title("🧠 AI Job Recommender")
    if st.button("Logout"):
        for k in ('authenticated', 'generated_otp', 'recommendations', 'user_data'):
            st.session_state[k] = None
        st.session_state.page = 'login'
        st.rerun()
    if st.button("💬 Go to Chatbot"):
        st.session_state.page = 'chatbot'
        st.rerun()

    with st.form("user_input_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=18, max_value=70, value=25)
        location = st.selectbox("Select Your Location (State)", indian_states)
        skills = st.multiselect("Select Skills (Job Types)", available_skills)
        salary = st.number_input("Expected Monthly Salary (INR)", min_value=0)
        top_n = st.slider("Number of Job Recommendations", 1, 10, 3)
        submitted = st.form_submit_button("Get Recommendations")

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        elif not skills:
            st.error("Please select at least one skill.")
        else:
            with st.spinner('Generating recommendations...'):
                session_id = str(uuid.uuid4())
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                skills_str = ", ".join(skills)
                st.session_state.user_data = {
                    "name": name, "age": age, "location": location,
                    "skills": skills_str, "salary": salary, "top_n": top_n,
                    "session_id": session_id, "timestamp": timestamp
                }
                st.session_state.recommendations = recommend_jobs(
                    user_name=name, user_age=age, user_location=location,
                    user_skills=skills_str, expected_salary=salary, top_n=top_n
                )

    if st.session_state.recommendations is not None:
        if not st.session_state.recommendations.empty:
            st.write(f"🔍 Recommendations for **{st.session_state.user_data['name']}**:")
            recs = st.session_state.recommendations[['Company', 'Job type', 'State', 'match_score']].sort_values(by="match_score", ascending=False)
            for index, row in recs.iterrows():
                job_key = f"expander_{index}"
                with st.expander(f"📌 {row['Company']}"):
                    st.write(f"**Job Type**: {row['Job type']}")
                    st.write(f"**Location**: {row['State']}")
                    st.write(f"**Match Score**: {row['match_score']}")
                    if st.button(f"I'm interested in {row['Company']}", key=f"button_{job_key}"):
                        interaction_data = {
                            "Timestamp": st.session_state.user_data['timestamp'],
                            "Session ID": st.session_state.user_data['session_id'],
                            "Name": st.session_state.user_data['name'],
                            "Age": st.session_state.user_data['age'],
                            "Location": st.session_state.user_data['location'],
                            "Skills": st.session_state.user_data['skills'],
                            "Expected Salary": st.session_state.user_data['salary'],
                            "Top N": st.session_state.user_data['top_n'],
                            "Jobs Recommended": "|".join(st.session_state.recommendations["Company"].astype(str).tolist()),
                            "Jobs Clicked": row['Company'],
                            "Match Scores": "|".join(st.session_state.recommendations["match_score"].astype(str).tolist())
                        }
                        if os.path.exists(INTERACTION_LOG):
                            df_log = pd.read_csv(INTERACTION_LOG)
                            df_log = pd.concat([df_log, pd.DataFrame([interaction_data])], ignore_index=True)
                        else:
                            df_log = pd.DataFrame([interaction_data])
                        df_log.to_csv(INTERACTION_LOG, index=False)
                        st.success(f"Your interest in {row['Company']} has been logged!")
        else:
            st.warning("⚠️ No jobs found matching your profile.")

elif st.session_state.page == 'chatbot':
    st.set_page_config(page_title="InnoDatatics Chat", layout="wide")
    st.title("💬 InnoDatatics Chat")

    if st.button("🔙 Back to Recommender"):
        st.session_state.page = 'main'
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your message…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            reply = run_flow(
                user_message=prompt,
                session_id=st.session_state.session_id,
                user_name=st.session_state.user_name
            )
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
