# Python_Compiler_TINY

This is an effort to learn more about compilers by creating one. I was watching a Primeagen video where he is reviewing a blog post which highlights some challenging software engineering projects. One of the projects was to build a compiler. I dived deeper into [this link](https://austinhenley.com/blog/teenytinycompiler1.html) where Austin Henley has done an incredible job of teaching how to build a very simple compiler using Python. This is a link to his [GitHub repo](https://github.com/AZHenley/teenytinycompiler). 

I have currently finished part 1, which involves creating the Lexer.
- Added functionality for identifiers and keywords
- Added functionality for numbers
- Added functionality for strings
- Added functionality for comments
- Added operators

Finished coding the Parser. 
- Created the respective grammar in grammar.txt
- Each aspect of the grammar is coded as functions in parser.py
- The parser will check the syntax of the input code
- It also checks for undeclared variables and if labels match the gotos