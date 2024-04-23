## HCI Paper Bot 

This is simple paper bot that helps you filter through the past 6.5 years of CHI and CSCW papers (N=11K) to find papers that satisfy your criteria.

### Usage

1. Clone the repository. Install dependencies: `pip install openai anthropic`

2. Download the SIGCHI data from [this link](https://drive.google.com/file/d/1Yns5_cL0h6lnaVpRCsz8go7vYqXStU6R/view?usp=sharing) and unzip it. 

3. Customize your prompt in `paper_filter_bot.py` (line 13-22). 

4. Put your OpenAI / Anthropic API keys in `keys.json`. For OpenAI users, put your API key in `api_key` (you can also additionally specify `organization_id`). For Anthropic users, put your API key in `anthropic_key`. 

5. Run the bot using `python3 paper_filter_bot.py`.