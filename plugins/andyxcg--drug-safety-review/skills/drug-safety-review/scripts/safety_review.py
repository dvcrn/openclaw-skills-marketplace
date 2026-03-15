#!/usr/bin/env python3
"""
Drug Safety Review System with Free Trial
Comprehensive medication safety analysis with interaction detection,
contraindication screening, allergy checks, and dosing optimization.
"""

import json
import sys
import argparse
import os
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


class DrugSafetyReviewer:
    """Core drug safety review engine."""
    
    # Major drug interactions (simplified database)
    DRUG_INTERACTIONS = {
        ('warfarin', 'amoxicillin'): {
            'severity': 'major',
            'mechanism': 'Amoxicillin may enhance anticoagulant effect by reducing vitamin K producing gut bacteria',
            'recommendation': 'Monitor INR closely. Consider alternative antibiotic like doxycycline.',
            'monitoring': ['INR', 'signs of bleeding']
        },
        ('warfarin', 'aspirin'): {
            'severity': 'major',
            'mechanism': 'Additive antiplatelet effect increases bleeding risk',
            'recommendation': 'Avoid combination if possible. If necessary, use lowest effective aspirin dose.',
            'monitoring': ['INR', 'bleeding signs', 'GI symptoms']
        },
        ('metformin', 'contrast'): {
            'severity': 'major',
            'mechanism': 'Increased risk of lactic acidosis with iodinated contrast',
            'recommendation': 'Hold metformin 48 hours before and after contrast administration.',
            'monitoring': ['renal function', 'lactate levels']
        },
        ('lisinopril', 'spironolactone'): {
            'severity': 'major',
            'mechanism': 'Increased risk of hyperkalemia',
            'recommendation': 'Monitor potassium closely. Consider alternative antihypertensive.',
            'monitoring': ['serum potassium', 'renal function']
        },
        ('simvastatin', 'clarithromycin'): {
            'severity': 'major',
            'mechanism': 'CYP3A4 inhibition increases statin levels, risk of rhabdomyolysis',
            'recommendation': 'Avoid combination. Use pravastatin or rosuvastatin instead.',
            'monitoring': ['CK levels', 'muscle symptoms']
        },
        ('fluoxetine', 'tramadol'): {
            'severity': 'major',
            'mechanism': 'Increased risk of serotonin syndrome',
            'recommendation': 'Avoid combination. Consider alternative pain management.',
            'monitoring': ['mental status', 'autonomic symptoms']
        },
    }
    
    # Drug contraindications
    CONTRAINDICATIONS = {
        'metformin': {
            'conditions': ['severe_renal_impairment', 'acidosis', 'severe_infection'],
            'reason': 'Risk of lactic acidosis'
        },
        'warfarin': {
            'conditions': ['active_bleeding', 'pregnancy', 'hemorrhagic_stroke'],
            'reason': 'High bleeding risk'
        },
        'ace_inhibitors': {
            'conditions': ['bilateral_renal_artery_stenosis', 'angioedema_history'],
            'reason': 'Risk of acute renal failure or angioedema'
        },
        'beta_blockers': {
            'conditions': ['severe_asthma', 'heart_block', 'cardiogenic_shock'],
            'reason': 'Risk of bronchospasm or hemodynamic compromise'
        },
        'nsaids': {
            'conditions': ['active_peptic_ulcer', 'severe_heart_failure', 'third_trimester_pregnancy'],
            'reason': 'Risk of bleeding, fluid retention, or fetal harm'
        },
    }
    
    # Drug allergies and cross-reactivity
    ALLERGY_CROSS_REACTIVITY = {
        'penicillin': ['amoxicillin', 'ampicillin', 'piperacillin', 'cephalosporins'],
        'sulfa': ['sulfamethoxazole', 'furosemide', 'hydrochlorothiazide'],
        'cephalosporin': ['penicillin'],  # Partial cross-reactivity
    }
    
    # Renal dosing adjustments
    RENAL_DOSING = {
        'metformin': {'egfr_cutoff': 30, 'action': 'contraindicated'},
        'gabapentin': {'egfr_cutoff': 30, 'action': 'reduce_dose'},
        'levofloxacin': {'egfr_cutoff': 50, 'action': 'reduce_dose'},
        'enoxaparin': {'egfr_cutoff': 30, 'action': 'reduce_dose'},
    }
    
    def __init__(self):
        self.billing = SkillPayBilling()
        self.trial = TrialManager("drug-safety-review")
    
    def check_drug_interactions(self, medications: List[Dict]) -> List[Dict]:
        """Check for drug-drug interactions."""
        alerts = []
        drug_names = [m['drug'].lower() for m in medications]
        
        for i, drug1 in enumerate(drug_names):
            for drug2 in drug_names[i+1:]:
                # Check both directions
                interaction = self.DRUG_INTERACTIONS.get((drug1, drug2)) or \
                             self.DRUG_INTERACTIONS.get((drug2, drug1))
                
                if interaction:
                    alerts.append({
                        'alert_id': f'DDI-{drug1[:3].upper()}-{drug2[:3].upper()}',
                        'severity': interaction['severity'],
                        'category': 'drug_drug_interaction',
                        'title': f'{drug1.title()} - {drug2.title()} Interaction',
                        'description': interaction['mechanism'],
                        'recommendation': interaction['recommendation'],
                        'monitoring': interaction['monitoring']
                    })
        
        return alerts
    
    def check_contraindications(self, medications: List[Dict], 
                                patient_conditions: List[str] = None) -> List[Dict]:
        """Check for drug contraindications."""
        alerts = []
        patient_conditions = patient_conditions or []
        
        for med in medications:
            drug = med['drug'].lower()
            
            # Check specific drug contraindications
            if drug in self.CONTRAINDICATIONS:
                contraindication = self.CONTRAINDICATIONS[drug]
                for condition in contraindication['conditions']:
                    if condition in patient_conditions:
                        alerts.append({
                            'alert_id': f'CONTRA-{drug[:3].upper()}',
                            'severity': 'critical',
                            'category': 'contraindication',
                            'title': f'{drug.title()} Contraindicated',
                            'description': f'{drug.title()} is contraindicated in patients with {condition}',
                            'recommendation': f'Reason: {contraindication["reason"]}. Consider alternative therapy.',
                            'monitoring': []
                        })
        
        return alerts
    
    def check_allergies(self, medications: List[Dict], 
                       allergies: List[Dict]) -> List[Dict]:
        """Check for drug allergies and cross-reactivity."""
        alerts = []
        
        for med in medications:
            drug = med['drug'].lower()
            
            for allergy in allergies:
                allergen = allergy.get('allergen', '').lower()
                reaction = allergy.get('reaction', 'unknown reaction')
                
                # Direct allergy match
                if allergen in drug or drug in allergen:
                    severity = 'critical' if 'anaphylaxis' in reaction.lower() else 'major'
                    alerts.append({
                        'alert_id': f'ALLERGY-{drug[:3].upper()}',
                        'severity': severity,
                        'category': 'allergy',
                        'title': f'{drug.title()} - Known Allergy',
                        'description': f'Patient has documented {allergen} allergy with {reaction}',
                        'recommendation': f'Avoid {drug.title()}. Use alternative medication.',
                        'monitoring': ['for allergic reaction signs']
                    })
                
                # Cross-reactivity check
                elif allergen in self.ALLERGY_CROSS_REACTIVITY:
                    cross_drugs = self.ALLERGY_CROSS_REACTIVITY[allergen]
                    if drug in cross_drugs or any(d in drug for d in cross_drugs):
                        alerts.append({
                            'alert_id': f'CROSS-{drug[:3].upper()}',
                            'severity': 'major',
                            'category': 'cross_reactivity',
                            'title': f'Possible Cross-Reactivity: {drug.title()}',
                            'description': f'Patient allergic to {allergen}. Potential cross-reactivity with {drug}.',
                            'recommendation': f'Consider allergy testing or use alternative. Monitor closely if used.',
                            'monitoring': ['for allergic reaction signs']
                        })
        
        return alerts
    
    def check_renal_dosing(self, medications: List[Dict], 
                          renal_function: Dict) -> List[Dict]:
        """Check for renal dosing adjustments."""
        alerts = []
        egfr = renal_function.get('egfr', 90)
        
        for med in medications:
            drug = med['drug'].lower()
            
            if drug in self.RENAL_DOSING:
                dosing_info = self.RENAL_DOSING[drug]
                if egfr < dosing_info['egfr_cutoff']:
                    if dosing_info['action'] == 'contraindicated':
                        alerts.append({
                            'alert_id': f'RENAL-{drug[:3].upper()}',
                            'severity': 'critical',
                            'category': 'renal_dosing',
                            'title': f'{drug.title()} Contraindicated (Renal)',
                            'description': f'eGFR {egfr} below threshold ({dosing_info["egfr_cutoff"]}). Drug contraindicated.',
                            'recommendation': 'Use alternative medication not requiring renal clearance.',
                            'monitoring': ['renal function']
                        })
                    else:
                        alerts.append({
                            'alert_id': f'RENAL-{drug[:3].upper()}',
                            'severity': 'moderate',
                            'category': 'renal_dosing',
                            'title': f'{drug.title()} Dose Adjustment Required',
                            'description': f'eGFR {egfr} below threshold ({dosing_info["egfr_cutoff"]}). Dose adjustment needed.',
                            'recommendation': 'Reduce dose based on renal function. Consult dosing guidelines.',
                            'monitoring': ['renal function', 'drug levels if available']
                        })
        
        return alerts
    
    def suggest_alternatives(self, problematic_drug: str, 
                            patient_conditions: List[str] = None) -> List[Dict]:
        """Suggest alternative medications."""
        alternatives = []
        
        # Simplified alternative suggestions
        alternative_map = {
            'amoxicillin': [
                {'drug': 'doxycycline', 'reasoning': 'No significant warfarin interaction', 'formulary_status': 'available'},
                {'drug': 'azithromycin', 'reasoning': 'Minimal interaction with warfarin', 'formulary_status': 'available'}
            ],
            'simvastatin': [
                {'drug': 'pravastatin', 'reasoning': 'Not metabolized by CYP3A4', 'formulary_status': 'available'},
                {'drug': 'rosuvastatin', 'reasoning': 'Minimal CYP3A4 metabolism', 'formulary_status': 'available'}
            ],
            'tramadol': [
                {'drug': 'acetaminophen', 'reasoning': 'No serotonergic effect', 'formulary_status': 'available'},
                {'drug': 'ibuprofen', 'reasoning': 'No serotonergic effect (if no contraindications)', 'formulary_status': 'available'}
            ],
        }
        
        return alternative_map.get(problematic_drug.lower(), [])
    
    def calculate_risk_score(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Calculate overall medication regimen risk score."""
        severity_weights = {
            'critical': 10,
            'major': 5,
            'moderate': 2,
            'minor': 1
        }
        
        total_score = sum(severity_weights.get(a['severity'], 0) for a in alerts)
        
        if total_score >= 20:
            risk_level = 'very_high'
            safety_status = 'requires_immediate_intervention'
        elif total_score >= 10:
            risk_level = 'high'
            safety_status = 'requires_intervention'
        elif total_score >= 5:
            risk_level = 'moderate'
            safety_status = 'caution_advised'
        elif total_score > 0:
            risk_level = 'low'
            safety_status = 'monitoring_recommended'
        else:
            risk_level = 'minimal'
            safety_status = 'safe'
        
        return {
            'score': total_score,
            'level': risk_level,
            'safety_status': safety_status
        }
    
    def review(self, medications: List[Dict], allergies: List[Dict] = None,
               patient_data: Dict = None) -> Dict[str, Any]:
        """Main safety review method."""
        allergies = allergies or []
        patient_data = patient_data or {}
        
        all_alerts = []
        
        # Check drug-drug interactions
        all_alerts.extend(self.check_drug_interactions(medications))
        
        # Check contraindications
        patient_conditions = patient_data.get('conditions', [])
        all_alerts.extend(self.check_contraindications(medications, patient_conditions))
        
        # Check allergies
        all_alerts.extend(self.check_allergies(medications, allergies))
        
        # Check renal dosing
        renal_function = patient_data.get('renal_function', {})
        if renal_function:
            all_alerts.extend(self.check_renal_dosing(medications, renal_function))
        
        # Sort alerts by severity
        severity_order = {'critical': 0, 'major': 1, 'moderate': 2, 'minor': 3}
        all_alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        # Calculate risk score
        risk_assessment = self.calculate_risk_score(all_alerts)
        
        # Generate recommendations
        recommendations = []
        for alert in all_alerts:
            if alert['severity'] in ['critical', 'major']:
                alternatives = self.suggest_alternatives(
                    alert['title'].split()[0], 
                    patient_conditions
                )
                if alternatives:
                    recommendations.append({
                        'type': 'alternative_therapy',
                        'for_alert': alert['alert_id'],
                        'alternatives': alternatives
                    })
        
        return {
            'review_id': f'SAFETY_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'safety_status': risk_assessment['safety_status'],
            'risk_score': risk_assessment,
            'medication_count': len(medications),
            'alert_count': len(all_alerts),
            'alerts': all_alerts,
            'recommendations': recommendations,
            'disclaimer': 'This is clinical decision support. Verify with qualified healthcare providers.'
        }
    
    def process(self, medications: List[Dict], allergies: List[Dict] = None,
                patient_data: Dict = None, user_id: str = "") -> Dict[str, Any]:
        """Full processing pipeline with billing and free trial support."""
        if not user_id:
            return {'success': False, 'error': 'User ID is required'}
        
        # Check free trial status
        trial_remaining = self.trial.get_trial_remaining(user_id)
        
        if trial_remaining > 0:
            # Free trial mode - no billing
            self.trial.use_trial(user_id)
            review_result = self.review(medications, allergies, patient_data)
            
            return {
                'success': True,
                'trial_mode': True,
                'trial_remaining': trial_remaining - 1,
                'balance': None,
                'review': review_result
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
        
        # Perform safety review
        review_result = self.review(medications, allergies, patient_data)
        
        return {
            'success': True,
            'trial_mode': False,
            'trial_remaining': 0,
            'balance': charge_result.get('balance'),
            'review': review_result
        }


def review_medications(medications: List[Dict], allergies: List[Dict] = None,
                      patient_data: Dict = None, user_id: str = "",
                      api_key: str = API_KEY, skill_id: str = SKILL_ID) -> Dict[str, Any]:
    """Convenience function for medication safety review."""
    reviewer = DrugSafetyReviewer()
    reviewer.billing = SkillPayBilling(api_key, skill_id)
    reviewer.trial = TrialManager("drug-safety-review")
    return reviewer.process(medications, allergies, patient_data, user_id)


def main():
    parser = argparse.ArgumentParser(description='Drug Safety Review')
    parser.add_argument('--medications', '-m', required=True, 
                       help='JSON array of medications [{"drug":"name","dose":"5mg"}]')
    parser.add_argument('--allergies', '-a', default='[]',
                       help='JSON array of allergies [{"allergen":"penicillin"}]')
    parser.add_argument('--patient', '-p', default='{}',
                       help='JSON object with patient data {"age":65,"weight":75}')
    parser.add_argument('--user-id', '-u', required=True, help='User ID for billing')
    parser.add_argument('--api-key', '-k', default=API_KEY, help='SkillPay API key')
    parser.add_argument('--skill-id', default=SKILL_ID, help='Skill ID')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    # Parse JSON inputs
    try:
        medications = json.loads(args.medications)
        allergies = json.loads(args.allergies)
        patient_data = json.loads(args.patient)
    except json.JSONDecodeError as e:
        print(json.dumps({'success': False, 'error': f'Invalid JSON: {str(e)}'}, 
                        ensure_ascii=False))
        return 1
    
    # Use environment variables if not provided
    api_key = args.api_key or os.environ.get('SKILL_BILLING_API_KEY', '')
    skill_id = args.skill_id or os.environ.get('SKILL_ID', '')
    
    if not api_key or not skill_id:
        print(json.dumps({
            'success': False,
            'error': 'API key and Skill ID required. Set SKILL_BILLING_API_KEY and SKILL_ID environment variables.'
        }, ensure_ascii=False))
        return 1
    
    # Process review
    result = review_medications(medications, allergies, patient_data, 
                               args.user_id, api_key, skill_id)
    
    # Output result
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
