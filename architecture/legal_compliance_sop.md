# Legal Compliance SOP

## Purpose
Ensure WhichDoctor operates within legal and ethical boundaries for medical information tools.

## Critical Rules

### 1. Never Diagnose
- ❌ **NEVER** say: "You have [condition]"
- ❌ **NEVER** say: "You are diagnosed with [condition]"
- ❌ **NEVER** say: "This is [condition]"
- ✅ **ALWAYS** say: "These symptoms may indicate...", "Consider consulting...", "Could be related to..."

### 2. Never Prescribe or Recommend Treatment
- ❌ **NEVER** recommend medications
- ❌ **NEVER** suggest dosages
- ❌ **NEVER** recommend specific treatments
- ✅ **ONLY** suggest specialist types who can help

### 3. Always Include Disclaimer
**Required Disclaimer Text** (must appear prominently):
```
⚠️ MEDICAL DISCLAIMER
This tool provides educational information only and is not a substitute for 
professional medical advice, diagnosis, or treatment. Always seek the advice 
of your physician or other qualified health provider with any questions you 
may have regarding a medical condition. Never disregard professional medical 
advice or delay in seeking it because of something you have read on this site.

If you think you may have a medical emergency, call 911 or go to the nearest 
emergency room immediately.
```

### 4. Emergency Warning Triggers
**Immediate Emergency Warning Required For**:
- Chest pain or pressure
- Severe difficulty breathing / shortness of breath
- Sudden severe headache (worst headache of life)
- Severe bleeding that won't stop
- Loss of consciousness or fainting
- Confusion or altered mental state
- Stroke symptoms (FAST):
  - **F**ace drooping
  - **A**rm weakness
  - **S**peech difficulty
  - **T**ime to call 911
- Severe allergic reaction (anaphylaxis)
- Suicidal thoughts or self-harm ideation
- Severe abdominal pain
- Coughing up blood
- Seizures
- Severe burns
- Poisoning or overdose

**Emergency Warning Display**:
```
🚨 SEEK IMMEDIATE MEDICAL ATTENTION 🚨
Call 911 or go to the nearest emergency room immediately.
These symptoms may indicate a medical emergency.
```

## Language Guidelines

### Advisory Language (✅ Use This)
- "may indicate"
- "could be related to"
- "consider consulting"
- "might suggest"
- "worth discussing with"
- "appropriate specialist for"
- "commonly associated with"
- "often seen in"

### Diagnostic Language (❌ Never Use)
- "you have"
- "diagnosed with"
- "you need"
- "you must"
- "definitely"
- "certainly"
- "this is"
- "treatment for"

### Role Definition
- ✅ **We are**: Medical navigator, advisor, educational resource
- ❌ **We are NOT**: Doctor, diagnostician, prescriber, medical authority

## Privacy Requirements

### Data Collection
- ✅ **Allowed**: Process symptoms in-memory for analysis
- ❌ **Prohibited**: Store symptoms in database
- ❌ **Prohibited**: Log symptom descriptions
- ❌ **Prohibited**: Track user medical history server-side

### Local Storage (Client-Side)
- ✅ **Allowed**: Browser localStorage for user's own history
- ✅ **Allowed**: PDF download for user
- ✅ **User control**: Clear history anytime
- ❌ **Never**: Send localStorage data to server

### Logging Restrictions
**What CAN be logged**:
- Request timestamp
- Response time
- Success/failure status
- Error types
- Symptom count (number only)

**What CANNOT be logged**:
- ❌ Symptom descriptions
- ❌ User demographics
- ❌ Medical history
- ❌ Any PII (Personally Identifiable Information)

## Terms of Service Requirements

### Disclaimer of Warranties
```
WhichDoctor is provided "as-is" without any warranties, express or implied.
We do not warrant the accuracy, completeness, or usefulness of any information.
```

### Limitation of Liability
```
WhichDoctor and its creators shall not be liable for any damages arising from
the use or inability to use this tool, including but not limited to direct,
indirect, incidental, or consequential damages.
```

### User Responsibility
```
Users assume all risk associated with using this tool. This tool is not a
substitute for professional medical judgment. Users are responsible for
seeking appropriate medical care.
```

### Age Restriction
```
This tool is intended for adults 18 years and older. If you are under 18,
please consult with a parent or guardian before using this tool.
```

## Compliance Checklist

Before ANY response is sent to user, verify:
- [ ] Disclaimer is present and prominent
- [ ] No diagnostic language used
- [ ] Only specialist types suggested (not specific doctors)
- [ ] No treatment recommendations
- [ ] No medication suggestions
- [ ] Advisory language used throughout
- [ ] Emergency warning displayed if applicable
- [ ] No PII logged

## Legal Jurisdictions

### United States
- **HIPAA**: Not applicable (we don't store PHI)
- **FDA**: Not a medical device (informational only)
- **State laws**: Varies, but advisory role is generally safe

### International
- **GDPR (Europe)**: Compliant (no data storage, user controls local data)
- **Other jurisdictions**: Consult local legal counsel if expanding

## Updates and Maintenance

### When to Update This SOP
- New emergency symptom triggers identified
- Legal requirements change
- User feedback indicates confusion about role
- Regulatory guidance updates

### Review Schedule
- **Monthly**: Review emergency triggers
- **Quarterly**: Review disclaimer language
- **Annually**: Legal compliance audit

## Escalation

### When to Consult Legal Counsel
- User threatens legal action
- Regulatory inquiry received
- Expanding to new jurisdiction
- Adding new features that may change legal status
- Media attention or public scrutiny

### Emergency Response
If a user reports harm or adverse outcome:
1. Do NOT admit fault
2. Document the incident (no PII)
3. Consult legal counsel immediately
4. Do NOT communicate with user without legal guidance
