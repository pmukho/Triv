import wikipediaapi
from openai import OpenAI


def print_categorymembers(categorymembers, level=0, max_level=1):
    for c in categorymembers.values():
        print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)


def test():
    wiki_wiki = wikipediaapi.Wikipedia(user_agent= 'SWEats (njwei@g.ucla.edu)', language='en')
    page_py = wiki_wiki.page('Pablo_Escobar')
    print("Page - Exists: %s" % page_py.exists())
    print("Page - Title: %s" % page_py.title)
    print("Page - Summary: %s" % page_py.summary)

    client = OpenAI()
    prompt = "Create a NAQT style triva prompt using 3 clues in decreasing obscurity given the following abstract:\n" + page_py.summary
    prompt += "\n The first clue should be prefaced with '1.', the second with '2.', and the third with '3.'. The answer should be prefaced with 'ANSWER:'."
    # prompt += "\n Each clue and question should be prefaced with *|*."
    
    completion = client.chat.completions.create(
        model="gpt-4o",
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

    prompt1 = content.split("1.")[1].split("2.")[0].strip()
    prompt2 = content.split("2.")[1].split("3.")[0].strip()
    prompt3 = content.split("3.")[1].split("ANSWER:")[0].strip()
    answer = content.split("ANSWER:")[1].strip()

    print('PROMPT 1', prompt1)
    print('PROMPT 2', prompt2)
    print('PROMPT 3', prompt3)
    print('ANSWER', answer)


    # print("Page - Abstract: %s" % page_py.section_by_title('Abstract').text)
    # print("Page - Text: %s" % page_py.text)

    # cat = wiki_wiki.page('Category:Physics')
    # print_categorymembers(cat.categorymembers)

if __name__ == '__main__':
    test()