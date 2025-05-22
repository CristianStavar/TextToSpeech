# TextToSpeech
Python program that takes text input and pdf files and transform them to audio.
Basic program I made for myself to process text and pdf's into audio.

It uses the following libraries:

-**Coqui TTS** for transforming text to audio.

-**PyDub** for audio segmentation and combination.

-**PdfPlumber** for pdf file processing.

-**Num2Words** for text cleaning. Transforming numbers to text to improve Coqui's processing.

-**Re** for text cleeaning. Eliminates unwanted characters in the text improve Coqui's processing.

A sample of the program's UI , if no language is checked, it defaults to english :

![TextToSpeechUI](https://github.com/user-attachments/assets/fd2ec43f-c524-4535-bdaf-7fe6747b2675)
