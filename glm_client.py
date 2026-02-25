#!/usr/bin/env python3
"""
GLM-5 Client for WellTegra Forensic Engine
Uses built-in urllib (no external dependencies)
"""

import urllib.request
import urllib.error
import json
import os
import sys

class GLMClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ZAI_API_KEY")
        self.base_url = "https://api.z.ai/api/paas/v4/chat/completions"
        self.model = "glm-5"
        
        if not self.api_key:
            raise ValueError("Set ZAI_API_KEY environment variable")
    
    def chat(self, prompt, max_tokens=4096):
        """Send prompt to GLM-5"""
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {"error": json.loads(e.read().decode('utf-8'))}

def main():
    client = GLMClient()
    
    if len(sys.argv) < 2:
        print("Usage: python3 glm_client.py <prompt>")
        return
    
    prompt = " ".join(sys.argv[1:])
    print(f"Sending: {prompt}\n")
    result = client.chat(prompt)
    
    if "choices" in result:
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error: {result}")

if __name__ == "__main__":
    main()
