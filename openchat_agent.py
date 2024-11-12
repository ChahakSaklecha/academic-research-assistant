import streamlit as st
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import arxiv
import pandas as pd
import sqlite3
import json
import asyncio
import aiohttp
import ollama
from functools import lru_cache

class OpenChatAgent:
    def __init__(self):
        self.model = "openchat"
        self.system_prompt = """You are an expert academic research assistant with deep knowledge 
        of scientific literature and research methodologies. Your goal is to help researchers 
        understand papers, identify trends, and generate insights."""
    
    @lru_cache(maxsize=100)
    async def generate_response(self, prompt: str) -> str:
        try:
            # Format prompt following OpenChat's preferred style
            formatted_prompt = f"""System: {self.system_prompt}
            
            Human: {prompt}
            
            Assistant: Let me help you with that. I'll provide a detailed and academically rigorous response."""
            
            response = ollama.generate(
                model=self.model,
                prompt=formatted_prompt,
            )
            return response['response']
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def analyze_paper(self, paper: Dict) -> Dict:
        prompt = f"""Please analyze this research paper in detail:
        
        Title: {paper['title']}
        Authors: {', '.join(paper['authors'])}
        Abstract: {paper['summary']}
        
        Provide the following:
        1. Main Research Question
        2. Methodology Overview
        3. Key Findings
        4. Theoretical Contributions
        5. Practical Implications
        6. Limitations and Future Work
        
        Format your response in a structured manner suitable for academic review."""
        
        analysis = await self.generate_response(prompt)
        return {
            **paper,
            'detailed_analysis': analysis
        }
    
    async def generate_research_directions(self, papers: List[Dict]) -> str:
        recent_papers = "\n\n".join([
            f"Title: {p['title']}\nKey Findings: {p['summary']}"
            for p in papers[:5]
        ])
        
        prompt = f"""Based on these recent papers in the field:

        {recent_papers}

        Please provide:
        1. Synthesis of Current Research Trends
        2. Identification of Research Gaps
        3. Promising Future Research Directions
        4. Methodological Recommendations
        5. Potential Breakthrough Areas

        Focus on actionable research directions that could lead to significant advances."""
        
        return await self.generate_response(prompt)
    
    async def answer_research_question(self, question: str, context: List[Dict]) -> str:
        context_text = "\n\n".join([
            f"Paper {i+1}:\nTitle: {paper['title']}\nSummary: {paper['summary']}"
            for i, paper in enumerate(context[:3])
        ])
        
        prompt = f"""Based on these research papers:

        {context_text}

        Please answer this research question:
        {question}

        Provide:
        1. Direct answer to the question
        2. Supporting evidence from the papers
        3. Critical analysis
        4. Related considerations
        5. Potential limitations of the answer"""
        
        return await self.generate_response(prompt)