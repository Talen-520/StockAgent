import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))  # Add src to PATH, adjust the path based on the file location
import unittest 

from agent import ConversationalAssistant

class TestConversationalAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant = ConversationalAssistant()

    def test_process_user_input(self):
        response = self.assistant.process_user_input("Hello")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_clear_conversation(self):
        self.assistant.process_user_input("Hello")
        self.assistant.clear_conversation()
        self.assertEqual(len(self.assistant.conversation_history), 0)

if __name__ == "__main__":
    unittest.main()