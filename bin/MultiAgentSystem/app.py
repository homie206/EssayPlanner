from .ochestrator import multiagent_chat_once

if __name__ == "__main__":
    # Example usage
    # change the subject and user message as needed
    subject = "The impact of social media on mental health"
    user_message = "I want to write an essay about history of UK."
    facilitator_response, idea_generator_response = multiagent_chat_once(subject, user_message)
    print("Facilitator says:", facilitator_response)
    print("Idea Generator says:", idea_generator_response)