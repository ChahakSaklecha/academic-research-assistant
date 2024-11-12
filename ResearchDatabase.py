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

class ResearchDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('research_papers.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS papers
                    (id TEXT PRIMARY KEY,
                     title TEXT,
                     authors TEXT,
                     summary TEXT,
                     published_date TEXT,
                     topic TEXT,
                     analysis TEXT)''')
        self.conn.commit()
    
    def store_paper(self, paper: Dict):
        c = self.conn.cursor()
        c.execute('''INSERT OR REPLACE INTO papers
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (paper['id'],
                  paper['title'],
                  json.dumps(paper['authors']),
                  paper['summary'],
                  paper['published_date'],
                  paper['topic'],
                  paper.get('detailed_analysis', '')))
        self.conn.commit()
    
    def get_papers(self, topic: str, limit: int = 10) -> List[Dict]:
        c = self.conn.cursor()
        c.execute('''SELECT * FROM papers WHERE topic = ? 
                    ORDER BY published_date DESC LIMIT ?''',
                 (topic, limit))
        papers = []
        for row in c.fetchall():
            papers.append({
                'id': row[0],
                'title': row[1],
                'authors': json.loads(row[2]),
                'summary': row[3],
                'published_date': row[4],
                'topic': row[5],
                'detailed_analysis': row[6]
            })
        return papers