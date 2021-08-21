# Advent of Code 2020

These are my solutions for Advent Of Code 2020 algorithmic puzzles. See: https://adventofcode.com/2020  

I started doing these puzzles during the Advent 2020, then had a long break, then kept solving something from time to time in spare time. Finished in August 2021. It was a great fun :)

Regarding implementation, I started day 1 with Go, but then decided to use Python, because it is convenient for such small programs. Another solution not in pure Python is day 23, part 2 - I wrote also an implementation in C to compare performance, just out of curiosity (see comment in day23/solve2.c).

Usually I love clean code, but this time I did not spend much time refactoring or documenting what I did after finding the solution (and highly-algorithmic code is always difficult to understand no matter how good you write it). Nevertheless, some puzzles have modest algorithm descriptions in the code.
  
Most difficult puzzles for me were:
* Day 13, part 2 - brute-force solution was easy, but to find solution for full dataset in a reasonable time I had to lookup how other people did it and learn some maths (Chinese remainder theorem).
* Day 18 - maybe not very hard, because I knew from the beginning what to do, but I had to learn / refresh knowledge about parsing operators with precedence using reversed Polish notation.
* Day 20, part 2 - this was definitely the most complex puzzle. It involved geometrical transformations, backtracking search of possible solution space (with some optimisations to reduce the number of options checked) and finding patterns in an "image".
* Day 21 - it was not very hard, but I spent a lot of time trying to optimize algorithmic complexity of the solution (it did not work for full dataset in a reasonable time) just to realize that I missed some property of the data in the puzzle that makes the solution search space many orders of magnitude smaller.
