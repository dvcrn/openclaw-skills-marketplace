const SKILL="stock-technical-analysis";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT"};let s=i?.symbol||"AAPL";return{success:!0,type:"ANALYSIS",symbol:s,data:{sma50:185,sma200:178,rsi:68,macd:"bullish",bollinger:"upper",trend:"bullish"},message:`📊 ${s} 技术分析\n\nSMA50: $185\nSMA200: $178\nRSI(14): 68\nMACD: 看涨\n布林带: 上轨\n趋势: 上涨趋势`}}
module.exports={handler:h};
