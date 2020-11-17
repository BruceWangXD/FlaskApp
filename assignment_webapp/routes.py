"""
Route management.

This provides all of the websites routes and handles what happens each
time a browser hits each of the paths. This serves as the interaction
between the browser and the database while rendering the HTML templates
to be displayed.

You will have to make 
"""

# Importing the required packages
from modules import *
from flask import *
import database



import re
from werkzeug.security import generate_password_hash, check_password_hash


user_details = {}                   # User details kept for us
session = {}                        # Session information (logged in state)
page = {}                           # Determines the page information

# Initialise the application
app = Flask(__name__)
app.secret_key = """U29tZWJvZHkgb25jZSB0b2xkIG1lIFRoZSB3b3JsZCBpcyBnb25uYSBy
b2xsIG1lIEkgYWluJ3QgdGhlIHNoYXJwZXN0IHRvb2wgaW4gdGhlIHNoZWQgU2hlIHdhcyBsb29r
aW5nIGtpbmRhIGR1bWIgV2l0aCBoZXIgZmluZ2VyIGFuZCBoZXIgdGh1bWIK"""


#####################################################
#   INDEX
#####################################################

@app.route('/')
def index():
    """
    Provides the main home screen if logged in.
        - Shows user playlists
        - Shows user Podcast subscriptions
        - Shows superUser status
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'User Management'

    # Get a list of user playlists
    user_playlists = None
    user_playlists = database.user_playlists(user_details['username'])
    # Get a list of subscribed podcasts
    user_subscribed_podcasts = None
    user_subscribed_podcasts = database.user_podcast_subscriptions(user_details['username'])
    # Get a list of in-progress items
    user_in_progress_items = None
    user_in_progress_items = database.user_in_progress_items(user_details['username'])
    # Data integrity checks
    if user_playlists == None:
        user_playlists = []
    
    if user_subscribed_podcasts == None:
        user_subscribed_podcasts = []

    if user_in_progress_items == None:
        user_in_progress_items = []

    global contact
    contact = None
    contact = database.get_contact(user_details.get('username'))

    # Data integrity checks
    if contact == None:
        contact = []
    return render_template('index.html',
                           session=session,
                           page=page,
                           user=user_details,
                           playlists=user_playlists,
                           subpodcasts=user_subscribed_podcasts,
                           usercurrent=user_in_progress_items,
                           contact=contact)

#####################################################
#####################################################
####    User Management
#####################################################
#####################################################

#####################################################
#   LOGIN
#####################################################

@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Provides /login
        - [GET] If they are just viewing the page then render login page.
        - [POST] If submitting login details, check login.
    """
    # Check if they are submitting details, or they are just logging in
    if(request.method == 'POST'):
        # submitting details
        # The form gives back EmployeeID and Password
        login_return_data = database.check_login(
            request.form['username'],
            request.form['password']
        )

        # If it's null, saying they have incorrect details
        if login_return_data is None:
            page['bar'] = False
            flash("Incorrect username/password, please try again")
            return redirect(url_for('login'))

        # If there was no error, log them in
        page['bar'] = True
        flash('You have been logged in successfully')
        session['logged_in'] = True

        # Store the user details for us to use throughout
        global user_details
        user_details = login_return_data[0]

        contact = None
        contact = database.get_contact(user_details.get('username'))

    
        if contact == None:
            contact = []


          
        print(contact)
        return redirect(url_for('index'))

    elif(request.method == 'GET'):
        return(render_template('login.html', session=session, page=page))


#####################################################
#   LOGOUT
#####################################################

@app.route('/logout')
def logout():
    """
    Logs out of the current session
        - Removes any stored user data.
    """
    session['logged_in'] = False
    page['bar'] = True
    flash('You have been logged out')
    return redirect(url_for('index'))

#####################################################
#####################################################
####    List All items
#####################################################
#####################################################



