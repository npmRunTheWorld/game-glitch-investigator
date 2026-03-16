# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").


1. difficulty system errors, like Easy difficulty ranges from 1 to 20, and Mid Difficulty ranges from 1 to 100 while hard difficulty is from 1 to 50

2. Wrong guess can award points

3. New game doesnt reset score


---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).


1. I allowed for 3 sub agents to spawn one would be a PM with goals for finding bugs and notifying the developer agent. The developer agent would then fix it and the QA agent would check the work

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

1. Yes the goal is for the Agent QA to write these tests

---


## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.


1. Definately start with plan mode to get everything organized and mission planned.
2. Create defiend /configs with Claude.md allowing it to understand the global context and repeatable process
3. Save and use ephimeral contexts from SESSION_NOTES or CHANGELOG.md files.
4. Having some sort of sub agent or alternate agent which would help with Testing the code and summarize changes 

