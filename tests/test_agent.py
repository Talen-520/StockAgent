
import sys
import os
import unittest 
from agentDeprecated import ConversationalAssistant

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

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