
---
title: Blog gneration agent from Youtube videos
emoji: 🤖
colorFrom: teal
colorTo: blue
sdk: docker        
app_port: 8501   
---


# Blog Generation from Youtube Video 

### 🎯 Goal
The aim of this project is to build a complete agentic pipeline from generating a blog post from a youtube video url. We will be using Langgraph framework for building 
the complete workflow. 
**Note**: You will require your own Groq, Tavily search and langsmith API key for running this project. <br> 

- Groq API: It is for using open source LLMs being provided by the Groq inference(Best part : it is free to some extent). You can use OpenAI, Gemini or any other API key as well.
- Tavily Search API: This is required for the web search capability we are providing to the llm.
- Langsmith API: To observe the whole workflow of the pipeline, and see how it is executing in each step. You can see the whole tracing of this project on your langsmith dashboard.
Other alternatives for this: LangFuse and Arize.

### 🚀 Approach
- The process begins by taking a YouTube URL and extracting the video's transcript.
- An AI agent then generates a suitable title and conducts a web search to gather additional context and relevant information.
- Using both the transcript and the search results, the system drafts an initial blog post.
- A distinctive feature of this workflow is its review
and refinement cycle. A specialized "reviewer" agent assesses the initial draft and provides feedback.
The process then allows for human-in-the-loop intervention, where a user can offer
  their own comments for improvement. If refinement is requested, another agent incorporates the feedback to enhance the blog
   post. <br>

  This iterative process, orchestrated using LangGraph, ensures the final output is well-structured, informative, and
  polished. The underlying language model operations are powered by the Groq API for efficient processing.

<img width="286" height="811" alt="Image" src="https://github.com/user-attachments/assets/f9187521-1aed-4a01-9d0b-bc2bf67aef41" />

### 📢 Future Work
There videos on youtube which are 2, 3 hours long. So, this whole context cannot be provided to the llm in one go. Because they don't have long context window. 
In future, we would be integrating this pipeline with Agentic RAG capabilities for longer videos. 
