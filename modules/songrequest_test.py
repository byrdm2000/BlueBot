import unittest
from modules.songrequest import Media


class MediaTest(unittest.TestCase):
    """
    Partition: location is a YouTube ID, location is a YouTube link, location is a non-YouTube video link

    Note: YouTube test video being used is 'Rick Astley - Never Gonna Give You Up'
    """
    def test_youtube_video_id(self):
        request = Media("dQw4w9WgXcQ", "RickAstley")
        self.assertEqual(request.get_media_url(), "http://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(request.get_requester(), "RickAstley")
        self.assertEqual(request.get_media_title(), "Rick Astley - Never Gonna Give You Up (Video)")
        self.assertEqual(request.get_media_duration(), "00:03:32")
        self.assertEqual(request.get_media_length(), 212)
        self.assertTrue(request.get_audio_url().find("googlevideo"))

    def test_youtube_video_link(self):
        request = Media("http://www.youtube.com/watch?v=dQw4w9WgXcQ", "RickAstley")
        self.assertEqual(request.get_media_url(), "http://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(request.get_requester(), "RickAstley")
        self.assertEqual(request.get_media_title(), "Rick Astley - Never Gonna Give You Up (Video)")
        self.assertEqual(request.get_media_duration(), "00:03:32")
        self.assertEqual(request.get_media_length(), 212)
        self.assertTrue(request.get_audio_url().find("googlevideo"))

    def test_non_youtube_video(self):
        self.assertRaises(ValueError, Media, "http://www.youtube.com/", "RickAstley")


if __name__ == '__main__':
    unittest.main()
