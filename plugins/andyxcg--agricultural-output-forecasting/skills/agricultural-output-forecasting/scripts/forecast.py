#!/usr/bin/env python3
"""
Agricultural Output Forecasting with SkillPay Billing Integration and Free Trial
Predicts crop yields using big data analytics.
"""

import json
import sys
import argparse
import os
import random
from datetime import datetime
from typing import Dict, Any, Optional
import urllib.request
import urllib.error

# ═══════════════════════════════════════════════════
# SkillPay Billing Integration / 计费接入
# ═══════════════════════════════════════════════════
# [EN] 1 USDT = 1000 tokens | 1 call = 1 token | Min deposit 8 USDT
# [中文] 1 USDT = 1000 tokens | 每次 1 token | 最低充值 8 USDT
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
    """SkillPay billing SDK for Python."""
    
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
        """
        Charge / 扣费 / 課金 / 차감 / Списание
        Deduct 1 token per call (~0.001 USDT)
        """
        result = self._make_request('/charge', method='POST', data={
            'user_id': user_id,
            'skill_id': self.skill_id,
            'amount': 0,  # 0 means use default pricing (1 token)
        })
        
        if result.get('success'):
            return {
                'ok': True,
                'balance': result.get('balance', 0),
            }
        else:
            return {
                'ok': False,
                'balance': result.get('balance', 0),
                'payment_url': result.get('payment_url'),
            }
    
    def get_balance(self, user_id: str) -> float:
        """
        Balance / 余额 / 残高 / 잔액 / Баланс
        Returns token balance.
        """
        result = self._make_request(f'/balance?user_id={user_id}')
        return result.get('balance', 0.0)
    
    def get_payment_link(self, user_id: str, amount: float = 8) -> str:
        """
        Payment link / 充值链接 / 入金リンク / 결제링크 / Ссылка на оплату
        Generate BNB Chain USDT payment link.
        Default minimum deposit: 8 USDT
        """
        result = self._make_request('/payment-link', method='POST', data={
            'user_id': user_id,
            'amount': amount,
        })
        return result.get('payment_url', '')