@app.route('/changepassword', methods=['POST', 'GET'])
def changepassword():
    """
    changepassword
    """
    # Check if they are submitting details, or they are just logging in
    if(request.method == 'POST'):
        # submitting details
        # The form gives back EmployeeID and Password
        
        if request.form['passwordfirst'] is None or request.form['passwordsecond'] is None:
            flash("the passwords you entered can not be None")
            return redirect(url_for('changepassword'))



        if request.form['passwordfirst']!=request.form['passwordsecond']:
            flash("the passwords you entered are not the same")
            return redirect(url_for('changepassword'))
        
        if request.form['passwordfirst']==user_details.get('password'):
            flash("the password must be different to your current one")
            return redirect(url_for('changepassword'))


        lowerRegex = re.compile('[a-z]')
        upperRegex = re.compile('[A-Z]')
        digitRegex = re.compile('[0-9]')
        if len(request.form['passwordfirst'])<8:
            flash("the length of your password must be at least 8")
            return redirect(url_for('changepassword'))
        
        
        
        if lowerRegex.search(request.form['passwordfirst']) == None or upperRegex.search(request.form['passwordfirst']) == None or digitRegex.search(request.form['passwordfirst']) == None:
            flash("the password must be made up by at least one digit, one lower case letter and one upper case letter")
            return redirect(url_for('changepassword'))



        
        return_value=database.change_password(
            
            request.form['passwordfirst'],
            user_details.get('username')
        )

        
        
        

    

        

        # If there was no error, log them in
        
        flash('You have changed password successfully')
        return redirect(url_for('index'))

        

    elif(request.method == 'GET'):
        return(render_template('changepassword.html', session=session, page=page,contact=contact))




################################################
#email
############################################

@app.route('/changeemail', methods=['POST', 'GET'])
def changeemail():
    """
    changeemail
    """
    # Check if they are submitting details, or they are just logging in
    if(request.method == 'POST'):
        # submitting details
        # The form gives back EmployeeID and Password
        
        str='^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'

        if not  re.match(str, request.form['email']):
            flash("Please make sure your email address is in correct format")
            return redirect(url_for('changeemail'))


        
        return_value=database.change_email(
            
            request.form['email'],
            user_details.get('username')
        )


       

        
        
    

        

        # If there was no error, log them in
        
        flash('You have changed email successfully')
        return redirect(url_for('index'))

        

    elif(request.method == 'GET'):
        return(render_template('changeemail.html', session=session, page=page,contact=contact))



#####################################################
#   Phone
#####################################################



@app.route('/changephonenumber', methods=['POST', 'GET'])
def changephonenumber():
    """
    changephonenumber
    """
    # Check if they are submitting details, or they are just logging in
    if(request.method == 'POST'):
        # submitting details
        # The form gives back EmployeeID and Password
        
        try:
            temp=int(request.form['phone'])

        except:
            flash("Please make sure your phone number is in a correct format")
            return redirect(url_for('changephonenumber'))


        
        return_value=database.change_phone(
            
            request.form['phone'],
            user_details.get('username')
        )


        
        
    

        

        # If there was no error, log them in
        
        flash('You have changed phone successfully')
        return redirect(url_for('index'))

        

    elif(request.method == 'GET'):
        return(render_template('changephonenumber.html', session=session, page=page,contact=contact))





#####################################################

#####################################################
#   List Artists
#####################################################
@app.route('/list/artists')
def list_artists():
    """
    Lists all the artists in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Artists'

    # Get a list of all artists from the database
    allartists = None
    allartists = database.get_allartists()

    # Data integrity checks
    if allartists == None:
        allartists = []


    return render_template('listitems/listartists.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allartists=allartists,
                           contact=contact)


#####################################################
#   List Songs
#####################################################
@app.route('/list/songs')
def list_songs():
    """
    Lists all the songs in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Songs'

    # Get a list of all songs from the database
    allsongs = None
    allsongs = database.get_allsongs()


    # Data integrity checks
    if allsongs == None:
        allsongs = []


    return render_template('listitems/listsongs.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allsongs=allsongs,
                           contact=contact)

