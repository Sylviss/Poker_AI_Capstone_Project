# Poker AI
----------------
This is the readme file for the Poker AI project. First on the project, I want you to learn about how to use basic feature about Github. Try to learn about commit, issues, pull request and branches. The first week will only be about material. Try to scrape some thesis from others university. We can't understand them anyway, because if we can, maybe we should graduate. 
# Installation & running guide:
## Prerequisites:
This repository assumes Python 3.11 or newer is used.
Used package:
- bext

## Installation guide:
- Install the code from the repo
- Run the code:
<p align="left">
  <img src="https://github.com/Sylviss/Poker_AI_Capstone_Project/blob/main/doc/run_the_code.PNG">
</p>

## Run the code:
- Change the constant value in the poker_ai/poker/play.py:
<p align="center">
  <img src="https://github.com/Sylviss/Poker_AI_Capstone_Project/blob/main/doc/play_constant.PNG">
</p>

## The simple roadmap:
- [x] Simple warmup and learn to use Github
- [x] Find some material
- [x] Implement the basic UI and game structure
- [ ] Implement the AI:
    - [x] Implement the evaluate function using simple Monte-Carlo simulations
    - [x] Implement the Monte-Carlo simulation and probability-based AI
    - [ ] Implement the Monte-Carlo tree search-based AI
    - [ ] Implement a reinforcement learning for opponent modelling in the Monte-Carlo simulations
        - [ ] Improve the simulations so that it is not just straight all-in simulations.
        - [ ] Using opponent modelling to implement enumeration weighting, improving the CALL_CONFIDENT and the simulation itself (2.5.2.4, 2.6)
        - [ ] After enumeration weighting, use selective sampling to only simulate cases that have high weight to be relevant.
        - [ ] Implement adaptive sampling based on the current game state, opponents' behaviors, or other relevant factors.
    - [ ] Implement a supervised learning to calculate all constant that is relevant in the two above AI. 99% we will be using linear regression, because the function is a polynomial function.
- [ ] Implement a performance evaluation
- [x] Drink some water
- [x] Touch the grass

Try ur best.

