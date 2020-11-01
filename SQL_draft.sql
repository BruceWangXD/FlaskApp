These are draft query statements for the SQL tasks. If you have any changes you’d like to make, add them below the original code block in a different colour / font or just comment on it so its easier for us to compare and discuss later

Formatting and spacing is a little dodgy when I copy over from the .sql file


-- Q1: Landing page data after login --

-- Check login exists
SELECT *
FROM mediaserver.UserAccount
WHERE username = '%s' AND password = '%s';

-- Get subbed podcasts
SELECT podcast_id, podcast_title, podcast_uri, podcast_last_updated
FROM mediaserver.UserAccount JOIN mediaserver.Subscribed_Podcasts USING (username)
   	                  	JOIN mediaserver.Podcast USING (podcast_id)
WHERE username = '%s';

-- Get user playlists
SELECT collection_id, collection_name, COUNT(media_id)
FROM mediaserver.UserAccount JOIN mediaserver.MediaCollection USING (username)           	 
                         	JOIN mediaserver.MediaCollectionContents USING (collection_id)
WHERE username = '%s'
GROUP BY collection_id, collection_name;
--ORDER BY COUNT(media_id);

-- Get in progress media
SELECT media_id, play_count, progress, lastviewed, storage_location
FROM mediaserver.UserAccount JOIN mediaserver.UserMediaConsumption USING (username) JOIN mediaserver.MediaItem USING (media_id)
                         	LEFT JOIN mediaserver.Song ON (media_id = song_id)
                         	LEFT JOIN mediaserver.PodcastEpisode USING (media_id)
WHERE username = '%s' AND progress > 0 AND (progress < length OR progress < podcast_episode_length);



-- Q2: Retrieve details for a given song --

-- Get title and length
SELECT song_title, length
FROM mediaserver.Song
WHERE song_id = '%s';

-- Get all artist names
SELECT artist_name
FROM mediaserver.Song JOIN mediaserver.Song_Artists USING (song_id) JOIN mediaserver.Artist ON (performing_artist_id = artist_id)
WHERE song_id = '%s';

-- Get song metadata

-- All in one query (harder, need to filter in Python)
SELECT md_value
FROM mediaserver.Song JOIN mediaserver.AudioMedia ON (song_id = media_id)
                  	JOIN mediaserver.MediaItemMetaData USING (media_id)
                  	LEFT JOIN mediaserver.MetaData USING (md_id)
                  	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE song_id = '%s' AND md_type_name IN ('artwork', 'description', 'song genre');

-- Three separate queries (easier, less filtering)
SELECT md_value
FROM mediaserver.Song JOIN mediaserver.AudioMedia ON (song_id = media_id)
                  	JOIN mediaserver.MediaItemMetaData USING (media_id)
                  	LEFT JOIN mediaserver.MetaData USING (md_id)
                  	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE song_id = '%s' AND md_type_name = 'artwork';
     	 
SELECT md_value
FROM mediaserver.Song JOIN mediaserver.AudioMedia ON (song_id = media_id)
                  	JOIN mediaserver.MediaItemMetaData USING (media_id)
                  	LEFT JOIN mediaserver.MetaData USING (md_id)
                  	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE song_id = '%s' AND md_type_name = 'description';
     	 
SELECT md_value
FROM mediaserver.Song JOIN mediaserver.AudioMedia ON (song_id = media_id)
                  	JOIN mediaserver.MediaItemMetaData USING (media_id)
                  	LEFT JOIN mediaserver.MetaData USING (md_id)
                  	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE song_id = '%s' AND md_type_name = 'song genre';


-- Q3: Retrieve details for all TV show info --
SELECT tvshow_id, tvshow_title, COUNT(media_id)
FROM mediaserver.TVShow JOIN mediaserver.TVEpisode USING (tvshow_id)
GROUP BY tvshow_id, tvshow_title;

-- Q4: Retrieve details for a single TV show and its episodes --

-- Get TVSHow name
SELECT tvshow_title
FROM mediaserver.TVShow
WHERE tvshow_id = '%s';

-- Get TVShow metadata
SELECT md_value
FROM mediaserver.TVShow LEFT JOIN mediaserver.TVShowMetaData USING(tvshow_id)
                    	LEFT JOIN mediaserver.MetaData USING (md_id)
                    	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE tvshow_id = '%s' AND md_type_name IN ('artwork', 'description', 'film genre');

-- Get data about each episode
SELECT media_id, tvshow_episode_title, season, episode, air_date
FROM mediaserver.TVShow JOIN mediaserver.TVEpisode USING (tvshow_id)
ORDER BY season, episode
WHERE tvshow_id = '%s';

-- Q5: Retrieve details for a single album --

-- Get Album name
SELECT album_title
FROM mediaserver.Album
WHERE album_id = '%s';

