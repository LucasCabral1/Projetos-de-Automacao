from gpt4all import GPT4All

model = GPT4All("ggml-gpt4all-j-v1.3-groovy.bin")

model.open()
response = model.prompt("Summarize this article: https://news.ycombinator.com/")
print(response)