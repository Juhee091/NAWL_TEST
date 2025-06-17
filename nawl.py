import streamlit as st
import pandas as pd
import math

# Function to load and assign days
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    total = len(df)
    per_day = math.ceil(total / 30)
    df['day'] = (df.index // per_day) + 1
    return df

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = pd.DataFrame()
if 'wrong_df' not in st.session_state:
    st.session_state.wrong_df = pd.DataFrame()
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

st.title('Day-based Vocabulary Quiz')

# Sidebar inputs
with st.sidebar:
    name = st.text_input('Enter your name:')
    day = st.selectbox('Select day (1-30):', list(range(1, 31)))
    if st.button('Start Test'):
        data = load_data('nawl.csv')
        st.session_state.questions = data[data['day'] == day].reset_index(drop=True)
        st.session_state.submitted = False
        st.session_state.wrong_df = pd.DataFrame()
        st.experimental_rerun()

# Prompt to start
if not name or st.session_state.questions.empty:
    st.info('Please enter your name and select a day, then click "Start Test".')
else:
    st.header(f'Vocabulary Quiz: Day {day}')
    st.write(f'Student: {name}')
    questions = st.session_state.questions
    # Quiz form
    with st.form('quiz_form'):
        for idx, row in questions.iterrows():
            st.markdown(f"**Q{idx+1}.** {row['English Definition']} ({row['POS']})")
            st.text_input('', key=f'answer_{idx}')
        if st.form_submit_button('Submit Answers'):
            wrong = []
            for idx, row in questions.iterrows():
                user_ans = st.session_state.get(f'answer_{idx}', '').strip().lower()
                correct = str(row['Meanings']).strip().lower()
                if user_ans != correct:
                    wrong.append({
                        'No.': idx+1,
                        'Definition': row['English Definition'],
                        'POS': row['POS'],
                        'Answer': row['Meanings']
                    })
            st.session_state.wrong_df = pd.DataFrame(wrong)
            st.session_state.submitted = True
            st.experimental_rerun()

# Results and retake
if st.session_state.submitted:
    total = len(st.session_state.questions)
    wrong_df = st.session_state.wrong_df
    correct = total - len(wrong_df)
    st.success(f"{name}, you answered {correct} out of {total} correctly!")
    if not wrong_df.empty:
        st.warning('Questions you missed:')
        st.table(wrong_df)
        if st.button('Retake missed'):
            idxs = [row-1 for row in wrong_df['No.']]
            st.session_state.questions = st.session_state.questions.iloc[idxs].reset_index(drop=True)
            st.session_state.submitted = False
            st.session_state.wrong_df = pd.DataFrame()
            st.experimental_rerun()
