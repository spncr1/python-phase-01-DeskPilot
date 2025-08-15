# Logic for handling GPT integration
import sys
import random
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config import ASSISTANT_NAME, USER_NAME, MAX_TOKENS, TEMPERATURE, openai_client, OPENAI_AVAILABLE


# existing ask_gpt function retained for direct calls
def ask_gpt(prompt, system_message=None):
    """
    Send a prompt to GPT-3.5-turbo and return the response
    """
    try:
        # Check if OpenAI is available
        if not OPENAI_AVAILABLE or openai_client is None:
            return f"Sorry {USER_NAME}, OpenAI integration is not available. Please check your API key."

        if system_message is None:
            system_message = (
                f"You are {ASSISTANT_NAME}, an interactive personal desktop assistant. "
                f"You help with app launching, file organization, and general productivity tasks. "
                f"The user prefers to be addressed as '{USER_NAME}'. "
                f"Keep responses concise and helpful. Always address the user as 'sir'."
            )
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        answer = response.choices[0].message.content
        return answer.strip()
    except Exception as e:
        print(f"Error communicating with GPT: {e}")
        return f"Sorry {USER_NAME}, I'm having trouble processing that request right now."


def ask_gpt_with_context(prompt, context_messages):
    """
    Send a prompt with conversation context to GPT
    """
    try:
        # Check if OpenAI is available
        if not OPENAI_AVAILABLE or openai_client is None:
            return f"Sorry {USER_NAME}, OpenAI integration is not available. Please check your API key."

        if not context_messages or context_messages[0]["role"] != "system":
            system_msg = {
                "role": "system",
                "content": f"You are {ASSISTANT_NAME}, a helpful desktop assistant. Always address the user as 'sir'."
            }
            context_messages.insert(0, system_msg)

        messages = context_messages + [{"role": "user", "content": prompt}]

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in GPT conversation: {e}")
        return f"Sorry {USER_NAME}, I encountered an error during our conversation."


