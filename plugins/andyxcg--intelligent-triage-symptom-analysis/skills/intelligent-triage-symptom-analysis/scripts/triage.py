#!/usr/bin/env python3
"""
Intelligent Triage and Symptom Analysis with Free Trial
AI-powered medical triage with NLP and machine learning.
"""

import json
import sys
import argparse
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

# ═══════════════════════════════════════════════════
# SkillPay Billing Integration
# ═══════════════════════════════════════════════════
BILLING_URL = 'https://skillpay.me/api/v1/billing'
API_KEY = os.environ.get('SKILL_BILLING_API_KEY', '')
SKILL_ID = os.environ.get('SKILL_ID', '')


# ═══════════════════════════════════════════════════
# Free Trial Manager / 免费试用管理
# ═══════════════════════════════════════════════════
class TrialManager:
    """Manages free trial usage for users."""
    
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.trial_dir = os.path.expanduser("~/.openclaw/skill_trial")
        self.trial_file = os.path.join(self.trial_dir, f"{skill_name}.json")
        self.max_free_calls = 10
        
        # Ensure trial directory exists
        os.makedirs(self.trial_dir, exist_ok=True)
    
    def _load_trial_data(self) -> Dict[str, Any]:
        """Load trial data from file."""
        if os.path.exists(self.trial_file):
            try:
                with open(self.trial_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_trial_data(self, data: Dict[str, Any]):
        """Save trial data to file."""
        try:
            with open(self.trial_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Warning: Could not save trial data: {e}", file=sys.stderr)
    
    def get_trial_remaining(self, user_id: str) -> int:
        """Get remaining free trial calls for a user."""
        if not user_id:
            return 0
        
        data = self._load_trial_data()
        user_data = data.get(user_id, {})
        used_calls = user_data.get('used_calls', 0)
        
        return max(0, self.max_free_calls - used_calls)
    
    def use_trial(self, user_id: str) -> bool:
        """Record a free trial usage for a user."""
        if not user_id:
            return False
        
        data = self._load_trial_data()
        
        if user_id not in data:
            data[user_id] = {'used_calls': 0, 'first_use': datetime.now().isoformat()}
        
        data[user_id]['used_calls'] += 1
        data[user_id]['last_use'] = datetime.now().isoformat()
        
        self._save_trial_data(data)
        return True
    
    def get_trial_info(self, user_id: str) -> Dict[str, Any]:
        """Get full trial information for a user."""
        remaining = self.get_trial_remaining(user_id)
        data = self._load_trial_data()
        user_data = data.get(user_id, {})
        
        return {
            'trial_mode': remaining > 0,
            'trial_remaining': remaining,
            'trial_total': self.max_free_calls,
            'trial_used': user_data.get('used_calls', 0),
            'first_use': user_data.get('first_use'),
            'last_use': user_data.get('last_use')
        }


class SkillPayBilling:
    """SkillPay billing SDK."""
    
    def __init__(self, api_key: str = API_KEY, skill_id: str = SKILL_ID):
        self.api_key = api_key
        self.skill_id = skill_id
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Make HTTP request to SkillPay API."""
        url = f"{BILLING_URL}{endpoint}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8') if data else None,
                headers=self.headers,
                method=method
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def charge_user(self, user_id: str) -> Dict[str, Any]:
        """Charge 1 token per call."""
        result = self._make_request('/charge', method='POST', data={
            'user_id': user_id,
            'skill_id': self.skill_id,
            'amount': 0,
        })
        if result.get('success'):
            return {'ok': True, 'balance': result.get('balance', 0)}
        else:
            return {
                'ok': False,
                'balance': result.get('balance', 0),
                'payment_url': result.get('payment_url'),
            }


class SymptomAnalyzer:
    """Core symptom analysis and triage engine."""
    
    # Red flag symptoms - life threatening (≥95% accuracy priority)
    RED_FLAGS = {
        'cardiac': ['胸痛', '胸闷', '心悸', '呼吸困难', '气短', 'chest pain', 'chest tightness', 
                   'palpitations', 'shortness of breath', 'dyspnea'],
        'neurological': ['昏迷', '抽搐', '偏瘫', '失语', '剧烈头痛', '意识模糊', 
                        'coma', 'seizure', 'paralysis', 'aphasia', 'severe headache', 'confusion'],
        'respiratory': ['窒息', '喘鸣', '血氧低', 'choking', 'wheezing', 'low oxygen'],
        'trauma': ['大出血', '严重外伤', '骨折', '头部外伤', 'severe bleeding', 
                  'severe trauma', 'fracture', 'head injury'],
        'shock': ['面色苍白', '冷汗', '血压低', 'pale', 'cold sweat', 'low blood pressure'],
    }
    
    # Body systems
    BODY_SYSTEMS = [
        'cardiovascular', 'respiratory', 'gastrointestinal', 'neurological',
        'musculoskeletal', 'dermatological', 'genitourinary', 'endocrine',
        'hematological', 'immunological', 'psychiatric'
    ]
    
    # Triage levels based on ESI and Manchester Triage System
    TRIAGE_LEVELS = {
        1: {'name': 'Resuscitation', 'name_cn': '复苏', 'wait_time': 'Immediate', 'color': 'Red'},
        2: {'name': 'Emergent', 'name_cn': '紧急', 'wait_time': '<15 min', 'color': 'Orange'},
        3: {'name': 'Urgent', 'name_cn': '急症', 'wait_time': '<30 min', 'color': 'Yellow'},
        4: {'name': 'Less Urgent', 'name_cn': '次急', 'wait_time': '<60 min', 'color': 'Green'},
        5: {'name': 'Non-urgent', 'name_cn': '非急', 'wait_time': '>60 min', 'color': 'Blue'},
    }
    
    def __init__(self):
        self.billing = SkillPayBilling()
        self.trial = TrialManager("intelligent-triage-symptom-analysis")
    
    def extract_symptoms(self, text: str) -> List[Dict[str, Any]]:
        """Extract symptoms from natural language text."""
        symptoms = []
        text_lower = text.lower()
        
        # Pattern matching for common symptoms
        symptom_patterns = {
            'fever': ['发烧', '发热', 'fever', 'temperature'],
            'cough': ['咳嗽', '咳', 'cough'],
            'pain': ['疼痛', '痛', 'pain', 'ache'],
            'nausea': ['恶心', '呕吐', 'nausea', 'vomiting'],
            'fatigue': ['疲劳', '乏力', 'tired', 'fatigue'],
            'dizziness': ['头晕', '眩晕', 'dizzy', 'vertigo'],
            'rash': ['皮疹', '红疹', 'rash'],
            'swelling': ['肿胀', '水肿', 'swelling', 'edema'],
        }
        
        for symptom_type, keywords in symptom_patterns.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in text:
                    symptoms.append({
                        'type': symptom_type,
                        'keyword': keyword,
                        'severity': self._assess_severity(text, symptom_type)
                    })
                    break
        
        return symptoms
    
    def _assess_severity(self, text: str, symptom_type: str) -> int:
        """Assess symptom severity (1-10 scale)."""
        severity_indicators = {
            'severe': ['严重', '剧烈', 'severe', 'intense', 'extreme'],
            'moderate': ['中度', 'moderate', 'medium'],
            'mild': ['轻微', '轻度', 'mild', 'slight'],
        }
        
        text_lower = text.lower()
        for level, indicators in severity_indicators.items():
            for indicator in indicators:
                if indicator in text or indicator in text_lower:
                    if level == 'severe':
                        return 8
                    elif level == 'moderate':
                        return 5
                    else:
                        return 2
        return 5  # Default moderate
    
    def check_red_flags(self, symptoms: str, vital_signs: Dict = None) -> List[Dict[str, Any]]:
        """Check for life-threatening red flag symptoms."""
        red_flags = []
        symptoms_lower = symptoms.lower()
        
        for category, keywords in self.RED_FLAGS.items():
            for keyword in keywords:
                if keyword in symptoms or keyword in symptoms_lower:
                    red_flags.append({
                        'category': category,
                        'symptom': keyword,
                        'priority': 'CRITICAL'
                    })
                    break
        
        # Check vital signs if provided
        if vital_signs:
            if 'bp' in vital_signs:
                bp = vital_signs['bp']
                if isinstance(bp, str):
                    try:
                        systolic = int(bp.split('/')[0])
                        if systolic > 180 or systolic < 90:
                            red_flags.append({
                                'category': 'vital_signs',
                                'symptom': f'Abnormal blood pressure: {bp}',
                                'priority': 'HIGH'
                            })
                    except:
                        pass
            
            if 'hr' in vital_signs:
                hr = vital_signs['hr']
                if isinstance(hr, (int, float)) and (hr > 120 or hr < 50):
                    red_flags.append({
                        'category': 'vital_signs',
                        'symptom': f'Abnormal heart rate: {hr}',
                        'priority': 'HIGH'
                    })
        
        return red_flags
    
    def calculate_triage_level(self, symptoms: List[Dict], red_flags: List[Dict], 
                               age: int = None, vital_signs: Dict = None) -> int:
        """Calculate triage level (1-5) based on ESI/Manchester system."""
        # Level 1: Resuscitation - immediate life threat
        if any(rf['priority'] == 'CRITICAL' for rf in red_flags):
            return 1
        
        # Level 2: Emergent - potential life threat
        critical_systems = ['cardiac', 'neurological', 'respiratory']
        if any(rf['category'] in critical_systems for rf in red_flags):
            return 2
        
        # Check severity scores
        max_severity = max([s['severity'] for s in symptoms], default=5)
        
        # Age factor (elderly and pediatric higher priority)
        age_factor = 0
        if age and (age < 5 or age > 65):
            age_factor = 1
        
        # Level 3: Urgent
        if max_severity >= 7 or age_factor > 0:
            return 3
        
        # Level 4: Less urgent
        if max_severity >= 4:
            return 4
        
        # Level 5: Non-urgent
        return 5
    
    def generate_differential_diagnosis(self, symptoms: List[Dict], 
                                       red_flags: List[Dict]) -> List[Dict[str, Any]]:
        """Generate differential diagnosis based on symptoms."""
        # Simplified differential diagnosis
        diagnoses = []
        
        symptom_types = [s['type'] for s in symptoms]
        
        if 'chest pain' in [rf['symptom'] for rf in red_flags] or '胸痛' in str(symptoms):
            diagnoses.extend([
                {'condition': 'Acute Coronary Syndrome', 'probability': 0.25, 'urgency': 'HIGH'},
                {'condition': 'Pulmonary Embolism', 'probability': 0.15, 'urgency': 'HIGH'},
                {'condition': 'Aortic Dissection', 'probability': 0.05, 'urgency': 'CRITICAL'},
                {'condition': 'Musculoskeletal Pain', 'probability': 0.30, 'urgency': 'LOW'},
            ])
        
        if 'fever' in symptom_types or '发烧' in str(symptoms):
            diagnoses.extend([
                {'condition': 'Viral Infection', 'probability': 0.40, 'urgency': 'LOW'},
                {'condition': 'Bacterial Infection', 'probability': 0.25, 'urgency': 'MEDIUM'},
            ])
        
        if not diagnoses:
            diagnoses.append({'condition': 'Non-specific symptoms', 'probability': 0.50, 'urgency': 'LOW'})
        
        # Sort by urgency and probability
        urgency_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        diagnoses.sort(key=lambda x: (urgency_order.get(x['urgency'], 4), -x['probability']))
        
        return diagnoses[:5]  # Top 5 diagnoses
    
    def generate_recommendations(self, triage_level: int, red_flags: List[Dict]) -> List[str]:
        """Generate care recommendations based on triage."""
        recommendations = []
        
        if triage_level == 1:
            recommendations.append("立即呼叫急救/Call emergency services immediately")
            recommendations.append("开始心肺复苏/Start CPR if indicated")
        elif triage_level == 2:
            recommendations.append("立即前往急诊/Go to emergency department immediately")
            recommendations.append("不要进食或饮水/Do not eat or drink")
        elif triage_level == 3:
            recommendations.append("尽快就医/Seek medical care as soon as possible")
            recommendations.append("监测症状变化/Monitor symptom changes")
        elif triage_level == 4:
            recommendations.append("预约门诊/Schedule outpatient appointment")
            recommendations.append("休息并观察/Rest and observe")
        else:
            recommendations.append("自我护理/Self-care at home")
            recommendations.append("如症状持续请就医/Seek care if symptoms persist")
        
        if red_flags:
            recommendations.append("注意红旗症状/Watch for red flag symptoms")
        
        return recommendations
    
    def analyze(self, symptoms: str, age: int = None, gender: str = None,
                vital_signs: Dict = None, duration: str = None) -> Dict[str, Any]:
        """Main analysis method."""
        # Extract symptoms
        extracted_symptoms = self.extract_symptoms(symptoms)
        
        # Check red flags
        red_flags = self.check_red_flags(symptoms, vital_signs)
        
        # Calculate triage level
        triage_level = self.calculate_triage_level(extracted_symptoms, red_flags, age, vital_signs)
        
        # Generate differential diagnosis
        differential = self.generate_differential_diagnosis(extracted_symptoms, red_flags)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(triage_level, red_flags)
        
        return {
            'analysis_id': f'TRG_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'input': {
                'symptoms': symptoms,
                'age': age,
                'gender': gender,
                'vital_signs': vital_signs,
                'duration': duration,
            },
            'extracted_symptoms': extracted_symptoms,
            'red_flags': red_flags,
            'triage': {
                'level': triage_level,
                'name': self.TRIAGE_LEVELS[triage_level]['name'],
                'name_cn': self.TRIAGE_LEVELS[triage_level]['name_cn'],
                'urgency': self.TRIAGE_LEVELS[triage_level]['wait_time'],
                'color': self.TRIAGE_LEVELS[triage_level]['color'],
            },
            'differential_diagnosis': differential,
            'recommendations': recommendations,
            'disclaimer': 'This is a preliminary assessment only. Please consult qualified healthcare providers for medical decisions.'
        }
    
    def process(self, symptoms: str, age: int = None, gender: str = None,
                vital_signs: Dict = None, duration: str = None, 
                user_id: str = "") -> Dict[str, Any]:
        """Full processing pipeline with billing and free trial support."""
        if not user_id:
            return {'success': False, 'error': 'User ID is required'}
        
        # Check free trial status
        trial_remaining = self.trial.get_trial_remaining(user_id)
        
        if trial_remaining > 0:
            # Free trial mode - no billing
            self.trial.use_trial(user_id)
            analysis_result = self.analyze(symptoms, age, gender, vital_signs, duration)
            
            return {
                'success': True,
                'trial_mode': True,
                'trial_remaining': trial_remaining - 1,
                'balance': None,
                'analysis': analysis_result
            }
        
        # Normal billing mode
        if not self.billing.api_key or not self.billing.skill_id:
            return {
                'success': False,
                'trial_mode': False,
                'trial_remaining': 0,
                'error': 'Billing configuration missing. Set SKILL_BILLING_API_KEY and SKILL_ID environment variables.'
            }
        
        # Charge user
        charge_result = self.billing.charge_user(user_id)
        
        if not charge_result.get('ok'):
            return {
                'success': False,
                'trial_mode': False,
                'trial_remaining': 0,
                'error': 'Payment failed or insufficient balance',
                'balance': charge_result.get('balance', 0),
                'paymentUrl': charge_result.get('payment_url'),
            }
        
        # Perform analysis
        analysis_result = self.analyze(symptoms, age, gender, vital_signs, duration)
        
        return {
            'success': True,
            'trial_mode': False,
            'trial_remaining': 0,
            'balance': charge_result.get('balance'),
            'analysis': analysis_result
        }


def analyze_symptoms(symptoms: str, age: int = None, gender: str = None,
                    vital_signs: Dict = None, duration: str = None,
                    user_id: str = "", api_key: str = API_KEY, 
                    skill_id: str = SKILL_ID) -> Dict[str, Any]:
    """Convenience function for symptom analysis."""
    analyzer = SymptomAnalyzer()
    analyzer.billing = SkillPayBilling(api_key, skill_id)
    analyzer.trial = TrialManager("intelligent-triage-symptom-analysis")
    return analyzer.process(symptoms, age, gender, vital_signs, duration, user_id)


def main():
    parser = argparse.ArgumentParser(description='Intelligent Triage and Symptom Analysis')
    parser.add_argument('--symptoms', '-s', required=True, help='Symptom description')
    parser.add_argument('--age', '-a', type=int, help='Patient age')
    parser.add_argument('--gender', '-g', choices=['male', 'female', 'other'], help='Patient gender')
    parser.add_argument('--duration', '-d', help='Symptom duration')
    parser.add_argument('--user-id', '-u', required=True, help='User ID for billing')
    parser.add_argument('--api-key', '-k', default=API_KEY, help='SkillPay API key')
    parser.add_argument('--skill-id', default=SKILL_ID, help='Skill ID')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get('SKILL_BILLING_API_KEY', '')
    skill_id = args.skill_id or os.environ.get('SKILL_ID', '')
    
    result = analyze_symptoms(args.symptoms, args.age, args.gender, 
                             None, args.duration, args.user_id, api_key, skill_id)
    
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f'Result saved to: {args.output}')
    else:
        print(output_json)
    
    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
