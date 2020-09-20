import pafy
import vlc

# You can import anything that your module may need at the top, just like a regular Python script

HANDLED_COMMANDS = {"songrequest"}  # Add commands that your module can handle here, without prefix


class Output(object):
    # Output class is used for communicating between the module and the main process. REQUIRED.
    def __init__(self):
        """
        Initializes a Output object for passing module output to main process
        """
        self.out = ''
        self.updated = False

    def read(self):
        """
        Reads from output
        :return: String, representing output from module
        """
        self.updated = False
        return self.out

    def write(self, o):
        """
        Writes to Output object
        :param o: Object, as long as it has a string representation
        :return: None
        """
        self.updated = True
        self.out = str(o)

    def is_updated(self):
        """
        Checks if new text has been written to output
        :return: True if output has updated since last read, False if not
        """
        return self.updated


out = Output()  # Make Output object for communicating with main. REQUIRED. Use out.write(o) as if sending a msg to chat

# You can add additional classes your module may need here


class Media(object):
    """
    Media object represents a YouTube video at url self.url playable with this module
    """

    def __init__(self, location, requester):
        """
        Initializes a Media object
        :param location: String, URL or video ID of YouTube video
        :param requester: String, username of Twitch user who made request
        :except ValueError if location is not a YouTube video
        """
        self.requester = requester
        video = pafy.new(location)
        self.title = video.title
        self.duration = video.duration
        self.length = video.length
        self.id = video.videoid
        self.audio_url = video.getbestaudio().url

    def get_media_url(self):
        """
        Getter function for retrieving YouTube video link
        :return: String, link of Media object's YouTube video
        """
        return "http://www.youtube.com/watch?v=" + self.id

    def get_requester(self):
        """
        Getter function for retrieving song requester
        :return: String, username of Twitch user who made request
        """
        return self.requester

    def get_media_title(self):
        """
        Getter function for retrieving YouTube video title
        :return: String, title of Media object's YouTube video
        """
        return self.title

    def get_media_duration(self):
        """
        Getter function for retrieving duration of YouTube video
        :return: String, duration formatted as HH:MM:SS of Media object's YouTube video
        """
        return self.duration

    def get_media_length(self):
        """
        Getter function for retrieving length of YouTube video
        :return: int, length in seconds of Media object's YouTube video
        """
        return self.length

    def get_audio_url(self):
        """
        Getter function for retrieving audio url of YouTube video for playback
        :return: String, url for audio stream of Media object's YouTube video
        """
        return self.audio_url


class Player(object):
    """
    Player that plays song requests using VLC

    Invariant regarding current_media and len(queue): if len(queue) > 0, there MUST be an item currently playing
    """

    def __init__(self):
        """
        Initializes Player object with VLC instance self.instance, VLC player self.player, event manager self.events,
        current media self.media, media list self.queue, allowed playback status self.playback_allowed,
        and volume self.volume
        """
        # VLC objects
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.events = self.player.event_manager()

        # Player state objects
        self.current_media = None
        self.queue = []
        self.playback_allowed = True
        self.volume = 100

    def add_media(self, media):
        """
        Adds Media object to queue if playing media, or sets as current song if not playing
        :param media: Media object
        :return: None, modifies queue or player directly
        """
        if self.current_media is None:  # no current media playing
            self.current_media = media
            self.play_queue()
        else:
            self.queue.append(media)

    def add_loc(self, loc, requester):
        """
        Adds location to player as Media object
        :param loc: String, url for media
        :param requester: String, username of requester
        :return: None, modifies queue directly
        :raises: ValueError if location is not a YouTube video
        """
        media = Media(loc, requester)
        self.add_media(media)

    def play_queue(self):
        """
        Plays queue in current state
        :return: None, modifies player directly
        """
        if self.playback_allowed:
            if self.player.is_playing():  # have to stop current player so songs do not overlap
                self.player.stop()
            self.player = self.instance.media_player_new(self.current_media.get_audio_url())
            self.events = self.player.event_manager()
            self.player.play()
            # callback to advance queue at end of song
            self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.advance_queue)

    def stop(self):
        """
        Stops playback, clears queue
        :return: None, modifies queue and player directly
        """
        self.player.stop()
        self.queue = []
        self.current_media = None

    def play_pause(self):
        """
        Stops or resumes playback without clearing queue
        :return: None, modifies player directly
        """
        self.player.set_pause(self.player.is_playing())  # tbh i don't the behavior of this function

    def get_queue(self):
        """
        Getter function for retrieving queue
        :return: Copy of queue object
        """
        return self.queue[::]  # return a protective copy

    def get_current_media(self):
        """
        Getter function for retrieving current media
        :return: Current media object, or None if there is no current media
        """
        return self.current_media

    def advance_queue(self, event=None):
        """
        Callback function to advances queue on media end
        :param event: Optional event object for VLC event handler
        :return: None, modifies queue and player directly
        """
        if len(self.queue) > 1:  # can advance to item directly
            self.current_media = self.queue[0]
            self.queue = self.queue[1::]
        elif len(self.queue) == 1:  # on last item
            self.current_media = self.queue[0]
            self.queue = []
        elif len(self.queue) == 0:  # queue is now completely empty
            self.current_media = None
            self.stop()

    def set_volume(self, volume):
        """
        Sets player volume to specified volume
        :param volume: Integer representing volume
        :return: None, modifies player directly
        """
        self.volume = volume
        self.player.audio_set_volume(volume)

    def get_volume(self):
        """
        Getter function for media volume
        :return: Volume of player
        """
        return self.volume

    def enable_playback(self):
        """
        Enables playback for play_queue function
        :return: None, modifies Player directly
        """
        self.playback_allowed = True

    def disable_playback(self):
        """
        Disables playback for play_queue function
        :return: None, modifies Player directly
        """
        self.playback_allowed = False

    def is_playback_allowed(self):
        """
        Gets state of if playback is currently allowed
        :return: True if playback is allowed, False if not
        """
        return self.playback_allowed


# Command handler function allows commands to be handled from main python file. REQUIRED.
def command_handler(command):
    pass


# You can add additional functions your module may need here.

# Put any initialization code here
pass