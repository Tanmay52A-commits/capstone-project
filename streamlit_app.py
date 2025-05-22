
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
#      'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
#      'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
#      'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
#      'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
#      'Dadra and Nagar Haveli and Daman and Diu', 'Lakshadweep', 'Delhi', 'Puducherry'
#  ]

# # ---------- Session State Initialization ----------
# def init_session():
#     keys = {
#         'authenticated': False,
#         'page': 'login',
#         'login_trigger': 0,
#         'user_data': {},
#         'recommendations': None,
#         'interaction_trigger': 0,
#         'generated_otp': None,
#         'user_id': None,
#         'user_name': None,
#         'session_id': None,
#         'messages': []
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
#                 # Set user_name and clear chat history for new user session
#                 st.session_state.user_name = phone_number
#                 st.session_state.messages = []
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
#     st.title("💬 InnoDatatics Chat")

#     if st.button("🔙 Back to Recommender"):
#         st.session_state.page = 'main'
#         st.rerun()

#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     if prompt := st.chat_input("Type your message…"):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("assistant"):
#             reply = run_flow(
#                 user_message=prompt,
#                 session_id=st.session_state.session_id,
#                 user_name=st.session_state.user_name
#             )
#             st.markdown(reply)
#             st.session_state.messages.append({"role": "assistant", "content": reply})

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import uuid
import requests
from recommender import recommend_jobs


# 🔧 Set constant layout and page width for all pages
st.set_page_config(
    page_title="Job Recommender System",
    layout="centered",  # Use "wide" if you want full screen width
    initial_sidebar_state="auto"
)

