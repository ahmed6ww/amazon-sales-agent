#!/usr/bin/env python3
"""
Final focused test for the research agent to verify OpenAI traces
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append('/home/ahmed/Desktop/code/Freelance/amazon-sales-agent/backend')

def test_research_agent_final():
    """Final test of the research agent to verify it works and generates traces"""
    print("🤖 Final Research Agent Test...")
    
    try:
        from app.local_agents.research.runner import ResearchRunner
        
        test_url = "https://www.amazon.ae/Apple-MYQY3ZE-A-EarPods-USB-C/dp/B0DD413Q9J"
        print(f"📍 Testing URL: {test_url}")
        print("🔬 This should generate OpenAI traces visible in your dashboard...")
        
        runner = ResearchRunner()
        
        # Force the agent approach (this will definitely use OpenAI SDK and generate traces)
        print("\n🤖 Forcing Agent Approach (should generate OpenAI traces)...")
        result = runner._try_agent_approach(test_url, "Forced agent test")
        
        if result.get("success"):
            print("✅ Research Agent successful!")
            print(f"📄 Output preview: {result.get('final_output', 'No output')[:300]}...")
            
            # Check for key indicators of successful processing
            output = result.get('final_output', '')
            
            success_indicators = [
                'TITLE' in output,
                'IMAGES' in output,
                'Extracted' in output,
                'MVP' in output or 'mvp' in output.lower(),
                len(output) > 100  # Substantial output
            ]
            
            successful_indicators = sum(success_indicators)
            print(f"📊 Success indicators: {successful_indicators}/5")
            
            if successful_indicators >= 3:
                print("🎉 Research Agent appears to be working well!")
                print("🔍 Check your OpenAI dashboard for traces of this request.")
            else:
                print("⚠️ Output seems limited, but agent is responding.")
                
        else:
            print(f"❌ Research Agent failed: {result.get('error', 'Unknown error')}")
            
        print(f"\n📝 Full result keys: {list(result.keys())}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def verify_openai_setup():
    """Verify OpenAI setup for traces"""
    print("🔑 Verifying OpenAI Setup for Traces...")
    
    try:
        from app.core.config import settings
        print(f"✅ OpenAI API Key: {'Present' if settings.OPENAI_API_KEY else 'Missing'}")
        print(f"✅ Use AI Agents: {settings.USE_AI_AGENTS}")
        print(f"✅ OpenAI Configured: {settings.openai_configured}")
        
        if settings.openai_configured:
            print("\n🎯 Your research agent should generate traces in OpenAI dashboard!")
            print("🔗 Check: https://platform.openai.com/playground/realtime")
        else:
            print("\n❌ OpenAI not properly configured - no traces will be generated")
            
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")

if __name__ == "__main__":
    print("🚀 Final Research Agent Test\n")
    verify_openai_setup()
    print()
    test_research_agent_final()
    print("\n✨ Test completed!")
    print("\n🎯 If successful, check your OpenAI dashboard for agent traces!") 