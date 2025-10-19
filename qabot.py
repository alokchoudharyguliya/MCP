import openai
class QABotMCP:
    def __init__(self,model="gpt-4",max_history=10):
        """
        MCP-based Q&A bot with memory of past conversation
        """
        self.model=model
        self.max_history=max_history
        self.history=[]

    def add_to_context(self,role,content):
        """
        Adds a message to conversation history
        """
        self.history.append({"role":role,"content":content})
        if len(self.history)>self.max_history:
            self.history=self.history[-self.max_history:]

    def ask(self,question):
        """
        Sends a question to OpenAI API with context and returns answer.
        """
        self.add_to_context("user",question)
        response=openai.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=0.7
        )
        answer=response.choices[0].message.content
        self.add_to_context("assistant",answer)
        return answer