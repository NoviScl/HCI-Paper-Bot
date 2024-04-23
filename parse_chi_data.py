import json 
import re
import os

# decide if it is a main conference paper
def paper_filter(paper):
    title_prefix = paper["title"].strip().split()[0]
    
    ## remove demos 
    if re.match(r'^D\d+:', title_prefix):
        return False 
    
    ## remove LBWs
    if re.match(r'^LBW\d+:', title_prefix):
        return False
    
    ## remove panels
    if title_prefix.startswith("Panel:"):
        return False
    
    ## remove empty entries
    if "abstract" not in paper or len(paper["abstract"]) < 50:
        return False
    if len(paper["authors"]) < 1:
        return False
    
    return True

## scan through all papers and return a list 
def find_all_papers():
    filenames = os.listdir("SIGCHI_data")
    return_lst = []
    counter = 0

    for filename in filenames:
        if filename.endswith("json"):
            filename = os.path.join("SIGCHI_data", filename)

            with open(filename, "r") as f:
                data = json.load(f)
            
            for paper in data["contents"]:
                if paper_filter(paper):
                    return_lst.append(paper)
                    counter += 1
                    # if counter % 1000 == 0:
                    #     print (paper["title"].strip())
                    #     print (paper["abstract"].strip())

            # print (counter)

    return return_lst


if __name__ == "__main__":
    # filenames = os.listdir("SIGCHI_data")
    # counter = 0

    # for filename in filenames:
    #     print (filename)
    #     filename = os.path.join("SIGCHI_data", filename)

    #     with open(filename, "r") as f:
    #         data = json.load(f)
        
    #     for paper in data["contents"]:
    #         if paper_filter(paper):
    #             counter += 1
    #             if counter % 1000 == 0:
    #                 print (paper["title"].strip())
    #                 print (paper["abstract"].strip())

    #     print (counter)

    with open("filtered_papers.json", "r") as f:
        filtered_papers = json.load(f) 
    for paper in filtered_papers:
        print (paper["title"].strip())