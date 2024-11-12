# Importing necessary libraries
import streamlit as st
import asyncio
import arxiv  # Make sure you have installed the arxiv library

# Import necessary classes
from openchat_agent import OpenChatAgent  # Make sure OpenChatAgent is implemented here
from ResearchDatabase import ResearchDatabase  # Make sure ResearchDatabase is implemented here

# Define the main function for Streamlit UI
def main():
    st.title("Academic Research Assistant (OpenChat)")

    # Initialize OpenChat agent
    if 'chat_agent' not in st.session_state:
        st.session_state.chat_agent = OpenChatAgent()
    
    # Initialize database
    if 'db' not in st.session_state:
        st.session_state.db = ResearchDatabase()
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Choose Function",
        ["Search & Analyze", "Research Q&A", "Generate Review"]
    )

    # Handle page-specific actions
    if page == "Search & Analyze":
        handle_search_and_analyze()
    elif page == "Research Q&A":
        handle_research_qa()
    elif page == "Generate Review":
        handle_generate_review()

# Function to handle Search & Analyze page
def handle_search_and_analyze():
    st.header("Search & Analyze Research Papers")

    topic = st.text_input("Enter research topic:")
    num_papers = st.slider("Number of papers to analyze", 1, 20, 5)

    if st.button("Search and Analyze"):
        if topic:
            with st.spinner("Searching and analyzing papers..."):
                papers = search_and_analyze_papers(topic, num_papers)
                display_papers(papers)
        else:
            st.warning("Please enter a research topic.")

# Function to search and analyze papers
def search_and_analyze_papers(topic, num_papers):
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=num_papers,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []

    for result in client.results(search):
        paper = {
            'id': result.entry_id,
            'title': result.title,
            'authors': [str(author) for author in result.authors],
            'summary': result.summary,
            'published_date': result.published.strftime('%Y-%m-%d'),
            'topic': topic
        }
        
        # Analyze paper with OpenChat
        try:
            analysis = asyncio.run(st.session_state.chat_agent.analyze_paper(paper))
            paper['detailed_analysis'] = analysis['detailed_analysis']
            st.session_state.db.store_paper(paper)
            papers.append(paper)
        except Exception as e:
            st.error(f"Error analyzing paper: {e}")

    return papers

# Function to display papers
def display_papers(papers):
    st.success(f"Analyzed {len(papers)} papers")
    for paper in papers:
        with st.expander(f"📄 {paper['title']}"):
            st.write(f"**Authors:** {', '.join(paper['authors'])}")
            st.write(f"**Published:** {paper['published_date']}")
            st.write("**Original Abstract:**")
            st.write(paper['summary'])
            st.write("**Detailed Analysis:**")
            st.write(paper.get('detailed_analysis', "No analysis available"))

# Function to handle Research Q&A page
def handle_research_qa():
    st.header("Research Questions & Answers")

    topic = st.text_input("Select research topic for context:")
    question = st.text_area("Enter your research question:")

    if st.button("Get Answer"):
        if topic and question:
            with st.spinner("Analyzing and generating answer..."):
                context_papers = st.session_state.db.get_papers(topic, limit=3)
                if not context_papers:
                    st.warning("No papers found for this topic. Please search for papers first.")
                else:
                    answer = generate_answer(question, context_papers)
                    st.write("**Answer:**")
                    st.write(answer)
                    st.write("**Based on papers:**")
                    for paper in context_papers:
                        st.write(f"- {paper['title']}")
        else:
            st.warning("Please provide both topic and question.")

# Function to generate an answer using OpenChat
def generate_answer(question, context_papers):
    try:
        return asyncio.run(
            st.session_state.chat_agent.answer_research_question(question, context_papers)
        )
    except Exception as e:
        st.error(f"Error generating answer: {e}")
        return "Could not generate an answer due to an error."

# Function to handle Generate Review page
def handle_generate_review():
    st.header("Generate Research Review")

    topic = st.text_input("Enter research topic:")

    if st.button("Generate Review"):
        if topic:
            with st.spinner("Generating research review..."):
                papers = st.session_state.db.get_papers(topic, limit=10)
                if not papers:
                    st.warning("No papers found for this topic. Please search for papers first.")
                else:
                    research_directions = generate_research_review(papers)
                    st.write("**Research Review and Future Directions:**")
                    st.write(research_directions)
                    st.write("**Based on papers:**")
                    for paper in papers:
                        st.write(f"- {paper['title']}")
        else:
            st.warning("Please enter a topic.")

# Function to generate a research review
def generate_research_review(papers):
    try:
        return asyncio.run(
            st.session_state.chat_agent.generate_research_directions(papers)
        )
    except Exception as e:
        st.error(f"Error generating research review: {e}")
        return "Could not generate a review due to an error."

# Run the Streamlit app
if __name__ == "__main__":
    main()
