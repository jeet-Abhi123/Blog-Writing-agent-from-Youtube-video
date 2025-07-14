import os
import streamlit as st
from typing import Optional, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.tools import TavilySearchResults

import re

# --- Setup ---
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

web_search_tool = TavilySearchResults(k=3)
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.6)

class State(TypedDict):
    video_url: str
    transcript: Optional[str]
    title: Optional[str]
    blog_content: Optional[str]
    review_feedback: Optional[str]
    refine_blog: Optional[bool]
    search_query: Optional[str]
    search_results: Optional[str]
    additional_comments: Optional[str]

def extract_video_id(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^&\s]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL")

def Document_Loader(state: State) -> State:
    try:
        video_id = extract_video_id(state['video_url'])
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry['text'] for entry in transcript_list])
        return {**state, 'transcript': transcript}
    except Exception as e:
        return {**state, 'transcript': "Unable to load transcript."}

def Title_Generator(state: State) -> State:
    if not state['transcript'] or state['transcript'] == "Unable to load transcript.":
        return {**state, 'title': "Could not generate title due to transcript loading issue."}
    prompt = f"Generate a only one catchy and relevant title for a blog post based on the following transcript:\n\nTranscript:\n{state['transcript']}\n Note: Just give only one title."
    title = llm.invoke(prompt)
    return {**state, 'title': title.content}

def Web_Search(state: State) -> State:
    search_query = state.get('title', '').strip()
    if not search_query:
        transcript = state.get('transcript', '')
        if transcript and transcript != "Unable to load transcript.":
            search_query = " ".join(transcript.split()[:100])
        else:
            return {**state, 'search_results': 'No search query could be generated.'}
    try:
        results = web_search_tool.run(search_query)
        return {**state, 'search_query': search_query, 'search_results': results}
    except Exception as e:
        return {**state, 'search_results': f"An error occurred during web search: {e}"}

def Blog_Creator(state: State) -> State:
    if not state['transcript'] or state['transcript'] == "Unable to load transcript.":
        return {**state, 'blog_content': "Could not generate blog content due to transcript loading issue."}
    prompt = f"Create a comprehensive and engaging blog post from the following transcript. " \
             f"Use the following web search results for additional context and enrichment. " \
             f"Ensure the content is well-structured, informative, and captures the key points.\n\n" \
             f"Transcript:\n{state['transcript']}\n\n" \
             f"Web Search Results:\n{state.get('search_results', 'No search results.')}"
    blog_content = llm.invoke(prompt)
    return {**state, 'blog_content': blog_content.content}

def Reviewer(state: State) -> State:
    review_prompt = f"Review the following blog post and provide constructive feedback:\n\n{state['blog_content']}"
    feedback = llm.invoke(review_prompt)
    return {**state, 'review_feedback': feedback.content}

def Blog_Refiner(state: State) -> State:
    if state.get('refine_blog', False):
        refined_prompt = f"Refine the following blog post based on these comments: {state['additional_comments']}\n\nOriginal Blog:\n{state['blog_content']}"
        refined_blog_content = llm.invoke(refined_prompt)
        return {**state, 'blog_content': refined_blog_content.content}
    return state

# --- Streamlit UI ---
# ...existing code...

# --- Streamlit UI ---
st.set_page_config(page_title="YouTube to Blog Generator", page_icon="📝", layout="centered")
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
    }
    .stButton>button {
        background-color: #6366f1;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 2em;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1.5px solid #6366f1;
    }
    .stTextArea textarea {
        border-radius: 8px;
        border: 1.5px solid #6366f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; color: #6366f1;'>📝 YouTube to Blog Generator</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 1.2em;'>Turn any YouTube video into a beautiful blog post with AI magic!</p>",
    unsafe_allow_html=True,
)

st.image(
    "https://cdn.pixabay.com/photo/2017/01/10/19/05/typing-1972328_1280.jpg",
    use_container_width =True,
    caption="Let AI do the writing for you!"
)

if "output_state" not in st.session_state:
    st.session_state.output_state = None

video_url = st.text_input("Enter YouTube URL:")

if st.button("Generate Blog"):
    with st.spinner("Generating blog post..."):
        initial_state = {'video_url': video_url}
        # Run pipeline
        state = Document_Loader(initial_state)
        state = Title_Generator(state)
        state = Web_Search(state)
        state = Blog_Creator(state)
        state = Reviewer(state)
        st.session_state.output_state = state

if st.session_state.output_state:
    st.subheader("📰 Generated Blog Post")
    st.markdown(st.session_state.output_state.get('blog_content', 'No blog content generated.'))

    st.markdown("---")
    st.markdown("<h4 style='color:#6366f1;'>Want to refine your blog post?</h4>", unsafe_allow_html=True)
    refine = st.checkbox("Refine blog post with your comments?")
    if refine:
        comments = st.text_area("Your comments for refinement:")
        if st.button("Refine Blog"):
            with st.spinner("Refining blog post..."):
                state = st.session_state.output_state
                state['refine_blog'] = True
                state['additional_comments'] = comments
                state = Blog_Refiner(state)
                state = Reviewer(state)
                st.session_state.output_state = state
                st.success("Blog refined!")
                st.markdown(st.session_state.output_state.get('blog_content', 'No refined blog content generated.'))
