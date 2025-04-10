import requests
import json
import pandas as pd
from datetime import datetime
import time
import random

class QuoraScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.quora.com/',
            'Origin': 'https://www.quora.com'
        }
        self.session.headers.update(self.headers)
    
    def get_question_id(self, url):
        """Extract the question ID from the URL"""
        # This is a simplified example - in reality, we'd need to get this from the page
        return url.split('/')[-1]
    
    def get_answers(self, question_id, cursor=None, limit=20):
        """Get answers using Quora's GraphQL API"""
        api_url = "https://www.quora.com/graphql/gql_para_POST?q=QuestionAnswerPagedListQuery"
        
        variables = {
            "questionId": question_id,
            "first": limit,
            "after": cursor
        }
        
        payload = {
            "queryName": "QuestionAnswerPagedListQuery",
            "variables": json.dumps(variables),
            "extensions": {
                "hash": "graphql_query_hash"  # This would need to be updated with the correct hash
            }
        }
        
        try:
            response = self.session.post(api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching answers: {e}")
            return None
    
    def extract_answers_from_response(self, response_data):
        """Extract answers from the API response"""
        answers = []
        
        try:
            # This is a simplified example - the actual response structure would need to be determined
            answer_nodes = response_data.get('data', {}).get('question', {}).get('answers', {}).get('edges', [])
            
            for idx, node in enumerate(answer_nodes, 1):
                answer = node.get('node', {})
                
                answers.append({
                    'answer_number': idx,
                    'author': answer.get('author', {}).get('name', 'Anonymous'),
                    'timestamp': answer.get('createdTime', 'Unknown date'),
                    'text': answer.get('text', '')
                })
                
                print(f"Extracted answer {idx}")
                
        except Exception as e:
            print(f"Error processing answers: {e}")
        
        return answers
    
    def save_to_csv(self, answers, filename='quora_stories.csv'):
        """Save the extracted answers to a CSV file"""
        if answers:
            df = pd.DataFrame(answers)
            df.to_csv(filename, index=False)
            print(f"Successfully saved {len(answers)} answers to {filename}")
        else:
            print("No answers to save")
    
    def save_to_json(self, answers, filename='quora_stories.json'):
        """Save the extracted answers to a JSON file"""
        if answers:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(answers, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(answers)} answers to {filename}")
        else:
            print("No answers to save")
    
    def scrape_stories(self, url, max_answers=100):
        """Main method to scrape stories from Quora"""
        try:
            print(f"Processing URL: {url}")
            question_id = self.get_question_id(url)
            
            all_answers = []
            cursor = None
            
            while len(all_answers) < max_answers:
                print(f"Fetching answers (current count: {len(all_answers)})")
                
                response_data = self.get_answers(question_id, cursor)
                if not response_data:
                    break
                
                new_answers = self.extract_answers_from_response(response_data)
                if not new_answers:
                    break
                
                all_answers.extend(new_answers)
                
                # Update cursor for next page
                # This would need to be extracted from the response
                cursor = response_data.get('data', {}).get('question', {}).get('answers', {}).get('pageInfo', {}).get('endCursor')
                
                if not cursor:
                    break
                
                # Add a delay between requests
                time.sleep(random.uniform(1, 3))
            
            # Save the results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_to_csv(all_answers, f'quora_stories_{timestamp}.csv')
            self.save_to_json(all_answers, f'quora_stories_{timestamp}.json')
            
            return all_answers
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

if __name__ == "__main__":
    # URL of the Quora question
    url = "https://www.quora.com/What-is-your-personal-story-of-gender-inequality"
    
    # Initialize the scraper
    scraper = QuoraScraper()
    
    # Scrape the stories
    stories = scraper.scrape_stories(url)
    
    print(f"Scraped {len(stories)} stories successfully!") 