#####################################################
#   List Podcasts
#####################################################
@app.route('/list/podcasts')
def list_podcasts():
    """
    Lists all the podcasts in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List podcasts'

    # Get a list of all podcasts from the database
    allpodcasts = None
    allpodcasts = database.get_allpodcasts()

    # Data integrity checks
    if allpodcasts == None:
        allpodcasts = []


    return render_template('listitems/listpodcasts.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allpodcasts=allpodcasts,
                           contact=contact)


#####################################################
#   List Movies
#####################################################
@app.route('/list/movies')
def list_movies():
    """
    Lists all the movies in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Movies'

    # Get a list of all movies from the database
    allmovies = None
    allmovies = database.get_allmovies()


    # Data integrity checks
    if allmovies == None:
        allmovies = []


    return render_template('listitems/listmovies.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allmovies=allmovies,
                           contact=contact)


#####################################################
#   List Albums
#####################################################
@app.route('/list/albums')
def list_albums():
    """
    Lists all the albums in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Albums'

    # Get a list of all Albums from the database
    allalbums = None
    allalbums = database.get_allalbums()


    # Data integrity checks
    if allalbums == None:
        allalbums = []


    return render_template('listitems/listalbums.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allalbums=allalbums,
                           contact=contact)


#####################################################
#   List TVShows
#####################################################
@app.route('/list/tvshows')
def list_tvshows():
    """
    Lists all the tvshows in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List TV Shows'

    # Get a list of all tvshows from the database
    alltvshows = None
    alltvshows = database.get_alltvshows()


    # Data integrity checks
    if alltvshows == None:
        alltvshows = []


    return render_template('listitems/listtvshows.html',
                           session=session,
                           page=page,
                           user=user_details,
                           alltvshows=alltvshows,
                           contact=contact)




#####################################################
#####################################################
####    List Individual items
#####################################################
#####################################################

#####################################################
#   Individual Artist
#####################################################
@app.route('/artist/<artist_id>')
def single_artist(artist_id):
    """
    Show a single artist by artist_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'Artist ID: '+ str(artist_id)

    # Get a list of all artist by artist_id from the database
    artist = None
    artist = database.get_artist(artist_id)

    # Data integrity checks
    if artist == None:
        artist = []

    return render_template('singleitems/artist.html',
                           session=session,
                           page=page,
                           user=user_details,
                           artist=artist,
                           contact=contact)


#####################################################
#   Individual Song
#####################################################
@app.route('/song/<song_id>')
def single_song(song_id):
    """
    Show a single song by song_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'Song'

    # Get a list of all song by song_id from the database
    song = None
    song = database.get_song(song_id)

    songmetadata = None
    songmetadata = database.get_song_metadata(song_id)

    # Data integrity checks
    if song == None:
        song = []

    if songmetadata == None:
        songmetadata = []

    return render_template('singleitems/song.html',
                           session=session,
                           page=page,
                           user=user_details,
                           song=song,
                           songmetadata=songmetadata,
                           contact=contact)

#####################################################
#   Query 6
#   Individual Podcast
#####################################################
@app.route('/podcast/<podcast_id>')
def single_podcast(podcast_id):
    """
    Show a single podcast by podcast_id in your media server
    Can do this without a login
    """
    #########
    # TODO  #
    #########

    #############################################################################
    # Fill in the Function below with to do all data handling for a podcast     #
    #############################################################################

    page['title'] = 'Single podcast' + podcast_id # Add the title

    # Set up some variables to manage the returns from the database fucntions

    podcast = None
    podcast = database.get_podcast(podcast_id)

    all_podcasteps = None
    all_podcasteps = database.get_all_podcasteps_for_podcast(podcast_id)

    # Once retrieved, do some data integrity checks on the data

    if podcast == None:
        podcast = []

    if all_podcasteps == None:
        all_podcasteps = []

    # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
    return render_template('singleitems/podcast.html',
                           session=session,
                           page=page,
                           user=user_details,
                           podcast=podcast,
                           all_podcasteps=all_podcasteps,
                           contact=contact
                           )