-- Get Album metadata
SELECT md_value
FROM mediaserver.Album LEFT JOIN mediaserver.AlbumMetaData USING (album_id)
                   	LEFT JOIN mediaserver.MetaData USING (md_id)
                   	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE album_id = '%s' AND md_type_name IN ('artwork', 'description', 'song genre');
     	 
-- Get data about list of songs --
SELECT song_id, song_title, artist_name
FROM mediaserver.Album JOIN mediaserver.Album_Songs USING (album_id)
       	JOIN mediaserver.Song USING (song_id)
       	JOIN mediaserver.Song_Artists USING (song_id)
       	JOIN mediaserver.Artist ON (performing_artist_id = artist_id)
WHERE album_id = '%s';
ORDER BY track_num;

-- Q6: Retrieve genres for an album in Q5 based on the genres of its songs --
SELECT song_id, song_title, md_value
FROM mediaserver.Album JOIN mediaserver.Album_Songs USING (album_id)
                   	JOIN mediaserver.Song USING (song_id)
                   	LEFT JOIN mediaserver.AlbumMetaData USING (album_id)
                   	LEFT JOIN mediaserver.MetaData USING (md_id)
                   	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE album_id = '%s' AND md_type_name = 'song genre';

-- Q7: Retrieve data about a single podcast --
-- Get basic podcast data
SELECT podcast_id, podcast_title, podcast_uri, podcast_last_updated
FROM mediaserver.Podcast
WHERE podcast_id = '%s';

-- Get podcast metadata
SELECT md_value
FROM mediaserver.Podcast LEFT JOIN mediaserver.PodcastMetaData USING (podcast_id)
         	LEFT JOIN mediaserver.MetaData USING (md_id)
         	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE podcast_id = '%s' AND md_type_name IN ('artwork', 'description', 'podcast genre', 'copyright holder');
        	 
-- Get data about episodes within podcast
SELECT media_id, podcast_episode_title, podcast_episode_URI, podcast_episode_published_date, podcast_episode_length
FROM mediaserver.Podcast JOIN mediaserver.PodcastEpisode USING (podcast_id)
WHERE podcast_id = '%s'
ORDER BY podcast_episode_published_date DESC;

-- Q8: Retrieve data about a single podcast episode --

-- Get basic data about podcast episode
SELECT media_id, podcast_episode_title, podcast_episode_URI, podcast_episode_published_date, podcast_episode_length
FROM  mediaserver.PodcastEpisode
WHERE media_id = '%s';

-- Get metadata about podcast episode
SELECT md_value
FROM  mediaserver.PodcastEpisode LEFT JOIN mediaserver.PodcastMetaData USING (podcast_id)
                             	LEFT JOIN mediaserver.MetaData USING (md_id)
                             	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE media_id = '%s' AND md_type_name IN ('artwork', 'description');

-- Q9: Rewrite addSong() function to have proper checks and inserts --

create or replace function mediaserver.addSong(
    location text,
    songdescription text,
    title varchar(250),
    songlength int,
    songgenre text,
	artistid int)
RETURNS int AS
$BODY$
	-- incomplete, needs to be updated to better resemble addmovie()
    
	-- add data into Media
	INSERT INTO mediaserver.mediaItem(storage_location)
    	VALUES(location)
    	RETURNING media_id;
	-- add data into MetaData for genre
	INSERT INTO mediaserver.metadata(md_type_id, md_value)
    	SELECT md_type_id, songgenre
    	FROM mediaserver.MetaDataType where md_type_name = 'song genre';
	-- add data into MetaData for description
	INSERT INTO mediaserver.metadata(md_type_id, md_value)
    	SELECT md_type_id, songgenre
    	FROM mediaserver.MetaDataType where md_type_name = 'description';
	-- add data into Song
	INSERT INTO Song
    	VALUES(media_id, title, songlength);
	-- add data into Song_Artists
	INSERT INTO Songt_Artists
    	VALUES(song_id, artistid);
$BODY$
LANGUAGE sql;

-- Q10: Query for getting relevant details when searching for movies by title

-- Get basic data about movie including metadata count
SELECT movie_id, movie_title, release_year, COUNT(md_type_name)
FROM mediaserver.Movie JOIN mediaserver.VideoMedia ON (movie_id = media_id)
                   	LEFT JOIN mediaserver.MediaItemMetaData USING   (media_id)
                   	LEFT JOIN mediaserver.MetaData USING (md_id)
                   	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE movie_title LIKE '%s%' AND movie_title LIKE '%s' AND md_type_name IN ('artwork', 'description', 'film genre')
GROUP BY movie_id, movie_title, release_year;


-- Get metadata about movie
SELECT md_value
FROM mediaserver.Movie JOIN mediaserver.VideoMedia ON (movie_id = media_id)
                   	LEFT JOIN mediaserver.MediaItemMetaData USING (media_id)
                   	LEFT JOIN mediaserver.MetaData USING (md_id)
                   	LEFT JOIN mediaserver.MetaDataType USING (md_type_id)
WHERE movie_title LIKE '%s' AND md_type_name IN ('artwork', 'description', 'film genre');




