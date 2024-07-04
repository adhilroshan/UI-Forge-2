import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

# PROMPT_TEMPLATE = """
# Answer the question based only on the following context:

# {context} 

# ---

# Answer the question based on the above context: {question}
# """

PROMPT_TEMPLATE = """
Given a simple description of a website component, generate the HTML, CSS, and JavaScript code for that component. Use the context provided to help you generate the code.
generate stunning ui. 
Component Description: {question}

Context:
{context}

Code:
"""

GENERATE_LIT= """
Convert the following HTML, CSS, and JavaScript code into a Lit web component:

HTML:
{html}

CSS:
{css}

JavaScript:
{js}

To create the Lit web component, follow these steps:

1. Import the necessary dependencies from the Lit library.
2. Create a new class that extends LitElement.
3. Define the component's properties, if any.
4. Implement the render() method to return the component's HTML template.
5. Move the HTML markup from the provided HTML code into the render() method's template literal.
6. Move the CSS styles into a static styles property in the component class.
7. Move the JavaScript code into the component class methods or event handlers.
8. Encapsulate any DOM interactions or state management within the component class.
9. Use the @property decorator to define reactive properties, if needed.
10. Export the component class so it can be used in other parts of the application.

Once you have completed these steps, provide the Lit web component code as the solution.
"""

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = Ollama(model="codeqwen")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return formatted_response

def componentBundler(html:str, css:str,js:str):
    prompt_template = ChatPromptTemplate.from_template(GENERATE_LIT)
    prompt = prompt_template.format(html=html,css=css,js=js)
    print(prompt)

    model = Ollama(model="codeqwen")
    response_text = model.invoke(prompt)

    formatted_response = f"Response: {response_text}\n"
    print(formatted_response)
    return formatted_response


if __name__ == "__main__":
    main()