#####################################################
#   Query 7
#   Individual Podcast Episode
#####################################################
@app.route('/podcastep/<media_id>')
def single_podcastep(media_id):
    """
    Show a single podcast epsiode by media_id in your media server
    Can do this without a login
    """
    #########
    # TODO  #
    #########

    #############################################################################
    # Fill in the Function below with to do all data handling for a podcast ep  #
    #############################################################################

    page['title'] = 'Postcast Episode'  + media_id # Add the title

    # Set up some variables to manage the returns from the database fucntions

    podcaststep = None
    podcaststep = database.get_podcastep(media_id)

    

    # Once retrieved, do some data integrity checks on the data
    if podcaststep == None:
        podcaststep = []


    # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
    return render_template('singleitems/podcastep.html',
                           session=session,
                           page=page,
                           user=user_details,
                           podcaststep=podcaststep,
                           contact=contact
                           )



#####################################################
#   Individual Movie
#####################################################
@app.route('/movie/<movie_id>')
def single_movie(movie_id):
    """
    Show a single movie by movie_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Movies'

    # Get a list of all movies by movie_id from the database
    movie = None
    movie = database.get_movie(movie_id)


    # Data integrity checks
    if movie == None:
        movie = []


    return render_template('singleitems/movie.html',
                           session=session,
                           page=page,
                           user=user_details,
                           movie=movie,
                           contact=contact)


#####################################################
#   Individual Album
#####################################################
@app.route('/album/<album_id>')
def single_album(album_id):
    """
    Show a single album by album_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Albums'

    # Get the album plus associated metadata from the database
    album = None
    album = database.get_album(album_id)

    album_songs = None
    album_songs = database.get_album_songs(album_id)

    album_genres = None
    album_genres = database.get_album_genres(album_id)

    # Data integrity checks
    if album_songs == None:
        album_songs = []

    if album == None:
        album = []

    if album_genres == None:
        album_genres = []

    return render_template('singleitems/album.html',
                           session=session,
                           page=page,
                           user=user_details,
                           album=album,
                           album_songs=album_songs,
                           album_genres=album_genres,
                           contact=contact)


#####################################################
#   Individual TVShow
#####################################################
@app.route('/tvshow/<tvshow_id>')
def single_tvshow(tvshow_id):
    """
    Show a single tvshows and its eps in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'TV Show'

    # Get a list of all tvshows by tvshow_id from the database
    tvshow = None
    tvshow = database.get_tvshow(tvshow_id)

    tvshoweps = None
    tvshoweps = database.get_all_tvshoweps_for_tvshow(tvshow_id)

    # Data integrity checks
    if tvshow == None:
        tvshow = []

    if tvshoweps == None:
        tvshoweps = []

    return render_template('singleitems/tvshow.html',
                           session=session,
                           page=page,
                           user=user_details,
                           tvshow=tvshow,
                           tvshoweps=tvshoweps,
                           contact=contact)

#####################################################
#   Individual TVShow Episode
#####################################################
@app.route('/tvshowep/<tvshowep_id>')
def single_tvshowep(tvshowep_id):
    """
    Show a single tvshow episode in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List TV Shows'

    # Get a list of all tvshow eps by media_id from the database
    tvshowep = None
    tvshowep = database.get_tvshowep(tvshowep_id)


    # Data integrity checks
    if tvshowep == None:
        tvshowep = []


    return render_template('singleitems/tvshowep.html',
                           session=session,
                           page=page,
                           user=user_details,
                           tvshowep=tvshowep,
                           contact=contact)


#####################################################
#####################################################
####    Search Items
#####################################################
#####################################################

