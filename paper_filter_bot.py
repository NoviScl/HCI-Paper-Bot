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
    prompt = "You are a helpful literature review assistant whose job is to read the below paper and help me decide if it satisfies all my criteria. The criteria are:\n"
    prompt += "(1) The paper is about conducting both large-scale quantitative surveys and in-depth qualitative interviews with human participants. The paper's main contribution should be to draw insights from the survey and interview results (conducting human evaluation of a model or system does not count).\n"
    prompt += "(2) The participants involved are all recruited from online crowdsourcing platforms, such as Amazon Mechanical Turk or Prolific. And the participants shouldn't be from special backgrounds such as domain experts in niche areas.\n"
    prompt += "(3) The surveys and interviews do not require participants to use any special equipment or software, such as VR headsets or internal apps.\n"
    prompt += "(4) The surveys and interviews should not be overly long, for example, involving multi-day longitudinal tracking. Participants should be able to finish the survey or interview within an hour.\n"
    prompt += "(5) The research questions that the paper is trying to answer should not be very time-sensitive, such as studying the impact of COVID-19.\n\n"
    prompt += "The paper is:\n" 
    prompt += "Title: " + paper["title"].strip() + "\n" 
    prompt += "Abstract: " + paper["abstract"].strip() + "\n\n"
    prompt += "Please give me a binary answer (yes/no) on whether this paper satisfies all the criteria (you should say no as long as any one of the criteria is not met). Do not include any other explanation, the output should be either yes or no."
    
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
    #     },
    #     {
    #         "title": "I Like Their Autonomy and Closeness to Me: Uncovering the Perceived Appeal of Social-Media Influencers",
    #         "abstract": "The proliferation of influencers on social-media platforms has drawn considerable research attention, particularly in the field of marketing. Nevertheless, there is limited understanding among HCI and communication researchers of what leads these social-media influencers’ (SMIs’) audiences to favor and choose their content over traditional media. To fill this gap, we conducted semi-structured interviews with 45 SMI audience members. Our findings revealed a total of eight categories of SMIs’ appeals, i.e., factors that made the interviewees favor their content over traditional media. These appeals can further be grouped into three categories: content, presentation, and closeness. In particular, we identified the key role of SMIs’ perceived high autonomy and independence, which led both their content and their presentation styles to be seen as distinct from and more appealing than traditional media. Likewise, four closeness appeals made our participants feel emotionally attached to SMIs, resulting in sustained engagement."
    #     },
    #     {
    #         "title": "Interface Design for Crowdsourcing Hierarchical Multi-Label Text Annotations",
    #         "abstract": "Human data labeling is an important and expensive task at the heart of supervised learning systems. Hierarchies help humans understand and organize concepts. We ask whether and how concept hierarchies can inform the design of annotation interfaces to improve labeling quality and efficiency. We study this question through annotation of vaccine misinformation, where the labeling task is difficult and highly subjective. We investigate 6 user interface designs for crowdsourcing hierarchical labels by collecting over 18,000 individual annotations. Under a fixed budget, integrating hierarchies into the design improves crowdsource workers' F1 scores. We attribute this to (1) Grouping similar concepts, improving F1 scores by +0.16 over random groupings, (2) Strong relative performance on high-difficulty examples (relative F1 score difference of +0.40), and (3) Filtering out obvious negatives, increasing precision by +0.07. Ultimately, labeling schemes integrating the hierarchy outperform those that do not - achieving mean F1 of 0.70."
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





