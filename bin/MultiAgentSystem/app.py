from .ochestrator import multiagent_chat_once

if __name__ == "__main__":
    subject = "The impact of social media on mental health"
    user_message = "I want to write an essay about how social media affects teenagers' mental health."
    response = multiagent_chat_once(subject, user_message)
    print("Facilitator says:", response)