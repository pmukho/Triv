import pandas as pd
from openai import OpenAI, RateLimitError
import wikipediaapi
from os import environ
import dotenv
import json
dotenv.load_dotenv()

wiki_wiki = wikipediaapi.Wikipedia(user_agent=environ['OPENAI_USER_AGENT'], language='en')
llm = OpenAI()
def sample_df(df, category_column, n=10):
    """
    Should only run after seed.py has been run to populate the database with articles.
    Sample n rows for each category in the DataFrame.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    category_column : str
        The column that contains the categories.
    n : int, optional
        The number of rows to sample for each category. The default is 10.

    Returns
    -------
    pandas.DataFrame
        The sampled DataFrame of questions.

    """

    
    # Sample n rows for each category
    sampled_df = df.groupby(category_column).apply(lambda x: x.sample(n=n, replace=False)).reset_index(drop=True)

    # # Group by category and convert to dictionary
    # category_dict = {key: group.to_dict(orient="records") for key, group in sampled_df.groupby(category_column)}

    # # Print the dictionary
    # print(category_dict.keys())
    # print(category_dict["Arts"][0])

    return sampled_df

def seed_questions(sampled_df):
    ok = True
    questions = []
    for i, row in sampled_df.iterrows():
        print(f"Generating question for article {row['title']}")
        article_name = row["title"]
        page = wiki_wiki.page(article_name)
        

        prompt = "Create a NAQT style triva prompt using 3 clues which contain one fact each in decreasing obscurity given the following abstract:\n" + page.summary
        prompt += "\n Each clue should be less than 15 words long. The first clue should be prefaced with '1.', the second with '2.', and the third with '3.'. The answer should be prefaced with 'ANSWER:'."
        
        # NOTE: The following line actually makes the question generation significantly worse if used instead of the above line.
        # This is likely because the weird symbol makes the prompt out of distribution.

        # prompt += "\n The first clue should be prefaced with '*|*', the second with '*|*', and the third with *|*.'. The answer should be prefaced with '*|*'."
        while True:
            try: 
                completion = llm.chat.completions.create(
                    # model="gpt-4o",
                    model="gpt-4.5-preview",
                    messages=[
                        {"role": "developer", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                # print(completion.choices[0].message)
                print(completion.choices[0].message.content)
                content = completion.choices[0].message.content

                prompt1 = content.split("1.")[1].split("\n2.")[0].strip()
                prompt2 = content.split("\n2.")[1].split("\n3.")[0].strip()
                prompt3 = content.split("\n3.")[1].split("ANSWER:")[0].strip()
                answer = content.split("ANSWER:")[1].strip()

                if len(prompt1) and len(prompt2) and len(prompt3) and len(answer):
                    question = {'hint1': prompt1, 'hint2': prompt2, 'hint3': prompt3, 'answer': answer, 'category': row["category"], 'id': article_name}
                    questions.append(question)
                    print(question)
                    break
                else:
                    print(f"Invalid completion for article {article_name}. Trying again.")
            except RateLimitError as e:
                print(e)
                if e.type == 'insufficient_quota':
                    error = "Out of money"
                    ok = False
                    break
                else:
                    print("Rate limit error. Trying again.")
        if not ok:
            break        
    print(len(questions))
    questions_df = pd.DataFrame(questions)
    json_path = "db/data/questions.json"
    with open(json_path, 'w') as jsonfile:
        json.dump(questions, jsonfile)
    return questions_df

if __name__ == "__main__":
    # Read the CSV file
    df = pd.read_csv("db/data/wiki_articles.csv")
     # Define the column that contains categories
    category_column = "category"

    # Sample n rows for each category
    sampled_df = sample_df(df, category_column, n=5)
    print(len(sampled_df))

    
    # question_df = seed_questions(sampled_df)

    # # Save the questions to a CSV file
    # question_df.to_csv("db/data/questions.csv", index=False)
