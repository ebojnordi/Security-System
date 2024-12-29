import unittest
import os
import json
from app import log_event, save_events_to_file, events, event_log_file


class TestEventLogging(unittest.TestCase):
    def setUp(self):
        """
        Create a temporary environment for testing.
        """
        self.test_event_file = "test_events_log.json"
        self.test_image_folder = "test_images"
        os.makedirs(self.test_image_folder, exist_ok=True)

        # Use a temporary file for testing
        self.test_event_file = event_log_file

        # Clear events list
        events.clear()

    def test_log_event(self):
        """
        Test the log_event function to ensure it correctly adds events.
        """
        event_type = "Test Detection"
        image_filename = "test_image.jpg"
        log_event(event_type, image_filename)

        # Verify that the event was added
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], event_type)
        self.assertEqual(events[0]["image_filename"], image_filename)

    def test_save_events_to_file(self):
        """
        Test the save_events_to_file function to ensure it saves events to a JSON file.
        """
        # Log a sample event
        log_event("Test Event", "test_image.jpg")
        save_events_to_file()

        # Verify the file was created
        self.assertTrue(os.path.exists(self.test_event_file))

        # Verify the file contents
        with open(self.test_event_file, "r") as file:
            saved_events = json.load(file)
        self.assertEqual(len(saved_events), 1)
        self.assertEqual(saved_events[0]["event_type"], "Test Event")

    def test_image_capture(self):
        """
        Test that images can be saved to the designated folder.
        """
        test_image_path = os.path.join(self.test_image_folder, "test_image.jpg")
        dummy_image_data = b"dummy_image_data"

        # Simulate saving an image
        with open(test_image_path, "wb") as file:
            file.write(dummy_image_data)

        # Verify the image file exists
        self.assertTrue(os.path.exists(test_image_path))

        # Verify the image content
        with open(test_image_path, "rb") as file:
            saved_data = file.read()
        self.assertEqual(saved_data, dummy_image_data)


def test_save_events_to_file(self):
    # Create a test event
    test_event = {"timestamp": "2024-12-28 12:00:00", "event_type": "Test Event", "image_filename": "test.jpg"}
    events.append(test_event)

    # Save events to file
    save_events_to_file()

    # Check if the file exists
    self.assertTrue(os.path.exists(self.test_event_file), "The events file was not created.")

    # Check if the contents match
    with open(self.test_event_file, 'r') as file:
        saved_events = json.load(file)
        self.assertIn(test_event, saved_events, "The test event was not saved correctly.")


def tearDown(self):
    """
    Clean up the testing environment.
    """
    if os.path.exists(self.test_event_file):
        os.remove(self.test_event_file)

    for file in os.listdir(self.test_image_folder):
        os.remove(os.path.join(self.test_image_folder, file))

    os.rmdir(self.test_image_folder)


if __name__ == '__main__':
    unittest.main()
