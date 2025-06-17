import streamlit as st
import pandas as pd
import math

# Load CSV
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    # assign days evenly across 30 days
    total = len(df)
    per_day = math.ceil(total / 30)
    df['day'] = (df.index // per_day) + 1
    return df

# Initialize session state
if 'wrong_df' not in st.session_state:
    st.session_state['wrong_df'] = None
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False

st.title('Day-based Vocabulary Quiz')

# Sidebar: user name and day selection
with st.sidebar:
    name = st.text_input('Enter your name:')
    day = st.selectbox('Select day (1-30):', list(range(1, 31)))
    if st.button('Start Test'):
        # Reset state
        st.session_state['submitted'] = False
        st.session_state['wrong_df'] = None
        # Load questions for selected day
        data = load_data('nawl.csv')
        st.session_state['questions'] = data[data['day'] == day].reset_index(drop=True)
        # Clear previous answers
        for i in range(len(st.session_state['questions'])):
            st.session_state[f'answer_{i}'] = ''
        st.experimental_rerun()

# Display quiz when user and questions are set
if name and 'questions' in st.session_state:
    st.header(f'Vocabulary Quiz for Day {day}')
    st.write(f'Student: {name}')
    questions = st.session_state['questions']
    with st.form(key='quiz_form'):
        for idx, row in questions.iterrows():
            st.markdown(f"**Q{idx+1}.** {row['English Definition']} ({row['POS']})")
            st.text_input('Your answer:', key=f'answer_{idx}')
        if st.form_submit_button('Submit Answers') and not st.session_state['submitted']:
            st.session_state['submitted'] = True
            wrong = []
            for i, row in questions.iterrows():
                user_ans = st.session_state.get(f'answer_{i}', '').strip().lower()
                correct = str(row['Meanings']).strip().lower()
                if user_ans != correct:
                    wrong.append((i+1, row['English Definition'], row['POS'], row['Meanings']))
            st.session_state['wrong_df'] = pd.DataFrame(wrong, columns=['No.', 'Definition', 'POS', 'Answer'])
            st.experimental_rerun()

# Show results and retake option
if st.session_state['submitted']:
    total = len(st.session_state['questions'])
    wrong_df = st.session_state['wrong_df']
    correct_count = total - len(wrong_df)
    st.success(f"{name}, you got {correct_count} out of {total} correct!")
    if not wrong_df.empty:
        st.warning('Questions you missed:')
        st.table(wrong_df)
        if st.button('Retake missed questions'):
            retake_df = st.session_state['questions'].iloc[[i-1 for i in wrong_df['No.']]].reset_index(drop=True)
            st.session_state['questions'] = retake_df
            for i in range(len(retake_df)):
                st.session_state[f'answer_{i}'] = ''
            st.session_state['submitted'] = False
            st.session_state['wrong_df'] = None
            st.experimental_rerun()
