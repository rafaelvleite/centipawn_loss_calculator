# python-chess-analysis

The objective of this program is to generate an in depth game analysis

In addition to engine centipawn evaluations this program also provides metrics related to:
1) Material: Delta between sum of piece values for white and black
2) Development: Delta between the number of pieces (not pawns) no longer on their starting squares 
3) Mobility: Delta between the number of total legal moves
4) Control: Delta between the number of squares controlled by both sides.  This is associated with SPACE.
5) Tension (pressure): Delta between the number of attacking pieces for both sides
6) King safety: A weighted king tropism using the simple Chebyshev distance as the max of the 
   distance of the ranks or the files weighted based on piece values

The program identifies innaccuracies, mistakes and blunders based on the engine evaluation cp deltas and also 
indicates which side played a higher quality game overall based on the relative number of inaccuracies, mistakes, 
and blunders.

This early code assumes the PGN contains one game

NOTE: This code relies on the python-chess library. You need to install the python-chess package.

In the first block of the notebook your will find a number of variables that you can tinker with

Be sure to modify the path to your project folder, the path to your engine, your engine file name, and the pgn file name.
Also be sure to modify TOTALTIME that is your desired analysis time in minutes.  The program will convert this into an
analysis time per move in milliseconds.
