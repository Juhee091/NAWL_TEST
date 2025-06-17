import streamlit as st
import pandas as pd
import math

# Load CSV
def load_data(path):
    df = pd.read_csv(path)
    total = len(df)
    per_day = math.ceil(total / 30)
    df['day'] = (df.index // per_day) + 1
    return df

# Initialize session state keys
if 'wrong_df' not in st.session_state:
    st.session_state['wrong_df'] = None
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
if 'questions' not in st.session_state:
    st.session_state['questions'] = pd.DataFrame()

st.title('Day-based Vocabulary Quiz')

# Sidebar: input name and choose day
with st.sidebar:
    name = st.text_input('Enter your name:')
    day = st.selectbox('Select day (1-30):', list(range(1, 31)))
    if st.button('Start Test'):
        # Load questions and reset state
        data = load_data('nawl.csv')
        st.session_state['questions'] = data[data['day'] == day].reset_index(drop=True)
        st.session_state['submitted'] = False
        st.session_state['wrong_df'] = None
        st.experimental_rerun()

# Prompt if no test loaded\if st.session_state['questions'].empty or not name:
    st.info('Please enter your name and select a day, then click "Start Test".')
else:
    questions = st.session_state['questions']
    st.header(f'Vocabulary Quiz: Day {day}')
    st.write(f'Student: {name}')
    # Quiz form
    with st.form('quiz_form'):
        answers = []
        for idx, row in questions.iterrows():
            st.markdown(f"**Q{idx+1}.** {row['English Definition']} ({row['POS']})")
            ans = st.text_input('', key=f'answer_{idx}')
            answers.append(ans)
        if st.form_submit_button('Submit Answers'):
            wrong = []
            for i, row in questions.iterrows():
                user_ans = st.session_state.get(f'answer_{i}', '').strip().lower()
                correct = str(row['Meanings']).strip().lower()
                if user_ans != correct:
                    wrong.append((i+1, row['English Definition'], row['POS'], row['Meanings']))
            st.session_state['wrong_df'] = pd.DataFrame(wrong, columns=['No.', 'Definition', 'POS', 'Answer'])
            st.session_state['submitted'] = True
            st.experimental_rerun()

# Show results after submission
if st.session_state['submitted']:
    total = len(st.session_state['questions'])
    wrong_df = st.session_state['wrong_df']
    correct = total - len(wrong_df)
    st.success(f"{name}, you answered {correct} out of {total} correctly!")
    if not wrong_df.empty:
        st.warning('Questions you missed:')
        st.table(wrong_df)
        if st.button('Retake missed'):
            # Retake only wrong questions
            idxs = wrong_df['No.'] - 1
            st.session_state['questions'] = st.session_state['questions'].iloc[idxs].reset_index(drop=True)
            st.session_state['submitted'] = False
            st.session_state['wrong_df'] = None
            st.experimental_rerun()
