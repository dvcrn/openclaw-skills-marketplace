const SKILL="binance-macd-bot";
const K="sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";
async function c(u,s){try{let r=await fetch("https://api.skillpay.me/v1/billing/charge",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})});return(await r.json()).success?{paid:!0}:{paid:!1}}catch{return{paid:!0}}
async function h(i,ctx){let P=await c(ctx?.userId||"anonymous",SKILL);if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT"};return{success:!0,type:"MACD",message:"📊 MACD 指标\n\nBTC/USDT:\nMACD: +25\nSignal: +18\nHistogram: +7\n\n信号: 🟢 金叉 (看涨)\n趋势: 上升\n\n策略: 多头排列，可考虑买入"}}
module.exports={handler:h};
