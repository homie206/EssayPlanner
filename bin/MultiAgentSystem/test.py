from .llm_connector import create_agent, chat
from .prompts import build_prompt_for_agent
from .tools import Tools


prompt = build_prompt_for_agent("SubjectSpecialist", "mental health")
subject_specialist_agent = create_agent(prompt, tools=[Tools.retrieve_knowledge])


reply = chat(
            subject_specialist_agent,      
            "user message : " + "effects of soical media on mental health" + "\n" + "The ideas that are generated: " + "Excessive use of social media is linked to loneliness and social isolation despite its purpose to connect people.\n"
    "- Fear of missing out (FOMO) is a common effect, causing stress and dissatisfaction with one's own life.\n"
    "- Cyberbullying on social media platforms significantly worsens mental health, increasing depressive symptoms and emotional distress.\n"
    "- Social media can disrupt impulse control and emotional regulation, making users more sensitive to social rewards and punishments.\n"
    "- Heavy social media use is associated with higher risks of self-harm and suicidal thoughts, especially among adolescents.\n"
    "- Positive effects include opportunities for social support, community building, and mental health awareness campaigns.\n"
    "- Social media can affect sleep patterns negatively, which in turn impacts mental health.\n"
    "- The constant need for validation through likes and comments can lead to decreased self-esteem.\n"
    "- Social media platforms can sometimes provide a space for marginalized groups to find acceptance and reduce feelings of isolation.\n"
    "- Exposure to misinformation or negative news on social media can increase psychological distress.\n"
    "- Social media use can influence social behavior, sometimes reducing face-to-face interactions and real-world social skills.\n"
    "- Some studies suggest that mindful and limited use of social media can mitigate negative mental health effects.\n"
    "- Social media algorithms that prioritize sensational or emotionally charged content can exacerbate anxiety and stress.\n"
    "- Online communities focused on mental health can offer peer support and reduce stigma around mental illness.",
            thread_id="abc"
        )

print(reply)