import unittest
from modules.songrequest import Media
from modules.songrequest import Player


class MediaTest(unittest.TestCase):
    """
    Partition: location is a YouTube ID, location is a YouTube link, location is a non-YouTube video link

    Note: YouTube test video being used is 'Rick Astley - Never Gonna Give You Up'
    """
    def test_youtube_video_id(self):
        # Covers location is a YouTube ID
        request = Media("dQw4w9WgXcQ", "RickAstley")
        self.assertEqual(request.get_media_url(), "http://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(request.get_requester(), "RickAstley")
        self.assertEqual(request.get_media_title(), "Rick Astley - Never Gonna Give You Up (Video)")
        self.assertEqual(request.get_media_duration(), "00:03:32")
        self.assertEqual(request.get_media_length(), 212)
        self.assertTrue(request.get_audio_url().find("googlevideo"))

    def test_youtube_video_link(self):
        # Covers location is a YouTube link
        request = Media("http://www.youtube.com/watch?v=dQw4w9WgXcQ", "RickAstley")
        self.assertEqual(request.get_media_url(), "http://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(request.get_requester(), "RickAstley")
        self.assertEqual(request.get_media_title(), "Rick Astley - Never Gonna Give You Up (Video)")
        self.assertEqual(request.get_media_duration(), "00:03:32")
        self.assertEqual(request.get_media_length(), 212)
        self.assertTrue(request.get_audio_url().find("googlevideo"))

    def test_non_youtube_video(self):
        # Covers location is a non-YouTube video link
        self.assertRaises(ValueError, Media, "http://www.youtube.com/", "RickAstley")


class PlayerTest(unittest.TestCase):

    """
    Tests for add_media

    Partition on queue: queue is empty, queue is not empty
    Partition on current media: there is current media, there isn't current media
    """

    def test_add_media_empty_queue_no_media(self):
        # Covers queue is empty, there isn't current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        self.assertEqual([], player.get_queue())
        self.assertEqual(media, player.get_current_media())

    def test_add_media_empty_queue_current_media(self):
        # Covers queue is empty, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        self.assertEqual([media], player.get_queue())
        self.assertEqual(media, player.get_current_media())

    def test_add_media_nonempty_queue_current_media(self):
        # Covers queue is not empty, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        player.add_media(media)
        self.assertEqual([media, media], player.get_queue())
        self.assertEqual(media, player.get_current_media())

    # Since add_loc is a wrapper for add_media, its tests are covered by tests for the Media object

    # Since play_queue only interfaces with VLC, it does not need to be explicitly tested

    """
    Tests for stop
    
    Partition on queue: queue is empty, queue is non-empty
    Partition on current_media: there is current media, there isn't current media
    """

    def test_stop_empty_queue_no_media(self):
        # Covers queue is empty, there isn't current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.stop()
        self.assertEqual([], player.get_queue())
        self.assertIsNone(player.get_current_media())

    def test_stop_empty_queue_current_media(self):
        # Covers queue is empty, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        player.stop()
        self.assertEqual([], player.get_queue())
        self.assertIsNone(player.get_current_media())

    def test_stop_nonempty_queue_current_media(self):
        # Covers queue is not empty, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        player.add_media(media)
        player.stop()
        self.assertEqual([], player.get_queue())
        self.assertIsNone(player.get_current_media())

    # Since play_pause only interfaces with VLC, it does not need to be explicitly tested

    """
    Tests for get_queue
    
    Partition on queue: queue is empty, queue is nonempty
    """

    def test_get_queue_empty_queue(self):
        # Covers queue is empty
        player = Player()
        self.assertEqual([], player.get_queue())

    def test_get_queue_nonempty_queue(self):
        # Covers queue is nonempty
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        self.assertEqual([media], player.get_queue())

    """
    Tests for get_current_media
    
    Partition on current_media: there is current media, there isn't current media
    """

    def test_get_current_media_media_present(self):
        # Covers there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        self.assertEqual(media, player.get_current_media())

    def test_get_current_media_media_not_present(self):
        # Covers there isn't current media
        player = Player()
        self.assertEqual([], player.get_queue())

    """
    Tests for advance_queue
    
    Partition on queue: queue is empty, len(queue) = 1, len(queue) > 1
    Partition on current_media: there is current media, there isn't current media
    """

    def test_advance_queue_empty_queue_no_media(self):
        # Covers queue is empty, there isn't current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        player.advance_queue()
        self.assertEqual([], player.get_queue())
        self.assertIsNone(player.get_current_media())

    def test_advance_queue_empty_queue_current_media(self):
        # Covers queue is empty, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.advance_queue()
        self.assertEqual([], player.get_queue())
        self.assertIsNone(player.get_current_media())

    def test_advance_queue_1_queue_current_media(self):
        # Covers len(queue) = 1, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        player.advance_queue()
        self.assertEqual([], player.get_queue())
        self.assertEqual(media, player.get_current_media())

    def test_advance_queue_long_queue_current_media(self):
        # Covers len(queue) > 1, there is current media
        player = Player()
        player.disable_playback()  # to prevent media from playing
        media = Media("dQw4w9WgXcQ", "RickAstley")
        player.add_media(media)
        player.add_media(media)
        player.add_media(media)
        player.advance_queue()
        self.assertEqual([media], player.get_queue())
        self.assertEqual(media, player.get_current_media())

    """
    Tests for volume-related methods
    """

    def test_volume_set_and_get(self):
        player = Player()
        volume = 50
        player.set_volume(volume)
        self.assertEqual(volume, player.get_volume())

    """
    Tests for playback allowed methods
    
    Partition on is_playback_allowed: is_playback_allowed = True, is_playback_allowed = False
    """

    def test_playback_not_allowed(self):
        # Covers is_playback_allowed = False
        player = Player()
        player.disable_playback()
        self.assertFalse(player.is_playback_allowed())

    def test_playback_allowed(self):
        # Covers is_playback_allowed = True
        player = Player()
        player.enable_playback()
        self.assertTrue(player.is_playback_allowed())


if __name__ == '__main__':
    unittest.main()
