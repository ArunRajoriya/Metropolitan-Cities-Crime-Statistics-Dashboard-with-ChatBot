import requests
import time
import json

URL = "http://127.0.0.1:5000/chat"

questions = [

    # ===== YEAR TOTAL =====
    "How many total arrests were made in 2020?",
    "What was the overall arrest count in 2019?",
    "Can you tell me the total arrests recorded in 2018?",
    "How many people were arrested across all cities in 2017?",
    "What is the combined arrest figure for 2016?",
    "Give me the total number of arrests in 2020.",
    "Across metropolitan cities, how many arrests happened in 2019?",
    "What was the nationwide metro arrest total in 2018?",
    "Show me the arrest volume for 2017.",
    "How large was the arrest count in 2016?",

    # ===== GENDER =====
    "How many males were arrested in 2020?",
    "What was the total number of female arrests in 2019?",
    "Show me male arrest statistics for 2018.",
    "How many women were arrested across cities in 2017?",
    "Give me the male arrest count for 2016.",
    "What was the female arrest total in 2020?",
    "Total male arrests across all cities in 2017?",
    "Female arrest summary for 2016?",
    "In 2020, how many men were taken into custody?",
    "Women arrest numbers for 2017?",

    # ===== SINGLE CITY =====
    "How many arrests were recorded in Delhi in 2019?",
    "What was Mumbai’s arrest count in 2020?",
    "Show me the total arrests in Pune for 2018.",
    "How many people were arrested in Chennai during 2017?",
    "Arrest statistics for Hyderabad in 2016?",
    "Female arrests in Delhi for 2020?",
    "Male arrests in Mumbai for 2019?",
    "Total arrests in Ahmedabad in 2017?",
    "How did Surat perform in arrests in 2016?",
    "Give me Delhi’s arrest data for 2020.",

    # ===== MULTI YEAR =====
    "Compare Delhi’s arrest figures for 2016 and 2019.",
    "How did Mumbai’s arrests change between 2017 and 2020?",
    "Show Pune’s arrest trend from 2018 to 2020.",
    "Compare Chennai’s arrests in 2016, 2018, and 2020.",
    "How have Hyderabad’s arrests evolved from 2017 to 2019?",
    "Show Delhi’s arrest growth over 2016, 2017, and 2018.",
    "Compare Mumbai’s arrest record in 2019 and 2020.",
    "Female arrests in Delhi from 2018 to 2020?",
    "Male arrests in Chennai between 2017 and 2019?",
    "How consistent were Pune’s arrests from 2016 to 2020?",

    # ===== MULTI CITY =====
    "Compare Delhi and Mumbai arrests in 2019.",
    "How did Pune and Chennai perform in 2020?",
    "Compare Hyderabad and Ahmedabad arrests in 2018.",
    "Which had more arrests in 2017: Delhi or Surat?",
    "Show Mumbai vs Pune arrest comparison for 2016.",
    "Compare female arrests between Delhi and Chennai in 2019.",
    "Male arrest comparison for Mumbai and Hyderabad in 2020.",
    "Arrest comparison between Ahmedabad and Surat in 2018.",
    "Delhi, Mumbai, and Pune arrests in 2019?",
    "Which city recorded higher arrests in 2020: Chennai or Hyderabad?",

    # ===== RANKING =====
    "Which city had the highest arrests in 2019?",
    "Which metro recorded the lowest arrests in 2020?",
    "Show the top three cities by arrests in 2018.",
    "Top 3 male arrest cities in 2020?",
    "Which city had the least female arrests in 2017?",
    "Highest arrest city in 2016?",
    "Lowest arrest city in 2019?",
    "Top three performing cities by arrest numbers in 2020?",
    "Rank cities by female arrests in 2018.",
    "Which metro topped the arrest chart in 2017?",

    # ===== CRIME DATASET =====
    "How many murder cases were reported in 2019?",
    "Show rape statistics for 2020.",
    "Theft case details in 2018?",
    "Murder investigation summary for 2017.",
    "Compare murder cases between 2018 and 2019.",
    "Rape case investigation stats for 2020.",
    "Theft statistics across years 2016 and 2018.",
    "What were the murder case totals in 2016?",
    "Show crime breakdown for rape in 2019.",
    "Provide theft case summary for 2020.",

    # ===== JUVENILE =====
    "How many juveniles were arrested in 2019?",
    "Juvenile boys arrest figures for 2020?",
    "Juvenile girls statistics in 2018?",
    "Top cities for juvenile arrests in 2017?",
    "Compare juvenile arrests between 2019 and 2020.",

    # ===== EXTRA NATURAL VARIATIONS =====
    "What does the arrest landscape look like in 2020?",
    "How severe were arrests in 2019 overall?",
    "Is Delhi seeing higher arrests compared to Mumbai in 2019?",
    "Give me a breakdown of arrests in Chennai in 2018.",
    "How did arrest patterns shift between 2016 and 2020?",
    "Show overall custody figures in 2017.",
    "Which city lagged behind in arrests in 2018?",
    "Provide a comparative arrest overview for 2019.",
    "Was 2020 worse than 2019 in terms of arrests?",
    "Summarize the arrest scenario in metropolitan cities for 2016."
]

print("\n=========== STARTING FULL 100 QUESTION TEST ===========\n")

total = len(questions)
success = 0
fail = 0

start_time = time.time()

for i, question in enumerate(questions, start=1):

    print("------------------------------------------------------")
    print(f"[{i}] QUESTION: {question}")

    try:
        response = requests.post(URL, json={"message": question})

        if response.status_code != 200:
            print("❌ HTTP ERROR:", response.status_code)
            fail += 1
            continue

        data = response.json()

        print("✅ RESPONSE TYPE:", data.get("type"))
        print("📦 FULL RESPONSE:")
        print(json.dumps(data, indent=4))

        success += 1

    except Exception as e:
        print("❌ EXCEPTION:", str(e))
        fail += 1

end_time = time.time()

print("\n=========== TEST SUMMARY ===========")
print("Total Questions :", total)
print("Successful      :", success)
print("Failed          :", fail)
print("Success Rate    :", f"{(success/total)*100:.2f}%")
print("Time Taken      :", round(end_time - start_time, 2), "seconds")
print("====================================\n")