The most significant design decision we made was how we arranged the tables in our database. We first created a users table because we needed some way
to record user information. We included a username and password in this table for obvious reasons, as well as user_id that corresponds to the session["id"]
cookie that the browser stores to determine which user is logged in. We also included a field for "identity" which indicates whether a user is a teacher or
a student. We needed this field because teachers and students have access to different functionality so we will need to know whether a user is a student or
a teacher. In the controller, we stored this identity in the "name" attribute of the session object in the browser so taht we could identify whether the current
session is that of a teacher or a student. We then use this "name" attribute to determine which history tempate to display to the user as the index page
("teacher_history.html") or ("tudent_history.html"). We also use the "name" attribute in our layout template, "layout.html", where we use jinja to display
a different navigation bar for teachers versus students. Wr chose to store the identity in a cookie because we needed access to it throughout the entire session
and it was session specific information. This saves us from having to search for the user in the database and check their identity every single time that we
need to distinguish between teachers and students. Our solution is more speed efficient. There is a security concern when we use a cookie, but information
about a user's status as teacher or student is not particularly sensitive and reveals nothing about their real human identity so we felt comfortable using the cookie.

The next table we made was the "quizzes" table. This table stored information about quizzes. We used a "quiz_name" field as the unique identifier for the table.
The field is a varchar, unlike most numerical identifiers. We chose to use a varchar primary key because this way we can directly display this primary key to the user
as opposed to having to use a numerical identifier to search the database for the quiz name which is a slow operation. This also enables teachers to share quizzes
with students by giving them the quiz name which we can then use to lookup the quiz and display to the student. This is much more user friendly since a human readable
quiz name is much easier to remember than a numerical id that is likely meaningless to the user and therefore easy to forget/lose.One downside to this
decision is that teachers have to select a unique quiz name when making the quiz, but this is not such a hard task, especially since the teacher won't have to
remember this quiz name (it is displayed on the index page), so we felt comfortable making this decision.

This table also stores three text fields: "meter_songs", "tempo_songs", and "key_songs". These fields each hold a string of song id's extracted from the
Spotify API. Each song id identifies a unique track that we can then conduct audio analysis on using the API (see Spotify API docs for further info). The song id's
are separated by a single space (example: "2yQZwi1P8AkkxxFhQ8rMEK 1ipcb9qXpSHWhSUvdxJhsx"). We tested out a variety of solutions before settling on storing the id's
in the quizzes table. We initially tried to store the id's in a global variable, but this attempt failed because the information disappeared once a new session
was started or a different user logged in. We also tried storing the entire HTML used to generate the specific quiz in the table, but this solution was memory
inefficient and used too much space. We eventually settled on storing the id's because these three strings are the minimum amount of information necessary to
generate a quiz. Thus, any user can access the form for the quiz just using the quiz name which greately improves usability and minimizes space used. One concern
with this approach was that the fields could get quite long, but the solution still, on average, uses less space than other options. We were also concerned
that it might be difficult to extract individual strings from the longer strong of id's, but the simple str.split(" ") method enabled us to convert each string
into a list of id's, which we could then perform operations on.

The last table we made was a "history" table that stores all of the instances of users taking quizzes. This table has primary key "history_id",
a "quiz_name" field that stores the name of the quiz. We search on this key when rendering "teacher_history.html" in order to find all the scores for a
specific quiz. We also have a field for "username" that stores the username of the user that took the quiz in this instance. We search on this key when rendering
"student_history" to find all the quizzes taken by a particular student. Lastly we have a field to store the score recieved on this attempt for the quiz.
We chose to have a separate history and quizzes table to save memory. We could have just had one history table and stored the meter song ids, tempo song ids,
and key song ids for each instance of the quiz, but that would have taken way more memory, so we chose to create separate history and quizzes tables to optimize memory
usage.

The other major design decisions were made in the JavaScript of "quiz.html". We chose to load the HTML before the Javascript using the document.ready()
function because we wanted to be able to call elements of the page and assign event listeners to them. The for loop adds the events listeners to the
appropriate HTML elements after the HTML is loaded, so we can use element ids for all of our Javascript programming. We then did all the calculations in Javascript
so that all we have to do from the controller is extract the tempo that the user tapped and compare it to the answer given by the Spotify API. Most of our work
with the API was quite straightforward. We chose to use Spotipy, or the Python wrapper for the Spotify API because we don't like working with Javascript, which
is the language that the API was originally in.
