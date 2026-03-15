#!/usr/bin/env python3
"""
Medical Record Processor with SkillPay Billing Integration and Free Trial
Processes unstructured medical notes into standardized EMR format.
"""

import json
import sys
import argparse
import re
import os
from datetime import datetime
from typing import Dict, Any, Optional
import urllib.request
import urllib.error

# ═══════════════════════════════════════════════════
# SkillPay Billing Integration / 计费接入
# ═══════════════════════════════════════════════════
BILLING_API_URL = 'https://skillpay.me'
BILLING_API_KEY = os.environ.get('SKILLPAY_API_KEY', '')
SKILL_ID = os.environ.get('SKILLPAY_SKILL_ID', '')  # Set your SkillPay Skill ID
DEFAULT_PRICE = 0.001  # USDT per call

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
    """SkillPay billing integration handler."""
    
    def __init__(self, api_key: str = BILLING_API_KEY, skill_id: str = SKILL_ID):
        self.api_key = api_key
        self.skill_id = skill_id
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Make HTTP request to SkillPay API."""
        url = f"{BILLING_API_URL}{endpoint}"
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
        }
        
        try:
            if method == 'POST' and data:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers,
                    method=method
                )
            else:
                req = urllib.request.Request(url, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_balance(self, user_id: str) -> float:
        """
        ① Check balance / 查余额 / 残高確認
        Returns USDT balance amount.
        """
        result = self._make_request(f'/api/v1/billing/balance?user_id={user_id}')
        return result.get('balance', 0.0)
    
    def charge_user(self, user_id: str, amount: float = DEFAULT_PRICE) -> Dict[str, Any]:
        """
        ② Charge per call / 每次调用扣费 / 呼び出しごとの課金
        Returns: {ok: bool, balance: float, paymentUrl?: str}
        """
        result = self._make_request('/api/v1/billing/charge', method='POST', data={
            'user_id': user_id,
            'skill_id': self.skill_id,
            'amount': amount,
        })
        
        if result.get('success'):
            return {
                'ok': True,
                'balance': result.get('balance', 0.0),
            }
        else:
            # Insufficient balance → return payment link
            return {
                'ok': False,
                'balance': result.get('balance', 0.0),
                'paymentUrl': result.get('payment_url'),
            }
    
    def get_payment_link(self, user_id: str, amount: float) -> str:
        """
        ③ Generate payment link / 生成充值链接 / 決済リンク生成
        Returns BNB Chain USDT payment link.
        """
        result = self._make_request('/api/v1/billing/payment-link', method='POST', data={
            'user_id': user_id,
            'amount': amount,
        })
        return result.get('payment_url', '')


class MedicalRecordStructurer:
    """Main class for structuring medical records."""
    
    def __init__(self, api_key: str = BILLING_API_KEY):
        self.billing = SkillPayBilling(api_key)
        self.trial = TrialManager("medical-record-structurer")
        self.fields = {
            "patient_name": None,
            "gender": None,
            "age": None,
            "chief_complaint": None,
            "history_present_illness": None,
            "past_medical_history": None,
            "physical_examination": None,
            "diagnosis": None,
            "treatment_plan": None,
            "medications": None,
            "follow_up": None,
            "doctor_name": None,
            "record_date": None
        }
    
    def extract_patient_info(self, text: str) -> Dict[str, Any]:
        """Extract patient demographics from text."""
        info = {}
        
        # Extract name (支持中文和英文)
        name_patterns = [
            r'患者[：:]?\s*([\u4e00-\u9fa5]{2,4})',
            r'姓名[：:]?\s*([\u4e00-\u9fa5]{2,4})',
            r'([\u4e00-\u9fa5]{2,4})[，,]\s*(?:男|女)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                info['patient_name'] = match.group(1)
                break
        
        # Extract gender
        if '男' in text:
            info['gender'] = '男'
        elif '女' in text:
            info['gender'] = '女'
        elif 'male' in text.lower():
            info['gender'] = 'Male'
        elif 'female' in text.lower():
            info['gender'] = 'Female'
        
        # Extract age
        age_patterns = [
            r'(\d+)[\s]*岁',
            r'年龄[：:]?\s*(\d+)',
            r'(\d+)[\s]*years?\s*old',
            r'age[\s:]+(\d+)',
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['age'] = int(match.group(1))
                break
        
        return info
    
    def extract_medical_fields(self, text: str) -> Dict[str, Any]:
        """Extract medical information fields."""
        fields = {}
        
        # Chief complaint / 主诉
        cc_patterns = [
            r'主诉[：:]?\s*([^。\n]+)',
            r'chief complaint[：:]?\s*([^。\n]+)',
            r'(?:主诉|complaint)[：:]?\s*([^。\n]{3,50})',
        ]
        for pattern in cc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['chief_complaint'] = match.group(1).strip()
                break
        
        # Diagnosis / 诊断
        dx_patterns = [
            r'诊断[：:]?\s*([^。\n]+)',
            r'初步诊断[：:]?\s*([^。\n]+)',
            r'diagnosis[：:]?\s*([^。\n]+)',
        ]
        for pattern in dx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['diagnosis'] = match.group(1).strip()
                break
        
        # Treatment plan / 治疗方案
        tx_patterns = [
            r'(?:治疗|处理|方案)[：:]?\s*([^。\n]+)',
            r'治疗计划[：:]?\s*([^。\n]+)',
            r'treatment[：:]?\s*([^。\n]+)',
        ]
        for pattern in tx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['treatment_plan'] = match.group(1).strip()
                break
        
        # Medications / 药物
        med_patterns = [
            r'(?:药物|用药|处方)[：:]?\s*([^。\n]+)',
            r'(?:开|给予)[：:]?\s*([^。\n]+?)(?:口服|注射|外用)',
            r'medication[：:]?\s*([^。\n]+)',
        ]
        for pattern in med_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['medications'] = match.group(1).strip()
                break
        
        # Physical examination / 体格检查
        pe_patterns = [
            r'(?:体格检查|查体|体检)[：:]?\s*([^。\n]+)',
            r'physical examination[：:]?\s*([^。\n]+)',
        ]
        for pattern in pe_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['physical_examination'] = match.group(1).strip()
                break
        
        # History / 病史
        hx_patterns = [
            r'(?:现病史|病史)[：:]?\s*([^。\n]+)',
            r'history of present illness[：:]?\s*([^。\n]+)',
        ]
        for pattern in hx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['history_present_illness'] = match.group(1).strip()
                break
        
        return fields
    
    def structure_record(self, text: str) -> Dict[str, Any]:
        """
        Main method to structure a medical record.
        Returns standardized EMR format.
        """
        # Extract all information
        patient_info = self.extract_patient_info(text)
        medical_fields = self.extract_medical_fields(text)
        
        # Merge into standard format
        structured = {
            "emr_version": "1.0",
            "record_id": f"EMR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "record_date": datetime.now().isoformat(),
            "patient_demographics": {
                "name": patient_info.get('patient_name', 'Unknown'),
                "gender": patient_info.get('gender', 'Unknown'),
                "age": patient_info.get('age', None),
            },
            "clinical_information": {
                "chief_complaint": medical_fields.get('chief_complaint', ''),
                "history_of_present_illness": medical_fields.get('history_present_illness', ''),
                "past_medical_history": medical_fields.get('past_medical_history', ''),
                "physical_examination": medical_fields.get('physical_examination', ''),
            },
            "assessment_and_plan": {
                "diagnosis": medical_fields.get('diagnosis', ''),
                "treatment_plan": medical_fields.get('treatment_plan', ''),
                "medications": medical_fields.get('medications', ''),
                "follow_up_instructions": medical_fields.get('follow_up', ''),
            },
            "metadata": {
                "source_text": text,
                "processed_at": datetime.now().isoformat(),
                "processor_version": "1.0.4"
            }
        }
        
        return structured
    
    def process(self, text: str, user_id: str = "") -> Dict[str, Any]:
        """
        Full processing pipeline with SkillPay billing and free trial support.
        """
        if not user_id:
            return {
                "success": False,
                "error": "User ID is required"
            }
        
        # Check free trial status
        trial_remaining = self.trial.get_trial_remaining(user_id)
        
        if trial_remaining > 0:
            # Free trial mode - no billing
            self.trial.use_trial(user_id)
            structured_record = self.structure_record(text)
            
            return {
                "success": True,
                "trial_mode": True,
                "trial_remaining": trial_remaining - 1,
                "balance": None,
                "structured_record": structured_record
            }
        
        # Normal billing mode
        # Step 1: Check balance first
        balance = self.billing.check_balance(user_id)
        if balance < DEFAULT_PRICE:
            payment_url = self.billing.get_payment_link(user_id, DEFAULT_PRICE)
            return {
                "success": False,
                "trial_mode": False,
                "trial_remaining": 0,
                "error": "Insufficient balance",
                "balance": balance,
                "paymentUrl": payment_url,
            }
        
        # Step 2: Charge user
        charge_result = self.billing.charge_user(user_id, DEFAULT_PRICE)
        
        if not charge_result.get('ok'):
            return {
                "success": False,
                "trial_mode": False,
                "trial_remaining": 0,
                "error": "Payment failed",
                "balance": charge_result.get('balance', 0),
                "paymentUrl": charge_result.get('paymentUrl'),
            }
        
        # Step 3: Structure the record
        structured_record = self.structure_record(text)
        
        return {
            "success": True,
            "trial_mode": False,
            "trial_remaining": 0,
            "balance": charge_result.get('balance'),
            "structured_record": structured_record
        }


def process_medical_record(input_text: str, user_id: str = "", api_key: str = BILLING_API_KEY) -> Dict[str, Any]:
    """
    Convenience function for processing medical records.
    """
    processor = MedicalRecordStructurer(api_key)
    return processor.process(input_text, user_id)


def main():
    parser = argparse.ArgumentParser(description='Medical Record Structurer')
    parser.add_argument('--input', '-i', required=True, help='Input medical record text')
    parser.add_argument('--user-id', '-u', required=True, help='User ID for billing')
    parser.add_argument('--api-key', '-k', default=BILLING_API_KEY, help='SkillPay API key')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Use environment variable if not provided
    api_key = args.api_key or os.environ.get('SKILLPAY_API_KEY', '')
    
    # Process the record
    result = process_medical_record(args.input, args.user_id, api_key)
    
    # Output result
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Result saved to: {args.output}")
    else:
        print(output_json)
    
    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
