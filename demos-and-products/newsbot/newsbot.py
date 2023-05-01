"""
Sample code for getting a list of news articles, having OpenAI summarize them, and then deploying an email with the summaries.
"""

from phasellm.agents import EmailSenderAgent, NewsSummaryAgent
from phasellm.llms import OpenAIGPTWrapper

queries = ["inflation", "openai", "llm"] # We will generate a summary for each element in the list

##########################################################################
#
# ENVIRONMENT VARIABLES (Gmail, News API, etc.) (START)
# Update this to customize your newsbot experience.
#

import os
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI and newsapi.org API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
news_api_api_key = os.getenv("NEWS_API_API_KEY")

# Gmail credentials.
gmail_email = os.getenv("GMAIL_EMAIL")
gmail_password = os.getenv("GMAIL_PASSWORD")

RECIPIENT_EMAIL="<who will get the email summary>"
SENDER_NAME="<who is sending the email>"

#
# ENVIRONMENT VARIABLES (END) 
#
##########################################################################

def getArticlesAndSummarize(news_agent, llm, query, days_back=1, include_description=True, max_articles=30):
    """
    See NewsSummaryAgent docs for what the above variables mean.
    """

    # First, we obtain the news articles for the query We limit this to 30 articles going back 1 day.
    news_articles = news_agent.getQuery(query, days_back=1, include_descriptions=True, max_articles=30)

    # Set up messages for summarization.
    system = "You are a helpful news summarizer. We will provide you with a list of news articles and will ask that you summarize them and retain links to source by adding footnotes. For example, if you have a news article describing XYZ and URL to the article, you would discuss XYZ[1] and add '[1] URL' to the bottom of the message. Note that the footnotes should be counted as of the summary; you do not need to keep the numbers from the earlier order, just from your summary. In other words, footnotes should start at 1, 2, 3, etc..."
    user_prompt = f"The articles below are about '{query}'. Please summarize them into a short paragraph with link retained as per the earlier instructions.\n\n{news_articles}"
    messages = [{"role":"system", "content":system}, {"role":"user", "content":user_prompt}]

    news_message = llm.complete_chat(messages)

    return news_message

# News agent
news_agent = NewsSummaryAgent(news_api_api_key, name="tester agent")

# OpenAI model, GPT-4. You can use other models, of course.
llm = OpenAIGPTWrapper(openai_api_key, model="gpt-4")

news_content = ""
for query in queries:
    content = getArticlesAndSummarize(news_agent, llm, query)
    news_content += f"# News for {query}\n\n{content}\n\n"

# Generate subject line.
news_subject = f"News about: {', '.join(queries)}"

# Send email.
e = EmailSenderAgent(SENDER_NAME, 'smtp.gmail.com', gmail_email, gmail_password, 587)
e.sendPlainEmail(RECIPIENT_EMAIL, news_subject, news_content)