#####################################################
#   Search TVShow
#####################################################
@app.route('/search/tvshow', methods=['POST','GET'])
def search_tvshows():
    """
    Search all the tvshows in your media server
    """

    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'TV Show Search'

    # Get a list of matching tv shows from the database
    tvshows = None
    if(request.method == 'POST'):

        tvshows = database.find_matchingsongs(request.form['searchterm'])

    # Data integrity checks
    if tvshows == None or tvshows == []:
        tvshows = []
        page['bar'] = False
        flash("No matching tv shows found, please try again")
    else:
        page['bar'] = True
        flash('Found '+str(len(tvshows))+' results!')
        session['logged_in'] = True

    return render_template('searchitems/search_tvshows.html',
                           session=session,
                           page=page,
                           user=user_details,
                           tvshows=tvshows,
                           contact=contact)

#####################################################
#   Query 10
#   Search Movie
#####################################################
@app.route('/search/movie', methods=['POST','GET'])
def search_movies():
    """
    Search all the movies in your media server
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    #########
    # TODO  #  
    #########


    #############################################################################
    # Fill in the Function below with to do all data handling for searching for #
    # a movie                                                                   #
    #############################################################################

    page['title'] = 'Movie Search' # Add the title

        # Get a list of matching tv shows from the database
    movies = None
 

    if request.method == 'POST':
        # Set up some variables to manage the post returns

        movies = database.find_matchingmovies(request.form['searchterm'])

        # Data integrity checks
        if movies == None or movies == []:
            movies = []
            page['bar'] = False
            flash("No matching movies found, please try again")
        else:
            page['bar'] = True
            flash('Found '+str(len(movies))+' results!')
            session['logged_in'] = True

        # Once retrieved, do some data integrity checks on the data

        # Once verified, send the appropriate data to 

        # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES or Go elsewhere
        return render_template('searchitems/search_movies.html',
                    session=session,
                    page=page,
                    user=user_details,
                    movies = movies,
                    contact=contact)
    # else:
    #     # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
    #     return render_template('searchitems/search_movies.html',
    #                        session=session,
    #                        page=page,
    #                        user=user_details,
    #                        movies = movies)


#####################################################
#   Search Song
#####################################################
@app.route('/search/song', methods=['POST','GET'])
def search_songs():
    """
    Search all the songs in your media server
    """

    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Song Search'

    # Get a list of matching songs from the database
    songs = None
    if(request.method == 'POST'):

        songs = database.find_matchingsongs(request.form['searchterm'])

    # Data integrity checks
    if songs == None or songs == []:
        songs = []
        page['bar'] = False
        flash("No matching songs found, please try again")
    else:
        page['bar'] = True
        flash('Found '+str(len(songs))+' results!')
        session['logged_in'] = True

    return render_template('searchitems/search_songs.html',
                           session=session,
                           page=page,
                           user=user_details,
                           songs=songs,
                           contact=contact)


#####################################################
#   Search Album
#####################################################
@app.route('/search/album', methods=['POST','GET'])
def search_albums():
    """
    Search all the songs in your media server
    """

    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Album Search'

    # Get a list of matching songs from the database
    albums = None
    if(request.method == 'POST'):

        albums = database.find_matchingalbums(request.form['searchterm'])

    # Data integrity checks
    if albums == None or albums == []:
        albums = []
        page['bar'] = False
        flash("No matching albums found, please try again")
    else:
        page['bar'] = True
        flash('Found '+str(len(albums))+' results!')
        session['logged_in'] = True

    return render_template('searchitems/search_albums.html',
                           session=session,
                           page=page,
                           user=user_details,
                           albums=albums,
                           contact=contact)


#####################################################
#   Search Album
#####################################################
@app.route('/search/artist', methods=['POST','GET'])
def search_artists():
    """
    Search all the songs in your media server
    """

    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Artist Search'

    # Get a list of matching songs from the database
    artists = None
    if(request.method == 'POST'):

        artists = database.find_matchingartists(request.form['searchterm'])

    # Data integrity checks
    if artists == None or artists == []:
        artists = []
        page['bar'] = False
        flash("No matching artists found, please try again")
    else:
        page['bar'] = True
        flash('Found '+str(len(artists))+' results!')
        session['logged_in'] = True

    return render_template('searchitems/search_artists.html',
                           session=session,
                           page=page,
                           user=user_details,
                           artists=artists,
                           contact=contact)

#####################################################
#   Add Movie
#####################################################
@app.route('/add/movie', methods=['POST','GET'])
def add_movie():
    """
    Add a new movie
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Movie Creation'

    movies = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('movie_title' not in request.form):
            newdict['movie_title'] = 'Empty Film Value'
        else:
            newdict['movie_title'] = request.form['movie_title']
            print("We have a value: ",newdict['movie_title'])

        if ('release_year' not in request.form):
            newdict['release_year'] = '0'
        else:
            newdict['release_year'] = request.form['release_year']
            print("We have a value: ",newdict['release_year'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('storage_location' not in request.form):
            newdict['storage_location'] = 'Empty storage location'
        else:
            newdict['storage_location'] = request.form['storage_location']
            print("We have a value: ",newdict['storage_location'])

        if ('film_genre' not in request.form):
            newdict['film_genre'] = 'drama'
        else:
            newdict['film_genre'] = request.form['film_genre']
            print("We have a value: ",newdict['film_genre'])

        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])
        
        print('newdict is:')
        print(newdict)

        #forward to the database to manage insert
        movies = database.add_movie_to_db(newdict['movie_title'],newdict['release_year'],newdict['description'],newdict['storage_location'],newdict['film_genre'])


        max_movie_id = database.get_last_movie()[0]['movie_id']
        print(movies)
        if movies is not None:
            max_movie_id = movies[0]

        # ideally this would redirect to your newly added movie
        return single_movie(max_movie_id)
    else:
        return render_template('createitems/createmovie.html',
                           session=session,
                           page=page,
                           user=user_details,
                           contact=contact)