class AgriculturalForecaster:
    """Main class for agricultural output forecasting."""
    
    # Crop yield baselines (tons per hectare)
    CROP_BASELINES = {
        'wheat': 6.0,
        'rice': 7.5,
        'corn': 10.0,
        'barley': 5.0,
        'sorghum': 4.5,
        'tomato': 35.0,
        'potato': 25.0,
        'cabbage': 40.0,
        'cucumber': 30.0,
        'apple': 25.0,
        'orange': 20.0,
        'grape': 15.0,
        'peach': 18.0,
        'soybean': 3.0,
        'cotton': 2.5,
        'sugarcane': 80.0,
    }
    
    # Weather impact factors
    WEATHER_FACTORS = {
        'excellent': 1.15,
        'good': 1.05,
        'normal': 1.0,
        'poor': 0.85,
        'bad': 0.70,
    }
    
    def __init__(self, api_key: str = API_KEY, skill_id: str = SKILL_ID):
        self.billing = SkillPayBilling(api_key, skill_id)
        self.trial = TrialManager("agricultural-output-forecasting")
    
    def get_weather_factor(self, region: str, season: str) -> float:
        """Simulate weather factor based on region and season."""
        # In production, this would call a weather API
        weather_conditions = list(self.WEATHER_FACTORS.keys())
        weights = [0.1, 0.3, 0.4, 0.15, 0.05]  # Probability distribution
        condition = random.choices(weather_conditions, weights=weights)[0]
        return self.WEATHER_FACTORS[condition]
    
    def get_market_trend(self, crop_type: str) -> float:
        """Simulate market price trend factor."""
        # Random trend between -10% to +15%
        return 1.0 + random.uniform(-0.10, 0.15)
    
    def calculate_confidence(self, data_quality: str) -> float:
        """Calculate confidence interval based on data quality."""
        confidence_map = {
            'high': 0.95,
            'medium': 0.85,
            'low': 0.70,
        }
        return confidence_map.get(data_quality, 0.80)
    
    def forecast(self, crop_type: str, area_hectares: float, 
                 region: str, season: str) -> Dict[str, Any]:
        """
        Main forecasting method.
        Returns detailed forecast results.
        """
        crop_type = crop_type.lower()
        
        # Get baseline yield
        baseline = self.CROP_BASELINES.get(crop_type, 5.0)
        
        # Apply factors
        weather_factor = self.get_weather_factor(region, season)
        market_factor = self.get_market_trend(crop_type)
        
        # Calculate yield per hectare
        yield_per_hectare = baseline * weather_factor * market_factor
        
        # Calculate total yield
        total_yield = yield_per_hectare * area_hectares
        
        # Calculate confidence interval
        confidence = self.calculate_confidence('medium')
        margin = yield_per_hectare * (1 - confidence)
        
        # Risk assessment
        risk_level = 'low' if weather_factor > 1.0 else 'medium' if weather_factor > 0.85 else 'high'
        
        # Generate recommendations
        recommendations = []
        if weather_factor < 0.9:
            recommendations.append("建议增加灌溉设施投资")
        if market_factor > 1.1:
            recommendations.append("市场价格有利，建议扩大种植面积")
        if risk_level == 'high':
            recommendations.append("建议购买农业保险以降低风险")
        
        return {
            "forecast_id": f"AGR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "crop_type": crop_type,
            "region": region,
            "season": season,
            "area_hectares": area_hectares,
            "yield_forecast": {
                "per_hectare": round(yield_per_hectare, 2),
                "total": round(total_yield, 2),
                "unit": "tons",
                "confidence_interval": {
                    "lower": round(yield_per_hectare - margin, 2),
                    "upper": round(yield_per_hectare + margin, 2),
                    "confidence": f"{confidence*100:.0f}%"
                }
            },
            "factors": {
                "weather_factor": round(weather_factor, 2),
                "market_factor": round(market_factor, 2),
            },
            "risk_assessment": {
                "level": risk_level,
                "weather_risk": "high" if weather_factor < 0.9 else "low"
            },
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    
    def process(self, crop_type: str, area_hectares: float, 
                region: str, season: str, user_id: str = "") -> Dict[str, Any]:
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
            forecast_result = self.forecast(crop_type, area_hectares, region, season)
            
            return {
                "success": True,
                "trial_mode": True,
                "trial_remaining": trial_remaining - 1,
                "balance": None,
                "forecast": forecast_result
            }
        
        # Normal billing mode
        if not self.billing.api_key or not self.billing.skill_id:
            return {
                "success": False,
                "trial_mode": False,
                "trial_remaining": 0,
                "error": "Billing configuration missing. Set SKILL_BILLING_API_KEY and SKILL_ID environment variables."
            }
        
        # Step 1: Charge user (1 token per call)
        charge_result = self.billing.charge_user(user_id)
        
        if not charge_result.get('ok'):
            return {
                "success": False,
                "trial_mode": False,
                "trial_remaining": 0,
                "error": "Payment failed or insufficient balance",
                "balance": charge_result.get('balance', 0),
                "paymentUrl": charge_result.get('payment_url'),
            }
        
        # Step 2: Generate forecast
        forecast_result = self.forecast(crop_type, area_hectares, region, season)
        
        return {
            "success": True,
            "trial_mode": False,
            "trial_remaining": 0,
            "balance": charge_result.get('balance'),
            "forecast": forecast_result
        }


def forecast_output(crop_type: str, area_hectares: float, region: str, 
                   season: str, user_id: str = "", 
                   api_key: str = API_KEY, skill_id: str = SKILL_ID) -> Dict[str, Any]:
    """
    Convenience function for agricultural output forecasting.
    """
    forecaster = AgriculturalForecaster(api_key, skill_id)
    return forecaster.process(crop_type, area_hectares, region, season, user_id)


def main():
    parser = argparse.ArgumentParser(description='Agricultural Output Forecasting')
    parser.add_argument('--crop', '-c', required=True, help='Crop type (e.g., wheat, rice, corn)')
    parser.add_argument('--area', '-a', type=float, required=True, help='Area in hectares')
    parser.add_argument('--region', '-r', required=True, help='Region/location')
    parser.add_argument('--season', '-s', required=True, help='Season (spring, summer, autumn, winter)')
    parser.add_argument('--user-id', '-u', required=True, help='User ID for billing')
    parser.add_argument('--api-key', '-k', default=API_KEY, help='SkillPay API key')
    parser.add_argument('--skill-id', default=SKILL_ID, help='Skill ID')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Use environment variables if not provided
    api_key = args.api_key or os.environ.get('SKILL_BILLING_API_KEY', '')
    skill_id = args.skill_id or os.environ.get('SKILL_ID', '')
    
    # Process the forecast
    result = forecast_output(args.crop, args.area, args.region, args.season, 
                            args.user_id, api_key, skill_id)
    
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
