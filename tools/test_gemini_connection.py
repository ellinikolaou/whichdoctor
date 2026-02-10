"""
Test script to verify Gemini API connection.
Phase 2: Link - Connectivity verification
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    """Test Gemini API connection and basic functionality."""
    
    print("=" * 60)
    print("GEMINI API CONNECTION TEST")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("[X] ERROR: GEMINI_API_KEY not found in .env file")
        print("Please ensure .env file exists with GEMINI_API_KEY=your_key_here")
        return False
    
    print(f"[OK] API Key loaded (length: {len(api_key)} characters)")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("[OK] Gemini API configured successfully")
        
        # Test with a simple medical query
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("\n[*] Testing API call with sample medical query...")
        
        test_prompt = """
        You are a medical advisor helping users find the right specialist.
        
        Symptoms: Persistent fatigue, unexplained weight gain, cold sensitivity
        
        Based on these symptoms, suggest ONE appropriate medical specialist type and explain why.
        Keep your response brief (2-3 sentences).
        """
        
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            print("[OK] API call successful!")
            print("\n" + "-" * 60)
            print("SAMPLE RESPONSE:")
            print("-" * 60)
            print(response.text)
            print("-" * 60)
            
            print("\n[OK] ALL TESTS PASSED")
            print("=" * 60)
            print("Gemini API is ready for use!")
            print("=" * 60)
            return True
        else:
            print("[X] ERROR: Empty response from API")
            return False
            
    except Exception as e:
        print(f"[X] ERROR: {type(e).__name__}: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify API key is correct in .env file")
        print("2. Check internet connection")
        print("3. Ensure API key has proper permissions")
        print("4. Check if you've exceeded rate limits")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
