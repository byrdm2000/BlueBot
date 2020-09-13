import pafy

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


# Command handler function allows commands to be handled from main python file. REQUIRED.
def command_handler(command):
    pass


# You can add additional functions your module may need here.

# Put any initialization code here
pass