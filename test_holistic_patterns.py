"""Test script for holistic doctor systems thinking enhancements"""
import os
import sys
import json
from dotenv import load_dotenv

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from analyze_symptoms import analyze_symptoms

load_dotenv()

# Verify API key is set
if not os.getenv('GEMINI_API_KEY'):
    print("ERROR: GEMINI_API_KEY not found in environment variables")
    sys.exit(1)

def print_divider(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def test_pattern(test_name, test_payload, expected_keywords):
    """Test a holistic symptom pattern"""
    print_divider(f"TEST: {test_name}")

    print("\nINPUT SYMPTOMS:")
    for i, symptom in enumerate(test_payload['symptoms'], 1):
        print(f"{i}. {symptom['description']}")
        if symptom.get('duration'):
            print(f"   Duration: {symptom['duration']}")
        if symptom.get('severity'):
            print(f"   Severity: {symptom['severity']}")

    print("\nCalling analyze_symptoms()...")
    try:
        result = analyze_symptoms(test_payload)

        # Check for errors
        if 'error' in result:
            print(f"\n❌ ERROR: {result['error']}")
            return False

        # Check for emergency warning
        if result.get('emergency_warning'):
            print(f"\n⚠️  EMERGENCY WARNING: {result['emergency_warning']}")

        # Display analysis
        analysis = result.get('analysis', {})

        print("\n📊 SYMPTOM CLUSTERS:")
        clusters = analysis.get('symptom_clusters', [])
        if clusters:
            for i, cluster in enumerate(clusters, 1):
                print(f"\nCluster {i}:")
                print(f"  Symptoms: {', '.join(cluster.get('symptoms', []))}")
                print(f"  Connections: {cluster.get('possible_connections', 'N/A')}")
                if 'system_involvement' in cluster:
                    print(f"  Systems Involved: {cluster['system_involvement']}")
        else:
            print("  None identified")

        print("\n🔍 POTENTIAL ROOT CAUSES:")
        root_causes = analysis.get('potential_root_causes', [])
        if root_causes:
            for i, cause in enumerate(root_causes, 1):
                print(f"\n{i}. {cause.get('category', 'Unknown')}")
                print(f"   Description: {cause.get('description', 'N/A')}")
                print(f"   Confidence: {cause.get('confidence', 'N/A')}")
                if 'systemic_explanation' in cause:
                    print(f"   Systemic Connection: {cause['systemic_explanation']}")
        else:
            print("  None identified")

        print("\n👨‍⚕️ SPECIALIST RECOMMENDATIONS:")
        specialists = result.get('specialist_recommendations', [])
        if specialists:
            for i, spec in enumerate(specialists, 1):
                print(f"\n{i}. {spec.get('specialist_type', 'Unknown')} ({spec.get('priority', 'N/A')})")
                print(f"   Reason: {spec.get('reason', 'N/A')}")
                print(f"   Treats: {spec.get('what_they_treat', 'N/A')}")
        else:
            print("  None provided")

        # Validation checks
        print("\n✅ VALIDATION CHECKS:")
        checks_passed = []
        checks_failed = []

        # Check 1: No "Primary Care Physician" recommendations
        pcp_found = any('primary care' in spec.get('specialist_type', '').lower()
                       for spec in specialists)
        if not pcp_found:
            checks_passed.append("✓ No 'Primary Care Physician' recommendations")
        else:
            checks_failed.append("✗ Found 'Primary Care Physician' recommendation")

        # Check 2: Systemic connections explained
        has_connections = any(cluster.get('possible_connections')
                            for cluster in clusters)
        if has_connections:
            checks_passed.append("✓ Symptom connections explained")
        else:
            checks_failed.append("✗ No symptom connections explained")

        # Check 3: Specific specialist recommended (not generic)
        has_specific = specialists and specialists[0].get('specialist_type') not in [
            'Primary Care Physician', 'General Practitioner', 'Family Doctor'
        ]
        if has_specific:
            checks_passed.append(f"✓ Specific specialist recommended: {specialists[0].get('specialist_type')}")
        else:
            checks_failed.append("✗ No specific specialist recommended")

        # Check 4: Expected keywords present in analysis
        full_response = json.dumps(result).lower()
        keywords_found = [kw for kw in expected_keywords if kw.lower() in full_response]
        if keywords_found:
            checks_passed.append(f"✓ Expected keywords found: {', '.join(keywords_found)}")

        # Print checks
        for check in checks_passed:
            print(f"  {check}")
        for check in checks_failed:
            print(f"  {check}")

        # Follow-up questions
        followup = result.get('followup_questions', [])
        if followup:
            print(f"\n❓ FOLLOW-UP QUESTIONS: {len(followup)} questions generated")
            for i, q in enumerate(followup[:2], 1):  # Show first 2
                print(f"  {i}. {q.get('question', 'N/A')}")

        return len(checks_failed) == 0

    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# TEST CASES
# =============================================================================

def run_all_tests():
    """Run all holistic pattern tests"""

    results = {}

    # TEST 1: Thyroid/Hormonal Pattern
    results['thyroid'] = test_pattern(
        "Thyroid/Hormonal Pattern",
        {
            'symptoms': [
                {
                    'description': 'Persistent fatigue and low energy levels',
                    'duration': '3 months',
                    'severity': 'moderate to severe',
                    'frequency': 'daily'
                },
                {
                    'description': 'Unexplained weight gain despite no diet changes',
                    'duration': '3 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Always feeling cold, especially hands and feet',
                    'duration': '2 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Constipation and sluggish digestion',
                    'duration': '2 months',
                    'severity': 'mild to moderate'
                },
                {
                    'description': 'Dry skin and brittle hair',
                    'duration': '1 month',
                    'severity': 'mild'
                }
            ],
            'age_range': '30-40',
            'existing_conditions': [],
            'medications': [],
            'additional_context': 'Symptoms seem to be getting progressively worse, especially in the mornings'
        },
        ['endocrin', 'thyroid', 'metabolic', 'hormonal', 'system']
    )

    # TEST 2: Autoimmune Pattern
    results['autoimmune'] = test_pattern(
        "Autoimmune/Inflammatory Pattern",
        {
            'symptoms': [
                {
                    'description': 'Joint pain and stiffness in multiple joints',
                    'duration': '4 months',
                    'severity': 'moderate',
                    'frequency': 'daily, worse in mornings'
                },
                {
                    'description': 'Persistent fatigue that doesn\'t improve with rest',
                    'duration': '4 months',
                    'severity': 'severe'
                },
                {
                    'description': 'Brain fog and difficulty concentrating',
                    'duration': '3 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Digestive issues including bloating and irregular bowel movements',
                    'duration': '3 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Skin rash that comes and goes',
                    'duration': '2 months',
                    'severity': 'mild'
                }
            ],
            'age_range': '25-35',
            'existing_conditions': [],
            'medications': [],
            'additional_context': 'Symptoms affect multiple parts of my body and seem connected'
        },
        ['autoimmune', 'inflammation', 'rheumat', 'systemic', 'immune']
    )

    # TEST 3: Nutritional Deficiency Pattern
    results['nutritional'] = test_pattern(
        "Nutritional Deficiency Pattern (B12)",
        {
            'symptoms': [
                {
                    'description': 'Extreme fatigue and weakness',
                    'duration': '5 months',
                    'severity': 'severe',
                    'frequency': 'constant'
                },
                {
                    'description': 'Tingling and numbness in hands and feet',
                    'duration': '3 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Mood changes including depression and irritability',
                    'duration': '4 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Pale skin and looking washed out',
                    'duration': '2 months',
                    'severity': 'mild'
                },
                {
                    'description': 'Memory problems and confusion',
                    'duration': '2 months',
                    'severity': 'mild to moderate'
                }
            ],
            'age_range': '40-50',
            'existing_conditions': [],
            'medications': [],
            'additional_context': 'Following a vegetarian diet for the past year'
        },
        ['nutritional', 'b12', 'deficiency', 'vitamin', 'hematol', 'neurolog']
    )

    # TEST 4: Gut-Brain Axis Pattern
    results['gut_brain'] = test_pattern(
        "Gut-Brain Axis Pattern",
        {
            'symptoms': [
                {
                    'description': 'Chronic digestive issues with bloating and abdominal discomfort',
                    'duration': '6 months',
                    'severity': 'moderate',
                    'frequency': 'daily, especially after meals'
                },
                {
                    'description': 'Anxiety and nervousness',
                    'duration': '5 months',
                    'severity': 'moderate to severe'
                },
                {
                    'description': 'Frequent headaches',
                    'duration': '4 months',
                    'severity': 'moderate'
                },
                {
                    'description': 'Fatigue and low energy',
                    'duration': '4 months',
                    'severity': 'moderate'
                }
            ],
            'age_range': '25-35',
            'existing_conditions': [],
            'medications': [],
            'additional_context': 'Symptoms seem worse when stressed'
        },
        ['gut', 'brain', 'gastro', 'digestive', 'axis', 'microbiome']
    )

    # Print summary
    print_divider("TEST SUMMARY")
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    print("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print("\n" + "=" * 80)

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Holistic thinking enhancements are working correctly.")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed. Review the output above.")

    return passed_tests == total_tests

if __name__ == "__main__":
    print("=" * 80)
    print(" HOLISTIC DOCTOR SYSTEMS THINKING TEST SUITE")
    print(" Testing enhanced AI prompts for interconnected symptom analysis")
    print("=" * 80)

    success = run_all_tests()
    sys.exit(0 if success else 1)