class GPTHandler:
    """
    Enhanced GPT handler for dynamic prompts and app launcher integration.
    """

    def __init__(self):
        # Local fallback prompts for quickness / offline dev
        self._local_prompts = [
            "What would you like to do, sir?",
            "How can I help you today, sir?",
            "Shall I open something for you, sir?",
            "What can I do for you, sir?",
            "Ready to assist you, sir. What shall we work on?",
            "What application would you like me to help with, sir?",
            "How may I be of service, sir?"
        ]

        # Track recent prompts to avoid repetition
        self._recent_prompts = []
        self._max_recent = 3

    def get_dynamic_prompt(self):
        """Get a varied, conversational prompt from GPT or fallback to local variants."""
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE or openai_client is None:
                print("OpenAI not available, using local prompt")
                return self._get_local_prompt()

            # Create a prompt that encourages variety
            gpt_request = (
                "Generate a short, polite prompt asking what the user would like to do. "
                "Make it conversational and professional. Address them as 'sir'. "
                "Consider suggesting they might want to open applications, check running apps, "
                "or ask questions. Keep it to one sentence under 15 words."
            )

            system_msg = (
                f"You are {ASSISTANT_NAME}, a sophisticated desktop assistant. "
                f"Create varied, engaging prompts that sound natural and professional. "
                f"Always address the user as 'sir'. Vary your phrasing to avoid repetition."
            )

            response = ask_gpt(gpt_request, system_message=system_msg)

            # Clean up the response
            first_line = response.split('\n')[0].strip()
            if len(first_line) > 0 and len(first_line) < 100:
                # Store in recent prompts and rotate if needed
                self._recent_prompts.append(first_line)
                if len(self._recent_prompts) > self._max_recent:
                    self._recent_prompts.pop(0)
                return first_line
            else:
                raise ValueError("GPT response too long or empty")

        except Exception as e:
            print(f"GPT prompt generation failed: {e}")
            return self._get_local_prompt()

    def _get_local_prompt(self):
        """Get a local fallback prompt"""
        # Return a local prompt that wasn't used recently
        available_prompts = [p for p in self._local_prompts if p not in self._recent_prompts]
        if not available_prompts:
            available_prompts = self._local_prompts

        chosen_prompt = random.choice(available_prompts)
        self._recent_prompts.append(chosen_prompt)
        if len(self._recent_prompts) > self._max_recent:
            self._recent_prompts.pop(0)

        return chosen_prompt

    def get_response(self, user_prompt):
        """Return a helpful response to a user prompt with app launcher context."""
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE or openai_client is None:
                return f"Sorry {USER_NAME}, I don't have access to GPT right now. Please check the OpenAI API configuration."

            # Enhanced system message for better app launcher integration
            system_msg = (
                f"You are {ASSISTANT_NAME}, a desktop assistant specializing in app launching and system management. "
                f"Always address the user as 'sir'. You can help with:\n"
                f"- Opening applications (Chrome, Safari, VS Code, Spotify, Notes, Terminal, Calculator, etc.)\n"
                f"- Closing/quitting applications\n"
                f"- Listing currently running applications\n"
                f"- General computer tasks and questions\n\n"
                f"For app requests, be encouraging and confirm what you'll do. "
                f"If you're unsure about an app name, suggest alternatives. "
                f"Keep responses concise but helpful."
            )

            return ask_gpt(user_prompt, system_message=system_msg)
        except Exception as e:
            return f"Sorry sir, I couldn't process that — {e}"

    def interpret_app_command(self, command):
        """
        Interpret voice commands for app operations using GPT.
        Returns a structured response with action and app name.
        """
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE or openai_client is None:
                return {'action': 'unknown', 'app': 'none', 'confidence': 'low', 'error': 'OpenAI not available'}

            gpt_request = (
                f"Analyze this voice command: '{command}'\n\n"
                f"Determine:\n"
                f"1. What action is requested (open, launch, start, quit, close, stop, list running apps)\n"
                f"2. Which application (if any) is mentioned\n\n"
                f"Respond in this format:\n"
                f"ACTION: [open/quit/list/unknown]\n"
                f"APP: [application name or 'none']\n"
                f"CONFIDENCE: [high/medium/low]\n\n"
                f"Common apps include: Chrome, Safari, Firefox, VS Code, Spotify, Notes, Terminal, Calculator, Mail, Calendar"
            )

            system_msg = (
                "You are an expert at parsing voice commands for a desktop assistant. "
                "Be precise in identifying actions and applications. "
                "Map common synonyms (e.g., 'browser' -> 'Chrome', 'code' -> 'VS Code')."
            )

            response = ask_gpt(gpt_request, system_message=system_msg)

            # Parse the structured response
            lines = response.split('\n')
            result = {'action': 'unknown', 'app': 'none', 'confidence': 'low'}

            for line in lines:
                if line.startswith('ACTION:'):
                    result['action'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('APP:'):
                    result['app'] = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    result['confidence'] = line.split(':', 1)[1].strip().lower()

            return result

        except Exception as e:
            print(f"Error interpreting command: {e}")
            return {'action': 'unknown', 'app': 'none', 'confidence': 'low', 'error': str(e)}

    def get_app_suggestion(self, failed_app_name):
        """Get GPT's suggestion for an app that couldn't be found."""
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE or openai_client is None:
                return f"Sorry sir, I couldn't find '{failed_app_name}' and I don't have access to GPT for suggestions right now."

            gpt_request = (
                f"The user tried to open '{failed_app_name}' but it's not installed or recognized. "
                f"Suggest 1-2 similar applications they might have meant, or explain what '{failed_app_name}' typically is. "
                f"Address them as 'sir' and keep it brief."
            )

            return ask_gpt(gpt_request)
        except Exception as e:
            return f"Sorry sir, I couldn't find '{failed_app_name}' and I'm having trouble suggesting alternatives right now."