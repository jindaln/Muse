# Proposal

## What will (likely) be the title of your project?

Muse

## In just a sentence or two, summarize your project. (E.g., "A website that lets you buy and sell stocks.")

A website that allows educators to create customizable music quizzes that are automatically graded. Features will include perfect pitch training,
meter recognition, tempo matching, key recognition.

## In a paragraph or more, detail your project. What will your software do? What features will it have? How will it be executed?

The thesis of the project is that it enables music teachers to easily create music theory quizzes that they don't have to manually grade. Specifics on features:
-pitch training, where it asks you to replicate a note and tells you far off you were (using Microsoft WebAudio API)
-meter training: plays you a section of a track and asks you what the meter is and checks it against the actual time signature of the track (using Spotify API)
-tempo training: plays you a section of a track and asks you to tap out the tempo and provides feedback on both accuracy and consistency (tempo info collected from Spotify API)
-key training: asks you to identify what key and mode a track is in and tells you if you you're right (using Spotify API)
We will also allow both students and teachers to access some data. Students will be able to see graphs of their prior scores. Teachers will be able
to see graphs of classroom trends and distributions of performance on specific quizzes. We will store this data in SQL.

We will implement the UI in HTML and the backend logic in Python.

## If planning to combine CS50's final project with another course's final project, with which other course? And which aspect(s) of your proposed project would relate to CS50, and which aspect(s) would relate to the other course?

TODO, if applicable

## In the world of software, most everything takes longer to implement than you expect. And so it's not uncommon to accomplish less in a fixed amount of time than you hope.

### In a sentence (or list of features), define a GOOD outcome for your final project. I.e., what WILL you accomplish no matter what?

Get the 4 features working without customizability of quizzes.

### In a sentence (or list of features), define a BETTER outcome for your final project. I.e., what do you THINK you can accomplish before the final project's deadline?

Get 4 features working with customizability of quizzes.

### In a sentence (or list of features), define a BEST outcome for your final project. I.e., what do you HOPE to accomplish before the final project's deadline?

Get features 4 working with customizability and data anlaytics.

## In a paragraph or more, outline your next steps. What new skills will you need to acquire? What topics will you need to research? If working with one of two classmates, who will do what?

We will need to familiarize ourselves with the APIs that we are using and we will need to plan out the pages of the site. Our research will include both
research on music theory and how it is currently taught as well as technical research on the APIs we want to use and how we want to analyze the data that
we will display to teachers and students. We will also need to figure out how to implement all of a website without the starter code that CS50 typically gives us.
Nikita will work on developing the Python helper functions for the pitch and key features, and Lavanya will work on the meter and tempo features. Once we are done with that,
we will develop the HTML layout for each of the features. We will then plan out the webpages we need and start writing the HTML necessary. We will then integrate
the Python and HTML to create a fully functioning site. We will then incorporate SQL and basic data analytics to make the platform more exciting and useful.