#####################################################
#   Query 9
#   Add song
#####################################################
@app.route('/add/song', methods=['POST','GET'])
def add_song():
    """
    Add a new Song
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    #########
    # TODO  #  
    #########

    #############################################################################
    # Fill in the Function below with to do all data handling for adding a song #
    #############################################################################


    page['title'] = 'Song Creation'

    songs = None

    Artists = None
    Artists = database.get_allartists()

    Album = None
    Album = database.get_allalbums()

    Genres = None
    Genres = database.get_allgenres()

    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('song_title' not in request.form):
            newdict['song_title'] = 'Empty song title'
        else:
            newdict['song_title'] = request.form['song_title']
            print("We have a value: ",newdict['song_title'])

        if ('length' not in request.form):
            newdict['length'] = '0'
        else:
            newdict['length'] = request.form['length']
            print("We have a value: ",newdict['length'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('storage_location' not in request.form):
            newdict['storage_location'] = 'Empty storage location'
        else:
            newdict['storage_location'] = request.form['storage_location']
            print("We have a value: ",newdict['storage_location'])


        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])

        newdict['artist'] = request.form['artist']
        newdict['song_genre'] = request.form['song_genre']
        newdict["Album"] = request.form['Album']

        try:
            if int(newdict['length'])<0 or int(newdict['length'])>1000000:
                flash("Invalid length")
                return render_template('createitems/createsong.html',
                            Artists = Artists,
                            Albums = Album,
                            Genres = Genres,
                            session=session,
                            page=page,
                            user=user_details,
                            contact=contact)
        except:
            flash("Invalid length")
            return render_template('createitems/createsong.html',
                        Artists = Artists,
                        Albums = Album,
                        Genres = Genres,
                        session=session,
                        page=page,
                        user=user_details,
                        contact=contact)

        if database.song_exist(newdict['song_title'],newdict['artist'],newdict['length']):
            print("The song already exist in database, Adding failed!")
            flash("The song already exist in database, Adding failed! Redirecting to the song")
            return single_song(database.song_exist(newdict['song_title'],newdict['artist'],newdict['length'])[0]['song_id'])


        if newdict["Album"] == 'None':
            songs = database.add_song_to_db1(newdict['storage_location'],newdict['description'],newdict['song_title'],newdict['length'],newdict['song_genre'],newdict['artist'])
        else:
            print(database.get_album(newdict["Album"])[0]['count'])
            albumtrack = int(database.get_album(newdict["Album"])[0]['count'])+1
            songs = database.add_song_to_db2(newdict['storage_location'],newdict['description'],newdict['song_title'],newdict['length'],newdict['song_genre'],newdict["Album"],albumtrack,newdict['artist'])
        songsid = songs[0]
        database.add_song_artist(songsid,newdict['artist'])
        flash("Success! You add a song into the database.")

        max_song_id = database.get_last_song()[0]['song_id']
        print("(routes)max song id is:")
        print(songs)
        if songs is not None:
            max_song_id = songs[0]

        # ideally this would redirect to your newly added song
        return single_song(max_song_id)
    else:
        return render_template('createitems/createsong.html',
                           Artists = Artists,
                           Albums = Album,
                           Genres = Genres,
                           session=session,
                           page=page,
                           user=user_details,
                           contact=contact)

#####################################################
#   Add artist
#####################################################
@app.route('/add/artist', methods=['POST','GET'])
def add_artist():
    """
    Add a new artist
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Artist Creation'

    Artist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('Artist_name' not in request.form):
            newdict['Artist_name'] = 'Empty Artist'
        else:
            newdict['Artist_name'] = request.form['Artist_name']
            print("We have a value: ",newdict['Artist_name'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])
        
        print('newdict is:')
        print(newdict)

        if database.artist_nameexist(newdict['Artist_name']):
            print("The artist already exist in database, Adding failed!")
            flash("The artist already exist in database, Adding failed!Redirecting to the artist")
            return single_artist(database.artist_nameexist(newdict['Artist_name'])[0]["artist_id"])

        #forward to the database to manage insert

        Artist = database.add_artist_to_db(newdict['Artist_name'],newdict['description'])
        flash("Success! You add an artist into the database.")

        max_artist_id = database.get_last_artist()[0]['artist_id']

        # ideally this would redirect to your newly added movie
        return single_artist(max_artist_id)
    else:
        return render_template('createitems/createartist.html',
                           session=session,
                           page=page,
                           user=user_details,
                           contact=contact)


#####################################################
#   Add album
#####################################################
@app.route('/add/album', methods=['POST','GET'])
def add_album():
    """
    Add a new album
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Album Creation'

    Album = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('Album_name' not in request.form):
            newdict['Album_name'] = 'Empty Album'
        else:
            newdict['Album_name'] = request.form['Album_name']
            print("We have a value: ",newdict['Album_name'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])

        

        if database.album_nameexist(newdict['Album_name']):
            print("The album already exist in database, Adding failed!")
            flash("The album already exist in database, Adding failed!Redirecting to the album")
            return single_album(database.album_nameexist(newdict['Album_name'])[0]["album_id"])

        #forward to the database to manage insert

        Album = database.add_album_to_db(newdict['Album_name'],newdict['description'])
        flash("Success! You add an album into the database.")

        max_album_id = database.get_last_album()[0]['album_id']

        # ideally this would redirect to your newly added movie
        return single_album(max_album_id)
    else:
        return render_template('createitems/createalbum.html',
                           session=session,
                           page=page,
                           user=user_details,
                           contact=contact)

@app.route('/add/media', methods=['POST','GET'])
def add_media():
    return render_template('createitems/createmedia.html',
                           session=session,
                           page=page,
                           user=user_details,
                           contact=contact)