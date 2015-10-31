# ChessDetectorMoveFinder
Hack project for CSUA Hackathon Fall 2015.

# Summary
In this project, we've developed a system that assists a player in a game of chess by utilizing an ASUS Prime sensor to detect a chess board and its game state. When it is the player's turn, the program will look up the best move and announce the recommended move. An additional applicaiton is that this can be used to help give advice to someone trying to learn how to play.

# Method
This project was mainly broken up into 3 portions:

*1.* Detection and Vision of the chess board.

*2.* Search & Recommendation of the best move.

*3.* Translation of string and announcing it.


## Vision
The large majority of the code to detect the chess board is in `detection.py`, with helper functions from  `difference.py` and `unrotate.py`.
The vision portion of the project was the trickiest as we wanted our project to be invariant to many different factors such as rotation. A lot of image preprocessing was necessary in order to be able to appropriately detect location of pieces and give appropriate advice. We mainly used OpenCV2 to be able to handle these operations. This step consisted of setting up the sensor, polling for a new image every given interval and then performing operations that would identify pieces. We took advantage of image gradients in order to eventually find a bounding box, where we then could isolate the image and try to determine if squares contained a black or white piece.

## Getting Best Move
An internal representation of the board state is then maintained to be able to track changes as we receive information from the vision portion of the code.
We utilized an open source engine Stockfish to help make suggestions for the player.
We also allowed two different modes where the program will either output the best move or it would output just a score, which would be based on the potential score the player could make if they made the "best move." In this way, a player would be encouraged to think about certain moves and understand the potential for certain shifts in the game.

## Translation
Once the program has determined the appropriate move, we used pyttsx which is a Python library for text-to-speech. A player could then make moves and can just wait for the program to announce the best move rather than look at the computer screen to see what the best move is.

