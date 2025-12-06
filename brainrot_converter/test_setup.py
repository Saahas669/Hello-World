#!/usr/bin/env python
"""
Quick test script to verify Ollama connection and Brainrot Converter setup
"""

import sys
import requests

def test_ollama():
    """Test if Ollama is running and Mistral is available"""
    print("Testing Ollama connection...")
    print("-" * 50)
    
    try:
        # Check if Ollama is running
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        print("✓ Ollama is running on http://localhost:11434")
        
        # Check if Mistral is available
        data = response.json()
        models = [model['name'] for model in data.get('models', [])]
        
        if not models:
            print("✗ No models installed")
            print("  Run: ollama pull mistral")
            return False
        
        print(f"✓ Available models: {', '.join(models)}")
        
        if 'mistral' not in ' '.join(models):
            print("⚠ Mistral not found. Available:", models)
            print("  Run: ollama pull mistral")
            return False
        
        print("✓ Mistral 7B is available")
        
        # Test a simple conversion
        print("\nTesting conversion...")
        print("-" * 50)
        
        from ollama import generate
        
        test_text = "Hello, how are you doing today?"
        print(f"Input: {test_text}")
        
        response = generate(
            model='mistral',
            prompt=f"Convert to Gen Z/brainrot slang: '{test_text}' while keeping meaning similar.",
            stream=False,
            host='http://localhost:11434'
        )
        
        converted = response['response'].strip()
        print(f"Output: {converted}")
        print("✓ Conversion test successful!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama")
        print("  Ollama is not running!")
        print("  Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Brainrot Converter - System Check")
    print("=" * 50 + "\n")
    
    success = test_ollama()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All systems go! Ready to convert PDFs")
        print("  Visit: http://localhost:5000")
    else:
        print("✗ Setup incomplete. See errors above")
    print("=" * 50 + "\n")
    
    sys.exit(0 if success else 1)
