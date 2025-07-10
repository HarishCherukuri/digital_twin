import duckdb as duck
import pandas as pd
from agents import function_tool

DB_PATH = 'data/dt_questions.db'

conn =duck.connect(DB_PATH)
conn.execute("CREATE SEQUENCE IF NOT EXISTS question_id_seq START 1")
conn.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY DEFAULT nextval('question_id_seq'), question TEXT, answer TEXT)")
conn.commit()
conn.close()

@function_tool
def record_question_with_no_answer(query: str) -> str:
    """
    Prior to recording the question, check if the question is already in the database by using the get_questions_with_no_answer function.
    If it is, return "Question already recorded"
    If it is not, record the question and return "Question added successfully"
    Record a question that the user has asked that agent cannot answer so that it can be leveraged to improve the agent's knowledge for future questions.
    Args:
        query: The question that the user asked, which agent cannot answer
    """
    conn =duck.connect(DB_PATH) 
    conn.execute("INSERT INTO questions (question) VALUES (?)", ([query]))
    conn.commit()
    conn.close()
    return "Question added successfully"


@function_tool
def get_questions_with_no_answer() -> str:
    """
    Get all questions that have no answer from the database. So the agent can identify if a question has already been recorded. 
    If not agent can record the question with no answer. If found, return the questions with ID and question.
    """
    conn =duck.connect(DB_PATH) 
    conn.execute("SELECT id, question FROM questions WHERE answer IS NULL")
    rows = conn.fetchall()
    conn.close()
    if rows:
        return "\n".join(f"ID-{row[0]}: {row[1]}" for row in rows)
    else:
        return "No questions without answer found"
    

@function_tool
def record_answer_for_question(id: int, answer: str) -> str:
    """
    Record the answer for a question that has no answer for future reference and help imporve the context of the agent.
    Args:
        id: The ID of the question to be answered
        answer: The answer to the question for future reference and help imporve the context of the agent.
    """
    conn =duck.connect(DB_PATH) 
    conn.execute("UPDATE questions SET answer = ? WHERE id = ?", (answer, id))
    conn.commit()
    conn.close()
    return "Answer added successfully"
@function_tool
def get_questions_with_answer() -> str:
    conn =duck.connect(DB_PATH) 
    conn.execute("SELECT id, question, answer FROM questions WHERE answer IS NOT NULL")
    rows = conn.fetchall()
    conn.close()
    if rows:
        return "\n".join(f"ID:{row[0]} Question: {row[1]} Answer: {row[2]}" for row in rows)
    else:
        return "No questions with answer found"
    
def get_question_tools() -> list:
    """
    Get all the question tools that can be used to record questions and answers.
    """
    return [record_question_with_no_answer, get_questions_with_no_answer, record_answer_for_question, get_questions_with_answer]

def get_questions_with_no_answer_text() -> str:
    """
    Get all questions that have no answer from the database. So the agent can identify if a question has already been recorded. 
    If not agent can record the question with no answer. If found, return the questions with ID and question.
    """
    conn =duck.connect(DB_PATH) 
    conn.execute("SELECT id, question FROM questions WHERE answer IS NULL")
    rows = conn.fetchall()
    conn.close()
    return "\n".join(f"ID-{row[0]}: {row[1]}" for row in rows)