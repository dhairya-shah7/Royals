import re
with open(r'C:\Users\Dhairya\Desktop\Rajasthan_Royals_SupeRR_Selector_Season_2_Methodology_Report.pdf', 'rb') as f:
    data = f.read()
    pages = re.findall(b'/Type\s*/Page\b', data)
    print("Page count:", len(pages))