# Optional: CSS for fixed width and spacing
st.markdown("""
    <style>
        .main {
            max-width: 720px;
            margin: 0 auto;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Full CSV file path for interaction logs
# need to set up google api - using google console to store interaction data on google sheets
INTERACTION_LOG = "/tmp/user_interactions.csv"

# LangFlow API constants
BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "1a520f57-f6b0-46b3-aa50-9041f4d83e60"

# Load jobs data
jobs_df = pd.read_csv("jobs.csv")

# Extract unique job types (skills) from 'Job type' column
available_skills = sorted(jobs_df["Job type"].dropna().unique().tolist())

# List of all Indian states
indian_states = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
    'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
    'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal',
    'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Lakshadweep', 'Delhi', 'Puducherry'
]

# Initialize session variables
for key, value in {
    'authenticated': False,
    'page': 'login',
    'login_trigger': 0,
    'user_data': {},
    'recommendations': None,
    'interaction_trigger': 0,
    'generated_otp': None,
    'user_role': 'user',
    'messages': [],               # for chatbot history
    'session_id': str(uuid.uuid4())  # for logging user sessions
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- LangFlow chatbot integration ----------

def run_flow(user_message, session_id, user_name, tweaks=None, api_key=None):
    api_url = f"{BASE_API_URL}/api/v1/run/{FLOW_ID}"
    payload = {
        "session_id": session_id,
        "input_value": user_message,
        "input_type": "chat",
        "output_type": "chat",
        "tweaks": tweaks or {}
    }
    # Pass context nodes for LangFlow components
    payload["tweaks"].update({
        "ChatInput-voquK": {"session_id": session_id},
        "TextInput-s26mJ": {"input_value": user_name},
        "Memory-rRETL": {"session_id": session_id},
        "ChatOutput-GFauW": {"session_id": session_id}
    })
    headers = {"x-api-key": api_key} if api_key else {}
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"]


# -------------- LOGIN PAGE --------------
if st.session_state.page == 'login':
    # Regular user login form
    st.title("🔐 Login")
    phone_number = st.text_input("Enter your phone number")
    name_input = st.text_input("Enter your name")

    valid_phone = False

    # Validate phone number length and digits
    if phone_number:
        if not phone_number.isdigit() or len(phone_number) != 10:
            st.error("Please enter a valid 10-digit phone number.")
        else:
            valid_phone = True

    valid_name = bool(name_input and name_input.strip())  # True if name is not empty or whitespace only

    send_otp_button = st.button("Send OTP", disabled=not (valid_phone and valid_name))

    if send_otp_button:
        st.session_state.generated_otp = "123456"
        st.session_state.user_data["name"] = name_input.strip()
        st.success("OTP sent! Use 123456 for demo.")

    if st.session_state.generated_otp:
        entered_otp = st.text_input("Enter OTP", key="entered_otp")
        if st.button("Verify OTP"):
            if entered_otp == st.session_state.generated_otp:
                st.session_state.authenticated = True
                st.session_state.user_role = "user"
                st.session_state.page = 'main'  # Switch to main app page
                st.session_state.login_trigger += 1
                st.rerun()
            else:
                st.error("Incorrect OTP")
                
    st.markdown("---")

    st.subheader("Admin Access")
    admin_email = st.text_input("Enter your work email", key="admin_email_input")
    if st.button("Admin Access"):
        if admin_email.lower().endswith("@innodatatics.com"):
            st.session_state.authenticated = True
            st.session_state.user_role = "admin"
            st.session_state.page = "admin_view"  # Redirect to admin view page
            st.success("Admin access granted.")
            st.rerun()
        else:
            st.error("Access denied. Please use a valid email.")

# -------------- MAIN APP PAGE --------------
elif st.session_state.page == 'main' and st.session_state.authenticated:
    st.title("🧠 AI Job Recommender")

    if st.button("Logout"):
        for key in ['authenticated', 'generated_otp', 'recommendations', 'user_data']:
            st.session_state[key] = False if isinstance(st.session_state[key], bool) else {}
        st.session_state.page = 'login'
        st.rerun()

    if st.button("Chatbot Help"):
        st.session_state.page = "chatbot"
        st.rerun()

    # User input form
    with st.form("user_input_form"):
        name = st.text_input("Name", value=st.session_state.user_data.get("name", ""))
        age = st.number_input("Age", min_value=18, max_value=90, value=30)
        location = st.selectbox("Select Your Location (State)", indian_states)
        skills = st.multiselect("Select Skills (Job Types)", available_skills)
        salary = st.number_input("Expected Monthly Salary (INR)", min_value=0)
        model_choice = st.selectbox("Choose Recommendation Model", ["Rule-Based", "Unsupervised"])
        top_n = st.slider("Number of Job Recommendations", 1, 20, 3)
        submitted = st.form_submit_button("Get Recommendations")

    # Handle recommendation generation with basic validation
    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        elif not skills or len(skills) == 0:
            st.error("Please select at least one skill.")
        else:
            with st.spinner('Generating recommendations...'):
                session_id = str(uuid.uuid4())
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                skills_str = ", ".join(skills) if isinstance(skills, list) else skills
                st.session_state.user_data = {
                    "name": name,
                    "age": age,
                    "location": location,
                    "skills": skills_str,
                    "salary": salary,
                    "top_n": top_n,
                    "session_id": session_id,
                    "timestamp": timestamp
                }

                if model_choice == "Rule-Based":
                    st.session_state.recommendations = recommend_jobs(
                        user_name=name,
                        user_age=age,
                        user_location=location,
                        user_skills=skills_str,
                        expected_salary=salary,
                        top_n=top_n
                    )
                else:
                    st.session_state.recommendations = recommend_unsupervised(
                        skills=skills_str,  # Convert list to comma-separated string
                        location=location,
                        expected_monthly_salary=salary,
                        top_n=top_n
                    )
                
                
    # Display recommendations if available
    if st.session_state.recommendations is not None and not st.session_state.recommendations.empty:
        st.write(f"🔍 Recommendations for **{st.session_state.user_data['name']}**:")
        recommendations_display = st.session_state.recommendations[['Company', 'Job type', 'State', 'match_score']].sort_values(by="match_score", ascending=False)

        for index, row in recommendations_display.iterrows():
            job_key = f"expander_{index}"
            is_open = st.session_state.get("last_clicked_job") == job_key
        
            with st.expander(f"📌 {row['Company']}", expanded=is_open):
                st.write(f"**Job Type**: {row['Job type']}")
                st.write(f"**Location**: {row['State']}")
                st.write(f"**Match Score**: {row['match_score']}")
        
                if st.button(f"I'm interested in {row['Company']}", key=f"button_{job_key}"):
                    st.session_state["last_clicked_job"] = job_key
                    st.session_state["clicked_job"] = job_key  #
        
                    # Log interaction
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
                        "Match Scores": "|".join(st.session_state.recommendations["match_score"].astype(str).tolist()),
                    }
        
                    # Save to CSV
                    if os.path.exists(INTERACTION_LOG):
                        df_log = pd.read_csv(INTERACTION_LOG)
                        df_log = pd.concat([df_log, pd.DataFrame([interaction_data])], ignore_index=True)
                    else:
                        df_log = pd.DataFrame([interaction_data])
        
                    df_log.to_csv(INTERACTION_LOG, index=False)
                    st.session_state['interaction_trigger'] = st.session_state.get('interaction_trigger', 0) + 1
                    st.rerun()  # 🔄 Trigger page refresh after saving
        
                # After rerun, show success if this was the clicked job
                if st.session_state.get('clicked_job') == job_key:
                    st.success(f"Your interest in {row['Company']} has been logged!")
        
    elif st.session_state.recommendations is not None and st.session_state.recommendations.empty:
        st.warning("⚠️ No jobs found matching your profile.")


# ---------- PAGE: CHATBOT ----------
elif st.session_state.page == 'chatbot':
    st.title("💬 InnoDatatics Chat")

    if st.button("🔙 Back to Recommender"):
        st.session_state.page = 'main'
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle new user input
    if prompt := st.chat_input("Type your message…"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = run_flow(
                    user_message=prompt,
                    session_id=st.session_state.session_id,
                    user_name=st.session_state.user_data.get("name", "")
                )
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
             
# ----------- ADMIN VIEW PAGE -----------
elif st.session_state.page == "admin_view" and st.session_state.authenticated and st.session_state.user_role == "admin":
    st.title("🛠 Admin View")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.page = 'login'
        st.session_state.user_role = 'user'
        st.rerun()

    selected_action = st.radio("Choose an action:", [
        "View Dashboard",
        "Download Interaction Data",
        "Append to jobs.csv"
    ])

    if selected_action == "View Dashboard":
        st.info("📊 Show some Streamlit charts or tables here.")

    elif selected_action == "Download Interaction Data":
        if os.path.exists(INTERACTION_LOG):
            interaction_df = pd.read_csv(INTERACTION_LOG)
            csv = interaction_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Interaction CSV", csv, "interactions.csv", "text/csv")
        else:
            st.warning("No interaction data found.")

    elif selected_action == "Append to jobs.csv":
        st.info("📥 Add your job appending logic here.")
        new_job = st.text_area("Paste new job data (CSV format)")
        if st.button("Append Job"):
            if new_job:
                try:
                    from io import StringIO
                    new_df = pd.read_csv(StringIO(new_job))
                    existing_df = pd.read_csv("jobs.csv")
                    combined = pd.concat([existing_df, new_df], ignore_index=True)
                    combined.to_csv("jobs.csv", index=False)
                    st.success("New job(s) added successfully.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter job data first.")