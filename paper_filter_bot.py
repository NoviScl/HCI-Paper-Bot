from openai import OpenAI
import anthropic
from utils import call_api
from tqdm import tqdm 
from parse_chi_data import find_all_papers
import json
import os
import retry

@retry.retry(tries=3, delay=2)
def paper_filter(paper, client, model, seed):
    ## use LLM to decide whether the paper satisfied the criteria 
    prompt = "You are a helpful literature review assistant whose job is to read the below paper and help me decide if it satisfies my criteria. The criteria are:\n"
    prompt += "(1) The paper conducts both quantitative surveys and qualitative interviews. The paper's main contribution should be drawing insights from the survey and interview results.\n"
    prompt += "(2) The participants involved are all recruited from online crowdsourcing platforms, such as Amazon Mechanical Turk or Prolific. And the participants shouldn't be from special backgrounds such as domain experts in niche areas.\n"
    prompt += "(3) The surveys or interviews do not require participants to use any special equipment or software, such as VR headsets or internal chat apps.\n"
    prompt += "(4) The surveys and interviews should not be overly long, for example, involving multi-day longitudinal tracking. Participants should be able to finish the survey or interview within an hour.\n"
    prompt += "(5) The research questions that the paper is trying to answer should not be very time-sensitive, such as studying the impact of COVID-19.\n\n"
    prompt += "The paper is:\n" 
    prompt += "Title: " + paper["title"].strip() + "\n" 
    prompt += "Abstract: " + paper["abstract"].strip() + "\n\n"
    prompt += "Please give me a binary answer (yes/no) on whether this paper satisfies both criteria. Do not include any other explanation, the output should be either yes or no."
    
    prompt_messages = [{"role": "user", "content": prompt}]
    response, cost = call_api(client, model, prompt_messages, temperature=0., max_tokens=1, seed=seed, json_output=False)
    return prompt, response, cost


if __name__ == "__main__":
    engine = "claude-3-opus-20240229"
    seed = 2024 

    with open("keys.json", "r") as f:
        keys = json.load(f)

    ANTH_KEY = keys["anthropic_key"]
    OAI_KEY = keys["api_key"]
    ORG_ID = keys["organization_id"]
    S2_KEY = keys["s2_key"]
    
    if "claude" in engine:
        client = anthropic.Anthropic(
            api_key=ANTH_KEY,
        )
    else:
        client = OpenAI(
            organization=ORG_ID,
            api_key=OAI_KEY
        )

    ## unit test
    # all_papers = [
    #     {
    #         "title": "Will AI Console Me when I Lose my Pet? Understanding Perceptions of AI-Mediated Email Writing",
    #         "abstract": "Large language models are increasingly mediating, modifying, and even generating messages for users, but the receivers of these messages may not be aware of the involvement of AI. To examine this emerging direction of AI-Mediated Communication (AI-MC), we investigate people's perceptions of AI written messages. We analyze how such perceptions change in accordance with the interpersonal emphasis of a given message. We conducted both large-scale surveys and in-depth interviews to investigate how a diverse set of factors influence people's perceived trust in AI-mediated writing of emails. We found that people's trust in email writers decreased when they were told that AI was involved in the writing process. Surprisingly trust increased when AI was used for writing more interpersonal emails (as opposed to more transactional ones). Our study provides insights regarding how people perceive AI-MC and has practical design implications on building AI-based products to aid human interlocutors in communication."
    #     }
    # ]

    all_papers = find_all_papers()

    filtered_papers = []

    for paper in tqdm(all_papers):
        try:
            prompt, response, cost = paper_filter(paper, client, engine, seed)

            if response.strip().lower() == "yes":
                filtered_papers.append(paper)
                print ("Passed: ", paper["title"].strip())
        except: 
            print ("Error in prompting, skipped: ", paper["title"].strip())
            continue
        
    print ("total number of acceptable papers: ", len(filtered_papers))
    with open("filtered_papers.json", "w") as f:
        json.dump(filtered_papers, f, indent=4)





