from groq import Groq
import os

def curate_newsletter(articles: list, user_topics: list):
    """Use Groq LLM to curate and summarize articles"""
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Combine articles into context
    context = "\n\n".join([
        f"Source: {a['source']}\n{a['content']}" 
        for a in articles
    ])
    
    prompt = f"""You are an AI newsletter curator. Based on these articles about {', '.join(user_topics)}, create:

1. A catchy subject line
2. A 3-paragraph summary of the most important developments
3. One key learning point
4. One action item the reader can do today

Articles:
{context}

Format your response as:
SUBJECT: [subject line]
SUMMARY: [3 paragraphs]
LEARNING: [key point]
ACTION: [one specific task]
"""
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content