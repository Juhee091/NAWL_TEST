import streamlit as st
import pandas as pd
import math

# Load CSV and assign days
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    total = len(df)
    per_day = math.ceil(total / 30)
    df['day'] = (df.index // per_day) + 1
    return df

st.title('Day-based Vocabulary Quiz')

# Initialize session state
if 'started' not in st.session_state:
    st.session_state.started = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'questions' not in st.session_state:
    st.session_state.questions = pd.DataFrame()
if 'wrong_df' not in st.session_state:
    st.session_state.wrong_df = pd.DataFrame()

# Sidebar: name input and day selection
with st.sidebar:
    name_input = st.text_input('Enter your name:', key='name_input')
    day_input = st.selectbox('Select day (1-30):', list(range(1, 31)), key='day_input')
    if st.button('Start Test'):
        if name_input:
            data = load_data('nawl.csv')
            st.session_state.questions = data[data['day'] == day_input].reset_index(drop=True)
            st.session_state.started = True
            st.session_state.submitted = False
            st.session_state.wrong_df = pd.DataFrame()
        else:
            st.warning('Please enter your name.')

# If test not started
if not st.session_state.started:
    st.info('Please enter your name and select a day, then click "Start Test".')
else:
    # Display quiz
    st.header(f"Vocabulary Quiz: Day {st.session_state.day_input}")
    st.write(f"Student: {st.session_state.name_input}")
    df = st.session_state.questions
    if not st.session_state.submitted:
        with st.form('quiz_form'):
            for idx, row in df.iterrows():
                st.markdown(f"**Q{idx+1}.** {row['English Definition']} ({row['POS']})")
                st.text_input('', key=f'answer_{idx}')
            if st.form_submit_button('Submit Answers'):
                wrong = []
                for idx, row in df.iterrows():
                    ans = st.session_state.get(f'answer_{idx}', '').strip().lower()
                    if ans != str(row['Meanings']).strip().lower():
                        wrong.append({
                            'No.': idx+1,
                            'Definition': row['English Definition'],
                            'POS': row['POS'],
                            'Answer': row['Meanings']
                        })
                st.session_state.wrong_df = pd.DataFrame(wrong)
                st.session_state.submitted = True
    else:
        # Show results
        total = len(st.session_state.questions)
        wrong_df = st.session_state.wrong_df
        correct = total - len(wrong_df)
        st.success(f"{st.session_state.name_input}, you answered {correct} out of {total} correctly!")
        if not wrong_df.empty:
            st.warning('Questions you missed:')
            st.table(wrong_df)
            if st.button('Retake missed questions'):
                idxs = [row['No.']-1 for _, row in wrong_df.iterrows()]
                st.session_state.questions = st.session_state.questions.iloc[idxs].reset_index(drop=True)
                st.session_state.submitted = False
                # clear previous answers
                for i in range(len(st.session_state.questions)):
                    if f'answer_{i}' in st.session_state:
                        del st.session_state[f'answer_{i}']
                st.session_state.wrong_df = pd.DataFrame()
